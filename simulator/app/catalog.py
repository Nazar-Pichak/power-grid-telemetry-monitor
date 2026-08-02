"""Catalog of substations and transformers in the simulated grid."""

from app.models import Substation, TransformerProfile


def create_substations() -> tuple[Substation, ...]:
    """Create all substations in the simulated electrical grid."""
    
    return (
        Substation(
            code="PLZEN-NORTH",
            name="Plzen North Substation",
            city="Plzen",
        ),
        Substation(
            code="PLZEN-SOUTH",
            name="Plzen South Substation",
            city="Plzen",
        ),
        Substation(
            code="PRAHA-WEST",
            name="Prague West Substation",
            city="Prague",
        ),
    )
    
    
def create_substation_lookup(substations: tuple[Substation, ...]) -> dict[str, Substation]:
    """Create a lookup that maps station codes to substations."""
    
    lookup: dict[str, Substation] = {}

    for substation in substations:
        if substation.code in lookup:
            raise ValueError(
                f"Duplicate substation code: {substation.code}"
            )

        lookup[substation.code] = substation

    return lookup


def create_transformers(substations_by_code: dict[str, Substation]) -> tuple[TransformerProfile, ...]:
    """Create all transformer profiles in the simulated grid."""
    
    station_configurations = (
        ("PLZEN-NORTH", "PLN"),
        ("PLZEN-SOUTH", "PLS"),
        ("PRAHA-WEST", "PRW"),
    )

    rated_powers_kva = (400.0, 630.0, 800.0, 1000.0)
    transformers: list[TransformerProfile] = []

    for station_code, device_prefix in station_configurations:
        substation = substations_by_code[station_code]

        for device_number, rated_power_kva in enumerate(rated_powers_kva, start=1):
            device_code = (f"TRF-{device_prefix}-{device_number:02d}")
            base_load_ratio = round(0.35 + device_number * 0.05, 2)
            base_temperature_c = (42.0 + device_number * 2.0)
            
            transformer = TransformerProfile(
                code=device_code,
                name=(
                    f"Transformer "
                    f"{device_prefix} "
                    f"{device_number:02d}"
                ),
                substation=substation,
                nominal_voltage_v=400.0,
                rated_power_kva=rated_power_kva,
                base_load_ratio=base_load_ratio,
                base_temperature_c=base_temperature_c,
            )

            transformers.append(transformer)

    return tuple(transformers)