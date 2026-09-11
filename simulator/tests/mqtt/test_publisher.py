"""Tests for the MQTT telemetry publisher."""

import json
from datetime import datetime, timezone
from uuid import UUID

import paho.mqtt.client as mqtt
import pytest

import app.mqtt.publisher as mqtt_publisher_module
from app.mqtt.publisher import MqttTelemetryPublisher
from app.mqtt.settings import MqttSettings
from app.models import TelemetryStatus
from app.telemetry import TelemetryMessage


class FakeReasonCode:
    """Represent an MQTT connection reason code in tests."""

    def __init__(self, is_failure: bool = False) -> None:
        self.is_failure = is_failure

    def __str__(self) -> str:
        if self.is_failure:
            return "Not authorized"

        return "Success"


class FakePublishResult:
    """Represent the result of a fake MQTT publish operation."""

    def __init__(self, rc: int = mqtt.MQTT_ERR_SUCCESS, published: bool = True) -> None:
        self.rc = rc
        self._published = published
        self.wait_timeout: float | None = None

    def wait_for_publish(self, timeout: float | None = None) -> None:
        self.wait_timeout = timeout

    def is_published(self) -> bool:
        return self._published


class FakeMqttClient:
    """Provide controllable MQTT client behaviour for unit tests."""

    def __init__(self, callback_api_version: mqtt.CallbackAPIVersion, client_id: str) -> None:
        self.callback_api_version = callback_api_version
        self.client_id = client_id
        self.on_connect = None

        self.connect_result = mqtt.MQTT_ERR_SUCCESS
        self.connection_is_failure = False
        self.acknowledge_connection = True
        self.publish_result = FakePublishResult()

        self.connect_arguments: tuple[str, int, int] | None = None
        self.publish_arguments: tuple[str, str, int, bool] | None = None
        self.connect_call_count = 0
        self.loop_started = False
        self.loop_stopped = False
        self.disconnected = False

    def connect(self, host: str, port: int, keepalive: int) -> int:
        self.connect_call_count += 1
        self.connect_arguments = (host, port, keepalive)

        return self.connect_result

    def loop_start(self) -> None:
        self.loop_started = True

        if self.acknowledge_connection and self.on_connect is not None:
            self.on_connect(self, None, None, FakeReasonCode(self.connection_is_failure), None)

    def publish(self, topic: str, payload: str, qos: int, retain: bool) -> FakePublishResult:
        self.publish_arguments = (topic, payload, qos, retain)

        return self.publish_result

    def disconnect(self) -> int:
        self.disconnected = True

        return mqtt.MQTT_ERR_SUCCESS

    def loop_stop(self) -> None:
        self.loop_stopped = True


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> FakeMqttClient:
    client = FakeMqttClient(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="power-grid-simulator")

    def create_fake_client(callback_api_version: mqtt.CallbackAPIVersion, client_id: str) -> FakeMqttClient:
        client.callback_api_version = callback_api_version
        client.client_id = client_id

        return client
    # Replace the real Paho MQTT client in the publisher module so the test
    # can verify publisher behaviour without opening a network connection.
    monkeypatch.setattr(mqtt_publisher_module.mqtt, "Client", create_fake_client)

    return client


@pytest.fixture
def telemetry_message() -> TelemetryMessage:
    return TelemetryMessage(
        message_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc),
        station_code="PLZEN-NORTH",
        device_code="TRF-PLN-01",
        sequence=1,
        voltage_v=400.0,
        current_a=100.0,
        frequency_hz=50.0,
        power_factor=0.95,
        active_power_kw=65.818,
        temperature_c=45.0,
        status=TelemetryStatus.NORMAL,
    )


def test_connect_starts_network_loop_and_waits_for_broker(fake_client: FakeMqttClient) -> None:
    publisher = MqttTelemetryPublisher(MqttSettings())

    publisher.connect()

    assert fake_client.connect_arguments == ("mqtt", 1883, 60)
    assert fake_client.loop_started is True


