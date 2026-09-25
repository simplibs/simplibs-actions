"""
Tests for assert_action_raises — checking that an action raises on invalid input.
"""
import pytest

from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.asserts.assert_action_raises import assert_action_raises


@to_action
def _reciprocal(data: float) -> float:
    if data == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return 1 / data


def test_assert_action_raises_passes_for_actually_raising_input(subtests):
    """Verify that an input which really raises the expected type passes the check.

    Uses 0.0, not 0 — _reciprocal's `data: float` annotation means an int 0 would be
    rejected by validate_call's own type check (ValidationError) before ever reaching
    the ZeroDivisionError inside the function body.
    """
    action = _reciprocal()
    assert_action_raises(
        subtests,
        action,
        invalid_values=[0.0],
        expected_exception_type=ZeroDivisionError,
        verbose=False,
    )


def test_assert_action_raises_fails_for_non_raising_input(subtests):
    """Verify that an input which does NOT raise is treated as a failure."""
    action = _reciprocal()
    with pytest.raises(BaseException):
        assert_action_raises(
            subtests,
            action,
            invalid_values=[2],
            expected_exception_type=ZeroDivisionError,
            verbose=False,
        )


def test_assert_action_raises_fails_on_wrong_exception_type(subtests):
    """Verify that raising the wrong exception type is treated as a failure."""
    action = _reciprocal()
    with pytest.raises(BaseException):
        assert_action_raises(
            subtests,
            action,
            invalid_values=[0],
            expected_exception_type=ValueError,
            verbose=False,
        )


def test_assert_action_raises_supports_per_index_sequence(subtests):
    """Verify that a Sequence of expected_exception_type is matched index-by-index."""

    @to_action
    def _pick(data: int) -> int:
        if data == 1:
            raise ValueError("bad-one")
        if data == 2:
            raise TypeError("bad-two")
        return data

    action = _pick()

    assert_action_raises(
        subtests,
        action,
        invalid_values=[1, 2],
        expected_exception_type=[ValueError, TypeError],
        verbose=False,
    )


def test_assert_action_raises_raises_on_sequence_length_mismatch(subtests):
    """Verify that a mismatched-length Sequence expected_exception_type raises ValueError up front."""
    action = _reciprocal()
    with pytest.raises(ValueError):
        assert_action_raises(
            subtests,
            action,
            invalid_values=[0],
            expected_exception_type=[ZeroDivisionError, TypeError],
            verbose=False,
        )
