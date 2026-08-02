"""Public telemetry contract produced by the simulator."""

from dataclasses import field
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import TelemetryStatus


class TelemetryMessage(BaseModel):
    """
    Represent one versioned transformer telemetry message which is serialized to JSON
    and be consumed by downstream systems.
    
    Important concepts:
    - BaseModel - provides validation and JSON serialization.
    - frozen=True - makes a validated message immutable.
    - populate_by_name=True - allows Python field names when creating the object.
    - alias - defines the public camelCase JSON field name.
    - Field() - defines validation rules.
    - UUID - provides a standard unique message identifier.
    - datetime - represents the measurement time.
    - schemaVersion - allows the contract to evolve later.
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)
    schema_version: str = Field(default="1.0", alias="schemaVersion", pattern=r"^1\.0$")
    message_id: UUID = Field(alias="messageId")
    timestamp: datetime
    station_code: str = Field(alias="stationCode", pattern=r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
    device_code: str = Field(alias="deviceCode", pattern=r"^TRF-[A-Z0-9]+-\d{2}$")
    sequence: int = Field(ge=1)
    voltage_v: float = Field(alias="voltageV", gt=0)
    current_a: float = Field(alias="currentA", ge=0)
    frequency_hz: float = Field(alias="frequencyHz", gt=0)
    power_factor: float = Field(alias="powerFactor", gt=0, le=1)
    active_power_kw: float = Field(alias="activePowerKw", ge=0)
    temperature_c: float = Field(alias="temperatureC", ge=-273.15)
    status: TelemetryStatus
    simulated: bool = True
    
    @field_validator("timestamp")
    @classmethod
    def timestamp_must_include_timezone(cls, value: datetime) -> datetime:
        """
        Reject timestamps without timezone information.
        @field_validator("timestamp") tells Pydantic to run this method whenever it validates the timestamp field
        """
        
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include timezone information.")

        return value