"""Execution loop for repeated telemetry generation."""

from collections.abc import Iterator
from time import sleep

from app.fleet import FleetSimulator
from app.scenarios import FaultScenario
from app.telemetry import TelemetryMessage


def run_simulation_cycles(
    fleet_simulator: FleetSimulator,
    cycles: int | None,
    interval_seconds: float,
    scenarios_by_device: dict[str, FaultScenario] | None = None,
) -> Iterator[tuple[TelemetryMessage, ...]]:
    """Generate finite or endless telemetry cycles."""

    if cycles is not None and cycles <= 0:
        raise ValueError("Number of cycles must be greater than zero.")

    if interval_seconds < 0:
        raise ValueError("Interval cannot be negative.")

    completed_cycles = 0
    
    # When cycles=None, the first condition is always True.
    # When cycles=3, the loop stops after three cycles.
    while cycles is None or completed_cycles < cycles:
        messages = fleet_simulator.generate_messages(scenarios_by_device=scenarios_by_device)

        yield messages

        completed_cycles += 1

        if cycles is None or completed_cycles < cycles:
            sleep(interval_seconds)