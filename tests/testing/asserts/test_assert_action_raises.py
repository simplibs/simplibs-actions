"""
Tests for assert_action_raises — checking that an action raises on invalid input.

NOTE on the values used: `_reciprocal` is annotated `data: float`, so an `int` is rejected by
validate_call's own type check (ValidationError) before it ever reaches the function body.
Inputs meant to reach the body (0.0 raising ZeroDivisionError, 2.0 returning normally) are
therefore floats — with an int, a test would "pass" for the wrong reason.
"""
import pytest

from simplibs.actions.base_class import Action
from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.asserts.assert_action_raises import assert_action_raises
from simplibs.exception import ParamError


@to_action
def _reciprocal(data: float) -> float:
    if data == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return 1 / data


@to_action
def _pick(data: int) -> int:
    if data == 1:
        raise ValueError("bad-one")
    if data == 2:
        raise TypeError("bad-two")
    return data


class _SyncOnlyRaising(Action):
    """Hand-written sync action raising ValueError. Its async channel fails with a different
    error, so a test that (wrongly) goes through `acall` is caught immediately."""

    def __call__(self, data, /):
        raise ValueError("boom")

    async def acall(self, data, /):
        raise AssertionError("acall must not be used to test a sync action")


class _NativeAsyncRaising(Action):
    """Hand-written native-async action: __call__ is the misuse guard, acall raises KeyError."""

    is_async = True

    def __call__(self, data, /):
        raise RuntimeError("use acall")

    async def acall(self, data, /):
        raise KeyError("async-boom")


# ==============================================================================
# 1. RAISES CHECK
# ==============================================================================

def test_assert_action_raises_passes_for_actually_raising_input(subtests):
    """Verify that an input which really raises the expected type passes the check."""
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
            invalid_values=[2.0],   # float on purpose — runs the body and returns 0.5, nothing raised
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
            invalid_values=[0.0],   # raises ZeroDivisionError, which is not a ValueError
            expected_exception_type=ValueError,
            verbose=False,
        )


def test_assert_action_raises_without_expected_type_accepts_any_exception(subtests):
    """Verify that expected_exception_type=None (default) only requires that something is raised."""
    action = _reciprocal()
    assert_action_raises(subtests, action, invalid_values=[0.0], verbose=False)


# ==============================================================================
# 2. expected_exception_type AS A SEQUENCE
# ==============================================================================

def test_assert_action_raises_supports_per_index_sequence(subtests):
    """Verify that a Sequence of expected_exception_type is matched index-by-index."""
    action = _pick()

    assert_action_raises(
        subtests,
        action,
        invalid_values=[1, 2],
        expected_exception_type=[ValueError, TypeError],
        verbose=False,
    )


def test_assert_action_raises_sequence_none_entry_accepts_any_exception(subtests):
    """Verify that a None entry in the Sequence skips the type check for that index."""
    action = _pick()

    assert_action_raises(
        subtests,
        action,
        invalid_values=[1, 2],
        expected_exception_type=[ValueError, None],
        verbose=False,
    )


def test_assert_action_raises_sequence_mismatching_entry_fails(subtests):
    """Verify that a wrong type at one index of the Sequence is a failure."""
    action = _pick()

    with pytest.raises(BaseException):
        assert_action_raises(
            subtests,
            action,
            invalid_values=[1, 2],
            expected_exception_type=[ValueError, ValueError],   # index 1 raises TypeError
            verbose=False,
        )


def test_assert_action_raises_raises_on_sequence_length_mismatch(subtests):
    """Verify that a mismatched-length Sequence expected_exception_type raises ValueError up front."""
    action = _reciprocal()
    with pytest.raises(ValueError):
        assert_action_raises(
            subtests,
            action,
            invalid_values=[0.0],
            expected_exception_type=[ZeroDivisionError, TypeError],
            verbose=False,
        )


# ==============================================================================
# 3. ASYNC AUTO-DETECTION (is_async=None reads `action.is_async`)
# ==============================================================================

def test_assert_action_raises_supports_async_action(subtests):
    """Verify that assert_action_raises correctly catches exceptions in async actions."""

    @to_action
    async def _async_reciprocal(data: float) -> float:
        if data == 0:
            raise ZeroDivisionError("cannot divide by zero")
        return 1 / data

    action = _async_reciprocal()

    assert_action_raises(
        subtests,
        action,
        invalid_values=[0.0],
        expected_exception_type=ZeroDivisionError,
        verbose=False,
    )


def test_assert_action_raises_uses_sync_channel_for_sync_action(subtests):
    """Verify auto-detection does not route a sync action through acall.

    Regression: `inspect.iscoroutinefunction(action.acall)` is True for EVERY action, because the
    base `Action.acall` is always `async def`. Detection must read `action.is_async` instead.
    """
    assert_action_raises(
        subtests,
        _SyncOnlyRaising(),
        invalid_values=[1],
        expected_exception_type=ValueError,
        verbose=False,
    )


def test_assert_action_raises_uses_async_channel_for_flagged_action(subtests):
    """Verify auto-detection uses acall for a hand-written action flagged `is_async = True`."""
    assert_action_raises(
        subtests,
        _NativeAsyncRaising(),
        invalid_values=[1],
        expected_exception_type=KeyError,
        verbose=False,
    )


# ==============================================================================
# 4. EXPLICIT is_async OVERRIDE
# ==============================================================================

def test_assert_action_raises_respects_explicit_is_async_override(subtests):
    """Verify that is_async parameter can explicitly control the execution mode."""

    @to_action
    async def _async_fail(data: int) -> int:
        raise ValueError("async-fail")

    action = _async_fail()

    assert_action_raises(
        subtests,
        action,
        invalid_values=[1],
        expected_exception_type=ValueError,
        is_async=True,
        verbose=False,
    )


def test_assert_action_raises_sync_misuse_guard_on_async_action(subtests):
    """Verify is_async=False calls an async action synchronously and sees its ParamError guard.

    This is exactly how assert_action verifies the sync-misuse guard under deep_check.
    """

    @to_action
    async def _async_greet(data: str) -> str:
        return f"Hello {data}"

    action = _async_greet()

    assert_action_raises(
        subtests,
        action,
        invalid_values=["World"],
        expected_exception_type=ParamError,
        is_async=False,
        verbose=False,
    )
