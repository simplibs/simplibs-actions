from typing import Any
from simplibs.types import tuple_not_empty
# Outers
from ...decorator import to_action
from .._helpers import as_action


@to_action
def parallel(
    data: Any,
    branches: tuple_not_empty,
) -> tuple[Any, ...]:
    """Runs N actions over the same data in parallel."""

    # 1. Map each branch to an Action and execute sequentially over the same input data
    return tuple(
        as_action(branch)(data)
        for branch in branches
    )


parallel = parallel
"""
Runs N actions over the same `data`, returning a tuple of results.

Init Params:
    branches (tuple_not_empty[Action | Rule | Callable[[Any], Any]]): The
        actions to run, in order. Must contain at least one branch.

Main Param:
    data (Any): The value passed unchanged to every branch.

Output:
    tuple[Any, ...]: One result per branch, in the same order as `branches`.

For the self-flattening variant `Action.__and__`/`&` actually builds
under the hood, see `ParallelCompose` in `compose_class/`.

Example:
    >>> parallel(branches=(upper, lower))("Hi")
    ('HI', 'hi')
"""


_DESIGN_NOTES = """
# parallel — n-ary parallel run

## Why a tuple parameter, not `*branches`
Same reason as `sequence` — `create_action`'s `validate_param_kinds`
rejects `VAR_POSITIONAL`. `branches: tuple_not_empty[Any]` is compatible and
still meaningfully typeable.

## Non-empty tuple contract via type annotation
Instead of manual `if not branches:` runtime checks inside the body, `parallel`
leverages `tuple_not_empty[Any]` from `simplibs.types`. Validation of empty branch
tuples is delegated directly to the `@to_action` decorator layer.

## Relationship to ParallelCompose
This plain `parallel` container works correctly on its own, but nesting
it directly changes the *shape* of the result — `Parallel(branches=(a,)) & b`
without flattening would produce a tuple containing a tuple, not one
flat tuple. `ParallelCompose` (in `compose_class/`) is what
`Action.__and__` actually constructs, precisely to prevent that. Construct
`parallel` directly only when you deliberately want a fixed,
non-flattening group of branches as a single unit.
"""