"""Creation of public telemetry messages."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.classification import classify_measurements
from app.models import ElectricalMeasurements, TransformerProfile
from app.telemetry import TelemetryMessage


def create_telemetry_message(
    profile: TransformerProfile, measurements: ElectricalMeasurements,
    sequence: int,
    timestamp: datetime | None = None,
    message_id: UUID | None = None,
    ) -> TelemetryMessage:
    
    """Create a validated telemetry message from generated measurements."""
    
    telemetry_status = classify_measurements(profile=profile, measurements=measurements)
    message_timestamp = timestamp or datetime.now(timezone.utc)
    unique_message_id = message_id or uuid4()

    return TelemetryMessage(
        message_id=unique_message_id,
        timestamp=message_timestamp,
        station_code=profile.substation.code,
        device_code=profile.code,
        sequence=sequence,
        voltage_v=measurements.voltage_v,
        current_a=measurements.current_a,
        frequency_hz=measurements.frequency_hz,
        power_factor=measurements.power_factor,
        active_power_kw=measurements.active_power_kw,
        temperature_c=measurements.temperature_c,
        status=telemetry_status,
    )