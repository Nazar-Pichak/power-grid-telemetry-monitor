"""Tests for individual transformer simulation."""

from datetime import datetime, timezone
from random import Random
from uuid import UUID

import pytest

from app.models import (
    Substation,
    TelemetryStatus,
    TransformerProfile,
)
from app.scenarios import FaultScenario
from app.sequence import SequenceTracker
from app.simulator import TransformerSimulator
from app.telemetry import TelemetryMessage


def create_profile() -> TransformerProfile:
    """Create a transformer profile for simulator tests."""

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


def create_simulator(seed: int = 42) -> TransformerSimulator:
    """Create a deterministic transformer simulator."""

    return TransformerSimulator(
        profile=create_profile(),
        random_generator=Random(seed),
        sequence_tracker=SequenceTracker(),
    )


def measurement_values(message: TelemetryMessage) -> tuple[float, float, float, float, float, float]:
    """Extract generated measurement values for comparison."""

    return (
        message.voltage_v,
        message.current_a,
        message.frequency_hz,
        message.power_factor,
        message.active_power_kw,
        message.temperature_c,
    )


def test_simulator_creates_normal_telemetry_message() -> None:
    simulator = create_simulator()
    timestamp = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
    message_id = UUID("12345678-1234-5678-1234-567812345678")
    message = simulator.generate_message(timestamp=timestamp, message_id=message_id)

    assert message.schema_version == "1.0"
    assert message.message_id == message_id
    assert message.timestamp == timestamp
    assert message.station_code == "PLZEN-NORTH"
    assert message.device_code == "TRF-PLN-01"
    assert message.sequence == 1
    assert message.status == TelemetryStatus.NORMAL
    assert message.simulated is True


def test_simulator_increases_sequence_for_each_message() -> None:
    simulator = create_simulator()

    first_message = simulator.generate_message()
    second_message = simulator.generate_message()
    third_message = simulator.generate_message()

    assert first_message.sequence == 1
    assert second_message.sequence == 2
    assert third_message.sequence == 3


def test_simulation_is_deterministic_for_same_seed() -> None:
    first_simulator = create_simulator(seed=42)
    second_simulator = create_simulator(seed=42)

    first_message = first_simulator.generate_message()
    second_message = second_simulator.generate_message()

    assert measurement_values(first_message) == measurement_values(second_message)


@pytest.mark.parametrize(
    "scenario",
    [
        FaultScenario.OVERVOLTAGE,
        FaultScenario.UNDERVOLTAGE,
        FaultScenario.OVERLOAD,
        FaultScenario.OVERHEATING,
        FaultScenario.FREQUENCY_HIGH,
    ],
)
def test_fault_scenario_produces_critical_message(scenario: FaultScenario) -> None:
    simulator = create_simulator()
    message = simulator.generate_message(scenario=scenario)

    assert message.status == TelemetryStatus.CRITICAL
    assert message.sequence == 1