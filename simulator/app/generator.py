from random import Random

from app.calculations import calculate_active_power_kw, calculate_apparent_power_kva, calculate_line_current_a
from app.models import ElectricalMeasurements, TransformerProfile


def generate_voltage_v(profile: TransformerProfile, random_generator: Random) -> float:
    """Generate voltage around the transformer's nominal voltage."""
    
    voltage_v = random_generator.gauss(mu=profile.nominal_voltage_v, sigma=2.0,)

    return round(voltage_v, 3)


def generate_load_ratio(profile: TransformerProfile, random_generator: Random) -> float:
    """Generate a normal operating load ratio for a transformer."""
    
    load_ratio = random_generator.gauss(mu=profile.base_load_ratio, sigma=0.03)
    minimum_load_ratio = 0.10
    maximum_load_ratio = 0.90
    limited_load_ratio = max(minimum_load_ratio, min(load_ratio, maximum_load_ratio))

    return round(limited_load_ratio, 4)


def generate_power_factor(random_generator: Random) -> float:
    """Generate a realistic power factor for normal operation."""
    
    power_factor = random_generator.gauss(mu=0.95, sigma=0.01)
    minimum_power_factor = 0.85
    maximum_power_factor = 0.99
    limited_power_factor = max(minimum_power_factor, min(power_factor, maximum_power_factor))

    return round(limited_power_factor, 4)


def generate_frequency_hz(random_generator: Random) -> float:
    """Generate grid frequency for normal operation."""
    
    frequency_hz = random_generator.gauss(mu=50.0, sigma=0.025)
    minimum_frequency_hz = 49.8
    maximum_frequency_hz = 50.2
    limited_frequency_hz = max(minimum_frequency_hz, min(frequency_hz, maximum_frequency_hz))

    return round(limited_frequency_hz, 3)


def generate_temperature_c(profile: TransformerProfile, load_ratio: float, random_generator: Random ) -> float:
    """Generate transformer temperature based on operating load."""
    
    load_difference = load_ratio - profile.base_load_ratio
    load_temperature_effect = load_difference * 25.0
    expected_temperature_c = (profile.base_temperature_c + load_temperature_effect)
    temperature_c = random_generator.gauss(mu=expected_temperature_c, sigma=1.2)
    minimum_temperature_c = 20.0
    maximum_temperature_c = 75.0
    limited_temperature_c = max(minimum_temperature_c, min(temperature_c, maximum_temperature_c))

    return round(limited_temperature_c, 3)

def generate_normal_measurements(profile: TransformerProfile, random_generator: Random) -> ElectricalMeasurements:
    """
    This function is an orchestrator. It does not contain the individual formulas.
    Instead, it calls the small functions we already created and
    generate a complete set of normal transformer measurements.
    
    The calculation flow is:
        TransformerProfile
                ↓
        Generate voltage
                ↓
        Generate load ratio
                ↓
        Calculate apparent power
                ↓
        Calculate current
                ↓
        Generate power factor
                ↓
        Calculate active power
                ↓
        Generate frequency
                ↓
        Generate temperature
                ↓
        ElectricalMeasurements
    """
    
    voltage_v = generate_voltage_v(profile=profile, random_generator=random_generator)
    load_ratio = generate_load_ratio(profile=profile, random_generator=random_generator)
    apparent_power_kva = calculate_apparent_power_kva(rated_power_kva=profile.rated_power_kva, load_ratio=load_ratio)
    current_a = calculate_line_current_a(apparent_power_kva=apparent_power_kva, voltage_v=voltage_v)
    power_factor = generate_power_factor(random_generator=random_generator)
    active_power_kw = calculate_active_power_kw(voltage_v=voltage_v, current_a=current_a, power_factor=power_factor)
    frequency_hz = generate_frequency_hz(random_generator=random_generator)
    temperature_c = generate_temperature_c(profile=profile, load_ratio=load_ratio, random_generator=random_generator)

    return ElectricalMeasurements(
        voltage_v=voltage_v,
        current_a=current_a,
        frequency_hz=frequency_hz,
        power_factor=power_factor,
        active_power_kw=active_power_kw,
        temperature_c=temperature_c,
    )