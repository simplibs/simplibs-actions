import asyncio
import inspect
from typing import Any
from simplibs.exception.testing import maybe_subtest
# Outers
from ...base_class import Action


def assert_action_output(
    subtests: Any,
    action: Action,
    valid_values: list[Any],
    expected_outputs: list[Any],
    *,
    is_async: bool | None = None,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that calling the action on each valid value produces the matching expected output.

    Supports both sync (`action(value)`) and async (`await action.acall(value)`) actions.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        action: The Action instance under test.
        valid_values: Inputs expected to be accepted by the action.
        expected_outputs: Outputs expected for each corresponding entry in valid_values
            (must be the same length).
        is_async: Explicit flag specifying whether the action is async. If None, it is
            auto-detected via inspect.iscoroutinefunction(action.acall).
        verbose: Enables isolated pytest subtest tracking for each checked value.
        intro: Optional prefix string added to generated subtest identity names.

    Raises:
        ValueError: If valid_values and expected_outputs differ in length.
    """
    if len(valid_values) != len(expected_outputs):
        raise ValueError(
            "valid_values and expected_outputs must have the same length "
            f"(got {len(valid_values)} and {len(expected_outputs)})."
        )

    if is_async is None:
        is_async = inspect.iscoroutinefunction(getattr(action, "acall", None))

    for index, (value, expected) in enumerate(zip(valid_values, expected_outputs)):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_output_#index_{index}",
            verbose=verbose,
        ):
            if is_async:
                result = asyncio.run(action.acall(value))
            else:
                result = action(value)

            assert result == expected, (
                f"Expected action({value!r}) to return {expected!r}, got {result!r}."
            )


_DESIGN_NOTES = """
# assert_action_output (Execution Output Contract Blade)

## Purpose
Verifies the one thing generic tooling cannot infer on its own: that a specific action,
given a specific input, produces the specific business-logic output the caller expects.
Supports both synchronous (`action(value)`) and asynchronous (`await action.acall(value)`)
actions.

## Design Choices
* **Dual Sync/Async Execution Support:** Auto-detects `is_async` via `acall` or accepts an
  explicit override. Async execution is driven seamlessly via `asyncio.run(action.acall(value))`.
* **Index-Paired Lists, Not (input, output) Tuples:** Matches the calling convention of
  `assert_rule_contract`'s `valid_values`/`invalid_values` (parallel lists) rather than
  introducing a new tuple-pair shape.
* **Fail-Fast Length Guard:** A length mismatch between `valid_values` and `expected_outputs`
  is almost always a copy-paste mistake in the test itself — raising early avoids a confusing
  off-by-one `IndexError` mid-sweep.
"""