"""Tests for telemetry message creation."""

from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.message_factory import create_telemetry_message
from app.models import (
    ElectricalMeasurements,
    Substation,
    TelemetryStatus,
    TransformerProfile,
)


def create_profile() -> TransformerProfile:
    """Create a transformer profile for message factory tests."""

    substation = Substation(
        code="PLZEN-NORTH",
        name="Plzen North Substation",
        city="Plzen",
    )

    return TransformerProfile(
        code="TRF-PLN-01",
        name="Transformer PLN 01",
        substation=substation,
        nominal_voltage_v=400.0,
        rated_power_kva=630.0,
        base_load_ratio=0.6,
        base_temperature_c=40.0,
    )


def create_normal_measurements() -> ElectricalMeasurements:
    """Create normal transformer measurements."""

    return ElectricalMeasurements(
        voltage_v=400.0,
        current_a=500.0,
        frequency_hz=50.0,
        power_factor=0.95,
        active_power_kw=329.09,
        temperature_c=45.0,
    )


def test_message_contains_profile_and_measurement_values() -> None:
    profile = create_profile()
    measurements = create_normal_measurements()

    message = create_telemetry_message(
        profile=profile,
        measurements=measurements,
        sequence=1,
    )

    assert message.station_code == profile.substation.code
    assert message.device_code == profile.code
    assert message.sequence == 1
    assert message.voltage_v == measurements.voltage_v
    assert message.current_a == measurements.current_a
    assert message.frequency_hz == measurements.frequency_hz
    assert message.power_factor == measurements.power_factor
    assert message.active_power_kw == measurements.active_power_kw
    assert message.temperature_c == measurements.temperature_c
    assert message.status == TelemetryStatus.NORMAL
    assert message.simulated is True


def test_explicit_timestamp_and_message_id_are_preserved() -> None:
    timestamp = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
    message_id = UUID("12345678-1234-5678-1234-567812345678")

    message = create_telemetry_message(
        profile=create_profile(),
        measurements=create_normal_measurements(),
        sequence=5,
        timestamp=timestamp,
        message_id=message_id,
    )

    assert message.timestamp == timestamp
    assert message.message_id == message_id
    assert message.sequence == 5


def test_missing_timestamp_and_id_are_generated_automatically() -> None:
    before_creation = datetime.now(timezone.utc)

    message = create_telemetry_message(
        profile=create_profile(),
        measurements=create_normal_measurements(),
        sequence=1,
    )

    after_creation = datetime.now(timezone.utc)

    assert before_creation <= message.timestamp <= after_creation
    assert isinstance(message.message_id, UUID)
    assert message.timestamp.tzinfo is not None


def test_critical_measurements_produce_critical_status() -> None:
    measurements = ElectricalMeasurements(
        voltage_v=400.0,
        current_a=500.0,
        frequency_hz=50.0,
        power_factor=0.95,
        active_power_kw=329.09,
        temperature_c=100.0,
    )

    message = create_telemetry_message(
        profile=create_profile(),
        measurements=measurements,
        sequence=1,
    )

    assert message.status == TelemetryStatus.CRITICAL


def test_invalid_sequence_is_rejected() -> None:
    with pytest.raises(ValidationError):
        create_telemetry_message(
            profile=create_profile(),
            measurements=create_normal_measurements(),
            sequence=0,
        )