def test_connect_is_idempotent(fake_client: FakeMqttClient) -> None:
    publisher = MqttTelemetryPublisher(MqttSettings())

    publisher.connect()
    publisher.connect()

    assert fake_client.connect_call_count == 1


def test_rejected_connection_stops_network_loop(fake_client: FakeMqttClient) -> None:
    fake_client.connection_is_failure = True
    publisher = MqttTelemetryPublisher(MqttSettings())

    with pytest.raises(ConnectionError, match="MQTT broker rejected the connection"):
        publisher.connect()

    assert fake_client.loop_stopped is True


def test_connection_timeout_stops_network_loop(fake_client: FakeMqttClient) -> None:
    fake_client.acknowledge_connection = False
    settings = MqttSettings(connection_timeout_seconds=0.01)
    publisher = MqttTelemetryPublisher(settings)

    with pytest.raises(TimeoutError, match="MQTT broker did not acknowledge the connection"):
        publisher.connect()

    assert fake_client.loop_stopped is True


def test_publish_sends_serialized_message(fake_client: FakeMqttClient, telemetry_message: TelemetryMessage) -> None:
    settings = MqttSettings(qos=1, publish_timeout_seconds=3.0)
    publisher = MqttTelemetryPublisher(settings)
    publisher.connect()
    publisher.publish(telemetry_message)

    assert fake_client.publish_arguments is not None

    topic, payload, qos, retain = fake_client.publish_arguments

    assert topic == (
        "grid/stations/PLZEN-NORTH/"
        "devices/TRF-PLN-01/telemetry"
    )
    assert json.loads(payload)["messageId"] == ("12345678-1234-5678-1234-567812345678")
    assert qos == 1
    assert retain is False
    assert fake_client.publish_result.wait_timeout == 3.0


def test_publish_requires_active_connection(fake_client: FakeMqttClient, telemetry_message: TelemetryMessage) -> None:
    publisher = MqttTelemetryPublisher(MqttSettings())

    with pytest.raises(RuntimeError, match="MQTT publisher is not connected"):
        publisher.publish(telemetry_message)


def test_publish_error_is_reported(fake_client: FakeMqttClient, telemetry_message: TelemetryMessage) -> None:
    fake_client.publish_result = FakePublishResult(rc=mqtt.MQTT_ERR_NO_CONN)
    publisher = MqttTelemetryPublisher(MqttSettings())
    publisher.connect()

    with pytest.raises(RuntimeError, match="MQTT publish failed"):
        publisher.publish(telemetry_message)


def test_publish_acknowledgement_timeout_is_reported(fake_client: FakeMqttClient, telemetry_message: TelemetryMessage) -> None:
    fake_client.publish_result = FakePublishResult(published=False)
    publisher = MqttTelemetryPublisher(MqttSettings())
    publisher.connect()

    with pytest.raises(TimeoutError, match="MQTT broker did not acknowledge the message"):
        publisher.publish(telemetry_message)


def test_close_disconnects_and_stops_network_loop(fake_client: FakeMqttClient) -> None:
    publisher = MqttTelemetryPublisher(MqttSettings())
    publisher.connect()
    publisher.close()

    assert fake_client.disconnected is True
    assert fake_client.loop_stopped is True


def test_immediate_connection_failure_is_reported(fake_client: FakeMqttClient) -> None:
    fake_client.connect_result = mqtt.MQTT_ERR_NO_CONN
    publisher = MqttTelemetryPublisher(MqttSettings())

    with pytest.raises(ConnectionError, match="MQTT connection failed"):
        publisher.connect()

    assert fake_client.loop_started is False


def test_connect_failure_does_not_start_network_loop(fake_client: FakeMqttClient) -> None:
    fake_client.connect_result = mqtt.MQTT_ERR_NO_CONN
    publisher = MqttTelemetryPublisher(MqttSettings())

    with pytest.raises(ConnectionError, match="MQTT connection failed"):
        publisher.connect()

    assert fake_client.loop_started is False