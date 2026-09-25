from typing import Any
# Outers
from ...decorator import to_action


@to_action
def identity(
    data: Any
) -> Any:
    """No-op — returns data unchanged."""
    return data


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
empty step is needed syntactically.

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
"""
