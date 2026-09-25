# Outers
from ....base_class import Action
from ..sequence import sequence


class SequenceCompose(sequence):
    """Self-flattening variant of `sequence`, used internally by `Action.then`.

    Composing two actions via `>>` should never nest a Sequence inside
    another Sequence — `compose` unwraps either side that is already a
    `SequenceCompose` instance instead of wrapping it as a single step.
    Constructed the same way as `sequence` itself
    (`SequenceCompose(steps=(...))`); the only addition is `compose`.
    """

    __slots__ = ()

    @classmethod
    def compose(
        cls,
        first: Action,
        second: Action,
    ) -> "SequenceCompose":
        """Merge two actions into one flat `SequenceCompose`.

        Unwraps `first`/`second` when they are already `SequenceCompose`
        instances (in any combination), instead of nesting.
        """

        # 1. Extract existing steps if an operand is already SequenceCompose, otherwise wrap as single step
        first_steps = first.steps if isinstance(first, cls) else (first,)
        second_steps = second.steps if isinstance(second, cls) else (second,)

        # 2. Return new flattened SequenceCompose instance combining all steps
        return cls(steps=first_steps + second_steps)


_DESIGN_NOTES = """
# SequenceCompose — self-flattening Sequence used by Action.then

## Why a hand-written subclass, not part of `sequence` itself
`sequence` (in `../sequence.py`) is a plain `create_action`-generated
container — it works correctly on its own but nests when chained
(`a >> b >> c` naively builds `Sequence(Sequence(a, b), c)`). Flattening
is bespoke construction logic a generic factory can't derive by itself —
the same reason `AllOf`/`AnyOf` in `validate` are hand-written rather
than generated. `SequenceCompose` subclasses the generated `sequence`
base and adds exactly the one thing it's missing.

## Why flattening lives in `compose`, not in `__rshift__`/`then` here
`Action.then` (base class) calls `SequenceCompose.compose(self,
resolve_action(next_step))` regardless of whether `self` is already a
`SequenceCompose` or an ordinary `Action`. This makes flattening
symmetric on both sides without any operator override needed on this
class itself: `x >> sequence_instance`, `sequence_instance >> x`, and
`sequence_instance >> sequence_instance` all go through the same
`compose` call, because `Action`'s reflected `__rrshift__` already just
delegates to the forward `then`.
"""