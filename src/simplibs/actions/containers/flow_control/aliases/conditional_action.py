from ..branch import branch

conditional_action = branch
"""
Alias of `branch` — soft conditional routing over `data`.

Init Params:
    condition (Rule | Callable[[Any], bool]): Predicate deciding which
        branch runs.
    then_branch (Action | Rule | Callable[[Any], Any]): Runs when
        `condition` holds.
    else_branch (Action | Rule | Callable[[Any], Any] | None): Runs when
        `condition` fails. If omitted, `data` passes through unchanged.

Main Param:
    data (Any): The value routed to one of the branches.

Output:
    Any: Whatever the chosen branch returns, or `data` unchanged.

Provided for pipelines that favor a more descriptive name than `branch`.
See `branch`'s own module for the canonical implementation and design
notes — `conditional_action` is a pure alias, no separate behavior.
"""
