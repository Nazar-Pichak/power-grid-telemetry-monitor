"""Tests for the public telemetry contract."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models import TelemetryStatus
from app.telemetry import TelemetryMessage


def create_valid_message_data() -> dict[str, object]:
    """Return valid input data for one telemetry message."""

    return {
        "message_id": uuid4(),
        "timestamp": datetime.now(timezone.utc),
        "station_code": "PLZEN-NORTH",
        "device_code": "TRF-PLN-01",
        "sequence": 1,
        "voltage_v": 400.0,
        "current_a": 250.0,
        "frequency_hz": 50.0,
        "power_factor": 0.95,
        "active_power_kw": 164.5,
        "temperature_c": 45.0,
        "status": TelemetryStatus.NORMAL,
        "simulated": True,
    }


def test_valid_telemetry_message_is_created() -> None:
    data = create_valid_message_data()

    message = TelemetryMessage(**data)

    assert message.schema_version == "1.0"
    assert isinstance(message.message_id, UUID)
    assert message.device_code == "TRF-PLN-01"
    assert message.status == TelemetryStatus.NORMAL
    assert message.simulated is True


def test_public_serialization_uses_camel_case_aliases() -> None:
    message = TelemetryMessage(**create_valid_message_data())
    serialized = message.model_dump(by_alias=True)

    assert serialized["schemaVersion"] == "1.0"
    assert serialized["messageId"] == message.message_id
    assert serialized["stationCode"] == "PLZEN-NORTH"
    assert serialized["deviceCode"] == "TRF-PLN-01"
    assert serialized["voltageV"] == 400.0
    assert serialized["powerFactor"] == 0.95

    assert "schema_version" not in serialized
    assert "device_code" not in serialized


def test_timestamp_without_timezone_is_rejected() -> None:
    data = create_valid_message_data()
    data["timestamp"] = datetime(2026, 9, 9, 12, 0)

    with pytest.raises(ValidationError, match="Timestamp must include timezone information"):
        TelemetryMessage(**data)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("station_code", "plzen-north"),
        ("device_code", "PLN-01"),
        ("sequence", 0),
        ("voltage_v", 0),
        ("current_a", -1),
        ("frequency_hz", 0),
        ("power_factor", 0),
        ("power_factor", 1.1),
        ("active_power_kw", -1),
        ("temperature_c", -274),
    ],
)
def test_invalid_measurement_values_are_rejected(field_name: str, invalid_value: object) -> None:
    data = create_valid_message_data()
    data[field_name] = invalid_value

    with pytest.raises(ValidationError):
        TelemetryMessage(**data)


def test_telemetry_message_is_immutable() -> None:
    message = TelemetryMessage(**create_valid_message_data())

    with pytest.raises(ValidationError):
        message.sequence = 2