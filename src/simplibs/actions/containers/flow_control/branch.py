from typing import Any
# Outers
from ...decorator import to_action
from .._helpers import as_action, as_predicate


@to_action
def branch(
    data: Any,
    condition: Any,
    then_branch: Any,
    else_branch: Any | None = None,
) -> Any:
    """Soft conditional branching over `data`."""

    # 1. Normalize condition into a bool-returning predicate and adapt main branch to Action
    predicate = as_predicate(condition)
    then_action = as_action(then_branch)

    # 2. Evaluate predicate over data and execute positive branch (then)
    if predicate(data):
        return then_action(data)

    # 3. Evaluate negative branch (else) if explicitly provided
    if else_branch is not None:
        else_action = as_action(else_branch)
        return else_action(data)

    # 4. Pass original data through unchanged (when condition fails and no else_branch is defined)
    return data


branch = branch
"""
Soft conditional branching over `data`.

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
    Any: Whatever the chosen branch returns, or `data` unchanged if
        `condition` fails and no `else_branch` was given.

Unlike `guard`, a failing `condition` here is not an error — `branch`
answers "which way should data go", `guard` answers "is data even
allowed to continue". Two different roles, not an inconsistency between
similarly-shaped containers.

Example:
    >>> branch(condition=is_positive, then_branch=double, else_branch=zero)(5)
    10
"""


_DESIGN_NOTES = """
# branch — soft conditional routing

## Why "soft" branching, not raising
`branch` without `else_branch` passes data through unchanged when
`condition` fails — deliberately different from `guard`, where failure
always means raising. `branch` answers "which way should data go",
`guard` answers "is data even allowed to continue" — two different
roles, not an inconsistency.

## Typing
`condition`/`then_branch`/`else_branch` are behavioral objects
(Rule/Action/Callable), not values — `Rule`/`validated_type` adds nothing
here; the check stays structural via `as_predicate`/`as_action`.
"""