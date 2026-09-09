"""Tests for telemetry JSON serialization."""

import json
from datetime import datetime, timezone
from uuid import UUID

from app.models import TelemetryStatus
from app.serialization import serialize_telemetry_message
from app.telemetry import TelemetryMessage


def create_message() -> TelemetryMessage:
    """Create a telemetry message with deterministic values."""

    return TelemetryMessage(
        message_id=UUID("12345678-1234-5678-1234-567812345678"),
        timestamp=datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc),
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
        simulated=True,
    )


def test_serialization_produces_valid_json() -> None:
    result = serialize_telemetry_message(create_message())
    parsed_result = json.loads(result)

    assert isinstance(parsed_result, dict)


def test_serialization_uses_public_camel_case_field_names() -> None:
    result = serialize_telemetry_message(create_message())

    parsed_result = json.loads(result)

    assert parsed_result["schemaVersion"] == "1.0"
    assert parsed_result["messageId"] == ("12345678-1234-5678-1234-567812345678")
    assert parsed_result["stationCode"] == "PLZEN-NORTH"
    assert parsed_result["deviceCode"] == "TRF-PLN-01"
    assert parsed_result["frequencyHz"] == 50.0
    assert parsed_result["powerFactor"] == 0.95
    assert parsed_result["activePowerKw"] == 65.818
    assert parsed_result["temperatureC"] == 45.0

    assert "schema_version" not in parsed_result
    assert "device_code" not in parsed_result


def test_serialization_produces_one_compact_line() -> None:
    result = serialize_telemetry_message(create_message())

    assert "\n" not in result
    assert "\r" not in result
    assert ": " not in result
    assert result.startswith("{")
    assert result.endswith("}")