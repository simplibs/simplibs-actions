"""
Tests for assert_action — the master orchestrator delegating to the assert_action_* blades.
"""
import pytest

from simplibs.actions.base_class import Action
from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.assert_action import assert_action


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


class _SyncOnlyRaising(Action):
    """Hand-written sync action raising ValueError; its async channel fails with a different error."""

    def __call__(self, data, /):
        raise ValueError("boom")

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
# 1. TYPE GUARD
# ==============================================================================

def test_assert_action_rejects_non_action_target(subtests):
    """Verify that a non-Action object fails the fail-fast type guard."""
    with pytest.raises(AssertionError):
        assert_action(subtests, 42, verbose=False)


# ==============================================================================
# 2. OUTPUT & RAISES CHECKS
# ==============================================================================

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


# ==============================================================================
# 3. deep_check — _input_type / _output_type
# ==============================================================================

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


def test_assert_action_checks_expected_io_types_when_given(subtests):
    """Verify that expected_input_type/expected_output_type are compared with the declared types."""
    assert_action(
        subtests,
        _double(),
        expected_input_type=int,
        expected_output_type=int,
        verbose=False,
    )


def test_assert_action_fails_on_wrong_expected_input_type(subtests):
    """Verify that a wrong expected_input_type is a failure."""
    with pytest.raises(BaseException):
        assert_action(subtests, _double(), expected_input_type=str, verbose=False)


# ==============================================================================
# 4. deep_check — constructor guard
# ==============================================================================

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


def test_assert_action_construction_check_is_gated_by_deep_check(subtests):
    """Verify that with deep_check=False the construction sweep is not run at all.

    The 'invalid' init params below are in fact valid, so the sweep would fail if it ran.
    """

    @to_action
    def _greet(data: dict, prefix: str) -> str:
        return f"{prefix}, {data['name']}!"

    assert_action(
        subtests,
        _greet(prefix="Hi"),
        action_class=_greet,
        invalid_init_params=[((), {"prefix": "perfectly-valid"})],
        deep_check=False,
        verbose=False,
    )


# ==============================================================================
# 5. ASYNC
# ==============================================================================

def test_assert_action_supports_async_action(subtests):
    """Verify that assert_action seamlessly handles async actions."""

    @to_action
    async def _async_double(data: int) -> int:
        return data * 2

    action = _async_double()

    assert_action(
        subtests,
        action,
        valid_values=[1, 2],
        expected_outputs=[2, 4],
        verbose=False,
    )


def test_assert_action_respects_explicit_is_async(subtests):
    """Verify that an explicit is_async=True is accepted for an async action."""

    @to_action
    async def _async_double(data: int) -> int:
        return data * 2

    assert_action(
        subtests,
        _async_double(),
        valid_values=[1],
        expected_outputs=[2],
        is_async=True,
        verbose=False,
    )


def test_assert_action_async_deep_check_verifies_sync_misuse_guard(subtests):
    """Verify that deep_check=True asserts ParamError when sync __call__ is used on an async action."""

    @to_action
    async def _async_greet(data: str) -> str:
        return f"Hello {data}"

    action = _async_greet()

    # deep_check=True + valid_values will invoke action("World") synchronously inside assert_action,
    # which triggers raise_async_action_requires_acall_error (ParamError) and passes the check.
    assert_action(
        subtests,
        action,
        valid_values=["World"],
        expected_outputs=["Hello World"],
        deep_check=True,
        verbose=False,
    )


def test_assert_action_uses_sync_channel_for_sync_action(subtests):
    """Verify a sync action is tested through __call__, both for outputs and for raises.

    Regression: async detection must read `action.is_async`; `iscoroutinefunction(action.acall)`
    is True for every action (the base `Action.acall` is always `async def`).
    """
    assert_action(
        subtests,
        _SyncOnlyDouble(),
        valid_values=[1, 2],
        expected_outputs=[2, 4],
        deep_check=False,
        verbose=False,
    )
    assert_action(
        subtests,
        _SyncOnlyRaising(),
        invalid_values=[1],
        expected_exception_type=ValueError,
        deep_check=False,
        verbose=False,
    )


def test_assert_action_uses_async_channel_for_flagged_action(subtests):
    """Verify a hand-written action flagged `is_async = True` is tested through acall."""
    assert_action(
        subtests,
        _NativeAsyncDouble(),
        valid_values=[1, 2],
        expected_outputs=[2, 4],
        deep_check=False,   # hand-written: no _input_type / sync-misuse ParamError to check
        verbose=False,
    )
