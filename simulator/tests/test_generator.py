"""Tests for normal telemetry measurement generation."""

from random import Random
from unittest.mock import Mock

import pytest

from app.calculations import calculate_active_power_kw
from app.generator import (
    generate_frequency_hz,
    generate_load_ratio,
    generate_normal_measurements,
    generate_power_factor,
    generate_temperature_c,
    generate_voltage_v,
)
from app.models import Substation, TransformerProfile


def create_profile() -> TransformerProfile:
    """Create a transformer profile for generator tests."""

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


def create_random_returning(value: float) -> Mock:
    """Create a random generator mock returning one Gaussian value."""

    random_generator = Mock(spec=Random)
    random_generator.gauss.return_value = value

    return random_generator


def test_voltage_generation_is_deterministic_for_same_seed() -> None:
    profile = create_profile()

    first_result = generate_voltage_v(profile=profile, random_generator=Random(42))
    second_result = generate_voltage_v(profile=profile, random_generator=Random(42))

    assert first_result == second_result
    assert first_result == pytest.approx(399.712, abs=0.001)


@pytest.mark.parametrize(
    ("generated_value", "expected_value"),
    [
        (0.05, 0.10),
        (0.50, 0.50),
        (1.20, 0.90),
    ],
)
def test_load_ratio_is_limited_to_normal_range(generated_value: float, expected_value: float) -> None:
    result = generate_load_ratio(
        profile=create_profile(),
        random_generator=create_random_returning(generated_value),
    )

    assert result == expected_value


@pytest.mark.parametrize(
    ("generated_value", "expected_value"),
    [
        (0.80, 0.85),
        (0.95, 0.95),
        (1.00, 0.99),
    ],
)
def test_power_factor_is_limited_to_normal_range(generated_value: float, expected_value: float) -> None:
    result = generate_power_factor(random_generator=create_random_returning(generated_value))

    assert result == expected_value


@pytest.mark.parametrize(
    ("generated_value", "expected_value"),
    [
        (49.0, 49.8),
        (50.0, 50.0),
        (51.0, 50.2),
    ],
)
def test_frequency_is_limited_to_normal_range(generated_value: float, expected_value: float) -> None:
    result = generate_frequency_hz(random_generator=create_random_returning(generated_value))

    assert result == expected_value


@pytest.mark.parametrize(
    ("generated_value", "expected_value"),
    [
        (10.0, 20.0),
        (50.0, 50.0),
        (90.0, 75.0),
    ],
)
def test_temperature_is_limited_to_normal_range(generated_value: float, expected_value: float) -> None:
    result = generate_temperature_c(
        profile=create_profile(),
        load_ratio=0.6,
        random_generator=create_random_returning(generated_value),
    )

    assert result == expected_value


def test_temperature_mean_changes_with_load_ratio() -> None:
    random_generator = create_random_returning(45.0)

    result = generate_temperature_c(
        profile=create_profile(),
        load_ratio=0.8,
        random_generator=random_generator,
    )

    assert result == 45.0
    random_generator.gauss.assert_called_once_with(mu=45.0, sigma=1.2)


def test_complete_measurement_generation_is_deterministic() -> None:
    profile = create_profile()
    first = generate_normal_measurements(profile=profile, random_generator=Random(42))
    second = generate_normal_measurements(profile=profile, random_generator=Random(42))

    assert first == second


def test_complete_measurements_are_within_normal_generator_limits() -> None:
    measurements = generate_normal_measurements(profile=create_profile(), random_generator=Random(42))

    assert measurements.voltage_v > 0
    assert measurements.current_a >= 0
    assert 49.8 <= measurements.frequency_hz <= 50.2
    assert 0.85 <= measurements.power_factor <= 0.99
    assert 20.0 <= measurements.temperature_c <= 75.0

    expected_active_power = calculate_active_power_kw(
        voltage_v=measurements.voltage_v,
        current_a=measurements.current_a,
        power_factor=measurements.power_factor,
    )

    assert measurements.active_power_kw == expected_active_power