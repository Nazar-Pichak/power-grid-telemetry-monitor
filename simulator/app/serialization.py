"""Serialization of telemetry messages."""

from app.telemetry import TelemetryMessage


def serialize_telemetry_message(message: TelemetryMessage) -> str:
    """Serialize one telemetry message as a compact JSON line."""

    return message.model_dump_json(by_alias=True)