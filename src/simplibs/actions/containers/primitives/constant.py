from typing import Any
# Outers
from ...decorator import to_action


@to_action
def constant(
    data: Any,
    value: Any
) -> Any:
    """Ignores `data`, always returns `value`."""
    return value


async def _constant_acall(self, data: Any) -> Any:
    """Async counterpart of `constant` — returns the fixed `value`.

    A hand-written one-liner rather than `Action`'s default `acall`,
    for the same reason as `identity`: no work is ever actually done
    here, so there's nothing worth bridging into a worker thread.
    """
    return self.value


# Attach the hand-written async counterpart directly onto the generated class —
# see design notes for why this is worth the one extra line even for a fixed value.
constant.acall = _constant_acall

constant = constant
"""
Ignores `data`, always returns `value`.

Init Params:
    value (Any): The fixed value always returned.

Main Param:
    data (Any): Accepted for pipeline compatibility, never read.

Output:
    Any: `value`, unchanged.

Useful as a default for `fallback`'s `on_error` / `branch`'s
`else_branch`, or as a source step at the start of a pipeline where the
incoming `data` is purely formal. Callable both synchronously
(`constant(value=0)(data)`) and asynchronously
(`await constant(value=0).acall(data)`) — the async path never touches a
worker thread, since there is nothing here to bridge.

Example:
    >>> Constant(value=0)(anything)
    0
"""


_DESIGN_NOTES = """
# constant — ignores input, returns a fixed value

## `data` stays in the signature even though it's unused
`to_action` treats the first parameter as the main pipeline input
regardless of whether the function body reads it — `constant` must
accept `data` to remain callable like any other step inside `sequence`
or any other container that calls it as `(data)`.

## Why `acall` is hand-attached, even though the default would be *correct*
Same reasoning as `identity`'s own design notes: `constant` has no child
action to mis-await, so `Action`'s default `acall` would never be wrong
here — just wasteful, dispatching a worker thread for work that never
does anything besides return an already-known value. One trivial line
avoids that entirely, and `constant` sits in the same common
`on_error`/`else_branch` default position `identity` does, where the
difference is most likely to actually matter.
"""
