"""
Tests for fallback — tries `action`; on failure either runs `on_error` or returns data unchanged.
"""
import pytest
from simplibs.actions.containers.operators.fallback import fallback
from simplibs.actions.testing import assert_action


def _boom(_x):
    raise ValueError("boom")


def test_fallback_returns_primary_result_on_success():
    """Verify that fallback returns action's own result when it doesn't raise."""
    action = fallback(action=lambda x: x * 2)

    assert action(5) == 10


def test_fallback_runs_on_error_when_action_raises():
    """Verify that fallback runs on_error and returns its result when action raises."""
    action = fallback(action=_boom, on_error=lambda x: f"recovered:{x}")

    assert action(7) == "recovered:7"


def test_fallback_returns_original_data_when_no_on_error_given():
    """Verify that fallback returns the original data unchanged when action raises and no on_error is set."""
    action = fallback(action=_boom)

    assert action(7) == 7


def test_fallback_only_catches_the_declared_exception_types(subtests):
    """Verify that an exception outside the declared `exceptions` filter propagates, not swallowed."""

    def _type_error(_x):
        raise TypeError("not caught by this filter")

    action = fallback(action=_type_error, exceptions=ValueError)

    assert_action(
        subtests,
        action,
        invalid_values=[1],
        expected_exception_type=TypeError,
    )


async def _async_boom(_x):
    raise ValueError("async_boom")


@pytest.mark.asyncio
async def test_fallback_acall_returns_primary_result_on_success():
    """Verify that acall returns primary action's result when it doesn't raise."""

    async def async_double(x: int) -> int:
        return x * 2

    action = fallback(action=async_double)

    result = await action.acall(5)

    assert result == 10


@pytest.mark.asyncio
async def test_fallback_acall_runs_async_on_error_when_action_raises():
    """Verify that acall runs async on_error and returns its result when primary action raises."""

    async def async_recovery(x: int) -> str:
        return f"async_recovered:{x}"

    action = fallback(action=_async_boom, on_error=async_recovery)

    result = await action.acall(7)

    assert result == "async_recovered:7"