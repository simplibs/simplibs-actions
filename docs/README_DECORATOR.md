# 🎀 `to_action` — Decorator Interface for `create_action`

`to_action` is the decorator-shaped entry point for
[`create_action`](README_CREATOR.md#create_action) — every function-based example
throughout this library's docs (`guard`, `sequence`, `fallback`, ...) is written with
`@to_action` rather than a manual `create_action(...)` call. It carries exactly
`create_action`'s own configuration, in the same two-forms pattern
`simplibs-validate`'s own decorators use: bare (`@to_action`) for the common case of
"just wrap it, defaults are fine", or parametrized (`@to_action(...)`) whenever any of
`create_action`'s keyword options are needed.

```python
@to_action
def guard(data: Any, rule: Any) -> Any:
    ...

@to_action(class_name="Combine", main_param="note")
def combine(data: dict, note: str = "") -> str:
    ...
```

---

## 🧭 Table of Contents

* [`to_action`](#to_action)

[⬅️ Back to main README](../README.md#-to_action)

---

### `to_action`

**Parameters** — identical to [`create_action`](README_CREATOR.md#create_action)'s own
keyword arguments, applied to whatever function it decorates:

* `main_param` (*str | None*): Name of the parameter to use as the main pipeline
  input. Defaults to `None` — "the first parameter".
* `use_validations` (*bool*): Defaults to `True`.
* `use_logging` (*bool*): Defaults to `True`.
* `class_name` (*str | None*): Defaults to `None` — derived from the function's own
  name.

**Returns:**

* `type[Action]`, applied bare: the decorated function is replaced in-place by the
  `Action` subclass `create_action` builds from it.
* A decorator function, applied parametrized: calling `@to_action(...)` first returns
  a decorator carrying the given options, which is then applied to the function
  immediately below it — same two-call shape as `@validate_call`/`@validate_call(...)`
  in `simplibs-validate`.

**Example usage:**

```python
# Bare form — defaults are fine
@to_action
def double(data: int) -> int:
    return data * 2

double()(21)   # -> 42

# Parametrized form — explicit main_param and class_name
@to_action(main_param="note", class_name="Combine")
def combine(data: dict, note: str = "") -> str:
    return f"{note}:{data}"

Combine(data={"x": 1})("tag")   # -> "tag:{'x': 1}"
```

**Under the hood:**

```python
def to_action(
    func: Callable[..., Any] | None = None,
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
) -> Any:
    # 1. Define the inner decorator that performs the actual conversion
    def decorator(fn: Callable[..., Any]) -> Callable[..., Action]:
        return create_action(
            fn,
            main_param=main_param,
            use_validations=use_validations,
            use_logging=use_logging,
            class_name=class_name,
        )

    # 2. Bare-decorator form (@to_action, no parentheses) — apply directly
    if func is not None:
        return decorator(func)

    # 3. Parametrized form (@to_action(...)) — return the decorator itself
    return decorator
```

`to_action` carries no logic of its own beyond that `func is None` branch —
`decorator()` forwards every argument straight through to
[`create_action`](README_CREATOR.md#create_action) unchanged.

**A note on the two `@overload` pairs:** `create_action` already carries its own
`Concatenate`/`ParamSpec` overload, giving callers an accurate `Callable[P, Action]`
hover instead of the generic `type[Action]`. `to_action` needs its own pair rather
than reusing that one, because it's *called* differently: bare (`@to_action` — a
single, strictly positional function argument, hence the `/` in the overload) or
parametrized (`@to_action(...)` — no function yet, returning a decorator). One
overload can't describe both shapes:

```python
@overload
def to_action(func: Callable[Concatenate[DataT, P], R], /) -> Callable[P, Action]: ...

@overload
def to_action(
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
) -> Callable[[Callable[Concatenate[DataT, P], R]], Callable[P, Action]]: ...
```

The first overload matches the bare form and resolves directly to
`Callable[P, Action]`; the second matches the parametrized form and resolves to a
decorator function that itself produces `Callable[P, Action]` once applied. Both
ultimately deliver the exact same hover quality `create_action` provides on its own —
this file's job is purely to preserve that through either calling convention. The real
(non-overloaded) implementation has to accept the union of both shapes at runtime,
hence `func: ... | None = None` and the `if func is not None:` branch deciding which
behavior actually runs.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-to_action)
