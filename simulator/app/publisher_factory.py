"""Creation of telemetry publishers based on the selected transport."""

from app.console_publisher import ConsoleTelemetryPublisher
from app.mqtt.publisher import MqttTelemetryPublisher
from app.mqtt.settings import MqttSettings
from app.publisher import TelemetryPublisher
from app.transport import PublisherTransport


def create_telemetry_publisher(transport: PublisherTransport, mqtt_settings: MqttSettings | None = None) -> TelemetryPublisher:
    """Create the publisher required by the selected transport."""

    if transport is PublisherTransport.CONSOLE:
        return ConsoleTelemetryPublisher()

    if transport is PublisherTransport.MQTT:
        return MqttTelemetryPublisher(settings=mqtt_settings or MqttSettings())

    raise ValueError(f"Unsupported telemetry transport: {transport}")