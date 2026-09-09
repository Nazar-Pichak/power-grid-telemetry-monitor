"""Tests for simulator application orchestration."""

import pytest

from app.application import run_simulator
from app.settings import SimulationSettings
from app.telemetry import TelemetryMessage


class MemoryTelemetryPublisher:
    """Publisher that stores messages in memory for testing."""

    def __init__(self) -> None:
        self.connected = False
        self.closed = False
        self.messages: list[TelemetryMessage] = []

    def connect(self) -> None:
        self.connected = True

    def publish(self, message: TelemetryMessage) -> None:
        self.messages.append(message)

    def close(self) -> None:
        self.closed = True


class FailingTelemetryPublisher(MemoryTelemetryPublisher):
    """Publisher that raises an exception during publishing."""

    def publish(self, message: TelemetryMessage) -> None:
        raise RuntimeError("Publishing failed.")


def test_application_publishes_twelve_messages_for_one_cycle() -> None:
    publisher = MemoryTelemetryPublisher()
    settings = SimulationSettings(cycles=1, interval_seconds=0, seed=42)

    run_simulator(settings=settings, publisher=publisher)

    assert publisher.connected is True
    assert publisher.closed is True
    assert len(publisher.messages) == 12
    assert len({message.device_code for message in publisher.messages}) == 12
    assert all(message.sequence == 1 for message in publisher.messages)


def test_application_closes_publisher_when_publishing_fails() -> None:
    publisher = FailingTelemetryPublisher()
    settings = SimulationSettings(cycles=1, interval_seconds=0, seed=42)

    with pytest.raises(RuntimeError, match="Publishing failed"):
        run_simulator(settings=settings, publisher=publisher)

    assert publisher.connected is True
    assert publisher.closed is True