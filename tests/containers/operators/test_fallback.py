"""
Tests for fallback — tries `action`; on failure either runs `on_error` or returns data unchanged.
"""
from simplibs.actions.containers.operators.fallback import fallback
from simplibs.actions.testing import assert_action


def _boom(_x):
    raise ValueError("boom")


def test_fallback_returns_primary_result_on_success(subtests):
    """Verify that fallback returns action's own result when it doesn't raise."""
    action = fallback(action=lambda x: x * 2)

    assert_action(
        subtests,
        action,
        valid_values=[5],
        expected_outputs=[10],
    )


def test_fallback_runs_on_error_when_action_raises(subtests):
    """Verify that fallback runs on_error and returns its result when action raises."""
    action = fallback(action=_boom, on_error=lambda x: f"recovered:{x}")

    assert_action(
        subtests,
        action,
        valid_values=[7],
        expected_outputs=["recovered:7"],
    )


def test_fallback_returns_original_data_when_no_on_error_given(subtests):
    """Verify that fallback returns the original data unchanged when action raises and no on_error is set."""
    action = fallback(action=_boom)

    assert_action(
        subtests,
        action,
        valid_values=[7],
        expected_outputs=[7],
    )


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