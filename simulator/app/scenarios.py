"""Operating scenarios supported by the transformer simulator."""

from dataclasses import replace
from enum import StrEnum
from random import Random

from app.calculations import calculate_active_power_kw, calculate_apparent_power_kva, calculate_line_current_a
from app.models import ElectricalMeasurements, TransformerProfile


class FaultScenario(StrEnum):
    """Represent normal and abnormal transformer operation."""

    NORMAL = "normal"
    OVERVOLTAGE = "overvoltage"
    UNDERVOLTAGE = "undervoltage"
    OVERLOAD = "overload"
    OVERHEATING = "overheating"
    FREQUENCY_HIGH = "frequency_high"
    

def apply_overvoltage(measurements: ElectricalMeasurements, random_generator: Random) -> ElectricalMeasurements:
    """Create critical overvoltage measurements."""
    
    voltage_v = round(random_generator.uniform(444.0, 460.0), 3)
    active_power_kw = calculate_active_power_kw(voltage_v=voltage_v, current_a=measurements.current_a, power_factor=measurements.power_factor)
    
    return replace(measurements, voltage_v=voltage_v, active_power_kw=active_power_kw)


def apply_undervoltage(measurements: ElectricalMeasurements, random_generator: Random) -> ElectricalMeasurements:
    """Create critical undervoltage measurements."""
    
    voltage_v = round(random_generator.uniform(330.0, 355.0), 3)
    active_power_kw = calculate_active_power_kw(voltage_v=voltage_v, current_a=measurements.current_a, power_factor=measurements.power_factor)

    return replace(measurements, voltage_v=voltage_v, active_power_kw=active_power_kw)


def apply_overload( profile: TransformerProfile, measurements: ElectricalMeasurements, random_generator: Random) -> ElectricalMeasurements:
    """Create critical transformer-overload measurements."""
    
    load_ratio = round(random_generator.uniform(1.08, 1.22), 4)
    apparent_power_kva = calculate_apparent_power_kva(rated_power_kva=profile.rated_power_kva, load_ratio=load_ratio)
    current_a = calculate_line_current_a(apparent_power_kva=apparent_power_kva, voltage_v=measurements.voltage_v)
    active_power_kw = calculate_active_power_kw(voltage_v=measurements.voltage_v, current_a=current_a, power_factor=measurements.power_factor)

    return replace(measurements, current_a=current_a, active_power_kw=active_power_kw)


def apply_overheating(measurements: ElectricalMeasurements, random_generator: Random) -> ElectricalMeasurements:
    """Create critical transformer-overheating measurements."""
    
    temperature_c = round(random_generator.uniform(96.0, 112.0), 3)

    return replace(measurements, temperature_c=temperature_c)


def apply_frequency_high(measurements: ElectricalMeasurements, random_generator: Random) -> ElectricalMeasurements:
    """Create critical high-frequency measurements."""
    
    frequency_hz = round(random_generator.uniform(51.1, 51.6), 3)

    return replace(measurements, frequency_hz=frequency_hz)


def apply_scenario(scenario: FaultScenario, profile: TransformerProfile, measurements: ElectricalMeasurements, random_generator: Random) -> ElectricalMeasurements:
    """Apply the selected operating scenario to measurements."""
    
    if scenario is FaultScenario.NORMAL:
        return measurements

    if scenario is FaultScenario.OVERVOLTAGE:
        return apply_overvoltage(measurements=measurements, random_generator=random_generator)

    if scenario is FaultScenario.UNDERVOLTAGE:
        return apply_undervoltage(measurements=measurements, random_generator=random_generator)

    if scenario is FaultScenario.OVERLOAD:
        return apply_overload(profile=profile, measurements=measurements, random_generator=random_generator)

    if scenario is FaultScenario.OVERHEATING:
        return apply_overheating(measurements=measurements, random_generator=random_generator)

    if scenario is FaultScenario.FREQUENCY_HIGH:
        return apply_frequency_high(measurements=measurements, random_generator=random_generator)

    raise ValueError(f"Unsupported scenario: {scenario}")