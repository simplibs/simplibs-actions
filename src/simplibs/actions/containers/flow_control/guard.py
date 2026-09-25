from typing import Any
# Outers
from ...decorator import to_action
from .._helpers import as_predicate
# Inners
from ._validations import raise_guard_failed


@to_action
def guard(
    data: Any,
    rule: Any,
) -> Any:
    """Hard gate: raises if `rule` does not hold for `data`."""

    # 1. Normalize rule into a bool-returning predicate
    predicate = as_predicate(rule)

    # 2. Pass data through unchanged if condition holds
    if predicate(data):
        return data

    # 3. Raise custom exception if rule supports build_exception interface
    if hasattr(rule, "build_exception"):
        raise rule.build_exception(data, context="Guard evaluation failed")

    # 4. Raise standard structured exception on guard failure
    return raise_guard_failed(data)


guard = guard
"""
Hard gate — passes `data` through unchanged if `rule` holds, otherwise raises.

Init Params:
    rule (Rule | Callable[[Any], bool]): The predicate `data` must satisfy.
        Accepts a `Rule` instance (uses its own `.build_exception` on
        failure for a specific diagnostic) or a plain callable returning
        `bool` (raises a structured `ParamError` on failure).

Main Param:
    data (Any): The value being checked against `rule`.

Output:
    Any: The original `data`, unchanged, if `rule` holds.

`guard` is the container `Action.resolve_action` wraps every bare `Rule`
into. This makes it the single foundation for three reflected operators
between `Rule` and `Action`:

    rule >> action   # "check, then continue" (Sequence)
    rule & action    # "check AND run" (Parallel)
    rule | action    # "check, on failure run instead" (Fallback)

Anyone changing this file's raise-on-failure behavior is silently
changing the meaning of all three operators at once — not just this one
container. See `Action`'s own docs for the full reflected-operator story.

Example:
    >>> is_positive = greater_than(0)
    >>> guard(rule=is_positive)(5)
    5
    >>> guard(rule=is_positive)(-5)
    Traceback (most recent call last):
        ...
    simplibs.exception.ParamError: Guard evaluation failed...
"""


_DESIGN_NOTES = """
# guard — hard gate, load-bearing wall for reflected operators

## Not just another container
`guard` is what `Action.resolve_action` wraps every bare `Rule` into —
which means `rule >> action`, `rule & action`, and `rule | action`
(`Action`'s reflected operators) ALL rest on exactly this behavior: pass
through unchanged if `rule` holds, otherwise raise. A change here is a
silent change to three operators at once, not one container. Anyone
editing this file should know that before changing anything.

## How the raised exception behaves in each of the three operators
* `&` (Parallel) — no try/except, a failing gate kills the whole parallel
  run. Correct: "both must succeed".
* `|` (Fallback) — the exception is caught, execution switches to the
  fallback action. Correct: that is the entire point of a fallback.
* `>>` (Sequence) — the exception ends the sequence, no further step
  runs. Correct: short-circuit.
Three different behaviors for one exception from one source — this is
intentional, not an inconsistency; written down explicitly so it doesn't
read as a bug to a future reader.

## Diagnostics
If `rule` provides `build_exception`, its own specific message is used —
the same delegation pattern `AllOf`/`AnyOf` use in `validate`. A plain
callable without `build_exception` triggers `raise_guard_failed`.
"""