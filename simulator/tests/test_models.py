"""Tests for simulator domain models."""

from dataclasses import FrozenInstanceError

import pytest

from app.models import (
    ElectricalMeasurements,
    Substation,
    TransformerProfile,
)


def create_substation() -> Substation:
    return Substation(
        code="PLZEN-NORTH",
        name="Plzen North Substation",
        city="Plzen",
    )


def create_profile(**overrides: object) -> TransformerProfile:
    """Create a valid transformer profile with optional overrides."""

    values = {
        "code": "TRF-PLN-01",
        "name": "Transformer PLN 01",
        "substation": create_substation(),
        "nominal_voltage_v": 400.0,
        "rated_power_kva": 630.0,
        "base_load_ratio": 0.6,
        "base_temperature_c": 25.0,
    }
    values.update(overrides)

    return TransformerProfile(**values)


def create_measurements(**overrides: float) -> ElectricalMeasurements:
    """Create valid electrical measurements with optional overrides."""

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


def test_valid_substation_is_created() -> None:
    substation = create_substation()

    assert substation.code == "PLZEN-NORTH"
    assert substation.name == "Plzen North Substation"
    assert substation.city == "Plzen"


@pytest.mark.parametrize(
    ("overrides"),
    [
        {"code": ""},
        {"code": "plzen-north"},
        {"code": "PLZEN NORTH"},
        {"name": ""},
        {"city": ""},
    ],
)
def test_invalid_substation_is_rejected(overrides: dict[str, str]) -> None:
    values = {
        "code": "PLZEN-NORTH",
        "name": "Plzen North Substation",
        "city": "Plzen",
    }
    values.update(overrides)

    with pytest.raises(ValueError):
        Substation(**values)


def test_valid_transformer_profile_is_created() -> None:
    profile = create_profile()

    assert profile.code == "TRF-PLN-01"
    assert profile.name == "Transformer PLN 01"
    assert profile.nominal_voltage_v == 400.0
    assert profile.rated_power_kva == 630.0
    assert profile.base_load_ratio == 0.6
    assert profile.base_temperature_c == 25.0
    assert profile.substation.code == "PLZEN-NORTH"


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("code", ""),
        ("code", "PLN-01"),
        ("code", "TRF-pln-01"),
        ("name", ""),
        ("nominal_voltage_v", 0.0),
        ("rated_power_kva", 0.0),
        ("base_load_ratio", 0.0),
        ("base_load_ratio", 1.1),
        ("base_temperature_c", -50.1),
        ("base_temperature_c", 150.1),
    ],
)
def test_invalid_transformer_profile_is_rejected(field_name: str, value: object) -> None:
    with pytest.raises(ValueError):
        create_profile(**{field_name: value})


def test_transformer_temperature_boundaries_are_accepted() -> None:
    minimum_profile = create_profile(base_temperature_c=-50.0)
    maximum_profile = create_profile(base_temperature_c=150.0)

    assert minimum_profile.base_temperature_c == -50.0
    assert maximum_profile.base_temperature_c == 150.0


def test_valid_measurements_are_created() -> None:
    measurements = create_measurements()

    assert measurements.voltage_v == 400.0
    assert measurements.current_a == 100.0
    assert measurements.frequency_hz == 50.0
    assert measurements.power_factor == 0.95
    assert measurements.active_power_kw == 65.818
    assert measurements.temperature_c == 25.0


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("voltage_v", 0.0),
        ("current_a", -1.0),
        ("frequency_hz", 0.0),
        ("power_factor", 0.0),
        ("power_factor", 1.1),
        ("active_power_kw", -1.0),
        ("temperature_c", -273.16),
    ],
)
def test_invalid_measurements_are_rejected(field_name: str, value: float) -> None:
    with pytest.raises(ValueError):
        create_measurements(**{field_name: value})


def test_domain_models_are_immutable() -> None:
    substation = create_substation()

    with pytest.raises(FrozenInstanceError):
        substation.city = "Prague"