"""Tests for MQTT telemetry topic construction."""

from datetime import datetime, timezone
from uuid import UUID

from app.models import TelemetryStatus
from app.mqtt.topic import create_telemetry_topic
from app.telemetry import TelemetryMessage


def create_message() -> TelemetryMessage:
    """Create a valid telemetry message for topic tests."""

    return TelemetryMessage(
        message_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc),
        station_code="PLZEN-NORTH",
        device_code="TRF-PLN-01",
        sequence=1,
        voltage_v=400.0,
        current_a=200.0,
        frequency_hz=50.0,
        power_factor=0.95,
        active_power_kw=131.636,
        temperature_c=45.0,
        status=TelemetryStatus.NORMAL,
    )


def test_device_specific_telemetry_topic_is_created() -> None:
    topic = create_telemetry_topic(create_message())

    assert topic == (
        "grid/stations/PLZEN-NORTH/"
        "devices/TRF-PLN-01/telemetry"
    )