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
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that calling the action on each valid value produces the matching expected output.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        action: The Action instance under test — called directly as `action(value)`.
        valid_values: Inputs expected to be accepted by the action.
        expected_outputs: Outputs expected for each corresponding entry in valid_values
            (must be the same length).
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

    for index, (value, expected) in enumerate(zip(valid_values, expected_outputs)):
        with maybe_subtest(
            subtests,
            name=f"{intro}test_output_#index_{index}",
            verbose=verbose,
        ):
            result = action(value)
            assert result == expected, (
                f"Expected action({value!r}) to return {expected!r}, got {result!r}."
            )


_DESIGN_NOTES = """
# assert_action_output (Execution Output Contract Blade)

## Purpose
Verifies the one thing generic tooling cannot infer on its own: that a specific action,
given a specific input, produces the specific business-logic output the caller expects.
Everything mechanical (parameter binding, slot assignment, validate_call wiring) is
already covered elsewhere in the create_action/to_action pipeline itself — this blade
is deliberately the "user-supplied truth table" half of the contract.

## Why Not Reuse assert_function_valid_input
`assert_function_valid_input` (simplibs-exception) only asserts that the call completes
without raising — it has no concept of an expected return value. Since an Action
instance is directly callable, it could technically be passed there, but that would
silently skip the output-correctness check that is the entire point of this blade.
`assert_rule_validate` faced a similar situation and handled it via a local closure;
here it's promoted to its own blade because output checking (unlike a rule's boolean
passthrough) is the primary thing callers of `assert_action` actually care about.

## Design Choices
* **Index-Paired Lists, Not (input, output) Tuples:** Matches the calling convention of
  `assert_rule_contract`'s `valid_values`/`invalid_values` (parallel lists) rather than
  introducing a new tuple-pair shape.
* **Fail-Fast Length Guard:** A length mismatch between `valid_values` and
  `expected_outputs` is almost always a copy-paste mistake in the test itself — raising
  early avoids a confusing off-by-one `IndexError` mid-sweep.
"""
