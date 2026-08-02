"""Simulation of telemetry for individual transformers."""

from datetime import datetime
from random import Random
from uuid import UUID

from app.generator import generate_normal_measurements
from app.message_factory import create_telemetry_message
from app.models import TransformerProfile
from app.sequence import SequenceTracker
from app.telemetry import TelemetryMessage
from app.scenarios import FaultScenario, apply_scenario


class TransformerSimulator:
    """Generate ordered telemetry for one transformer."""

    def __init__(self, profile: TransformerProfile, random_generator: Random, sequence_tracker: SequenceTracker) -> None:
        """Initialize the transformer simulator dependencies."""
        
        self._profile = profile
        self._random_generator = random_generator
        self._sequence_tracker = sequence_tracker

    def generate_message(self, scenario: FaultScenario = FaultScenario.NORMAL, timestamp: datetime | None = None, message_id: UUID | None = None) -> TelemetryMessage:
        """
        Generate the next telemetry message for a selected scenario.
        The generation pipeline is now:
        
            Generate normal measurements
                      ↓
            Apply selected scenario
                      ↓
            Classify measurements
                      ↓
            Assign sequence
                      ↓
            Create TelemetryMessage
        """
        
        normal_measurements = generate_normal_measurements(profile=self._profile, random_generator=self._random_generator)
        scenario_measurements = apply_scenario(scenario=scenario, profile=self._profile, measurements=normal_measurements, random_generator=self._random_generator)
        sequence = self._sequence_tracker.next_sequence(self._profile.code)

        return create_telemetry_message(
            profile=self._profile,
            measurements=scenario_measurements,
            sequence=sequence,
            timestamp=timestamp,
            message_id=message_id,
        )