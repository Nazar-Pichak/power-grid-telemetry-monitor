"""Tests for application-level simulator validation."""

import pytest

from app.catalog import (
    create_substation_lookup,
    create_substations,
    create_transformers,
)
from app.settings import SimulationSettings
from app.validation import validate_selected_device


def create_profiles():
    """Create the complete transformer catalog."""

    substations = create_substations()
    lookup = create_substation_lookup(substations)

    return create_transformers(lookup)


def test_validation_accepts_missing_device_selection() -> None:
    settings = SimulationSettings(device_code=None)
    result = validate_selected_device(settings=settings, profiles=create_profiles())

    assert result is None


def test_validation_accepts_existing_device_code() -> None:
    settings = SimulationSettings(device_code="TRF-PLN-01")
    result = validate_selected_device(settings=settings, profiles=create_profiles())

    assert result is None


def test_validation_rejects_unknown_device_code() -> None:
    settings = SimulationSettings(device_code="TRF-UNKNOWN-01")

    with pytest.raises(ValueError, match="Unknown transformer code: TRF-UNKNOWN-01"):
        validate_selected_device(settings=settings, profiles=create_profiles())