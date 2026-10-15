import asyncio
from typing import Any, Annotated
from simplibs.types import tuple_not_empty
# Outers
from ...decorator import to_action
from .._helpers import as_action

tuple_not_empty = Annotated[tuple, tuple_not_empty]


@to_action
def parallel(
    data: Any,
    branches: tuple_not_empty,
) -> tuple[Any, ...]:
    """Runs N actions over the same data and collects the results (concurrently when awaited through `acall`)."""

    # 1. Map each branch to an Action and execute sequentially over the same input data
    return tuple(
        as_action(branch)(data)
        for branch in branches
    )


async def _parallel_acall(self, data: Any) -> tuple[Any, ...]:
    """Async counterpart of `parallel`'s own body.

    Unlike the synchronous version (which necessarily runs branches one
    after another), this awaits every branch CONCURRENTLY via
    `asyncio.gather`, each through its own `.acall(...)` — see this
    module's own design notes for why this is a genuine behavioral
    improvement, not just a safely-bridged equivalent of the sync path.
    """

    # 1. Run every branch concurrently, each resolved via its own acall
    return tuple(
        await asyncio.gather(
            *(as_action(branch).acall(data) for branch in self.branches)
        )
    )


# Attach the hand-written async counterpart directly onto the generated
# class — see design notes for why this can't be derived generically by
# create_action, the same way ParallelCompose.compose() can't be either.
parallel.acall = _parallel_acall

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
under the hood, see `ParallelCompose` in `compose_class/`. Callable both
synchronously (`parallel(branches=(...))(data)`, branches run one after
another) and asynchronously (`await parallel(branches=(...)).acall(data)`,
branches run CONCURRENTLY via `asyncio.gather`).

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

## Why `acall` is hand-attached, and why it uses `asyncio.gather`
Same underlying reasoning as `sequence`'s own design notes for why
`Action`'s default to-thread bridge would be wrong here (it would run
the whole loop inside one thread, and call each child's raising
synchronous `__call__` instead of its `.acall(...)`) — but `parallel`
has an additional, POSITIVE reason to hand-write `acall`, not just a
defect to avoid: `asyncio.gather` gives every branch genuine
concurrency, something no synchronous `for` loop — nor a single
to-thread wrapper around one — could ever provide. This is the one
place in the whole async design where the async path isn't merely "the
same result, safely bridged" — it is a real behavioral improvement over
the synchronous `&` whenever the branches are I/O-bound.

## Why `ParallelCompose` needs no equivalent change of its own
Same as `SequenceCompose` — inherits `acall` through the normal MRO,
since `_parallel_acall` only ever reads `self.branches`, present
identically on both the plain container and its flattened subclass.
"""
