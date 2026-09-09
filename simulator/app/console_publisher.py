"""Console adapter for telemetry publishing."""

import sys
from typing import TextIO

from app.serialization import serialize_telemetry_message
from app.telemetry import TelemetryMessage


class ConsoleTelemetryPublisher:
    """Publish telemetry messages as JSON Lines to an output stream."""

    def __init__(self, output: TextIO | None = None) -> None:
        self._output = output if output is not None else sys.stdout

    def connect(self) -> None:
        """Prepare the console publisher."""

    def publish(self, message: TelemetryMessage) -> None:
        """Write one serialized telemetry message followed by a newline."""

        json_line = serialize_telemetry_message(message)
        self._output.write(f"{json_line}\n")
        self._output.flush()

    def close(self) -> None:
        """Release console publisher resources."""