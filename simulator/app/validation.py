"""Application-level validation for simulator configuration."""

from app.models import TransformerProfile
from app.settings import SimulationSettings


def validate_selected_device(settings: SimulationSettings, profiles: tuple[TransformerProfile, ...]) -> None:
    """Ensure that the selected transformer exists in the catalog."""

    if settings.device_code is None:
        return

    available_device_codes = {profile.code for profile in profiles}

    if settings.device_code not in available_device_codes:
        raise ValueError(f"Unknown transformer code: {settings.device_code}.")