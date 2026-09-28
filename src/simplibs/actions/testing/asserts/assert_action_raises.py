import asyncio
import inspect
from typing import Any, Callable, Sequence
from simplibs.sentinels import UNSET
from simplibs.exception.testing import assert_function_raises
# Outers
from ...base_class import Action


def assert_action_raises(
    subtests: Any,
    action: Action,
    invalid_values: list[Any],
    *,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] | None = None,
    is_async: bool | None = None,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that calling the action on each invalid value raises the expected exception.

    Supports both sync (`action(value)`) and async (`await action.acall(value)`) execution.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        action: The Action instance under test.
        invalid_values: Inputs expected to raise when passed to the action.
        expected_exception_type: If provided, asserted against each raised exception.
            Can be a single exception class (applied to every value) or a Sequence
            matching invalid_values index-by-index (use None to skip specific indices,
            i.e. accept any exception for that index).
        is_async: Explicit flag specifying whether the action is async. If None, it is
            auto-detected via inspect.iscoroutinefunction(action.acall).
        verbose: Enables isolated pytest subtest tracking for each checked value.
        intro: Optional prefix string added to generated subtest identity names.

    Raises:
        ValueError: If a Sequence expected_exception_type doesn't match invalid_values in length.
    """
    is_sequence = (
        isinstance(expected_exception_type, Sequence)
        and not isinstance(expected_exception_type, type)
    )

    if is_sequence and len(expected_exception_type) != len(invalid_values):
        raise ValueError(
            "expected_exception_type sequence must have the same length as invalid_values."
        )

    if is_async is None:
        is_async = inspect.iscoroutinefunction(getattr(action, "acall", None))

    def make_execution_call(val: Any) -> Callable[[], Any]:
        if is_async:
            return lambda: asyncio.run(action.acall(val))
        return lambda: action(val)

    for index, value in enumerate(invalid_values):
        current_type = expected_exception_type[index] if is_sequence else expected_exception_type

        assert_function_raises(
            subtests,
            make_execution_call(value),
            invalid_params=(),
            exception_type=current_type if current_type is not None else UNSET,
            verbose=verbose,
            intro=f"{intro}test_action_raises_#index_{index}_",
        )


_DESIGN_NOTES = """
# assert_action_raises (Execution Negative-Path Contract Blade)

## Purpose
Verifies that an action correctly rejects invalid input by raising — the negative-path
counterpart to assert_action_output. Wraps execution in a zero-arg closure to support
both sync (`action(value)`) and async (`asyncio.run(action.acall(value))`) channels.
Also serves as the underlying driver for testing the synchronous misuse guard (`ParamError`)
on async actions.

## Design Choices
* **Closure Execution Wrapper:** By wrapping the sync or async call inside `make_execution_call`,
  `assert_function_raises` receives a standard callable regardless of whether the action's
  underlying execution path is sync or async.
* **Scalar vs. Sequence expected_exception_type:** Same flexible shape as
  `assert_rule_build_exception`'s expected_error_name/expected_exception_type — a single
  class applies uniformly, a Sequence lets each invalid_values entry assert a different
  exception type.
"""