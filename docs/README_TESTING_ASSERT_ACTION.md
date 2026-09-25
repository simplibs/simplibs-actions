# 🧪 `assert_action`

**Deterministic Execution-Contract Auditor for any `Action`**

`assert_action` is the single entry point for testing any `Action` instance — this
library's own containers (`guard`, `sequence`, `parallel`, `fallback`, ...) and,
equally, any action a downstream user builds via `@to_action`/`create_action` in their
own code. It mirrors the Facade pattern already established by `simplibs-rules`'
`assert_rule_contract` and `simplibs-exception`'s `assert_exception_function`: one
call, fed with data, exercises every deterministic corner of the contract — while
leaving the one thing no generic tool can infer (what a given input *should* produce)
to the caller.

## 💡 Table of Contents:
> * [⚙️ Architectural Principles](#-architectural-principles)
> * [🧭 Execution Flow](#-execution-flow)
> * [🔍 Quick Usage Examples](#-quick-usage-examples)
> * [🛠️ Configuration & Parameters](#-configuration--parameters)
> * [🔄 The Four Blades](#-the-four-blades)
>   * [`assert_action_output`](#assert_action_output)
>   * [`assert_action_raises`](#assert_action_raises)
>   * [`assert_action_io_types`](#assert_action_io_types)
>   * [`assert_action_construction`](#assert_action_construction)
> * [📖 Real-World Example](#-real-world-example)

[⬅️ Back to main README](../README.md#-testing-utilities)

---

## ⚙️ Architectural Principles

* **The Deterministic/Business-Logic Split:** Unlike a `Rule`, whose
  `is_valid`/`validate`/`build_exception` triad is entirely mechanical given
  valid/invalid values, an `Action` wraps arbitrary business logic — there is no
  generic way to know what output a given input *should* produce. So this tool splits
  cleanly: fully generic/mechanical checks (the object really is an `Action`; invalid
  inputs actually raise; `_input_type`/`_output_type` are declared when expected; a
  misconfigured constructor raises) run automatically; business-logic-specific checks
  (what each valid input should produce, which invalid input should trigger which
  exception) must be supplied by the caller.
* **Toolkit Reuse Over Reimplementation:** Because an `Action` instance is directly
  callable (`action(data)`), the negative-path check is a near-direct pass-through to
  `simplibs-exception`'s own `assert_function_raises` — no raise/type-check logic is
  duplicated here. Only the positive-path output check needed a purpose-built blade,
  since nothing else in this ecosystem checks a return value against an expectation.
* **Fail-Fast Type Guard:** `isinstance(action, Action)` is asserted immediately,
  before any check runs — a misuse of this helper itself produces one clear error, not
  a cascade of confusing subtest failures deep inside a loop.
* **Scope Boundary:** This orchestrator only checks what is fully deterministic given
  the supplied data. It does not assert anything about business-logic correctness
  beyond the exact valid/invalid value pairs supplied — that boundary is inherent, not
  a current limitation.

[▲ Back to Top](#-assert_action)

---

## 🧭 Execution Flow

1. **Fail-fast type guard** — `action` must be an `Action` instance.
2. **Output check** *(if `valid_values` given)* — delegated to
   [`assert_action_output`](#assert_action_output).
3. **Raises check** *(if `invalid_values` given)* — delegated to
   [`assert_action_raises`](#assert_action_raises).
4. **`deep_check` (default `True`)** additionally runs:
   * [`assert_action_io_types`](#assert_action_io_types) — always, once `deep_check`
     is on.
   * [`assert_action_construction`](#assert_action_construction) — only if both
     `action_class` and `invalid_init_params` are given.

[▲ Back to top](#-table-of-contents)

---

## 🔍 Quick Usage Examples

```python
# 1. Full contract sweep: valid + invalid execution, plus deep_check's default checks
assert_action(
    subtests,
    greet_action,
    valid_values=[{"name": "Ann"}],
    expected_outputs=["Hi, Ann!"],
    invalid_values=[{}],
    expected_exception_type=KeyError,
)

# 2. Opting into the constructor-guard sweep too
assert_action(
    subtests,
    greet_action,
    action_class=Greet,
    invalid_init_params=[((), {"prefix": 123})],
)

# 3. Basic contract only — skip _input_type/_output_type and construction checks
assert_action(subtests, identity_action, deep_check=False)
```

[▲ Back to Top](#-assert_action)

---

## 🛠️ Configuration & Parameters

### Mandatory Parameters

* **`subtests`** (`Any`): The native pytest subtests fixture manager instance.
* **`action`** (`Action`): The `Action` instance under test.

### Optional Parameters

* **`valid_values`** (`list[Any] | None`): Inputs expected to be accepted.
* **`expected_outputs`** (`list[Any] | None`): Outputs expected for each entry in
  `valid_values`, index-matched. **Required** whenever `valid_values` is given.
* **`invalid_values`** (`list[Any] | None`): Inputs expected to raise.
* **`expected_exception_type`** (`type[Exception] | Sequence[type[Exception] | None] | None`):
  Asserted against exceptions raised for `invalid_values`. Scalar (applied uniformly)
  or a `Sequence` index-matched to `invalid_values` (`None` entries accept any
  exception).
* **`expected_input_type` / `expected_output_type`** (`Any | UnsetType`): Asserted
  against the action class's declared `_input_type`/`_output_type`. Only checked when
  `deep_check` is `True`.
* **`action_class`** (`type[Action] | None`): The `Action` subclass itself (as opposed
  to `action`, an instance of it). Only needed together with `invalid_init_params`.
* **`invalid_init_params`** (`list[tuple[tuple[Any, ...], dict[str, Any]]] | None`):
  `(args, kwargs)` pairs expected to raise on construction. Requires `action_class`,
  runs only when `deep_check` is `True`.
* **`construction_exception_type`** (`type[Exception] | Sequence[type[Exception] | None]`):
  Default `ValidationError` — see [`assert_action_construction`](#assert_action_construction)
  for why.
* **`verbose`** (`bool`): Default `True`. Registers individual checks as isolated
  pytest subtests.
* **`intro`** (`str`): Default `""`. Prefix for generated subtest names.
* **`deep_check`** (`bool`): Default `True`. Gates the `_input_type`/`_output_type`
  and constructor-guard checks described above.

```python
def assert_action(
    subtests: Any,
    action: Action,
    *,
    valid_values: list[Any] | None = None,
    expected_outputs: list[Any] | None = None,
    invalid_values: list[Any] | None = None,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] | None = None,
    expected_input_type: Any | UnsetType = UNSET,
    expected_output_type: Any | UnsetType = UNSET,
    action_class: type[Action] | None = None,
    invalid_init_params: list[tuple[tuple[Any, ...], dict[str, Any]]] | None = None,
    construction_exception_type: type[Exception] | Sequence[type[Exception] | None] = ValidationError,
    verbose: bool = True,
    intro: str = "",
    deep_check: bool = True,
) -> None: ...
```

[▲ Back to Top](#-assert_action)

---

## 🔄 The Four Blades

### `assert_action_output`

Verifies that calling the action on each valid value produces the matching expected
output — the one thing generic tooling cannot infer on its own. Not built on top of
`assert_function_valid_input` (which only checks "doesn't raise", with no concept of
an expected return value); this is a small, purpose-built blade instead.

```python
def assert_action_output(
    subtests: Any, action: Action,
    valid_values: list[Any], expected_outputs: list[Any],
    *, verbose: bool = True, intro: str = "",
) -> None: ...
```

Raises `ValueError` up front if `valid_values`/`expected_outputs` differ in length —
almost always a copy-paste mistake in the test itself, caught before it turns into a
confusing off-by-one `IndexError` mid-sweep.

[▲ Back to top](#-table-of-contents)

---

### `assert_action_raises`

Verifies that calling the action on each invalid value raises the expected
exception — a thin, near-direct pass-through to `simplibs-exception`'s own
`assert_function_raises`, since an `Action` instance is callable exactly like a plain
function.

```python
def assert_action_raises(
    subtests: Any, action: Action, invalid_values: list[Any],
    *,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] | None = None,
    verbose: bool = True, intro: str = "",
) -> None: ...
```

`expected_exception_type` accepts the same scalar-or-`Sequence` shape as
`assert_rule_build_exception`'s own `expected_exception_type` — useful for a container
like `guard`, which can fail either via the wrapped `Rule`'s own `ValidationError` or
via a generic `ParamError` depending on the input.

[▲ Back to top](#-table-of-contents)

---

### `assert_action_io_types`

Verifies that the action's class exposes `_input_type`/`_output_type` (only present
when `use_validations=True`), and optionally matches them against explicit
expectations.

```python
def assert_action_io_types(
    subtests: Any, action: Action,
    *,
    expected_input_type: Any | UnsetType = UNSET,
    expected_output_type: Any | UnsetType = UNSET,
    verbose: bool = True, intro: str = "",
) -> None: ...
```

Their *absence* (an action built with `use_validations=False`) is treated as a
failure, not silently skipped — invoking `assert_action`'s `deep_check` is itself the
caller's assertion that type introspection should be available for this action.

[▲ Back to top](#-table-of-contents)

---

### `assert_action_construction`

Verifies that the action class's synthesized `__init__` rejects invalid configuration
arguments — the `Action`-level counterpart to `simplibs-rules`' own
`assert_rule_param_error`.

```python
def assert_action_construction(
    subtests: Any, action_class: type[Action],
    invalid_init_params: list[tuple[tuple[Any, ...], dict[str, Any]]],
    *,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] = ValidationError,
    verbose: bool = True, intro: str = "",
) -> None: ...
```

**Why `ValidationError`, not `ParamError`, is the default:** a wrong-typed constructor
kwarg is caught by the synthesized `__init__`'s own `@validate_call` wrapping (when
`use_validations=True`) — exactly the same way a wrong-typed call argument is.
`ParamError` is reserved for `create_action`'s own dedicated misuse guards (e.g.
passing an already-instantiated `Action` into `create_action`), not for per-parameter
type checking on an otherwise normal construction. Overridable for the rare action
whose `__init__` does its own hand-written validation instead.

Opt-in (via `action_class` + `invalid_init_params`), same reasoning as
`assert_rule_param_error`: not every action has constructor parameters worth
misuse-testing.

[▲ Back to top](#-table-of-contents)

---

## 📖 Real-World Example

```python
"""Tests for the greet action."""
from my_pipelines.actions import Greet, greet_action

from simplibs.actions.testing import assert_action


def test_greet_contract(subtests):
    """Verify greet's full execution and construction contract."""
    assert_action(
        subtests,
        greet_action,
        valid_values=[{"name": "Ann"}],
        expected_outputs=["Hi, Ann!"],
        invalid_values=[{}],
        expected_exception_type=KeyError,
        action_class=Greet,
        invalid_init_params=[((), {"prefix": 123})],
        verbose=False,
    )
```

One call replaces four separate hand-written checks (output correctness, raise
behavior, type declaration, constructor guard) — and the same call, repeated for every
`Action` this library or a downstream user ships, is what keeps the entire ecosystem's
actions provably conforming as they evolve.

[▲ Back to Top](#-assert_action)

---

[⬅️ Back to main README](../README.md#-testing-utilities)
