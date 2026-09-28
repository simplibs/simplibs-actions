"""
Tests for raise_async_action_requires_acall_error — guard against synchronous __call__ invocation on async actions.
"""
from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.creator._helpers.validations.raise_async_action_requires_acall_error import (
    raise_async_action_requires_acall_error,
)
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def test_raise_async_action_requires_acall_error_with_action_instance(subtests):
    """Verify that an async Action instance raises a structured ParamError with the class name."""

    @to_action
    async def _async_step(data: int) -> int:
        return data * 2

    instance = _async_step()

    assert_exception_function(
        subtests,
        raise_async_action_requires_acall_error,
        invalid_params=(instance,),
        exception_type=ParamError,
        value="AsyncStep",
        label="__call__",
        expected="An async caller using `await action.acall(data)`.",
        problem="wraps an async source function and cannot be called synchronously via __call__",
        how_to_fix="Call this action with `await action.acall(data)` instead of `action(data)`",
        exception=TypeError,
    )


def test_raise_async_action_requires_acall_error_with_raw_async_function(subtests):
    """Verify that a raw async callable raises a structured ParamError with function's __name__."""

    async def _raw_async_func(data: str) -> str:
        return data.upper()

    assert_exception_function(
        subtests,
        raise_async_action_requires_acall_error,
        invalid_params=(_raw_async_func,),
        exception_type=ParamError,
        value="_raw_async_func",
        label="__call__",
        expected="An async caller using `await action.acall(data)`.",
        problem="'_raw_async_func' wraps an async source function",
        how_to_fix="Call this action with `await action.acall(data)` instead of `action(data)`",
        exception=TypeError,
    )