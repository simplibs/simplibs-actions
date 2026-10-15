import asyncio
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

    `acall` is the async counterpart — always present, never abstract.
    Every `Action`, even one with no async awareness of its own, is
    awaitable via the default implementation below.
    """

    # Hook signaling to Rule that this object is not meant to be silently
    # absorbed by `Rule.__and__`/`__or__` as a plain predicate — see
    # Rule.py's own design notes for the full rationale.
    __not_rule__ = True

    # Flag indicating whether this action is natively asynchronous.
    # Defaults to False for synchronous/hand-written actions.
    is_async: bool = False

    # ----------------------------------------------------------------------
    # 1) Executable Interface
    # ----------------------------------------------------------------------

    @abstractmethod
    def __call__(self, data: Any, /) -> Any:
        """Run this action over `data` and return the result."""
        raise NotImplementedError

    async def acall(self, data: Any, /) -> Any:
        """Run this action asynchronously.

        Default implementation: bridges the synchronous `__call__` into
        an async context via a worker thread, so ANY Action — even one
        with no async awareness at all — is awaitable for free, without
        blocking the event loop it's awaited from.

        Actions built from a genuinely `async def` source function (via
        `create_action`) override this directly with a real coroutine
        that awaits their own async logic — no thread hop at all in
        that case. See `create_call`'s own design notes for exactly how
        that override is generated.
        """
        return await asyncio.to_thread(self.__call__, data)

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
        """Runs both actions over identical input data (concurrently only through `acall`): `actionA & actionB`."""
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
        """Supports `rule & action` — verify AND run the action over the same data."""
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
# Action — base abstract class (async-aware)

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

## `is_async` class attribute contract
Every `Action` subclass explicitly declares an `is_async: bool` flag.
* Defaults to `False` on the base abstract `Action` class, ensuring that all 
  legacy, hand-written, or synchronous actions carry this attribute uniformly 
  without requiring manual boilerplate.
* Dynamically generated actions via `create_action` set this flag to `True` 
  or `False` based on introspection of the underlying source function.

## `acall` — always present, never abstract

Every `Action` must be callable synchronously (`__call__` is the one
mandatory contract), but not every `Action` needs to think about async
at all to still be usable from one. `acall`'s default implementation —
`asyncio.to_thread(self.__call__, data)` — makes literally any `Action`
awaitable for free: a blocking sync call moved off the event loop, no
extra work required from whoever wrote it.

This default is a real, measured trade-off, not a free lunch:
* **When nothing ever calls `acall`:** genuinely free — an unused method
  on a class costs nothing at call time.
* **When a whole pipeline is natively async** (every step built from an
  `async def` source function): also cheap — one `await` per hop,
  no thread involved at all, because those actions override `acall`
  directly (see `create_call`'s design notes).
* **When a sync action's `acall` is actually invoked from async code:**
  real, non-negligible cost — a thread-pool dispatch, order of tens of
  microseconds, vs. nanoseconds for calling `__call__` directly. Worth
  paying for genuine I/O-bound work; wasteful for a cheap, purely
  computational action. This is an inherent cost of bridging sync code
  into an event loop safely, not something a cleverer default could
  remove — the alternative (calling blocking code directly on the loop)
  would stall every other coroutine sharing it.

## Reflected operators — `__rand__`/`__ror__`/`__rrshift__`

Triggered exclusively by the `__not_rule__` hook on the `Rule` side (see
`Rule.py`'s own design notes) — `rule & action` first hits
`Rule.__and__`, which returns `NotImplemented`, and only then does Python
try `action.__rand__(rule)`.

The semantics of all three are derived from what the `guard` container
does (pass through unchanged if the `Rule` holds, otherwise raise):
* `rule >> action` — check, then continue (sequence).
* `rule & action` — check AND run the action (over the same data, concurrently
  only through `acall`; both must succeed — the spirit of `AllOf`, shifted from 
  "predicate AND predicate" to "gate AND action").
* `rule | action` — check, and on failure run the action instead (the
  spirit of `AnyOf` — at least one path must succeed, only the first
  path is a hard gate).

All three are implemented as the same one-line pattern —
`self.resolve_action(other) <op> self` — wrap the left-hand operand,
hand off to the forward operator. No second copy of any container's
construction logic; one place of truth covers both `rule & action` and
`action & action`. This applies unchanged to the async path too: since
`then`/`__and__`/`__or__` build the SAME composite objects
(`SequenceCompose`/`ParallelCompose`/`fallback` instances) regardless of
whether `acall` will ever be invoked on them, no reflected-operator
logic needed duplicating for async — it was already async-transparent
by construction.

**A typing cost, not a behavioral one:** `Rule.__and__`/`__or__` can now
return either `Rule` or `Action`, depending on the right-hand operand's
type. This is already handled on the `Rule` side via a structural
`_NotARule` `Protocol` plus `@overload` pairs on every binary operator
(`__and__`/`__or__`/`__rand__`/`__ror__`).

## `__not_rule__` remains unchanged

Still the single hook driving this entire asymmetry — `Rule` declines to
treat `Action` as a predicate, `Action` supplies its own, meaningful
interpretation instead. See `Rule.py`'s design notes for the complete
rationale.

## What is deliberately NOT here yet

`sequence`/`parallel`/`fallback` — the containers that run OTHER actions
internally — need their own hand-written `acall`, not this class's
default, to get real concurrency (`parallel`'s `&`) and to correctly
await native-async steps without a needless thread hop. That logic lives
in each container's own module, for the same reason `compose()` lives on
`SequenceCompose`/`ParallelCompose` rather than here: it's bespoke to
what each container actually does with its children, not something this
base class could derive generically.
"""