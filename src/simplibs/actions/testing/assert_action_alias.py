import asyncio
from typing import Any
from simplibs.sentinels import UNSET
from simplibs.exception.testing import maybe_subtest
# Outers
from ..base_class import Action


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
        intro: Optional prefix string added to the generated subtest identity names.

    Raises:
        ValueError: Only one of `sample_action` and `expected_output` is given (the smoke test
            needs both, and would silently not run).
        AssertionError: If `alias` is not identical to `canonical`, or if the smoke test
            output does not match `expected_output`.
    """
    if (sample_action is None) != (expected_output is UNSET):
        raise ValueError("sample_action and expected_output must be given together (the smoke test needs both).")

    alias_name = getattr(alias, "__name__", type(alias).__name__)
    canonical_name = getattr(canonical, "__name__", type(canonical).__name__)
    prefix = f"{intro}[{alias_name}] "

    # 1. Structural Identity Check (alias is canonical)
    with maybe_subtest(
        subtests,
        name=f"{prefix}test_alias_is_canonical",
        verbose=verbose,
    ):
        assert alias is canonical, (
            f"Alias '{alias_name}' is not the exact same object as '{canonical_name}'."
        )

    # 2. End-to-End Behavioral Smoke Test (only when sample_action and expected_output are given)
    if sample_action is not None:
        with maybe_subtest(
            subtests,
            name=f"{prefix}test_smoke_run",
            verbose=verbose,
        ):
            if getattr(sample_action, "is_async", False):
                result = asyncio.run(sample_action.acall(sample_input))
            else:
                result = sample_action(sample_input)
            assert result == expected_output, (
                f"Alias action result {result!r} did not match expected output {expected_output!r}."
            )


_DESIGN_NOTES = """
# assert_action_alias (Alias Identity & Contract Verification)

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
   importable, correctly exposed, and callable in a real curried pipeline context. An async
   `sample_action` is run through `acall`.

## 2. Same Reporting as the Other Tools
Every check runs through `maybe_subtest` and carries the prefix `{intro}[alias_name] `, like
`assert_action` and the profile tools, so `verbose=False` is a plain block and the report names
the alias. The names are read with `getattr(..., "__name__", ...)`, so an alias that is not a
function (an instance, a `partial`) is reported by its type instead of crashing.

## 3. A Smoke Test Is All or Nothing
`sample_action` and `expected_output` belong together. With only one of them the smoke test would
not run and the test would be green for the wrong reason, so the call raises `ValueError`.

## 4. Atomic Design
This assertion function is intentionally lightweight. It does not attempt to test edge cases,
invalid inputs, or pipeline combinations — those belong exclusively to the test suite of
the canonical implementation.
"""
