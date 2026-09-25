"""
Tests for assert_action_io_types — checking an action class's _input_type/_output_type.
"""
import pytest

from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.asserts.assert_action_io_types import assert_action_io_types


@to_action
def _greet(data: dict) -> str:
    return f"Hi, {data['name']}!"


def test_assert_action_io_types_passes_when_declared_and_matching(subtests):
    """Verify that a use_validations=True action with matching declared types passes."""
    action = _greet()
    assert_action_io_types(
        subtests,
        action,
        expected_input_type=dict,
        expected_output_type=str,
        verbose=False,
    )


def test_assert_action_io_types_passes_without_expected_types(subtests):
    """Verify that omitting expected_input_type/expected_output_type only checks declaration."""
    action = _greet()
    assert_action_io_types(
        subtests,
        action,
        verbose=False,
    )


def test_assert_action_io_types_fails_on_type_mismatch(subtests):
    """Verify that a wrong expected_input_type is treated as a failure."""
    action = _greet()
    with pytest.raises(BaseException):
        assert_action_io_types(
            subtests,
            action,
            expected_input_type=int,
            verbose=False,
        )


def test_assert_action_io_types_fails_when_undeclared(subtests):
    """Verify that an action built with use_validations=False fails the declaration check."""

    @to_action(use_validations=False)
    def _loose(data):
        return data

    action = _loose()

    with pytest.raises(BaseException):
        assert_action_io_types(
            subtests,
            action,
            verbose=False,
        )
