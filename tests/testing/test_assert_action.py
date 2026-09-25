"""
Tests for assert_action — the master orchestrator delegating to the assert_action_* blades.
"""
import pytest

from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.assert_action import assert_action


@to_action
def _double(data: int) -> int:
    return data * 2


def test_assert_action_rejects_non_action_target(subtests):
    """Verify that a non-Action object fails the fail-fast type guard."""
    with pytest.raises(AssertionError):
        assert_action(subtests, 42, verbose=False)


def test_assert_action_runs_output_check_when_valid_values_given(subtests):
    """Verify that valid_values + expected_outputs are checked via the output blade."""
    action = _double()
    assert_action(
        subtests,
        action,
        valid_values=[1, 2],
        expected_outputs=[2, 4],
        verbose=False,
    )


def test_assert_action_requires_expected_outputs_alongside_valid_values(subtests):
    """Verify that valid_values without expected_outputs raises ValueError up front."""
    action = _double()
    with pytest.raises(ValueError):
        assert_action(
            subtests,
            action,
            valid_values=[1, 2],
            verbose=False,
        )


def test_assert_action_runs_raises_check_when_invalid_values_given(subtests):
    """Verify that invalid_values are checked via the raises blade."""

    @to_action
    def _reciprocal(data: float) -> float:
        if data == 0:
            raise ZeroDivisionError("cannot divide by zero")
        return 1 / data

    action = _reciprocal()

    # 0.0, not 0 — an int would be rejected by validate_call's own type check
    # (ValidationError) before ever reaching the ZeroDivisionError in the function body.
    assert_action(
        subtests,
        action,
        invalid_values=[0.0],
        expected_exception_type=ZeroDivisionError,
        verbose=False,
    )


def test_assert_action_deep_check_true_passes_when_io_types_declared(subtests):
    """Verify that deep_check=True (the default) runs the io_types blade and passes when declared."""
    action = _double()
    assert_action(subtests, action, verbose=False)


def test_assert_action_deep_check_true_fails_when_io_types_undeclared(subtests):
    """Verify that deep_check=True (default) surfaces an io_types failure for a use_validations=False action."""

    @to_action(use_validations=False)
    def _loose(data):
        return data

    action = _loose()

    with pytest.raises(BaseException):
        assert_action(subtests, action, verbose=False)


def test_assert_action_deep_check_false_skips_io_types(subtests):
    """Verify that deep_check=False skips the io_types blade entirely (no declaration required)."""

    @to_action(use_validations=False)
    def _loose(data):
        return data

    action = _loose()

    # Would fail under deep_check=True (no _input_type declared); must pass with deep_check=False.
    assert_action(
        subtests,
        action,
        deep_check=False,
        verbose=False,
    )


def test_assert_action_runs_construction_check_when_opted_in(subtests):
    """Verify that action_class + invalid_init_params triggers the construction blade under deep_check."""

    @to_action
    def _greet(data: dict, prefix: str) -> str:
        return f"{prefix}, {data['name']}!"

    action = _greet(prefix="Hi")

    assert_action(
        subtests,
        action,
        action_class=_greet,
        invalid_init_params=[((), {"prefix": 123})],
        verbose=False,
    )


def test_assert_action_skips_construction_check_without_action_class(subtests):
    """Verify that invalid_init_params alone, without action_class, is silently skipped (not an error)."""
    action = _double()

    assert_action(
        subtests,
        action,
        invalid_init_params=[((), {"bogus": 1})],
        verbose=False,
    )
