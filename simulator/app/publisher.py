"""Output port for telemetry publishing."""

from typing import Protocol, runtime_checkable

from app.telemetry import TelemetryMessage


@runtime_checkable
class TelemetryPublisher(Protocol):
    """Transport-independent interface for telemetry publishers."""

    def connect(self) -> None:
        """Prepare the publisher for sending telemetry."""
        ...

    def publish(self, message: TelemetryMessage) -> None:
        """Publish one telemetry message."""
        ...

    def close(self) -> None:
        """Release resources owned by the publisher."""
        ...