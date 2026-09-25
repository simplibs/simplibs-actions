from typing import Any, Callable
from simplibs.rules import Rule
# Inners
from .validations import raise_invalid_predicate


def as_predicate(condition: Any) -> Callable[[Any], bool]:
    """Normalize a Rule instance or a plain callable into a single bool-returning call.

    Replaces repeated duck-typing checks in `guard`/`branch` with a single
    source of truth — aligning with the helper pattern used across the library.
    """

    # 1. Official Rule instance -> direct method reference (fastest path)
    if isinstance(condition, Rule):
        return condition.is_valid

    # 2. Plain lambda / function / any callable
    if callable(condition):
        # noinspection PyTypeChecker
        return condition

    # 3. Structured exception helper for invalid predicate inputs
    raise_invalid_predicate(condition)


_DESIGN_NOTES = """
# as_predicate — shared condition adapter

## Purpose
`guard` and `branch` both need the same thing: "give me a function that
returns bool for `data`", whether `condition`/`rule` arrived as a `Rule`
instance (`is_valid`) or a plain callable. Without this helper, both
containers would carry duplicate validation and resolution logic. Using an
explicit `isinstance(condition, Rule)` check ensures fast and type-safe
method binding.

## Exception Handling
When an invalid predicate (neither a `Rule` nor a callable) is passed,
`raise_invalid_predicate` is triggered to throw a structured exception,
keeping validation error formats consistent across the library.

## Why it doesn't special-case Action
`Action.__call__` is callable too, but this helper treats it like any
other callable — it falls into the `callable(condition)` branch and gets
invoked directly. The result (`Any`, not necessarily `bool`) is then
evaluated by ordinary Python truthiness in `guard`/`branch`. This works,
but gives no guarantee the return value is meaningful as a condition —
left unaddressed here on purpose; if it ever needs constraining, that
belongs in `guard`/`branch` themselves, not this shared helper.

## Relationship to as_action
Sibling in this same `_helpers` package — `as_predicate` answers "is this
true?", `as_action` answers "run this over data". Split into two files,
not one `_helpers.py`, since each serves a different group of containers,
consistent with the "one item per file" convention across the rest
of the library.
"""