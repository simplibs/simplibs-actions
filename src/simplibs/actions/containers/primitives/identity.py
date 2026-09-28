from typing import Any
# Outers
from ...decorator import to_action


@to_action
def identity(
    data: Any
) -> Any:
    """No-op — returns data unchanged."""
    return data


async def _identity_acall(self, data: Any) -> Any:
    """Async counterpart of `identity` — returns `data` unchanged.

    A hand-written one-liner rather than `Action`'s default `acall`, so
    that a no-op action stays a genuine no-op even when awaited: no
    worker-thread dispatch for work that never does anything in the
    first place.
    """
    return data


# Attach the hand-written async counterpart directly onto the generated class —
# see design notes for why this is worth the one extra line even for a no-op.
identity.acall = _identity_acall

identity = identity
"""
No-op — returns `data` unchanged.

Init Params:
    (none)

Main Param:
    data (Any): The value returned unchanged.

Output:
    Any: The same object passed in as `data`.

A named, explicit "do nothing" is more readable inside `branch`'s
`else_branch` / `fallback`'s `on_error` than `None`/omission, and is the
correct neutral element for `sequence`/`parallel` wherever an explicit
empty step is needed syntactically. Callable both synchronously
(`identity()(data)`) and asynchronously (`await identity().acall(data)`)
— the async path never touches a worker thread, since there is nothing
here to bridge.

Example:
    >>> Identity()(42)
    42
"""


_DESIGN_NOTES = """
# identity — no-op

## Why a named function instead of "just don't use anything"
An explicit, named "do nothing" path is clearer than `None`/omission in
`branch`'s `else_branch` or `fallback`'s `on_error`, and is the correct
neutral element for `sequence`/`parallel` should a syntactically "empty"
step ever be required (both now fail fast on zero steps/branches — see
their own design notes).

## File name = class name = function name
The old hand-written version had `NoOp.py: class IdentityAction` — the
one place in the whole package where the file name and class name did
not match. The functional style unifies this automatically, since the
function's own name *is* the resulting action's name.

## Why `acall` is hand-attached, even though the default would be *correct*
Unlike `branch`/`for_each`/`retry`/`tap`, `Action`'s default `acall`
(`asyncio.to_thread(self.__call__, data)`) would not be WRONG here —
`identity` has no child action to mis-await, so nothing would break.
It would, however, be pure waste: dispatching a worker thread to do
literally nothing takes measurably longer than doing nothing directly.
Since `identity` sits at the bottom of the composition chain (a common
`else_branch`/`on_error` default), and the fix costs exactly one
trivial line, this is the rare case where the cost/benefit calculus from
`Action`'s own design notes tips all the way to "obviously worth it" —
see this file's own docstring for context on why `identity` shows up in
those positions often enough for the difference to matter.
"""
