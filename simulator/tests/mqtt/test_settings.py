"""Tests for MQTT publisher configuration."""

import pytest

from app.mqtt.settings import MqttSettings


def test_default_mqtt_settings_are_valid() -> None:
    settings = MqttSettings()

    assert settings.host == "mqtt"
    assert settings.port == 1883
    assert settings.client_id == "power-grid-simulator"
    assert settings.qos == 1
    assert settings.keepalive_seconds == 60
    assert settings.connection_timeout_seconds == 10.0
    assert settings.publish_timeout_seconds == 10.0


@pytest.mark.parametrize("host", ["", " ", "\t"])
def test_empty_mqtt_host_is_rejected(host: str) -> None:
    with pytest.raises(ValueError, match="MQTT host cannot be empty"):
        MqttSettings(host=host)


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_invalid_mqtt_port_is_rejected(port: int) -> None:
    with pytest.raises(ValueError, match="MQTT port must be between 1 and 65535"):
        MqttSettings(port=port)


@pytest.mark.parametrize("client_id", ["", " ", "\t"])
def test_empty_mqtt_client_id_is_rejected(client_id: str) -> None:
    with pytest.raises(ValueError, match="MQTT client ID cannot be empty"):
        MqttSettings(client_id=client_id)


@pytest.mark.parametrize("qos", [-1, 3])
def test_invalid_mqtt_qos_is_rejected(qos: int) -> None:
    with pytest.raises(ValueError, match="MQTT QoS must be 0, 1, or 2"):
        MqttSettings(qos=qos)


@pytest.mark.parametrize("keepalive_seconds", [0, -1])
def test_non_positive_keepalive_is_rejected(keepalive_seconds: int) -> None:
    with pytest.raises(ValueError, match="MQTT keepalive must be greater than zero"):
        MqttSettings(keepalive_seconds=keepalive_seconds)


@pytest.mark.parametrize("publish_timeout_seconds", [0.0, -1.0])
def test_non_positive_publish_timeout_is_rejected(publish_timeout_seconds: float) -> None:
    with pytest.raises(ValueError, match="MQTT publish timeout must be greater than zero"):
        MqttSettings(publish_timeout_seconds=publish_timeout_seconds)

@pytest.mark.parametrize("connection_timeout_seconds", [0.0, -1.0])
def test_non_positive_connection_timeout_is_rejected(connection_timeout_seconds: float) -> None:
    with pytest.raises(ValueError, match="MQTT connection timeout must be greater than zero"):
        MqttSettings(connection_timeout_seconds=connection_timeout_seconds)