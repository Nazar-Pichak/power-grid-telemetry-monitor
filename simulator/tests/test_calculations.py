"""Tests for three-phase electrical calculations."""

import pytest

from app.calculations import (
    calculate_active_power_kw,
    calculate_apparent_power_kva,
    calculate_line_current_a,
)


def test_active_power_is_calculated_correctly() -> None:
    result = calculate_active_power_kw(voltage_v=400.0, current_a=100.0, power_factor=0.9,)

    assert result == 62.354


def test_active_power_can_be_zero_when_current_is_zero() -> None:
    result = calculate_active_power_kw(voltage_v=400.0, current_a=0.0, power_factor=0.9,)

    assert result == 0.0


@pytest.mark.parametrize("voltage_v", [0.0, -1.0])
def test_active_power_rejects_non_positive_voltage(voltage_v: float) -> None:
    with pytest.raises(ValueError, match="Voltage must be greater than zero"):
        calculate_active_power_kw(voltage_v=voltage_v, current_a=100.0, power_factor=0.9,)


def test_active_power_rejects_negative_current() -> None:
    with pytest.raises(ValueError, match="Current cannot be negative"):
        calculate_active_power_kw(voltage_v=400.0, current_a=-1.0, power_factor=0.9)


@pytest.mark.parametrize("power_factor", [0.0, -0.1, 1.1])
def test_active_power_rejects_invalid_power_factor(power_factor: float) -> None:
    with pytest.raises(ValueError, match="Power factor must be"):
        calculate_active_power_kw(voltage_v=400.0, current_a=100.0, power_factor=power_factor)


def test_line_current_is_calculated_correctly() -> None:
    result = calculate_line_current_a(apparent_power_kva=630.0, voltage_v=400.0)

    assert result == 909.327


def test_line_current_can_be_zero() -> None:
    result = calculate_line_current_a(apparent_power_kva=0.0, voltage_v=400.0)

    assert result == 0.0


def test_line_current_rejects_negative_apparent_power() -> None:
    with pytest.raises(ValueError, match="Apparent power cannot be negative"):
        calculate_line_current_a(apparent_power_kva=-1.0, voltage_v=400.0,)


@pytest.mark.parametrize("voltage_v", [0.0, -1.0])
def test_line_current_rejects_non_positive_voltage(voltage_v: float) -> None:
    with pytest.raises(ValueError, match="Voltage must be greater than zero"):
        calculate_line_current_a(apparent_power_kva=630.0, voltage_v=voltage_v)


def test_apparent_power_is_calculated_correctly() -> None:
    result = calculate_apparent_power_kva(rated_power_kva=630.0, load_ratio=0.75)

    assert result == 472.5


def test_apparent_power_can_be_zero_when_load_is_zero() -> None:
    result = calculate_apparent_power_kva(rated_power_kva=630.0, load_ratio=0.0)

    assert result == 0.0


@pytest.mark.parametrize("rated_power_kva", [0.0, -1.0])
def test_apparent_power_rejects_non_positive_r_power(rated_power_kva: float) -> None:
    with pytest.raises(ValueError, match="Rated power must be greater than zero"):
        calculate_apparent_power_kva(rated_power_kva=rated_power_kva, load_ratio=0.5)


def test_apparent_power_rejects_negative_load_ratio() -> None:
    with pytest.raises(ValueError, match="Load ratio cannot be negative"):
        calculate_apparent_power_kva(rated_power_kva=630.0, load_ratio=-0.1)