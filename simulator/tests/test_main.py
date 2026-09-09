"""Tests for the simulator entry point."""

from unittest.mock import Mock, patch

from app.main import main
from app.settings import SimulationSettings


def test_main_starts_simulator_with_console_publisher() -> None:
    settings = SimulationSettings(cycles=1, interval_seconds=0, seed=42,)
    publisher = Mock()

    with (
        patch("app.main.parse_simulation_settings", return_value=settings) as parse_settings_mock,
        patch("app.main.ConsoleTelemetryPublisher", return_value=publisher) as publisher_class_mock,
        patch("app.main.run_simulator") as run_simulator_mock,
    ):
        main()

    parse_settings_mock.assert_called_once_with()
    publisher_class_mock.assert_called_once_with()
    run_simulator_mock.assert_called_once_with(settings=settings, publisher=publisher)


def test_main_handles_keyboard_interrupt(capsys) -> None:
    settings = SimulationSettings()
    publisher = Mock()

    with (
        patch("app.main.parse_simulation_settings", return_value=settings),
        patch("app.main.ConsoleTelemetryPublisher", return_value=publisher),
        patch("app.main.run_simulator", side_effect=KeyboardInterrupt),
    ):
        main()

    captured_output = capsys.readouterr()

    assert captured_output.out == ""
    assert captured_output.err == "Simulator stopped.\n"