"""Management of independent transformer message sequences."""


class SequenceTracker:
    """Track the latest sequence number for every transformer."""

    def __init__(self) -> None:
        """Initialize an empty collection of device sequences."""
        self._sequences: dict[str, int] = {}

    def next_sequence(self, device_code: str) -> int:
        """Increment and return the sequence for one transformer."""
        if not device_code:
            raise ValueError("Device code cannot be empty.")

        current_sequence = self._sequences.get(device_code, 0)
        next_sequence = current_sequence + 1
        self._sequences[device_code] = next_sequence

        return next_sequence