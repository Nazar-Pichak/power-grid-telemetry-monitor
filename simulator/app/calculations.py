"""Electrical calculations used by the telemetry simulator."""

from math import sqrt


def calculate_active_power_kw(voltage_v: float, current_a: float, power_factor: float) -> float:
    """Calculate active power for a balanced three-phase system."""
    
    if voltage_v <= 0:
        raise ValueError("Voltage must be greater than zero.")

    if current_a < 0:
        raise ValueError("Current cannot be negative.")

    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be greater than zero and not greater than one.")
        
    active_power_w = sqrt(3) * voltage_v * current_a * power_factor
    active_power_kw = active_power_w / 1000

    return round(active_power_kw, 3)


def calculate_line_current_a(apparent_power_kva: float, voltage_v: float) -> float:
    """Calculate line current for a balanced three-phase system."""
    
    if apparent_power_kva < 0:
        raise ValueError("Apparent power cannot be negative.")

    if voltage_v <= 0:
        raise ValueError("Voltage must be greater than zero.")

    apparent_power_va = apparent_power_kva * 1000
    current_a = apparent_power_va / (sqrt(3) * voltage_v)

    return round(current_a, 3)


def calculate_apparent_power_kva(rated_power_kva: float, load_ratio: float) -> float:
    """Calculate operating apparent power from transformer load."""
    
    if rated_power_kva <= 0:
        raise ValueError("Rated power must be greater than zero.")

    if load_ratio < 0:
        raise ValueError("Load ratio cannot be negative.")

    apparent_power_kva = rated_power_kva * load_ratio

    return round(apparent_power_kva, 3)