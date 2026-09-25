# Outers
from ....base_class import Action
from ..parallel import parallel


class ParallelCompose(parallel):
    """Self-flattening variant of `parallel`, used internally by `Action.__and__`.

    Composing two actions via `&` should never nest a Parallel inside
    another Parallel — `compose` unwraps either side that is already a
    `ParallelCompose` instance instead of wrapping it as a single branch.
    """

    __slots__ = ()

    @classmethod
    def compose(
        cls,
        first: Action,
        second: Action,
    ) -> "ParallelCompose":
        """Merge two actions into one flat `ParallelCompose`.

        Unwraps `first`/`second` when they are already `ParallelCompose`
        instances (in any combination), instead of nesting.
        """

        # 1. Extract existing branches if an operand is already ParallelCompose, otherwise wrap as single branch
        first_branches = first.branches if isinstance(first, cls) else (first,)
        second_branches = second.branches if isinstance(second, cls) else (second,)

        # 2. Return new flattened ParallelCompose instance combining all branches
        return cls(branches=first_branches + second_branches)


_DESIGN_NOTES = """
# ParallelCompose — self-flattening Parallel used by Action.__and__

## The real bug this fixes
Without flattening, `a & b & c` — left-associative `&` — built
`Parallel(Parallel(a, b), c)`, whose result was the nested tuple
`((r_a, r_b), r_c)` instead of the flat `(r_a, r_b, r_c)`. Unlike
`SequenceCompose` (where the un-flattened version was still functionally
correct, just less introspectable), here the un-flattened version
produced a genuinely different, wrong output SHAPE — this is the
container where flattening is a necessity, not just an improvement.

## Why flattening lives in `compose`, not in `__and__`/`__rand__` here
Same reasoning as `SequenceCompose` — `Action.__and__` (base class) calls
`ParallelCompose.compose(self, resolve_action(other))` regardless of
which side is already a `ParallelCompose`, so flattening is symmetric on
both sides without any operator override needed on this class itself.
"""