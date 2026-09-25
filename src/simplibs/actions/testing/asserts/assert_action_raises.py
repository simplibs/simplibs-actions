from typing import Any, Sequence
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
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that calling the action on each invalid value raises the expected exception.

    Thin wrapper around simplibs-exception's own assert_function_raises, taking advantage
    of the fact that an Action instance is directly callable as `action(value)` — no
    raise/type-check logic is reimplemented here.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        action: The Action instance under test.
        invalid_values: Inputs expected to raise when passed to the action.
        expected_exception_type: If provided, asserted against each raised exception.
            Can be a single exception class (applied to every value) or a Sequence
            matching invalid_values index-by-index (use None to skip specific indices,
            i.e. accept any exception for that index).
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

    for index, value in enumerate(invalid_values):
        current_type = expected_exception_type[index] if is_sequence else expected_exception_type

        assert_function_raises(
            subtests,
            action,
            invalid_params=(value,),
            exception_type=current_type if current_type is not None else UNSET,
            verbose=verbose,
            intro=f"{intro}test_action_raises_#index_{index}_",
        )


_DESIGN_NOTES = """
# assert_action_raises (Execution Negative-Path Contract Blade)

## Purpose
Verifies that an action correctly rejects invalid input by raising — the negative-path
counterpart to assert_action_output. Because an Action instance is callable exactly
like a plain function, this is a near-direct pass-through to
simplibs-exception's assert_function_raises, mirroring how assert_rule_param_error
reuses the same primitive for constructor misuse sweeps.

## Design Choices
* **Scalar vs. Sequence expected_exception_type:** Same flexible shape as
  assert_rule_build_exception's expected_error_name/expected_exception_type — a single
  class applies uniformly, a Sequence lets each invalid_values entry assert a different
  exception type (useful for a container like `guard`, which can fail either via the
  wrapped Rule's own ValidationError or via a generic ParamError depending on the input).
* **UNSET Fallback:** When no expected type is given (None, or a None entry inside a
  Sequence), UNSET is passed through to assert_function_raises, which then accepts any
  BaseException — appropriate when the caller only wants "does it raise at all", without
  committing to a specific exception class.
"""
