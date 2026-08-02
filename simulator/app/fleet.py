"""Simulation of the complete transformer fleet."""

from random import Random

from app.models import TransformerProfile
from app.sequence import SequenceTracker
from app.simulator import TransformerSimulator
from app.telemetry import TelemetryMessage
from app.scenarios import FaultScenario

class FleetSimulator:
    """Generate telemetry for a fleet of transformers."""

    def __init__(self, profiles: tuple[TransformerProfile, ...], seed: int | None = None) -> None:
        """Create one simulator for every transformer profile."""
        
        self._sequence_tracker = SequenceTracker()
        self._simulators: dict[str, TransformerSimulator] = {}
        
        # It creates a different deterministic seed for every transformer
        master_random_generator = Random(seed)

        for profile in profiles:
            device_seed = master_random_generator.getrandbits(64)

            transformer_simulator = TransformerSimulator(
                profile=profile,
                random_generator=Random(device_seed),
                sequence_tracker=self._sequence_tracker,
            )

            self._simulators[profile.code] = transformer_simulator

    def generate_messages(self, scenarios_by_device: dict[str, FaultScenario] | None = None) -> tuple[TelemetryMessage, ...]:
        """Generate one normal message from every transformer."""
        
        selected_scenarios = scenarios_by_device or {}
        messages: list[TelemetryMessage] = []

        for device_code, simulator in self._simulators.items():
            scenario = selected_scenarios.get(device_code, FaultScenario.NORMAL)
            message = simulator.generate_message(scenario=scenario)
            messages.append(message)

        return tuple(messages)