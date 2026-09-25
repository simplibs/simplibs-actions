from typing import Any
from ..base_class import Action
from simplibs.sentinels import UNSET


def assert_action_alias(
    subtests: Any,
    alias: Any,
    canonical: Any,
    *,
    sample_action: Action | None = None,
    sample_input: Any = None,
    expected_output: Any = UNSET,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Asserts that an alias is a true identity alias of a canonical container/action.

    Verifies the two load-bearing properties of any alias in this library:
    1. Identity: The alias is literally the exact same object in memory (`alias is canonical`).
    2. End-to-end execution: When called with sample arguments, the alias executes correctly
       and produces the exact same result as the canonical version.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        alias: The alias object under test (e.g., `run_in_sequence`).
        canonical: The canonical implementation object (e.g., `sequence`).
        sample_action: An optional Action constructed using `alias` to run a smoke test.
        sample_input: Data input passed to `sample_action` during the smoke test.
        expected_output: The expected output from running `sample_action(sample_input)`.
        verbose: If True, registers individual checks as isolated pytest subtests.
        intro: Optional prefix string added to the generated subtest identity name.

    Raises:
        AssertionError: If `alias` is not identical to `canonical`, or if the smoke test
            output does not match `expected_output`.
    """
    prefix = f"{intro} " if intro else ""

    # 1. Structural Identity Check (alias is canonical)
    if verbose:
        with subtests.test(f"{prefix}Identity Check: {alias.__name__} is {canonical.__name__}"):
            assert alias is canonical, (
                f"Alias '{alias.__name__}' is not the exact same object as '{canonical.__name__}'."
            )
    else:
        assert alias is canonical, (
            f"Alias '{alias.__name__}' is not the exact same object as '{canonical.__name__}'."
        )

    # 2. End-to-End Behavioral Smoke Test (optional if sample_action and expected_output are given)
    if sample_action is not None and expected_output is not UNSET:
        if verbose:
            with subtests.test(f"{prefix}Smoke Test Execution: {alias.__name__}"):
                result = sample_action(sample_input)
                assert result == expected_output, (
                    f"Alias action result '{result}' did not match expected output '{expected_output}'."
                )
        else:
            result = sample_action(sample_input)
            assert result == expected_output, (
                f"Alias action result '{result}' did not match expected output '{expected_output}'."
            )


from simplibs.sentinels import UNSET

_DESIGN_NOTES = """
# assert_alias (Alias Identity & Contract Verification)

## Purpose
The canonical helper for verifying aliases within the `simplibs-actions` library (such as
`run_in_sequence`, `run_in_parallel`, `try_or_fallback`). It eliminates duplicate test
batteries by focusing strictly on alias invariants rather than re-testing underlying logic.

---

## 1. The Two Invariants of an Alias

An alias in this architecture is NOT a wrapper, decorator, or proxy function — it is a
direct reference assignment (`run_in_sequence = sequence`). Therefore, testing an alias
requires verifying only two specific facts:

1. **Memory Identity (`alias is canonical`)**: Proves zero overhead, zero wrapping, and 100%
   behavioral identity. If this assertion passes, any test covering `canonical` transitively
   covers `alias`.
2. **End-to-End Smoke Test**: A single execution path to ensure the alias module is cleanly
   importable, correctly exposed, and callable in a real curried pipeline context.

## 2. Integration with pytest-subtests

Following the standard pattern across `simplibs` testing utilities (`assert_action`,
`assert_rule_contract`), `assert_alias` optionally splits its execution into isolated
`subtests`. This ensures that identity failure and execution failure are reported as clear,
independent test outcomes.

## 3. Atomic Design

This assertion function is intentionally lightweight. It does not attempt to test edge cases,
invalid inputs, or pipeline combinations — those belong exclusively to the test suite of
the canonical implementation.
"""