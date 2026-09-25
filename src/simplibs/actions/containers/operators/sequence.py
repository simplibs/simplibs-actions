from typing import Any
from simplibs.types import tuple_not_empty
# Outers
from ...decorator import to_action
from .._helpers import as_action


@to_action
def sequence(
    data: Any,
    steps: tuple_not_empty,
) -> Any:
    """Chains any number of steps left to right."""

    # 1. Initialize result with the incoming data
    result = data

    # 2. Sequentially process each step, feeding the result of one into the next
    for step in steps:
        result = as_action(step)(result)

    # 3. Return the final accumulated result
    return result


sequence = sequence
"""
Chains any number of steps left to right, threading the output of each
step into the next.

Init Params:
    steps (tuple_not_empty[Action | Rule | Callable[[Any], Any]]): The steps to
        run in order. Must contain at least one step.

Main Param:
    data (Any): The initial input fed to the first step.

Output:
    Any: The final step's return value.

For the self-flattening variant `Action.then`/`>>` actually builds under
the hood, see `SequenceCompose` in `compose_class/`.

Example:
    >>> sequence(steps=(strip, upper))("  hello  ")
    'HELLO'
"""


_DESIGN_NOTES = """
# sequence — n-ary sequential chaining

## Why a tuple parameter, not `*steps`
`create_action`'s `validate_param_kinds` rejects `VAR_POSITIONAL`
(`*args`) — a function with a variadic parameter cannot be wrapped by
`create_action`. `steps: tuple_not_empty` is the only compatible shape,
and it is meaningfully typeable (`IsTyping` handles `tuple` types
without trouble). Users still compose with `a >> b >> c` — this detail
only concerns the raw function's own call convention.

## Non-empty tuple contract via type annotation
Instead of manual `if not steps:` runtime checks inside the body, `sequence`
leverages `tuple_not_empty` from `simplibs.types`. Validation of empty step
tuples is delegated directly to the `@to_action` decorator layer.

## Relationship to SequenceCompose
This plain `sequence` container works correctly on its own but nests
when chained directly (`Sequence(steps=(a,)) >> b` would otherwise build
a `Sequence` holding another `Sequence` as one of its steps).
`SequenceCompose` (in `compose_class/`) is what `Action.then` actually
constructs, precisely to avoid that nesting. Construct `sequence`
directly only when you deliberately want a fixed, non-flattening group
of steps as a single unit.
"""