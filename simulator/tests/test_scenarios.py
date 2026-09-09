"""Tests for transformer operating scenarios."""

from random import Random
from typing import cast
from unittest.mock import Mock

import pytest

from app.calculations import (
    calculate_active_power_kw,
    calculate_apparent_power_kva,
    calculate_line_current_a,
)
from app.classification import classify_measurements
from app.models import (
    ElectricalMeasurements,
    Substation,
    TelemetryStatus,
    TransformerProfile,
)
from app.scenarios import (
    FaultScenario,
    apply_frequency_high,
    apply_overheating,
    apply_overload,
    apply_overvoltage,
    apply_scenario,
    apply_undervoltage,
)


def create_profile() -> TransformerProfile:
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


def create_measurements() -> ElectricalMeasurements:
    return ElectricalMeasurements(
        voltage_v=400.0,
        current_a=500.0,
        frequency_hz=50.0,
        power_factor=0.95,
        active_power_kw=329.09,
        temperature_c=45.0,
    )


def create_random_returning(value: float) -> Mock:
    random_generator = Mock(spec=Random)
    random_generator.uniform.return_value = value

    return random_generator


def test_normal_scenario_returns_original_measurements() -> None:
    measurements = create_measurements()

    result = apply_scenario(
        scenario=FaultScenario.NORMAL,
        profile=create_profile(),
        measurements=measurements,
        random_generator=Random(42),
    )

    assert result is measurements


def test_overvoltage_changes_voltage_and_recalculates_power() -> None:
    measurements = create_measurements()
    random_generator = create_random_returning(450.0)
    result = apply_overvoltage(measurements=measurements, random_generator=random_generator)

    expected_power = calculate_active_power_kw(
        voltage_v=450.0,
        current_a=measurements.current_a,
        power_factor=measurements.power_factor,
    )

    assert result.voltage_v == 450.0
    assert result.active_power_kw == expected_power
    assert measurements.voltage_v == 400.0
    random_generator.uniform.assert_called_once_with(444.0, 460.0)


def test_undervoltage_changes_voltage_and_recalculates_power() -> None:
    measurements = create_measurements()
    random_generator = create_random_returning(340.0)
    result = apply_undervoltage(measurements=measurements, random_generator=random_generator)

    expected_power = calculate_active_power_kw(
        voltage_v=340.0,
        current_a=measurements.current_a,
        power_factor=measurements.power_factor,
    )

    assert result.voltage_v == 340.0
    assert result.active_power_kw == expected_power
    assert measurements.voltage_v == 400.0
    random_generator.uniform.assert_called_once_with(330.0, 355.0)


def test_overload_recalculates_current_and_active_power() -> None:
    profile = create_profile()
    measurements = create_measurements()
    random_generator = create_random_returning(1.1)
    result = apply_overload(profile=profile, measurements=measurements, random_generator=random_generator)

    apparent_power = calculate_apparent_power_kva(
        rated_power_kva=profile.rated_power_kva,
        load_ratio=1.1,
    )
    expected_current = calculate_line_current_a(
        apparent_power_kva=apparent_power,
        voltage_v=measurements.voltage_v,
    )
    expected_power = calculate_active_power_kw(
        voltage_v=measurements.voltage_v,
        current_a=expected_current,
        power_factor=measurements.power_factor,
    )

    assert result.current_a == expected_current
    assert result.active_power_kw == expected_power
    assert measurements.current_a == 500.0
    random_generator.uniform.assert_called_once_with(1.08, 1.22)


def test_overheating_changes_only_temperature() -> None:
    measurements = create_measurements()
    random_generator = create_random_returning(100.0)
    result = apply_overheating(measurements=measurements, random_generator=random_generator)

    assert result.temperature_c == 100.0
    assert result.voltage_v == measurements.voltage_v
    assert result.current_a == measurements.current_a
    random_generator.uniform.assert_called_once_with(96.0, 112.0)


def test_frequency_high_changes_only_frequency() -> None:
    measurements = create_measurements()
    random_generator = create_random_returning(51.3)
    result = apply_frequency_high(measurements=measurements, random_generator=random_generator)

    assert result.frequency_hz == 51.3
    assert result.voltage_v == measurements.voltage_v
    assert result.current_a == measurements.current_a
    random_generator.uniform.assert_called_once_with(51.1, 51.6)


@pytest.mark.parametrize(
    ("scenario", "generated_value"),
    [
        (FaultScenario.OVERVOLTAGE, 450.0),
        (FaultScenario.UNDERVOLTAGE, 340.0),
        (FaultScenario.OVERLOAD, 1.1),
        (FaultScenario.OVERHEATING, 100.0),
        (FaultScenario.FREQUENCY_HIGH, 51.3),
    ],
)
def test_fault_scenarios_produce_critical_measurements(scenario: FaultScenario, generated_value: float) -> None:
    profile = create_profile()

    result = apply_scenario(
        scenario=scenario,
        profile=profile,
        measurements=create_measurements(),
        random_generator=create_random_returning(generated_value),
    )

    status = classify_measurements(profile=profile, measurements=result)

    assert status == TelemetryStatus.CRITICAL


def test_unsupported_scenario_is_rejected() -> None:
    unsupported_scenario = cast(FaultScenario, "unsupported")

    with pytest.raises(ValueError, match="Unsupported scenario"):
        apply_scenario(
            scenario=unsupported_scenario,
            profile=create_profile(),
            measurements=create_measurements(),
            random_generator=Random(42),
        )