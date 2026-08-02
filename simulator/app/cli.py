"""Command-line interface for simulator configuration."""

from argparse import ArgumentParser
from collections.abc import Sequence

from app.scenarios import FaultScenario
from app.settings import SimulationSettings


def parse_simulation_settings(arguments: Sequence[str] | None = None) -> SimulationSettings:
    """Parse command-line arguments into validated simulation settings."""

    parser = ArgumentParser(description="Generate simulated power-grid telemetry.")

    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help=(
            "Number of simulation cycles. "
            "If omitted, the simulator runs continuously."
        ),
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Delay between simulation cycles in seconds.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional seed for deterministic telemetry generation.",
    )

    parser.add_argument(
        "--device-code",
        type=str,
        default=None,
        help="Transformer code that receives the selected scenario.",
    )

    parser.add_argument(
        "--scenario",
        type=FaultScenario,
        choices=list(FaultScenario),
        default=FaultScenario.NORMAL,
        help="Scenario applied to the selected transformer.",
    )

    parsed_arguments = parser.parse_args(arguments)

    return SimulationSettings(
        cycles=parsed_arguments.cycles,
        interval_seconds=parsed_arguments.interval,
        seed=parsed_arguments.seed,
        device_code=parsed_arguments.device_code,
        scenario=parsed_arguments.scenario,
    )