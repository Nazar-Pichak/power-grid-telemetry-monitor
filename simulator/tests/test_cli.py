"""Tests for the simulator command-line interface."""

import pytest

from app.cli import parse_simulation_settings
from app.scenarios import FaultScenario
from app.transport import PublisherTransport


def test_cli_uses_default_settings_when_no_arguments_are_provided() -> None:
    settings = parse_simulation_settings([])

    assert settings.cycles is None
    assert settings.interval_seconds == 1.0
    assert settings.seed is None
    assert settings.device_code is None
    assert settings.scenario == FaultScenario.NORMAL


def test_cli_parses_all_supported_arguments() -> None:
    settings = parse_simulation_settings(
        [
            "--cycles",
            "2",
            "--interval",
            "0.5",
            "--seed",
            "42",
            "--device-code",
            "TRF-PLN-01",
            "--scenario",
            "overheating",
        ]
    )

    assert settings.cycles == 2
    assert settings.interval_seconds == 0.5
    assert settings.seed == 42
    assert settings.device_code == "TRF-PLN-01"
    assert settings.scenario == FaultScenario.OVERHEATING


def test_cli_rejects_unknown_argument() -> None:
    with pytest.raises(SystemExit) as exception:
        parse_simulation_settings(["--unknown"])

    assert exception.value.code == 2


def test_cli_rejects_non_integer_cycle_count() -> None:
    with pytest.raises(SystemExit) as exception:
        parse_simulation_settings(["--cycles", "abc"])

    assert exception.value.code == 2


def test_cli_rejects_unknown_scenario() -> None:
    with pytest.raises(SystemExit) as exception:
        parse_simulation_settings(["--scenario", "power_failure"])

    assert exception.value.code == 2


def test_cli_rejects_zero_cycle_count() -> None:
    with pytest.raises(ValueError, match="Number of cycles must be greater than zero"):
        parse_simulation_settings(["--cycles", "0"])


def test_cli_rejects_negative_interval() -> None:
    with pytest.raises(ValueError, match="Interval cannot be negative"):
        parse_simulation_settings(["--interval", "-0.1"])


def test_mqtt_transport_is_parsed() -> None:
    settings = parse_simulation_settings(["--transport", "mqtt"])

    assert settings.transport is PublisherTransport.MQTT


def test_unknown_transport_is_rejected() -> None:
    with pytest.raises(SystemExit):
        parse_simulation_settings(["--transport", "unknown"])