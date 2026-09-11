"""MQTT output adapter for telemetry messages."""

from threading import Event

import paho.mqtt.client as mqtt

from app.mqtt.settings import MqttSettings
from app.mqtt.topic import create_telemetry_topic
from app.serialization import serialize_telemetry_message
from app.telemetry import TelemetryMessage


class MqttTelemetryPublisher:
    """Publish telemetry messages through an MQTT broker."""

    def __init__(self, settings: MqttSettings) -> None:
        """Initialize the publisher without opening a connection."""

        self._settings = settings
        self._connected_event = Event()
        self._connection_error: str | None = None
        self._network_loop_started = False
        self._connected = False

        self._client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=settings.client_id)
        self._client.on_connect = self._on_connect

    def _on_connect(self, client: mqtt.Client, userdata: object, flags: mqtt.ConnectFlags, reason_code: mqtt.ReasonCode, properties: mqtt.Properties | None) -> None:
        """Record the broker response received by the network loop."""

        del client, userdata, flags, properties

        if reason_code.is_failure:
            self._connection_error = str(reason_code)
        else:
            self._connected = True

        # connect() waits for this event because mqtt.Client.connect()
        # opens the socket but does not wait for the MQTT CONNACK packet.
        self._connected_event.set()

    def connect(self) -> None:
        """Connect to the MQTT broker and wait for its acknowledgement."""

        if self._connected:
            return

        self._connected_event.clear()
        self._connection_error = None

        result = self._client.connect(host=self._settings.host, port=self._settings.port, keepalive=self._settings.keepalive_seconds)

        if result != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectionError(f"MQTT connection failed: {mqtt.error_string(result)}")

        self._client.loop_start()
        self._network_loop_started = True

        connection_completed = self._connected_event.wait(timeout=self._settings.connection_timeout_seconds)

        if not connection_completed:
            self.close()
            raise TimeoutError("MQTT broker did not acknowledge the connection in time.")

        if self._connection_error is not None:
            connection_error = self._connection_error
            self.close()
            raise ConnectionError(f"MQTT broker rejected the connection: {connection_error}")

    def publish(self, message: TelemetryMessage) -> None:
        """Serialize and publish one telemetry message."""

        if not self._connected:
            raise RuntimeError("MQTT publisher is not connected.")

        topic = create_telemetry_topic(message)
        payload = serialize_telemetry_message(message)

        publish_result = self._client.publish(topic=topic, payload=payload, qos=self._settings.qos, retain=False)

        if publish_result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT publish failed: {mqtt.error_string(publish_result.rc)}")

        # QoS 1 completes only after the broker sends PUBACK.
        publish_result.wait_for_publish(timeout=self._settings.publish_timeout_seconds)

        if not publish_result.is_published():
            raise TimeoutError("MQTT broker did not acknowledge the message in time.")

    def close(self) -> None:
        """Disconnect from MQTT and stop the background network loop."""

        if self._connected:
            self._client.disconnect()

        if self._network_loop_started:
            self._client.loop_stop()

        self._connected = False
        self._network_loop_started = False