"""Tests for telemetry status classification."""

import pytest

from app.classification import classify_measurements
from app.models import (
    ElectricalMeasurements,
    Substation,
    TelemetryStatus,
    TransformerProfile,
)


def create_profile() -> TransformerProfile:
    """Create a transformer profile for classification tests."""

    substation = Substation(code="PLZEN-NORTH", name="Plzen North Substation", city="Plzen")

    return TransformerProfile(
        code="TRF-PLN-01",
        name="Transformer PLN 01",
        substation=substation,
        nominal_voltage_v=400.0,
        rated_power_kva=630.0,
        base_load_ratio=0.6,
        base_temperature_c=25.0,
    )


def create_measurements(**overrides: float) -> ElectricalMeasurements:
    """Create measurements and optionally replace selected values."""

    values = {
        "voltage_v": 400.0,
        "current_a": 100.0,
        "frequency_hz": 50.0,
        "power_factor": 0.95,
        "active_power_kw": 65.818,
        "temperature_c": 25.0,
    }

    values.update(overrides)

    return ElectricalMeasurements(**values)


def test_normal_measurements_are_classified_as_normal() -> None:
    status = classify_measurements(profile=create_profile(), measurements=create_measurements())

    assert status == TelemetryStatus.NORMAL


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("voltage_v", 379.9),
        ("voltage_v", 420.1),
        ("current_a", 820.0),
        ("frequency_hz", 49.4),
        ("frequency_hz", 50.6),
        ("temperature_c", 80.1),
    ],
)
def test_warning_measurements_are_classified_as_warning(field_name: str, value: float) -> None:
    measurements = create_measurements(**{field_name: value})
    status = classify_measurements(profile=create_profile(), measurements=measurements)

    assert status == TelemetryStatus.WARNING


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("voltage_v", 359.9),
        ("voltage_v", 440.1),
        ("current_a", 960.0),
        ("frequency_hz", 48.9),
        ("frequency_hz", 51.1),
        ("temperature_c", 95.1),
    ],
)
def test_critical_measurements_are_classified_as_critical(field_name: str, value: float) -> None:
    measurements = create_measurements(**{field_name: value})
    status = classify_measurements(profile=create_profile(), measurements=measurements)

    assert status == TelemetryStatus.CRITICAL


def test_critical_condition_has_priority_over_warning() -> None:
    measurements = create_measurements(voltage_v=370.0, temperature_c=96.0)
    status = classify_measurements(profile=create_profile(), measurements=measurements)

    assert status == TelemetryStatus.CRITICAL