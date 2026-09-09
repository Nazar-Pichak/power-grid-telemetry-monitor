"""Tests for the simulated grid catalog."""

from collections import Counter

import pytest

from app.catalog import (
    create_substation_lookup,
    create_substations,
    create_transformers,
)
from app.models import Substation


def test_catalog_contains_three_unique_substations() -> None:
    substations = create_substations()

    assert len(substations) == 3
    assert len({substation.code for substation in substations}) == 3

    assert {substation.code for substation in substations} == {
        "PLZEN-NORTH",
        "PLZEN-SOUTH",
        "PRAHA-WEST",
    }


def test_substations_have_expected_cities() -> None:
    substations = create_substations()

    cities_by_code = {substation.code: substation.city for substation in substations}

    assert cities_by_code == {
        "PLZEN-NORTH": "Plzen",
        "PLZEN-SOUTH": "Plzen",
        "PRAHA-WEST": "Prague",
    }


def test_substation_lookup_maps_codes_to_original_objects() -> None:
    substations = create_substations()

    lookup = create_substation_lookup(substations)

    assert set(lookup) == {"PLZEN-NORTH", "PLZEN-SOUTH", "PRAHA-WEST"}
    assert lookup["PLZEN-NORTH"] is substations[0]
    assert lookup["PLZEN-SOUTH"] is substations[1]
    assert lookup["PRAHA-WEST"] is substations[2]


def test_duplicate_substation_code_is_rejected() -> None:
    first = Substation(
        code="PLZEN-NORTH",
        name="First station",
        city="Plzen",
    )
    duplicate = Substation(
        code="PLZEN-NORTH",
        name="Duplicate station",
        city="Plzen",
    )

    with pytest.raises(ValueError, match="Duplicate substation code: PLZEN-NORTH"):
        create_substation_lookup((first, duplicate))


def test_catalog_contains_twelve_unique_transformers() -> None:
    substations = create_substations()
    lookup = create_substation_lookup(substations)

    transformers = create_transformers(lookup)

    assert len(transformers) == 12
    assert len({transformer.code for transformer in transformers}) == 12


def test_each_substation_contains_four_transformers() -> None:
    substations = create_substations()
    lookup = create_substation_lookup(substations)
    transformers = create_transformers(lookup)
    counts = Counter(transformer.substation.code for transformer in transformers)

    assert counts == {"PLZEN-NORTH": 4, "PLZEN-SOUTH": 4, "PRAHA-WEST": 4}


def test_transformers_have_expected_operating_profiles() -> None:
    substations = create_substations()
    lookup = create_substation_lookup(substations)
    transformers = create_transformers(lookup)

    first_transformer = transformers[0]
    fourth_transformer = transformers[3]

    assert first_transformer.code == "TRF-PLN-01"
    assert first_transformer.rated_power_kva == 400.0
    assert first_transformer.base_load_ratio == 0.40
    assert first_transformer.base_temperature_c == 44.0

    assert fourth_transformer.code == "TRF-PLN-04"
    assert fourth_transformer.rated_power_kva == 1000.0
    assert fourth_transformer.base_load_ratio == 0.55
    assert fourth_transformer.base_temperature_c == 50.0

    assert all(transformer.nominal_voltage_v == 400.0 for transformer in transformers)


def test_missing_required_substation_is_rejected() -> None:
    incomplete_lookup = {"PLZEN-NORTH": create_substations()[0]}

    with pytest.raises(KeyError):
        create_transformers(incomplete_lookup)