"""Classification of transformer telemetry measurements."""

from app.calculations import calculate_line_current_a
from app.models import ElectricalMeasurements, TelemetryStatus, TransformerProfile


def classify_measurements(profile: TransformerProfile, measurements: ElectricalMeasurements) -> TelemetryStatus:
    """
    Classify measurements as normal, warning, or critical.
    The function checks critical conditions first. This is important because a critical value may also exceed a warning threshold.
    """
    
    rated_current_a = calculate_line_current_a(apparent_power_kva=profile.rated_power_kva, voltage_v=profile.nominal_voltage_v)

    critical_condition = (
        measurements.voltage_v < 360.0
        or measurements.voltage_v > 440.0
        or measurements.current_a > rated_current_a * 1.05
        or measurements.frequency_hz < 49.0
        or measurements.frequency_hz > 51.0
        or measurements.temperature_c > 95.0
    )

    if critical_condition:
        return TelemetryStatus.CRITICAL

    warning_condition = (
        measurements.voltage_v < 380.0
        or measurements.voltage_v > 420.0
        or measurements.current_a > rated_current_a * 0.90
        or measurements.frequency_hz < 49.5
        or measurements.frequency_hz > 50.5
        or measurements.temperature_c > 80.0
    )

    if warning_condition:
        return TelemetryStatus.WARNING

    return TelemetryStatus.NORMAL