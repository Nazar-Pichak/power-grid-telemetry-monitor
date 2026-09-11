"""Tests for the simulator entry point."""

from unittest.mock import Mock, patch

import pytest

from app.main import main
from app.settings import SimulationSettings
from app.transport import PublisherTransport


@pytest.mark.parametrize(
    "transport",
    [
        PublisherTransport.CONSOLE,
        PublisherTransport.MQTT,
    ],
)
def test_main_starts_simulator_with_selected_publisher(transport: PublisherTransport) -> None:
    settings = SimulationSettings(cycles=1, interval_seconds=0, seed=42, transport=transport)
    publisher = Mock()

    with (
        patch("app.main.parse_simulation_settings", return_value=settings) as parse_settings_mock,
        patch("app.main.create_telemetry_publisher", return_value=publisher) as create_publisher_mock,
        patch("app.main.run_simulator") as run_simulator_mock,
    ):
        main()

    parse_settings_mock.assert_called_once_with()
    create_publisher_mock.assert_called_once_with(transport=transport)
    run_simulator_mock.assert_called_once_with(settings=settings, publisher=publisher)


def test_main_handles_keyboard_interrupt(capsys: pytest.CaptureFixture[str]) -> None:
    settings = SimulationSettings()
    publisher = Mock()

    with (
        patch("app.main.parse_simulation_settings", return_value=settings),
        patch("app.main.create_telemetry_publisher", return_value=publisher),
        patch("app.main.run_simulator", side_effect=KeyboardInterrupt),
    ):
        main()

    captured_output = capsys.readouterr()

    assert captured_output.out == ""
    assert captured_output.err == "Simulator stopped.\n"


def test_main_reports_runtime_error(capsys: pytest.CaptureFixture[str]) -> None:
    settings = SimulationSettings()
    publisher = Mock()

    with (
        patch("app.main.parse_simulation_settings", return_value=settings),
        patch("app.main.create_telemetry_publisher", return_value=publisher),
        patch("app.main.run_simulator", side_effect=RuntimeError("MQTT publishing failed.")),
    ):
        with pytest.raises(SystemExit) as exit_error:
            main()

    captured = capsys.readouterr()

    assert exit_error.value.code == 1
    assert captured.out == ""
    assert captured.err == ("Simulator failed: MQTT publishing failed.\n")