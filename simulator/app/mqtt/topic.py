"""Construction of MQTT topics for telemetry messages."""

from app.telemetry import TelemetryMessage


def create_telemetry_topic(message: TelemetryMessage) -> str:
    """Create a device-specific MQTT topic for one telemetry message."""

    return (
        f"grid/stations/{message.station_code}"
        f"/devices/{message.device_code}/telemetry"
    )