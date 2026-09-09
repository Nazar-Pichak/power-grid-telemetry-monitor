"""Tests for finite and continuous simulation execution."""

from itertools import islice
from unittest.mock import Mock, call, patch

import pytest

from app.fleet import FleetSimulator
from app.scenarios import FaultScenario
from app.simulation_loop import run_simulation_cycles


def create_fleet_mock() -> Mock:
    """Create a fleet mock returning one identifiable cycle."""

    fleet = Mock(spec=FleetSimulator)
    fleet.generate_messages.return_value = ("message",)

    return fleet


def test_finite_loop_generates_requested_number_of_cycles() -> None:
    fleet = create_fleet_mock()

    with patch("app.simulation_loop.sleep") as sleep_mock:
        generated_cycles = list(run_simulation_cycles(fleet_simulator=fleet, cycles=3, interval_seconds=1.0))

    assert generated_cycles == [("message",), ("message",), ("message",)]
    assert fleet.generate_messages.call_count == 3
    assert fleet.generate_messages.call_args_list == [
        call(scenarios_by_device=None),
        call(scenarios_by_device=None),
        call(scenarios_by_device=None),
    ]
    assert sleep_mock.call_args_list == [call(1.0), call(1.0)]


def test_single_cycle_does_not_sleep() -> None:
    fleet = create_fleet_mock()

    with patch("app.simulation_loop.sleep") as sleep_mock:
        generated_cycles = list(run_simulation_cycles(fleet_simulator=fleet, cycles=1, interval_seconds=10.0))

    assert generated_cycles == [("message",)]
    fleet.generate_messages.assert_called_once_with(scenarios_by_device=None)
    sleep_mock.assert_not_called()


def test_scenarios_are_forwarded_to_fleet() -> None:
    fleet = create_fleet_mock()
    scenarios = {"TRF-PLN-01": FaultScenario.OVERHEATING}

    with patch("app.simulation_loop.sleep"):
        list(
            run_simulation_cycles(
                fleet_simulator=fleet,
                cycles=1,
                interval_seconds=0.0,
                scenarios_by_device=scenarios,
            )
        )

    fleet.generate_messages.assert_called_once_with(scenarios_by_device=scenarios)


@pytest.mark.parametrize("cycles", [0, -1])
def test_non_positive_cycle_count_is_rejected(cycles: int) -> None:
    fleet = create_fleet_mock()

    with pytest.raises(ValueError, match="Number of cycles must be greater than zero"):
        list(
            run_simulation_cycles(
                fleet_simulator=fleet,
                cycles=cycles,
                interval_seconds=0.0,
            )
        )

    fleet.generate_messages.assert_not_called()


def test_negative_interval_is_rejected() -> None:
    fleet = create_fleet_mock()

    with pytest.raises(ValueError, match="Interval cannot be negative"):
        list(
            run_simulation_cycles(
                fleet_simulator=fleet,
                cycles=1,
                interval_seconds=-0.1,
            )
        )

    fleet.generate_messages.assert_not_called()


def test_continuous_loop_can_be_consumed_incrementally() -> None:
    fleet = create_fleet_mock()

    with patch("app.simulation_loop.sleep") as sleep_mock:
        generated_cycles = list(
            islice(
                run_simulation_cycles(
                    fleet_simulator=fleet,
                    cycles=None,
                    interval_seconds=1.0,
                ),
                3,
            )
        )

    assert generated_cycles == [("message",), ("message",), ("message",)]
    assert fleet.generate_messages.call_count == 3
    assert sleep_mock.call_args_list == [call(1.0), call(1.0)]