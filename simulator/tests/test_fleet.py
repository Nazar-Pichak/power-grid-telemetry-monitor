"""Tests for complete transformer fleet simulation."""

from app.catalog import (
    create_substation_lookup,
    create_substations,
    create_transformers,
)
from app.fleet import FleetSimulator
from app.scenarios import FaultScenario
from app.telemetry import TelemetryMessage


def create_profiles():
    """Create the complete transformer catalog."""

    substations = create_substations()
    lookup = create_substation_lookup(substations)

    return create_transformers(lookup)


def create_fleet(seed: int = 42) -> FleetSimulator:
    """Create a deterministic fleet simulator."""

    return FleetSimulator(profiles=create_profiles(), seed=seed)


def message_fingerprint(message: TelemetryMessage) -> tuple:
    """
    Return deterministic message fields.
    UUIDs and timestamps are excluded because they are generated independently.
    """

    return (
        message.station_code,
        message.device_code,
        message.sequence,
        message.voltage_v,
        message.current_a,
        message.frequency_hz,
        message.power_factor,
        message.active_power_kw,
        message.temperature_c,
        message.status,
        message.simulated,
    )


def test_fleet_generates_one_message_per_transformer() -> None:
    fleet = create_fleet()

    messages = fleet.generate_messages()

    assert len(messages) == 12
    assert len({message.device_code for message in messages}) == 12
    assert all(message.sequence == 1 for message in messages)


def test_fleet_preserves_transformer_catalog_order() -> None:
    profiles = create_profiles()
    fleet = FleetSimulator(profiles=profiles, seed=42)

    messages = fleet.generate_messages()

    assert [message.device_code for message in messages] == [profile.code for profile in profiles]


def test_fleet_increments_every_device_sequence_independently() -> None:
    fleet = create_fleet()

    first_cycle = fleet.generate_messages()
    second_cycle = fleet.generate_messages()
    third_cycle = fleet.generate_messages()

    assert all(message.sequence == 1 for message in first_cycle)
    assert all(message.sequence == 2 for message in second_cycle)
    assert all(message.sequence == 3 for message in third_cycle)


def test_fleet_is_deterministic_for_same_seed() -> None:
    first_fleet = create_fleet(seed=42)
    second_fleet = create_fleet(seed=42)

    first_messages = first_fleet.generate_messages()
    second_messages = second_fleet.generate_messages()

    first_fingerprints = [message_fingerprint(message) for message in first_messages]
    second_fingerprints = [message_fingerprint(message) for message in second_messages]

    assert first_fingerprints == second_fingerprints


def test_fault_scenario_is_applied_only_to_selected_device() -> None:
    fleet = create_fleet()

    messages = fleet.generate_messages(scenarios_by_device={"TRF-PLN-02": FaultScenario.OVERHEATING})

    selected_message = next(message for message in messages if message.device_code == "TRF-PLN-02")
    other_messages = [message for message in messages if message.device_code != "TRF-PLN-02"]

    assert selected_message.status.value == "critical"
    assert selected_message.temperature_c > 95.0
    assert all(message.status.value == "normal"for message in other_messages)


def test_empty_fleet_generates_no_messages() -> None:
    fleet = FleetSimulator(profiles=(), seed=42)
    messages = fleet.generate_messages()

    assert messages == ()