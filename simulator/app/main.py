"""Entry point for the power-grid telemetry simulator."""

import sys

from app.application import run_simulator
from app.cli import parse_simulation_settings
from app.publisher_factory import create_telemetry_publisher


def main() -> None:
    """Parse configuration and start the simulator."""

    settings = parse_simulation_settings()
    publisher = create_telemetry_publisher(transport=settings.transport)

    try:
        run_simulator(settings=settings, publisher=publisher)
    except KeyboardInterrupt:
        print("Simulator stopped.", file=sys.stderr)
    except (OSError, RuntimeError) as error:
        print(f"Simulator failed: {error}", file=sys.stderr)
        raise SystemExit(1) from None

if __name__ == "__main__":
    main()