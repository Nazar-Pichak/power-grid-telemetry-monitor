"""Tests for simulator execution settings."""

import pytest

from app.scenarios import FaultScenario
from app.settings import SimulationSettings


def test_default_settings_enable_continuous_normal_simulation() -> None:
    settings = SimulationSettings()

    assert settings.cycles is None
    assert settings.interval_seconds == 1.0
    assert settings.seed is None
    assert settings.device_code is None
    assert settings.scenario == FaultScenario.NORMAL


def test_finite_simulation_settings_are_accepted() -> None:
    settings = SimulationSettings(
        cycles=2,
        interval_seconds=0,
        seed=42,
        device_code="TRF-PLN-01",
        scenario=FaultScenario.OVERHEATING,
    )

    assert settings.cycles == 2
    assert settings.interval_seconds == 0
    assert settings.seed == 42
    assert settings.device_code == "TRF-PLN-01"
    assert settings.scenario == FaultScenario.OVERHEATING


@pytest.mark.parametrize("cycles", [0, -1])
def test_non_positive_cycle_count_is_rejected(cycles: int) -> None:
    with pytest.raises(ValueError, match="Number of cycles must be greater than zero"):
        SimulationSettings(cycles=cycles)


def test_negative_interval_is_rejected() -> None:
    with pytest.raises(ValueError, match="Interval cannot be negative"):
        SimulationSettings(interval_seconds=-0.1)


@pytest.mark.parametrize("device_code", ["", " ", "\t"])
def test_empty_device_code_is_rejected(device_code: str) -> None:
    with pytest.raises(ValueError, match="Device code cannot be empty"):
        SimulationSettings(device_code=device_code)