from typing import Any
# Outers
from ...decorator import to_action
from .._helpers import as_action


@to_action
def tap(
    data: Any,
    action: Any,
) -> Any:
    """Runs `action` as a side effect, returns the ORIGINAL data unchanged."""

    # 1. Execute action as a side effect over data
    as_action(action)(data)

    # 2. Return original data unchanged
    return data


tap = tap
"""
Runs `action` as a side effect over `data`, returns `data` unchanged.

Init Params:
    action (Action | Rule | Callable[[Any], Any]): Runs for its side
        effect; its return value is discarded.

Main Param:
    data (Any): The value observed by `action` and returned unchanged.

Output:
    Any: The same `data`, unchanged.

`data & action` (via `parallel`) would also run `action` alongside the
original data, but returns a tuple `(data, action_result)` — the caller
would have to pick the first element to get a clean "side effect, data
unchanged" behavior. `tap` does this directly, as a named, readable
intent.

Example:
    >>> tap(action=log_to_file)(record)
"""


_DESIGN_NOTES = """
# tap — side effect without affecting data

## Why `tap`, not composing from `parallel`
`data & action` would also run `action` alongside the original data but
returns `(data, action_result)` — the caller must pick the first element
to get "side effect, data unchanged" behavior. `tap` does this directly
as a named, readable intent rather than a derivation from a more general
tool.
"""