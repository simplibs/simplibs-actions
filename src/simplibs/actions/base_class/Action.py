from abc import ABC, abstractmethod
from typing import Any
from simplibs.rules import Rule
# Inners
from ._validations import raise_invalid_action_target


class Action(ABC):
    """Abstract base class for all operative actions and transformations.

    `__call__` is the sole abstract method — unlike `Rule` (where
    `is_valid` is the answer to a question and `__call__` is just
    convenient sugar over it), for an `Action` being callable IS the
    whole point, so no second method (`execute`/`act`) is needed at the
    base level. Concrete subclasses arise in two ways: hand-written
    containers implementing `__call__` directly (e.g. `SequenceCompose`/
    `ParallelCompose`, which need bespoke flattening logic no generic
    factory can derive on its own), or generated from an ordinary
    function via `create_action`/`to_action` (e.g. `guard`, `branch`,
    `sequence`, `fallback` — nearly everything else).
    """

    # Hook signaling to Rule that this object is not meant to be silently
    # absorbed by `Rule.__and__`/`__or__` as a plain predicate — see
    # Rule.py's own design notes for the full rationale.
    __not_rule__ = True

    # ----------------------------------------------------------------------
    # 1) Executable Interface
    # ----------------------------------------------------------------------

    @abstractmethod
    def __call__(self, data: Any, /) -> Any:
        """Run this action over `data` and return the result."""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # 2) Operator-Based Composition — Forward Direction (self on the left)
    # ----------------------------------------------------------------------

    def then(self, next_step: Any) -> "Action":
        """Chains this action with a subsequent action, rule, or callable."""
        from ..containers.operators.compose_class import SequenceCompose
        return SequenceCompose.compose(first=self, second=self.resolve_action(next_step))

    def __rshift__(self, next_step: Any) -> "Action":
        """Chains this action with a subsequent step via the `>>` operator."""
        return self.then(next_step)

    def __and__(self, other: Any) -> "Action":
        """Executes actions in parallel over identical input data: `actionA & actionB`."""
        from ..containers.operators.compose_class import ParallelCompose
        return ParallelCompose.compose(first=self, second=self.resolve_action(other))

    def __or__(self, other: Any) -> "Action":
        """Fallback handling: executes `other` if this action fails: `actionA | actionB`."""
        from ..containers.operators import fallback
        return fallback(action=self, on_error=self.resolve_action(other))

    # ----------------------------------------------------------------------
    # 3) Operator-Based Composition — Reflected Direction (self on the right)
    # ----------------------------------------------------------------------
    #
    # Triggered when `Rule.__and__`/`__or__` declines the combination
    # because of `__not_rule__` (see Rule.py's own design notes) and
    # Python falls back to `other.__rand__`/`__ror__`/`__rrshift__` — or
    # when `other` is a plain callable/Rule with no operator of its own
    # at all. Each method simply wraps `other` via `resolve_action` and
    # hands off to the forward operator — one place of truth, no
    # duplicated container-construction logic.

    def __rand__(self, other: Any) -> "Action":
        """Supports `rule & action` — verify AND execute in parallel."""
        return self.resolve_action(other) & self

    def __ror__(self, other: Any) -> "Action":
        """Supports `rule | action` — verify, or run a fallback action on failure."""
        return self.resolve_action(other) | self

    def __rrshift__(self, other: Any) -> "Action":
        """Supports `rule >> action` — verify the rule, then continue with the action."""
        return self.resolve_action(other) >> self

    # ----------------------------------------------------------------------
    # 4) Resolution Helper
    # ----------------------------------------------------------------------

    @staticmethod
    def resolve_action(obj: Any) -> "Action":
        """Convert an Action, a Rule, or a plain callable into an Action instance.

        Args:
            obj: An `Action` instance (returned unchanged), a `Rule`
                instance (wrapped into `guard`), or any other callable
                (wrapped into `lambda_action`).

        Returns:
            An `Action` instance ready to be composed.

        Raises:
            TypeError: If `obj` is neither an `Action`, a `Rule`, nor callable.
        """

        # 1. Already an Action instance — return it unchanged
        if isinstance(obj, Action):
            return obj

        # 2. A Rule instance — wrap it into the hard-gate container
        if isinstance(obj, Rule):
            from ..containers.flow_control import guard
            return guard(rule=obj)

        # 3. Any other callable — wrap it into the plain-transformer adapter
        if callable(obj):
            from ..containers.wrappers import lambda_action
            return lambda_action(func=obj)

        # 4. Anything else is not a valid Action target
        return raise_invalid_action_target(obj)


