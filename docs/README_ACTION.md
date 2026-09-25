# ⚙️ `Action` — Abstract Base Class for Pipeline Steps

`Action` is the single foundation every executable step in `simplibs-actions` is built
on — from the simplest one-line transformer (`identity`, `constant`) to a fully
composed pipeline (`sequence >> guard >> parallel`). It does not implement any
transformation itself; instead it provides three things every action needs:

1. A minimal, mandatory contract every concrete action must fulfill (`__call__`).
2. Operator-based composition (`>>`, `&`, `|`) that lets any two actions — or an
   action and a `Rule`, or an action and a plain callable — combine into a new action,
   without either side needing to know anything about the other.
3. A single resolution helper (`resolve_action`) that turns any of those three
   acceptable shapes (`Action`, `Rule`, plain callable) into a real `Action` instance,
   used internally by every operator and every container that accepts "an action, a
   rule, or a callable" as one of its own parameters.

```python
from abc import ABC, abstractmethod
from typing import Any

class Action(ABC):
    ...
```

## A note on why `Action` is abstract, and why it has only one abstract method

`Action` can never be instantiated directly — `__call__` is declared with
`@abstractmethod` and carries no implementation of its own. Unlike `Rule` (where
`is_valid` answers a yes/no question and `__call__` is just convenient sugar over it),
for an `Action` **being callable IS the whole point** — there is no separate "real"
method underneath it that a second name would expose. This is why `Action` needs no
`execute`/`act` counterpart at the base-class level the way `Rule` needs `is_valid`
alongside its own `__call__`.

Concrete subclasses arise two ways:

