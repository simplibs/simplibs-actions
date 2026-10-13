"""
Tests for assert_action_output — checking an action's output against expected values.
"""
import pytest

from simplibs.actions.base_class import Action
from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.asserts.assert_action_output import assert_action_output
from simplibs.exception import ParamError


@to_action
def _double(data: int) -> int:
    return data * 2


class _SyncOnlyDouble(Action):
    """Hand-written sync action. Its async channel fails loudly, so a test that
    (wrongly) goes through `acall` is caught immediately."""

    def __call__(self, data, /):
        return data * 2

    async def acall(self, data, /):
        raise AssertionError("acall must not be used to test a sync action")


class _NativeAsyncDouble(Action):
    """Hand-written native-async action: __call__ is the misuse guard, acall does the work."""

    is_async = True

    def __call__(self, data, /):
        raise RuntimeError("use acall")

    async def acall(self, data, /):
        return data * 2


# ==============================================================================
# 1. OUTPUT CHECK
# ==============================================================================

def test_assert_action_output_passes_for_matching_outputs(subtests):
    """Verify that matching valid_values/expected_outputs pass without raising."""
    action = _double()
    assert_action_output(
        subtests,
        action,
        valid_values=[1, 2, 3],
        expected_outputs=[2, 4, 6],
        verbose=False,
    )


def test_assert_action_output_fails_for_mismatched_output(subtests):
    """Verify that a wrong expected output is treated as a failure naming the expected value."""
    action = _double()
    with pytest.raises(AssertionError, match="999"):
        assert_action_output(
            subtests,
            action,
            valid_values=[1],
            expected_outputs=[999],
            verbose=False,
        )


def test_assert_action_output_raises_on_length_mismatch(subtests):
    """Verify that mismatched valid_values/expected_outputs lengths raise ValueError up front."""
    action = _double()
    with pytest.raises(ValueError):
        assert_action_output(
            subtests,
            action,
            valid_values=[1, 2],
            expected_outputs=[2],
            verbose=False,
        )


# ==============================================================================
# 2. ASYNC AUTO-DETECTION (is_async=None reads `action.is_async`)
# ==============================================================================

def test_assert_action_output_supports_async_action(subtests):
    """Verify that assert_action_output correctly handles async actions via acall."""

    @to_action
    async def _async_double(data: int) -> int:
        return data * 2

    action = _async_double()

    assert_action_output(
        subtests,
        action,
        valid_values=[1, 2, 3],
        expected_outputs=[2, 4, 6],
        verbose=False,
    )


def test_assert_action_output_uses_sync_channel_for_sync_action(subtests):
    """Verify auto-detection does not route a sync action through acall.

    Regression: `inspect.iscoroutinefunction(action.acall)` is True for EVERY action, because the
    base `Action.acall` is always `async def`. Detection must read `action.is_async` instead.
    """
    assert_action_output(
        subtests,
        _SyncOnlyDouble(),
        valid_values=[1, 2],
        expected_outputs=[2, 4],
        verbose=False,
    )


def test_assert_action_output_uses_async_channel_for_flagged_action(subtests):
    """Verify auto-detection uses acall for a hand-written action flagged `is_async = True`."""
    assert_action_output(
        subtests,
        _NativeAsyncDouble(),
        valid_values=[1, 2],
        expected_outputs=[2, 4],
        verbose=False,
    )


# ==============================================================================
# 3. EXPLICIT is_async OVERRIDE
# ==============================================================================

def test_assert_action_output_respects_explicit_is_async_override(subtests):
    """Verify that is_async parameter explicitly forces async execution mode."""

    @to_action
    async def _async_greet(data: str) -> str:
        return f"Hello {data}"

    action = _async_greet()

    assert_action_output(
        subtests,
        action,
        valid_values=["World"],
        expected_outputs=["Hello World"],
        is_async=True,
        verbose=False,
    )


def test_assert_action_output_explicit_true_forces_acall_on_sync_action(subtests):
    """Verify the override wins over detection: is_async=True runs even a sync action via acall."""
    with pytest.raises(AssertionError, match="acall must not be used"):
        assert_action_output(
            subtests,
            _SyncOnlyDouble(),
            valid_values=[1],
            expected_outputs=[2],
            is_async=True,
            verbose=False,
        )


def test_assert_action_output_explicit_false_forces_sync_call_on_async_action(subtests):
    """Verify the override wins over detection: is_async=False calls an async action synchronously,
    which its misuse guard rejects with ParamError."""

    @to_action
    async def _async_greet(data: str) -> str:
        return f"Hello {data}"

    action = _async_greet()

    with pytest.raises(ParamError):
        assert_action_output(
            subtests,
            action,
            valid_values=["World"],
            expected_outputs=["Hello World"],
            is_async=False,
            verbose=False,
        )
