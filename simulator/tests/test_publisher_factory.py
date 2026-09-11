"""Tests for telemetry publisher creation."""
from typing import cast
import pytest

from app.console_publisher import ConsoleTelemetryPublisher
from app.mqtt.publisher import MqttTelemetryPublisher
from app.publisher_factory import create_telemetry_publisher
from app.transport import PublisherTransport


def test_console_transport_creates_console_publisher() -> None:
    publisher = create_telemetry_publisher(transport=PublisherTransport.CONSOLE)

    assert isinstance(publisher, ConsoleTelemetryPublisher)


def test_mqtt_transport_creates_mqtt_publisher() -> None:
    publisher = create_telemetry_publisher(transport=PublisherTransport.MQTT)

    assert isinstance(publisher, MqttTelemetryPublisher)


def test_unsupported_transport_is_rejected() -> None:
    unsupported_transport = cast(PublisherTransport, "unsupported")

    with pytest.raises(ValueError, match="Unsupported telemetry transport"):
        create_telemetry_publisher(transport=unsupported_transport)