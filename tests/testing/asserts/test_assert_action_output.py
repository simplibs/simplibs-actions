"""
Tests for assert_action_output — checking an action's output against expected values.
"""
import pytest

from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.asserts.assert_action_output import assert_action_output


@to_action
def _double(data: int) -> int:
    return data * 2


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
    """Verify that a wrong expected output is treated as a failure."""
    action = _double()
    with pytest.raises(AssertionError):
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