* **Hand-written containers** implementing `__call__` directly — `SequenceCompose`/
  `ParallelCompose`, which need bespoke flattening logic no generic factory can derive
  on its own (see [`README_CONTAINERS.md`](README_CONTAINERS.md#sequencecompose)).
* **Generated from an ordinary function** via `create_action`/`to_action` — `guard`,
  `branch`, `sequence`, `fallback`, and nearly every other built-in container (see
  [`README_CREATOR.md`](README_CREATOR.md)).

---

## 🧭 Table of Contents

* [`__call__`](#__call__)
* [`then` / `__rshift__`](#then--__rshift__)
* [`__and__`](#__and__)
* [`__or__`](#__or__)
* [`__rand__` / `__ror__` / `__rrshift__`](#__rand__--__ror__--__rrshift__)
* [`resolve_action`](#resolve_action)

[⬅️ Back to main README](../README.md#-the-action-class)

---

### `__call__`

**Abstract.** The single true entry point for running any action — every concrete
action, hand-written or generated, ultimately implements this and nothing else at the
base-class level.

**Parameters:**

* `data` (*Any*, positional-only): The value this action operates on.

**Returns:**

* `Any`: Whatever this action produces from `data`.

**Example usage:**

```python
result = my_action(some_input)
```

**Under the hood:**

```python
@abstractmethod
def __call__(self, data: Any, /) -> Any:
    """Run this action over `data` and return the result."""
    raise NotImplementedError
```

[▲ Back to top](#-table-of-contents)

---

### `then` / `__rshift__`

Chains this action with a subsequent step — the method behind the `>>` operator.
`next_step` is resolved into an `Action` first (via `resolve_action`), so it can be an
`Action`, a `Rule`, or any plain callable, not just another `Action` instance.

**Parameters:**

* `next_step` (*Action | Rule | Callable[[Any], Any]*): The step to run after this one.

**Returns:**

* `Action`: A flattened `SequenceCompose` — chaining three or more actions
  (`a >> b >> c`) never nests, it always produces one flat sequence of steps. See
  [`SequenceCompose`](README_CONTAINERS.md#sequencecompose) for the flattening
  mechanics.

**Example usage:**

```python
pipeline = strip_action >> upper_action >> save_action
pipeline("  hello  ")
```

**Under the hood:**

```python
def then(self, next_step: Any) -> "Action":
    from ..containers.operators.compose_class import SequenceCompose
    return SequenceCompose.compose(self, self.resolve_action(next_step))

def __rshift__(self, next_step: Any) -> "Action":
    return self.then(next_step)
```

[▲ Back to top](#-table-of-contents)

---

### `__and__`

Runs this action and `other` in parallel over the **same** input — the method behind
the `&` operator.

**Parameters:**

* `other` (*Action | Rule | Callable[[Any], Any]*): The action to run alongside this
  one.

**Returns:**

* `Action`: A flattened `ParallelCompose` whose result is a flat
  `tuple[Any, ...]` — one entry per branch, in order. Chaining three or more branches
  (`a & b & c`) never nests the result shape. See
  [`ParallelCompose`](README_CONTAINERS.md#parallelcompose).

**Example usage:**

```python
both = upper_action & lower_action
both("Hi")   # -> ("HI", "hi")
```

**Under the hood:**

```python
def __and__(self, other: Any) -> "Action":
    from ..containers.operators.compose_class import ParallelCompose
    return ParallelCompose.compose(self, self.resolve_action(other))
```

[▲ Back to top](#-table-of-contents)

---

### `__or__`

Fallback handling — the method behind the `|` operator. Runs this action; if it
raises, runs `other` instead.

**Parameters:**

* `other` (*Action | Rule | Callable[[Any], Any]*): The action to fall back to on
  failure.

**Returns:**

* `Action`: A `fallback` container with this action as `action` and `other` (resolved)
  as `on_error`. See [`fallback`](README_CONTAINERS.md#fallback) for the exact
  catch/return semantics.

**Example usage:**

```python
resilient = risky_parse | default_value
resilient(raw_input)   # -> default_value's result, if risky_parse raises
```

**Under the hood:**

```python
def __or__(self, other: Any) -> "Action":
    from ..containers.operators import fallback
    return fallback(self, self.resolve_action(other))
```

[▲ Back to top](#-table-of-contents)

---

### `__rand__` / `__ror__` / `__rrshift__`

The reflected counterparts of `__and__`/`__or__`/`__rshift__`, triggered when the
left-hand operand doesn't know how to combine with an `Action` — most commonly a
`Rule`, whose own `__and__`/`__or__` decline via the `__not_rule__` hook (see
`Rule`'s own design notes in the `simplibs-rules` documentation) and hand control back
to Python's reflected-operator protocol. Each one simply resolves the left-hand
operand into an `Action` and hands off to the forward operator — one place of truth,
no duplicated container-construction logic.

**Parameters:**

* `other` (*Any*): The left-hand operand Python couldn't combine any other way.

**Returns:**

* `Action`: Identical in shape to what the forward operator would build, with
  `resolve_action(other)` standing in on the left.

**Example usage:**

```python
# is_integer is a Rule, not an Action — this is what makes the following work:
checked = is_integer >> add_one     # verify, then continue
parallel_check = is_integer & double  # verify AND execute in parallel
fallback_check = is_integer | safe_default
```

**Under the hood:**

```python
def __rand__(self, other: Any) -> "Action":
    """Supports `rule & action` — verify AND execute in parallel."""
    return self.resolve_action(other) & self

def __ror__(self, other: Any) -> "Action":
    """Supports `rule | action` — verify, or run a fallback action on failure."""
    return self.resolve_action(other) | self

def __rrshift__(self, other: Any) -> "Action":
    """Supports `rule >> action` — verify the rule, then continue with the action."""
    return self.resolve_action(other) >> self
```

[▲ Back to top](#-table-of-contents)

---

### `resolve_action`

**Static method.** Converts an `Action`, a `Rule`, or a plain callable into a real
`Action` instance — the single normalization point every operator above, and every
container that accepts "an action, a rule, or a callable" as one of its own
parameters (`sequence`'s `steps`, `parallel`'s `branches`, `fallback`'s `action`/
`on_error`, `guard`'s `rule`, ...), routes through.

**Parameters:**

* `obj` (*Any*): The candidate — an `Action` instance, a `Rule` instance, or any other
  callable.

**Returns:**

* `Action`: `obj` unchanged if it already is one; a `guard` wrapping `obj` if it's a
  `Rule`; a `lambda_action` wrapping `obj` for any other callable.

**Raises:**

* `TypeError` (wrapped as `ParamError`): If `obj` is neither an `Action`, a `Rule`,
  nor callable at all.

**Example usage:**

```python
Action.resolve_action(my_action)        # -> my_action, unchanged
Action.resolve_action(is_integer)       # -> guard(is_integer)
Action.resolve_action(lambda x: x + 1)  # -> lambda_action(func=lambda x: x + 1)
Action.resolve_action(42)               # -> raises (not Action/Rule/callable)
```

**Under the hood:**

```python
@staticmethod
def resolve_action(obj: Any) -> "Action":
    # 1. Already an Action instance — return it unchanged
    if isinstance(obj, Action):
        return obj

    # 2. A Rule instance — wrap it into the hard-gate container
    if isinstance(obj, Rule):
        from ..containers.flow_control import guard
        return guard(obj)

    # 3. Any other callable — wrap it into the plain-transformer adapter
    if callable(obj):
        from ..containers.wrappers import lambda_action
        return lambda_action(obj)

    # 4. Anything else is not a valid Action target
    return raise_invalid_action_target(obj)
```

[▲ Back to top](#-table-of-contents)

---

## A note on the `__not_rule__` hook

`Action.__not_rule__ = True` is the mirror image of the mechanism documented in
`simplibs-rules`' own `Rule` class: it signals to `Rule.__and__`/`__or__` that an
`Action` must never be silently absorbed as a plain boolean predicate. Without it,
`is_integer & my_action` would try to treat `my_action` as a callable returning
`bool` (via `Rule`'s own composition path) instead of handing control back to
`Action.__rand__`, which is what actually produces a working pipeline step. See
`Rule`'s own design notes (in `simplibs-rules`) for the full rationale — this class
only needs to carry the marker, not re-explain it.

## A note on lazy container imports

Every operator method (`then`, `__and__`, `__or__`, `resolve_action`) imports the
concrete container it needs (`SequenceCompose`, `ParallelCompose`, `fallback`,
`guard`, `lambda_action`) *inside* the method body, not at module level.
`containers/` imports `Action` from `base_class` already — a module-level import here
would create a circular import. Deferring the import to the moment an operator is
actually used breaks that cycle, at the negligible one-time-per-call cost of a
repeated `import` statement.

## A note on flattening, and why it doesn't live here

Chained operators evaluate left-to-right, so `a >> b >> c` builds as `(a >> b) >> c`,
which would naively nest as `SequenceCompose(SequenceCompose(a, b), c)`. Rather than
handling this in `Action` itself, `SequenceCompose`/`ParallelCompose` each flatten
same-type nested instances inside their own `compose` classmethod — so `Action` stays
a pure, one-line delegation regardless of how many operators are chained. See
[`README_CONTAINERS.md`](README_CONTAINERS.md) for the flattening mechanics.

---

[⬅️ Back to main README](../README.md#-the-action-class)
