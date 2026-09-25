from typing import Any, Callable
# Outers
from ...decorator import to_action


@to_action
def lambda_action(
    data: Any,
    func: Callable[[Any], Any]
) -> Any:
    """Adapter for a raw callable that did not originate from `to_action`."""
    return func(data)


lambda_action = lambda_action
"""
Adapter that runs a raw, one-off callable as an Action.

Init Params:
    func (Callable[[Any], Any]): Any single-argument callable.

Main Param:
    data (Any): Passed straight into `func`.

Output:
    Any: `func`'s return value.

This is `Action.resolve_action`'s last-resort branch for a callable that
is neither an `Action` nor a `Rule` — typically an ad-hoc
`lambda x: x.strip()` passed directly into `>>`/`resolve_action`, with no
intent of being a named, independently documented action. Cheapest, no
dynamic class synthesis needed for one-off use.

Example:
    >>> LambdaAction(func=str.strip)("  hi  ")
    'hi'
"""


_DESIGN_NOTES = """
# lambda_action — adapter for a raw callable

## Why it stays separate even though `create_action` does "the same thing"
Not a duplicate of `create_action`'s general capability — it serves a
different purpose: it's the fallback branch `Action.resolve_action` uses
for a plain callable with no intention of being promoted into a named,
independently documented action. Cheapest, safest path for one-off use.

## Reflected operators and plain callables
`func & action`/`func | action`/`func >> action` work automatically
through this path (`resolve_action` -> `lambda_action`) with no special
interpretation needed — unlike `Rule` (where `guard` must invent a "gate"
meaning), `lambda_action` is a plain transformer, so it behaves exactly
like any other Action under `&`/`|`/`>>`.
"""
