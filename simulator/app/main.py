"""Entry point for the power-grid telemetry simulator."""

import sys

from app.application import run_simulator
from app.cli import parse_simulation_settings


def main() -> None:
    """Parse configuration and start the simulator."""

    settings = parse_simulation_settings()

    try:
        run_simulator(settings)
    except KeyboardInterrupt:
        print(
            "Simulator stopped.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()