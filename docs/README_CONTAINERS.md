# 📦 `containers` — Composable Action Containers

The `containers` package holds every built-in `Action` — the ready-made pipeline steps
that ship with this library, from single-purpose primitives (`identity`, `constant`) to
the composed containers `Action`'s own operators (`>>`, `&`, `|`) build under the hood
(`SequenceCompose`, `ParallelCompose`, `fallback`). Every container here is built the
same two ways described in `Action`'s own documentation: generated from a plain function
via `@to_action` (nearly all of them), or hand-written where generation alone can't
express the needed behavior (`SequenceCompose`, `ParallelCompose`).

## A note on the `as_action` / `as_predicate` helpers

Every container that accepts "an action, a rule, or a callable" as one of its own
parameters routes that value through one of two small shared helpers rather than
duck-typing it inline:

* **`as_action(obj)`** — `Action.resolve_action` under another name (`as_action =
  Action.resolve_action`), used by every container that needs to *run* the value it
  was given (`sequence`'s steps, `parallel`'s branches, `fallback`'s `action`/
  `on_error`, `for_each`'s `action`, `branch`'s `then_branch`/`else_branch`, `retry`'s
  `action`, `tap`'s `action`).
* **`as_predicate(condition)`** — normalizes a `Rule` instance or a plain callable
  into a single bool-returning call (`condition.is_valid` for a `Rule`, `condition`
  itself for a plain callable), used by containers that need to *evaluate* a
  condition rather than run it (`guard`'s `rule`, `branch`'s `condition`). Raises a
  structured `ParamError` (`raise_invalid_predicate`) for anything that is neither.

Every container documented below relies on one or both of these internally; they are
not part of this package's own public surface.

---

## 🧭 Table of Contents

* **Flow control** — [`guard`](#guard) · [`branch`](#branch) · [`for_each`](#for_each)
* **Operators** — [`sequence`](#sequence) · [`parallel`](#parallel) ·
  [`fallback`](#fallback) · [`SequenceCompose`](#sequencecompose) ·
  [`ParallelCompose`](#parallelcompose)
* **Primitives** — [`identity`](#identity) · [`constant`](#constant)
* **Wrappers** — [`lambda_action`](#lambda_action) · [`tap`](#tap) ·
  [`retry`](#retry) · [`log_action`](#log_action)
* [Aliases](#aliases)

[⬅️ Back to main README](../README.md#-built-in-containers)

---

## Flow control

### `guard`

Hard gate: passes `data` through unchanged if `rule` holds; raises otherwise. The one
container `Action.resolve_action` itself constructs whenever a plain `Rule` is used
anywhere an `Action` is expected — this is how `is_integer >> next_step` becomes a
real pipeline step.

**Init Params:**

* `rule` (*Rule | Callable[[Any], bool]*): The condition `data` must satisfy.

**Main Param:**

* `data` (*Any*): The value to check.

**Output:**

* `Any`: `data`, unchanged, if `rule` holds.

**Raises:**

* Whatever `rule.build_exception(data, ...)` constructs, if `rule` is a `Rule`
  instance (a proper diagnostic card, matching what `rule.validate(data)` would raise
  directly).
* A structured `ParamError` (`GUARD_CONDITION_FAILED`), if `rule` is a plain callable
  with no `build_exception` of its own to delegate to.

**Example usage:**

```python
guard(rule=is_positive)(5)     # -> 5
guard(rule=is_positive)(-5)    # -> raises
```

**Under the hood:**

```python
@to_action
def guard(data: Any, rule: Any) -> Any:
    predicate = as_predicate(rule)

    if predicate(data):
        return data

    if hasattr(rule, "build_exception"):
        raise rule.build_exception(data, context="Guard evaluation failed")

    return raise_guard_failed(data)
```

[▲ Back to top](#-table-of-contents)

---

### `branch`

Soft conditional branching: runs `then_branch` if `condition` holds, otherwise
`else_branch` (or passes `data` through unchanged if no `else_branch` is given).
Unlike `guard`, a failing condition here is never an error — it's simply the other
path.

**Init Params:**

* `condition` (*Rule | Callable[[Any], bool]*): The predicate to evaluate.
* `then_branch` (*Action | Rule | Callable[[Any], Any]*): Runs when `condition` holds.
* `else_branch` (*Action | Rule | Callable[[Any], Any] | None*): Runs when it doesn't.
  If omitted, `data` passes through unchanged instead.

**Main Param:**

* `data` (*Any*): The value to branch on.

**Output:**

* `Any`: `then_branch(data)`, `else_branch(data)`, or `data` unchanged.

**Example usage:**

```python
branch(condition=is_positive, then_branch=double, else_branch=negate)(5)    # -> double(5)
branch(condition=is_positive, then_branch=double)(-5)                       # -> -5, unchanged
```

**Under the hood:**

```python
@to_action
def branch(data: Any, condition: Any, then_branch: Any, else_branch: Any | None = None) -> Any:
    predicate = as_predicate(condition)
    then_action = as_action(then_branch)

    if predicate(data):
        return then_action(data)

    if else_branch is not None:
        else_action = as_action(else_branch)
        return else_action(data)

    return data
```

[▲ Back to top](#-table-of-contents)

---

### `for_each`

Applies `action` to every item of an iterable `data`, collecting the results into a
list.

**Init Params:**

* `action` (*Action | Rule | Callable[[Any], Any]*): Runs once per item.

**Main Param:**

* `data` (*Iterable[Any]*): The collection to iterate.

**Output:**

* `list[Any]`: One result per item, in iteration order.

**Raises:**

* A structured `ParamError` (`NOT_ITERABLE_DATA`) if `data` doesn't support iteration
  at all — reported as a diagnostic, not a bare `TypeError` from a failed `iter()`
  call.

**Example usage:**

```python
for_each(action=double)([1, 2, 3])   # -> [2, 4, 6]
```

**Under the hood:**

```python
@to_action
def for_each(data: Iterable[Any], action: Any) -> list[Any]:
    try:
        items = iter(data)
    except TypeError:
        raise_not_iterable(data)

    inner = as_action(action)
    return [inner(item) for item in items]
```

[▲ Back to top](#-table-of-contents)

---

## Operators

### `sequence`

Chains any number of steps left to right, threading the output of each into the next.
Plain `sequence` works correctly on its own but nests when chained directly
(`sequence(steps=(a,)) >> b` would build a `sequence` holding another `sequence`) —
that's exactly what [`SequenceCompose`](#sequencecompose) exists to avoid. Construct
`sequence` directly only when you deliberately want a fixed, non-flattening group of
steps as one unit; use `>>` for everything else.

**Init Params:**

* `steps` (*tuple_not_empty[Action | Rule | Callable[[Any], Any]]*): The steps to run
  in order. Must be non-empty.

**Main Param:**

* `data` (*Any*): The initial input fed to the first step.

**Output:**

* `Any`: The final step's return value.

**Example usage:**

```python
sequence(steps=(strip, upper))("  hello  ")   # -> "HELLO"
```

**Under the hood:**

```python
@to_action
def sequence(data: Any, steps: tuple_not_empty) -> Any:
    result = data
    for step in steps:
        result = as_action(step)(result)
    return result
```

[▲ Back to top](#-table-of-contents)

---

### `parallel`

Runs N actions over the **same** `data`, returning one result per branch as a tuple,
in order. Same relationship to [`ParallelCompose`](#parallelcompose) as `sequence` has
to `SequenceCompose` — plain `parallel` nests when chained directly, changing the
*shape* of the result, not just its introspectability.

**Init Params:**

* `branches` (*tuple_not_empty[Action | Rule | Callable[[Any], Any]]*): The actions to
  run. Must be non-empty.

**Main Param:**

* `data` (*Any*): The value passed unchanged to every branch.

**Output:**

* `tuple[Any, ...]`: One result per branch, in the same order as `branches`.

**Example usage:**

```python
parallel(branches=(upper, lower))("Hi")   # -> ("HI", "hi")
```

**Under the hood:**

```python
@to_action
def parallel(data: Any, branches: tuple_not_empty) -> tuple[Any, ...]:
    return tuple(as_action(branch)(data) for branch in branches)
```

[▲ Back to top](#-table-of-contents)

---

### `fallback`

Tries `action` over `data`; on failure either runs `on_error` or returns the original
`data` unchanged. Merges what used to be two separate containers (`Try`/`Fallback`)
into one: `on_error=None` behaves like the old `Try` (returns `data` on failure);
`on_error=<action>` behaves like the old `Fallback`, now with an optional `exceptions`
filter shared by both.

**Init Params:**

* `action` (*Action | Rule | Callable[[Any], Any]*): The primary action to attempt.
* `on_error` (*Action | Rule | Callable[[Any], Any] | None*): Runs instead of `action`
  if it raises. If omitted, `data` is returned unchanged on failure.
* `exceptions` (*type[BaseException] | tuple[type[BaseException], ...]*): Which
  exception types are caught. Defaults to `Exception` — deliberately broad for
  backward-compatible `Try` behavior, but narrow this whenever possible
  (`exceptions=ValueError`, ...) so real bugs inside `action` aren't silently
  swallowed as "expected failure".

**Main Param:**

* `data` (*Any*): The value passed to `action` (and to `on_error`, if used).

**Output:**

* `Any`: `action`'s result on success; `on_error`'s result, or `data` unchanged, on
  failure.

**Example usage:**

```python
fallback(action=risky_parse, on_error=default_value)(raw_input)
```

**Under the hood:**

```python
@to_action
def fallback(
    data: Any,
    action: Any,
    on_error: Any | None = None,
    exceptions: type[BaseException] | tuple[type[BaseException], ...] = Exception,
) -> Any:
    try:
        return as_action(action)(data)
    except exceptions:
        if on_error is not None:
            return as_action(on_error)(data)
        return data
```

**No flattening needed for `|`** — unlike `parallel`, nesting `fallback` calls behaves
identically whether grouped as `(a | b) | c` or `a | (b | c)`; sequential try/except is
naturally associative regardless of nesting depth. No compose-class counterpart exists
for this reason.

[▲ Back to top](#-table-of-contents)

---

### `SequenceCompose`

Self-flattening variant of [`sequence`](#sequence), used internally by `Action.then`/
`>>`. Composing two actions via `>>` should never nest a sequence inside another
sequence — `compose` unwraps either side that's already a `SequenceCompose` instead of
wrapping it as a single step. Constructed the same way as `sequence` itself
(`SequenceCompose(steps=(...))`); the only addition is `compose`.

**Parameters** *(of `compose`, a classmethod)*:

* `first` (*Action*): The left-hand operand.
* `second` (*Action*): The right-hand operand.

**Returns:**

* `SequenceCompose`: One flat instance — `a >> b >> c` produces a single
  `SequenceCompose` with three steps, never a `SequenceCompose` nested inside another.

**Example usage:**

```python
pipeline = strip_action >> upper_action >> save_action
isinstance(pipeline, SequenceCompose)   # -> True
len(pipeline.steps)                     # -> 3, never nested
```

**Under the hood:**

```python
class SequenceCompose(sequence):
    __slots__ = ()

    @classmethod
    def compose(cls, first: Action, second: Action) -> "SequenceCompose":
        first_steps = first.steps if isinstance(first, cls) else (first,)
        second_steps = second.steps if isinstance(second, cls) else (second,)
        return cls(steps=first_steps + second_steps)
```

> `Action.then` calls `SequenceCompose.compose(self, resolve_action(next_step))`
> regardless of whether `self` is already a `SequenceCompose` — flattening is
> symmetric on both sides with no operator override needed on this class itself.

[▲ Back to top](#-table-of-contents)

---

### `ParallelCompose`

Self-flattening variant of [`parallel`](#parallel), used internally by
`Action.__and__`/`&`. Without flattening, `a & b & c` (left-associative `&`) would
build `parallel(parallel(a, b), c)`, whose result is the nested tuple `((r_a, r_b),
r_c)` instead of the flat `(r_a, r_b, r_c)` — a genuinely different, wrong output
*shape*, not just a readability concern. This is the container where flattening is a
necessity.

**Parameters** *(of `compose`, a classmethod)*:

* `first` (*Action*): The left-hand operand.
* `second` (*Action*): The right-hand operand.

**Returns:**

* `ParallelCompose`: One flat instance whose call result is always a single flat
  tuple, regardless of how the `&` chain was grouped.

**Example usage:**

```python
pipeline = double & square & negate
isinstance(pipeline, ParallelCompose)   # -> True
pipeline(3)                             # -> (6, 9, -3), flat
```

**Under the hood:**

```python
class ParallelCompose(parallel):
    __slots__ = ()

    @classmethod
    def compose(cls, first: Action, second: Action) -> "ParallelCompose":
        first_branches = first.branches if isinstance(first, cls) else (first,)
        second_branches = second.branches if isinstance(second, cls) else (second,)
        return cls(branches=first_branches + second_branches)
```

[▲ Back to top](#-table-of-contents)

---

## Primitives

### `identity`

No-op — returns `data` unchanged. The building block underneath `guard`/`branch`'s
"pass data through" fallback paths, and useful on its own wherever a pipeline slot
needs to exist but do nothing.

**Main Param:**

* `data` (*Any*): Anything.

**Output:**

* `Any`: `data`, unchanged.

**Under the hood:**

```python
@to_action
def identity(data: Any) -> Any:
    return data
```

[▲ Back to top](#-table-of-contents)

---

### `constant`

Ignores `data`, always returns `value`.

**Init Params:**

* `value` (*Any*): The value to return, regardless of input.

**Main Param:**

* `data` (*Any*): Ignored.

**Output:**

* `Any`: `value`.

**Under the hood:**

```python
@to_action
def constant(data: Any, value: Any) -> Any:
    return value
```

[▲ Back to top](#-table-of-contents)

---

## Wrappers

### `lambda_action`

Adapter for a raw callable that didn't originate from `to_action` — the container
`Action.resolve_action` itself constructs for any plain callable used anywhere an
`Action` is expected.

**Init Params:**

* `func` (*Callable[[Any], Any]*): The callable to run.

**Main Param:**

* `data` (*Any*): Passed straight into `func`.

**Output:**

* `Any`: `func(data)`.

**Under the hood:**

```python
@to_action
def lambda_action(data: Any, func: Callable[[Any], Any]) -> Any:
    return func(data)
```

[▲ Back to top](#-table-of-contents)

---

### `tap`

Runs `action` as a side effect, but always returns the **original** `data` unchanged
— regardless of what `action` returns. For side effects (logging, metrics, writes)
that shouldn't alter the pipeline's data flow.

**Init Params:**

* `action` (*Action | Rule | Callable[[Any], Any]*): Runs for its side effect only;
  its return value is discarded.

**Main Param:**

* `data` (*Any*): Passed to `action`, and returned unchanged afterward.

**Output:**

* `Any`: `data`, unchanged.

**Under the hood:**

```python
@to_action
def tap(data: Any, action: Any) -> Any:
    as_action(action)(data)
    return data
```

[▲ Back to top](#-table-of-contents)

---

### `retry`

Retries `action` up to `attempts` times total on failure, re-raising the last caught
exception if every attempt is exhausted.

**Init Params:**

* `action` (*Action | Rule | Callable[[Any], Any]*): The action to attempt.
* `attempts` (*int*): Total attempts, including the first. Defaults to `3`. Must be
  `>= 1`.
* `exceptions` (*type[BaseException] | tuple[type[BaseException], ...]*): Which
  exception types trigger a retry. Defaults to `Exception`.

**Main Param:**

* `data` (*Any*): Passed to `action` on every attempt.

**Output:**

* `Any`: `action(data)`'s result, from whichever attempt first succeeds.

**Raises:**

* A structured `ParamError` (`INVALID_RETRY_ATTEMPTS`) if `attempts < 1`.
* The last caught exception, unchanged, if every attempt fails.

**Example usage:**

```python
retry(action=flaky_call, attempts=3)(payload)
```

**Under the hood:**

```python
@to_action
def retry(
    data: Any,
    action: Any,
    attempts: int = 3,
    exceptions: type[BaseException] | tuple[type[BaseException], ...] = Exception,
) -> Any:
    if attempts < 1:
        raise_invalid_attempts(attempts)

    last_exception: Exception | None = None
    inner = as_action(action)

    for _ in range(attempts):
        try:
            return inner(data)
        except exceptions as exc:
            last_exception = exc

    raise last_exception
```

[▲ Back to top](#-table-of-contents)

---

### `log_action`

Logs the data flowing through one pipeline point, then passes it through unchanged —
`tap`'s specialization for the single most common side effect.

**Init Params:**

* `logger` (*Callable[[Any], None]*): The logging callable (e.g. `print`, a `Logger`
  method).
* `message` (*str | None*): Optional prefix. If given, logs `f"{message}: {data!r}"`;
  otherwise logs `data` directly.

**Main Param:**

* `data` (*Any*): Logged, then returned unchanged.

**Output:**

* `Any`: `data`, unchanged.

**Under the hood:**

```python
@to_action
def log_action(data: Any, logger: Callable[[Any], None], message: str | None = None) -> Any:
    if message:
        logger(f"{message}: {data!r}")
    else:
        logger(data)
    return data
```

[▲ Back to top](#-table-of-contents)

---

## Aliases

Every alias below is a pure identity assignment (`alias = canonical`) — not a copy, not
a wrapper, the exact same object in memory. See
[`README_TESTING_ASSERT_ACTION_ALIAS.md`](README_TESTING_ASSERT_ACTION_ALIAS.md) for
how these are tested.

| Alias | Canonical | Package |
|---|---|---|
| `guarded_action` | [`guard`](#guard) | `flow_control/aliases` |
| `conditional_action` | [`branch`](#branch) | `flow_control/aliases` |
| `apply_to_each` | [`for_each`](#for_each) | `flow_control/aliases` |
| `run_in_sequence` | [`sequence`](#sequence) | `operators/aliases` |
| `run_in_parallel` | [`parallel`](#parallel) | `operators/aliases` |
| `try_or_fallback` | [`fallback`](#fallback) | `operators/aliases` |
| `pass_through` | [`identity`](#identity) | `primitives/aliases` |
| `replace_with` | [`constant`](#constant) | `primitives/aliases` |
| `callable_action` | [`lambda_action`](#lambda_action) | `wrappers/aliases` |
| `run_side_effect` | [`tap`](#tap) | `wrappers/aliases` |
| `retry_on_failure` | [`retry`](#retry) | `wrappers/aliases` |
| `log_step` | [`log_action`](#log_action) | `wrappers/aliases` |

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-built-in-containers)
