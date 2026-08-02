"""Configuration model for simulator execution."""

from dataclasses import dataclass

from app.scenarios import FaultScenario


@dataclass(frozen=True)
class SimulationSettings:
    """Validated settings used to run the telemetry simulator."""

    # None means that the simulator must run continuously.
    # A positive integer means that it must run for a limited number of cycles.
    cycles: int | None = None

    interval_seconds: float = 1.0
    seed: int | None = None
    device_code: str | None = None
    scenario: FaultScenario = FaultScenario.NORMAL

    def __post_init__(self) -> None:
        """Validate simulator settings after object creation."""

        if self.cycles is not None and self.cycles <= 0:
            raise ValueError("Number of cycles must be greater than zero.")

        if self.interval_seconds < 0:
            raise ValueError("Interval cannot be negative.")

        if self.device_code is not None and not self.device_code.strip():
            raise ValueError("Device code cannot be empty.")

        if self.scenario != FaultScenario.NORMAL and self.device_code is None:
            raise ValueError("A device code is required for a fault scenario.")