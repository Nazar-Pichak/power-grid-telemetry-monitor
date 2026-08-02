"""Application orchestration for the telemetry simulator."""

from app.fleet import FleetSimulator
from app.scenarios import FaultScenario
from app.settings import SimulationSettings
from app.catalog import create_substation_lookup, create_substations, create_transformers
from app.serialization import serialize_telemetry_message
from app.simulation_loop import run_simulation_cycles
from app.validation import validate_selected_device


def run_simulator(settings: SimulationSettings) -> None:
    """Build and run the complete telemetry simulation."""

    substations = create_substations()
    substations_by_code = create_substation_lookup(substations)
    transformers = create_transformers(substations_by_code)

    validate_selected_device(settings=settings, profiles=transformers)

    fleet_simulator = FleetSimulator(profiles=transformers, seed=settings.seed)
    scenarios_by_device: dict[str, FaultScenario] | None = None

    if settings.device_code is not None:
        scenarios_by_device = {
            settings.device_code: settings.scenario,
        }

    for messages in run_simulation_cycles(
        fleet_simulator=fleet_simulator,
        cycles=settings.cycles,
        interval_seconds=settings.interval_seconds,
        scenarios_by_device=scenarios_by_device,
    ):
        for message in messages:
            json_line = serialize_telemetry_message(message)
            print(json_line, flush=True)