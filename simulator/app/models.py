"""Domain models used by the telemetry simulator."""

from dataclasses import dataclass
from enum import StrEnum


class TelemetryStatus(StrEnum):
    """Represent the operational classification of telemetry."""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    

@dataclass(frozen=True)
class Substation:
    """Represent an electrical substation in the simulated grid."""
    
    code: str
    name: str
    city: str
    
    def __post_init__(self) -> None:
        "Validate a substation immidiately after its creation."
        
        if not self.code:
            raise ValueError("Substation code cannot be empty.")
        
        if self.code != self.code.upper():
            raise ValueError("Substation code must use uppercase letters.")

        if " " in self.code:
            raise ValueError("Substation code cannot contain spaces.")

        if not self.name:
            raise ValueError("Substation name cannot be empty.")

        if not self.city:
            raise ValueError("Substation city cannot be empty.")
        
           
@dataclass(frozen=True)
class TransformerProfile:
    """Represent the static configuration of a simulated transformer."""

    code: str
    name: str
    substation: Substation
    nominal_voltage_v: float
    rated_power_kva: float
    base_load_ratio: float
    base_temperature_c: float
    
    def __post_init__(self) -> None:
        """Validate the transformer profile after its creation."""
        if not self.code:
            raise ValueError("Transformer code cannot be empty.")

        if not self.code.startswith("TRF-"):
            raise ValueError("Transformer code must start with 'TRF-'.")

        if self.code != self.code.upper():
            raise ValueError("Transformer code must use uppercase letters.")

        if " " in self.code:
            raise ValueError("Transformer code cannot contain spaces.")

        if not self.name:
            raise ValueError("Transformer name cannot be empty.")

        if self.nominal_voltage_v <= 0:
            raise ValueError("Nominal voltage must be greater than zero.")

        if self.rated_power_kva <= 0:
            raise ValueError("Rated power must be greater than zero.")
        
        if not 0 < self.base_load_ratio <= 1:
            raise ValueError("Base load ratio must be greater than zero and not greater than one.")

        if self.base_temperature_c < -50:
            raise ValueError("Base temperature cannot be lower than -50 degrees Celsius.")

        if self.base_temperature_c > 150:
            raise ValueError("Base temperature cannot be higher than 150 degrees Celsius.")

        
@dataclass(frozen=True)
class ElectricalMeasurements:
    """Represent electrical measurements produced by a transformer."""

    voltage_v: float
    current_a: float
    frequency_hz: float
    power_factor: float
    active_power_kw: float
    temperature_c: float
    
    def __post_init__(self) -> None:
        """Validate that all measurements are physically possible."""
        if self.voltage_v <= 0:
            raise ValueError("Voltage must be greater than zero.")

        if self.current_a < 0:
            raise ValueError("Current cannot be negative.")

        if self.frequency_hz <= 0:
            raise ValueError("Frequency must be greater than zero.")

        if not 0 < self.power_factor <= 1:
            raise ValueError("Power factor must be greater than zero and not greater than one.")

        if self.active_power_kw < 0:
            raise ValueError("Active power cannot be negative.")

        if self.temperature_c < -273.15:
            raise ValueError("Temperature cannot be below absolute zero.")