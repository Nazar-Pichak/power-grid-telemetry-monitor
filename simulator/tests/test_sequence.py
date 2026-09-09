"""Tests for independent transformer message sequences."""

import pytest

from app.sequence import SequenceTracker


def test_first_sequence_for_device_is_one() -> None:
    tracker = SequenceTracker()

    result = tracker.next_sequence("TRF-PLN-01")

    assert result == 1


def test_sequence_increases_for_same_device() -> None:
    tracker = SequenceTracker()

    first = tracker.next_sequence("TRF-PLN-01")
    second = tracker.next_sequence("TRF-PLN-01")
    third = tracker.next_sequence("TRF-PLN-01")

    assert first == 1
    assert second == 2
    assert third == 3


def test_different_devices_have_independent_sequences() -> None:
    tracker = SequenceTracker()

    first_device_first = tracker.next_sequence("TRF-PLN-01")
    first_device_second = tracker.next_sequence("TRF-PLN-01")
    second_device_first = tracker.next_sequence("TRF-PLN-02")

    assert first_device_first == 1
    assert first_device_second == 2
    assert second_device_first == 1


def test_empty_device_code_is_rejected() -> None:
    tracker = SequenceTracker()

    with pytest.raises(ValueError, match="Device code cannot be empty"):
        tracker.next_sequence("")