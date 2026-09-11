"""Output transports supported by the telemetry simulator."""

from enum import StrEnum


class PublisherTransport(StrEnum):
    """Identify the output adapter selected for simulator execution."""

    CONSOLE = "console"
    MQTT = "mqtt"