_DESIGN_NOTES = """
# Action — base abstract class (redesigned)

## Why only `__call__`, no `execute`/`act` at the base level

An earlier version had `execute` as the abstract method and `__call__` as
a thin wrapper over it — mirroring `Rule.is_valid`/`__call__`. That
mirroring turned out to be a mistake: for `Rule`, `is_valid` is the
*answer to a question* and callability is a convenience on top; for
`Action`, callability itself IS the substance — an action *is* a
function with one main input. The second method was never actually
needed, and once caused a real bug (a class generated by `create_action`
had `__call__`, but the base `Action` required `execute` — the class
could not be instantiated at all). Collapsing to a single abstract
`__call__` removes that mismatch structurally, not with a patch.

Subclasses arise in two ways:
* **hand-written** — `SequenceCompose`/`ParallelCompose` implement
  `__call__` directly (inherited from their `create_action`-generated
  base, `sequence`/`parallel`) because they need bespoke flattening
  logic (`compose`) that no generic factory can derive on its own;
* **via `create_action`/`to_action`** — nearly everything else (`guard`,
  `branch`, `for_each`, `sequence`, `parallel`, `fallback`, `identity`,
  `constant`, `lambda_action`, `log_step`, `retry`, `tap`). There,
  `act`/`__init__`/`__call__` are implementation details of the
  *generator* (needed for the separate `validate_call`/`log_this`
  wrapping of each), not a requirement of the base class itself.

## Reflected operators — `__rand__`/`__ror__`/`__rrshift__`

Triggered exclusively by the `__not_rule__` hook on the `Rule` side (see
`Rule.py`'s own design notes) — `rule & action` first hits
`Rule.__and__`, which returns `NotImplemented`, and only then does Python
try `action.__rand__(rule)`.

The semantics of all three are derived from what the `guard` container
does (pass through unchanged if the `Rule` holds, otherwise raise):
* `rule >> action` — check, then continue (sequence).
* `rule & action` — check AND run the action (in parallel; both must
  succeed — the spirit of `AllOf`, shifted from "predicate AND
  predicate" to "gate AND action").
* `rule | action` — check, and on failure run the action instead (the
  spirit of `AnyOf` — at least one path must succeed, only the first
  path is a hard gate).

All three are implemented as the same one-line pattern —
`self.resolve_action(other) <op> self` — wrap the left-hand operand,
hand off to the forward operator. No second copy of any container's
construction logic; one place of truth covers both `rule & action` and
`action & action`.

**A typing cost, not a behavioral one:** `Rule.__and__`/`__or__` can now
return either `Rule` or `Action`, depending on the right-hand operand's
type. This is already handled on the `Rule` side via a structural
`_NotARule` `Protocol` plus `@overload` pairs on every binary operator
(`__and__`/`__or__`/`__rand__`/`__ror__`) — see `Rule.py`'s own design
notes, section 6, for why a `Protocol` is used instead of importing
`Action` directly (keeping `simplibs-validate` independent of
`simplibs-actions`, even for typing purposes).

## `__not_rule__` remains unchanged

Still the single hook driving this entire asymmetry — `Rule` declines to
treat `Action` as a predicate, `Action` supplies its own, meaningful
interpretation instead. See `Rule.py`'s design notes for the complete
rationale.
"""
