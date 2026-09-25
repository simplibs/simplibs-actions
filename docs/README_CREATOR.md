# 🏗️ `creator` — Dynamically Building Action Classes from Functions

`create_action` is the engine underneath `@to_action` (see
[`README_DECOTATOR.md`](README_DECOTATOR.md)) and underneath every built-in container
in this library — `guard`, `sequence`, `fallback`, and nearly everything else in
[`README_CONTAINERS.md`](README_CONTAINERS.md) is a plain function turned into an
`Action` subclass by this exact function. It is deliberately thin: it orchestrates,
it does not implement. Each real piece of work lives in its own helper, documented
below in the order `create_action` actually calls them.

```python
def create_action(
    func: Callable[..., Any],
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
) -> Any:
    ...
```

---

## 🧭 Table of Contents

* [`create_action`](#create_action) — the orchestrator
* **Resolvers** — [`resolve_param`](#resolve_param) ·
  [`resolve_class_name`](#resolve_class_name) ·
  [`unwrap_log_this_and_validate_call`](#unwrap_log_this_and_validate_call)
* **Creators** — [`create_init_and_slots`](#create_init_and_slots) ·
  [`create_call`](#create_call) · [`create_act`](#create_act)
* **Creator helpers** — [`build_init_docstring`](#build_init_docstring) ·
  [`build_call_docstring`](#build_call_docstring) ·
  [`_describe_annotation`](#_describe_annotation)
* **Validations** — [`validate_param_kinds`](#validate_param_kinds) ·
  [`validate_params_annotations`](#validate_params_annotations) ·
  [`validate_return_annotations`](#validate_return_annotations) ·
  [`_verify_type_is_validatable`](#_verify_type_is_validatable)
* **Diagnostic raisers** — [`raise_action_instance_error`](#raise_action_instance_error) ·
  [`raise_no_parameters`](#raise_no_parameters) ·
  [`raise_main_param_not_found`](#raise_main_param_not_found)
* [`EMPTY`](#empty)

[⬅️ Back to main README](../README.md#-create_action)

---

### `create_action`

The public orchestrator. Given an ordinary function, builds and returns a new `Action`
subclass whose instances are constructed with every parameter of `func` except the
main one (`MyAction(other_param=...)`), and called with the main parameter alone
(`instance(main_value)`).

**Parameters:**

* `func` (*Callable[..., Any]*): The source function to wrap. If it's already an
  `Action` subclass, it's returned unchanged (idempotent, like `Path(Path(x))`); if
  it's an `Action` *instance*, `raise_action_instance_error` is raised instead — its
  configuration is already bound, so silently misreading it as fresh constructor
  arguments would be wrong. If `func` already carries `@validate_call`/`@log_this`
  layers, they're peeled off first (see `unwrap_log_this_and_validate_call`).
* `main_param` (*str | None*): Name of the parameter to use as the main pipeline
  input. `None` (the default) means "the first parameter".
* `use_validations` (*bool*): If `True` (default), requires `func` to be fully
  annotated and wraps `act`/`__init__`/`__call__` with `validate_call`; the resulting
  class also carries `_input_type`/`_output_type` introspection attributes. If
  `False`, no annotation is required and no validation is applied — a fast,
  low-friction path for prototypes.
* `use_logging` (*bool*): If `True` (default), wraps `act` with `log_this` on top of
  `validate_call` (entry/exit/timing/exception logging).
* `class_name` (*str | None*): Explicit name for the generated class. Defaults to
  `func.__name__` converted from `snake_case` to `PascalCase`. Required for callables
  with no usable `__name__` (lambdas, `functools.partial`).

**Returns:**

* `type[Action]`: A new `Action` subclass.

**Example usage:**

```python
def greet(data: dict, prefix: str = "Hi") -> str:
    return f"{prefix}, {data['name']}!"

Greet = create_action(greet)
Greet(prefix="Hello")({"name": "Ann"})   # -> "Hello, Ann!"
```

**Under the hood** *(the orchestration steps, each delegated to its own helper below)*:

```python
def create_action(func, *, main_param=None, use_validations=True, use_logging=True, class_name=None):
    # 1. Pass an already-built Action class straight through
    if isinstance(func, type) and issubclass(func, Action):
        return func

    # 2. Reject an Action instance with a clear, dedicated diagnostic
    if isinstance(func, Action):
        raise_action_instance_error(func)

    # 3. Peel off any pre-existing @validate_call/@log_this layers
    _func = unwrap_log_this_and_validate_call(func)

    # 4. Retrieve the signature and its parameters
    _signature = inspect.signature(_func)
    _params = list(_signature.parameters.values())

    # 5. Reject unsupported parameter kinds
    validate_param_kinds(_params, _func)

    # 6. Prepare the data
    _class_name = resolve_class_name(_func, class_name)
    _main_param, _other_params = resolve_param(_params, main_param, _func)
    _return_annotation = _signature.return_annotation

    # 7. Validate the received annotations, if requested
    if use_validations:
        validate_params_annotations(_params, _func)
        validate_return_annotations(_return_annotation, _func)

    # 8. Build the pieces of the class dict
    init, slots = create_init_and_slots(_other_params)
    call = create_call(_main_param, _other_params, _return_annotation)
    act = create_act(_main_param, _other_params, _return_annotation, _func)

    # 9-11. Apply validation, logging, and turn act into a staticmethod
    if use_validations:
        init, call, act = validate_call(init), validate_call(call), validate_call(act)
    if use_logging:
        act = log_this(act)
    act = staticmethod(act)

    # 12-14. Assemble and build the class
    attrs = {"__doc__": _func.__doc__, "__slots__": slots, "__init__": init,
             "__call__": call, "act": act, "_main_name": _main_param.name}
    if use_validations:
        attrs["_input_type"] = _main_param.annotation
        attrs["_output_type"] = _return_annotation
    return type(_class_name, (Action,), attrs)
```

[▲ Back to top](#-table-of-contents)

---

## Resolvers

### `resolve_param`

Splits `func`'s parameters into the one main pipeline input and everything else —
the single place that decision gets made, so `create_action` itself never has to
reason about "which parameter is main" more than once.

**Parameters:**

* `params` (*list[inspect.Parameter]*): `func`'s full parameter list.
* `main_name` (*str | None*): The name to treat as main; `None` means "the first
  parameter" (the fast path — a plain slice, no loop needed).
* `func` (*Callable*): Used only for diagnostic messages.

**Returns:**

* `tuple[inspect.Parameter, list[inspect.Parameter]]`: `(main_param, other_params)`.

**Raises:**

* `raise_no_parameters` if `params` is empty.
* `raise_main_param_not_found` if `main_name` was given but matches nothing.

**Under the hood:**

```python
def resolve_param(params, main_name, func):
    if not params:
        raise_no_parameters(func)

    if main_name is None:
        return params[0], params[1:]

    main_param, other_params = None, []
    for param in params:
        if param.name == main_name:
            main_param = param
        else:
            other_params.append(param)

    if main_param is None:
        raise_main_param_not_found(main_name, func)

    return main_param, other_params
```

[▲ Back to top](#-table-of-contents)

---

### `resolve_class_name`

Determines the generated class's name — `func.__name__` converted `snake_case` ->
`PascalCase`, unless `class_name` is given explicitly.

**Parameters:**

* `func` (*Callable[..., Any]*): The source function.
* `class_name` (*str | None*): An explicit override.

**Returns:**

* `str`: The resolved class name.

**Why `class_name` exists at all:** it breaks down for anything without a meaningful
`__name__` — a lambda's `__name__` is the literal string `"<lambda>"` (not even valid
syntax as a class name), and `functools.partial` has no `__name__` at all.
`class_name` isn't a convenience for those cases — it's the only way `create_action`
can be used with them.

**Under the hood:**

```python
def resolve_class_name(func, class_name):
    if class_name is not None:
        return class_name
    return "".join(part.capitalize() for part in func.__name__.split("_"))
```

[▲ Back to top](#-table-of-contents)

---

### `unwrap_log_this_and_validate_call`

Peels off any pre-existing `@validate_call`/`@log_this` layers, in any order or depth,
until neither decorator's marker remains — preventing double validation/logging when
`create_action` wraps an already-decorated function.

**Parameters:**

* `func` (*Callable[..., Any]*): The callable to unwrap.

**Returns:**

* `Callable[..., Any]`: The underlying callable, free of both decorators.

**Why a fixed-point loop, not one pass of each unwrap function:** a function decorated
as `@validate_call` above `@log_this` above another `@validate_call` needs peeling in
alternation — one pass of each, in a fixed order, would only strip layers of one kind
stacked contiguously at the very top.

**Under the hood:**

```python
def unwrap_log_this_and_validate_call(func):
    while True:
        unwrapped = unwrap_log_this(unwrap_validate_call(func))
        if unwrapped is func:
            return func
        func = unwrapped
```

[▲ Back to top](#-table-of-contents)

---

## Creators

Each function below builds one real member of the generated class via `exec`-based
codegen — the same technique `dataclasses` uses to synthesize `__init__`. All three
generate parameters as **keyword-only** (after a bare `*`): `act`/`__init__` are never
called positionally anywhere in this architecture, and keyword-only avoids a
`SyntaxError` whenever a parameter with a default ends up ahead of one without (e.g.
when `main_param` is picked from the middle of `func`'s own signature).

### `create_init_and_slots`

Synthesizes `__init__` with a real signature matching the "other" parameters, plus the
matching `__slots__` tuple.

**Parameters:**

* `params` (*list[inspect.Parameter]*): The non-main parameters — everything the
  generated constructor should accept.

**Returns:**

* `tuple[Callable, tuple[str, ...]]`: `(init, slots)`.

**Under the hood:**

```python
def create_init_and_slots(params):
    namespace = {}
    params_entry = ["self"]
    if params:
        params_entry.append("*")
    slot_names, assignments = [], []

    for index, param in enumerate(params):
        entry = param.name
        if param.annotation is not EMPTY:
            namespace[f"_annotation_{index}"] = param.annotation
            entry += f": _annotation_{index}"
        if param.default is not EMPTY:
            namespace[f"_default_{index}"] = param.default
            entry += f" = _default_{index}"
        params_entry.append(entry)
        slot_names.append(param.name)
        assignments.append(f"    self.{param.name} = {param.name}")

    source = f"def __init__({', '.join(params_entry)}):\n" + ("\n".join(assignments) or "    pass")
    exec(source, namespace)
    generated_init = namespace["__init__"]
    generated_init.__doc__ = build_init_docstring(params)
    return generated_init, tuple(slot_names)
```

> The `("\n".join(assignments) or "    pass")` fallback guarantees the generated body
> is always syntactically valid — without it, a parameterless action (e.g.
> `identity`) would synthesize a body with nothing indented underneath, an
> `IndentationError` at `exec` time.

[▲ Back to top](#-table-of-contents)

---

### `create_call`

Synthesizes `__call__` — the `Action`'s single pipeline entry point. Only ever takes
`main_param`; the other parameters were already bound onto `self` at construction and
are read back off it.

**Parameters:**

* `main_param` (*inspect.Parameter*): `__call__`'s only real argument (besides
  `self`).
* `other_params` (*list[inspect.Parameter]*): Read off `self`, forwarded into
  `self.act(...)`.
* `return_annotation` (*Any*): Used to annotate `__call__`'s own return type and
  docstring.

**Returns:**

* `Callable[..., Any]`: The generated `__call__`.

**Under the hood:**

```python
def create_call(main_param, other_params, return_annotation):
    namespace = {}
    main_name = main_param.name
    call_param = main_name
    act_arguments = [f"{main_name}={main_name}"]

    if main_param.annotation is not EMPTY:
        namespace["_main_annotation"] = main_param.annotation
        call_param += ": _main_annotation"

    for param in other_params:
        act_arguments.append(f"{param.name}=self.{param.name}")
    act_arguments.append("_validate_call=_validate_call")

    call_return = ""
    if return_annotation is not EMPTY:
        namespace["_return_annotation"] = return_annotation
        call_return = " -> _return_annotation"

    source = (
        f"def __call__(self, {call_param}, *, _validate_call: bool = True){call_return}:\n"
        f"    return self.act({', '.join(act_arguments)})"
    )
    exec(source, namespace)
    generated_call = namespace["__call__"]
    generated_call.__doc__ = build_call_docstring(main_param, return_annotation)
    return generated_call
```

> `create_action` decorates the class this way so it satisfies `Action`'s abstract
> `__call__` directly — no `execute`/`act`-at-the-base-level indirection needed.

[▲ Back to top](#-table-of-contents)

---

### `create_act`

Synthesizes `act` — a thin wrapper carrying `func`'s **own real signature**, plus one
added keyword-only `_validate_call: bool = True` parameter that's accepted and
silently dropped, never forwarded into `func` itself. `func` never sees
`_validate_call` — it's the caller's own business logic, understood with no knowledge
of the validation bypass mechanism.

**Parameters:**

* `main_param` (*inspect.Parameter*): `func`'s main parameter.
* `other_params` (*list[inspect.Parameter]*): `func`'s remaining parameters.
* `return_annotation` (*Any*): `func`'s return annotation.
* `func` (*Callable[..., Any]*): The source function `act` ultimately calls.

**Returns:**

* `Callable[..., Any]`: A real function with `func`'s exact parameter names,
  annotations, docstring, `__name__`, and defaults, plus the one added bypass
  parameter.

**Under the hood:**

```python
def create_act(main_param, other_params, return_annotation, func):
    namespace = {"__func__": func}
    all_params = [main_param, *other_params]
    params_entry, call_args = [], []

    for index, param in enumerate(all_params):
        entry = param.name
        if param.annotation is not EMPTY:
            namespace[f"_annotation_{index}"] = param.annotation
            entry += f": _annotation_{index}"
        if param.default is not EMPTY:
            namespace[f"_default_{index}"] = param.default
            entry += f" = _default_{index}"
        params_entry.append(entry)
        call_args.append(f"{param.name}={param.name}")

    return_src = ""
    if return_annotation is not EMPTY:
        namespace["_return_annotation"] = return_annotation
        return_src = " -> _return_annotation"

    source = (
        f"def act(*, {', '.join(params_entry)}, _validate_call: bool = True){return_src}:\n"
        f"    return __func__({', '.join(call_args)})"
    )
    exec(source, namespace)
    generated_act = namespace["act"]
    generated_act.__doc__ = func.__doc__
    generated_act.__name__ = generated_act.__qualname__ = func.__name__
    return generated_act
```

**Why `act.__name__`/`__qualname__` are `func.__name__`, never `"act"`:** without
this, every generated `act` — regardless of which source function it wraps — would
report the literal name `"act"` in `inspect.signature()`, `repr()`, and tracebacks. A
stack trace through a `guard`, a `retry`, and a `sequence` would show three frames all
named `act`, with nothing to distinguish which action actually raised. This also
makes `log_this`'s own output correctly say `guard(...)`/`retry(...)` instead of
`act(...)` for every generated action, since `log_this` derives its logger name and
call-repr from the function it wraps.

[▲ Back to top](#-table-of-contents)

---

## Creator helpers

### `build_init_docstring`

Authors a fresh docstring for the generated `__init__`, listing every configuration
parameter with its type when known.

**Parameters:**

* `params` (*list[inspect.Parameter]*): The constructor's own parameters.

**Returns:**

* `str`: `"No additional configuration parameters."` if `params` is empty; otherwise
  an `Args:`-style listing, one line per parameter.

[▲ Back to top](#-table-of-contents)

---

### `build_call_docstring`

Authors a fresh docstring for the generated `__call__`, describing its one parameter
and return type.

**Parameters:**

* `main_param` (*inspect.Parameter*): `__call__`'s only real parameter.
* `return_annotation` (*Any*): `EMPTY` omits the `Returns:` section entirely.

**Returns:**

* `str`: A short docstring naming the parameter's type and, if known, the return type.

> Unlike `act` (whose docstring is `func.__doc__`, verbatim — see `create_act`'s own
> notes), `__call__` and `__init__`'s docstrings are authored fresh here, because
> *their* signatures genuinely differ from `func`'s own.

[▲ Back to top](#-table-of-contents)

---

### `_describe_annotation`

Best-effort human-readable naming of a raw annotation, shared by both docstring
builders above.

**Parameters:**

* `annotation` (*Any*): A raw annotation value, possibly `EMPTY`.

**Returns:**

* `str | None`: `None` for `EMPTY`; `annotation.__name__` for a plain type (`int` ->
  `"int"`); `str(annotation)` as a fallback for anything without `__name__` (e.g. a
  `X | Y` union).

[▲ Back to top](#-table-of-contents)

---

## Validations

### `validate_param_kinds`

Rejects unsupported parameter kinds before anything else runs — positional-only
(before `/`), `*args`, and `**kwargs` are all incompatible with the fixed
main-param/other-params split this architecture relies on.

**Parameters:**

* `params` (*list[inspect.Parameter]*): The full parameter list to check.
* `func` (*Callable[..., Any]*): Used only for diagnostic messages.

**Raises:**

* A structured `ParamError` (`UNSUPPORTED_PARAM_KIND`, wrapping `TypeError`) naming the
  first offending parameter.

[▲ Back to top](#-table-of-contents)

---

### `validate_params_annotations`

Requires every parameter to carry an explicit, validatable type annotation. Only
called when `use_validations=True`.

**Parameters:**

* `params` (*list[inspect.Parameter]*): The parameters to check.
* `func` (*Callable[..., Any]*): Used only for diagnostic messages.

**Raises:**

* A structured `ParamError` (`MISSING_PARAM_ANNOTATION`, wrapping `TypeError`) if any
  parameter has no annotation at all.
* Whatever `_verify_type_is_validatable` raises, for any annotation present but
  unsupported.

[▲ Back to top](#-table-of-contents)

---

### `validate_return_annotations`

The return-value counterpart to `validate_params_annotations`.

**Parameters:**

* `return_annotation` (*Any*): `func`'s return annotation.
* `func` (*Callable[..., Any]*): Used only for diagnostic messages.

**Raises:**

* A structured `ParamError` (`MISSING_RETURN_ANNOTATION`, wrapping `TypeError`) if
  there's no return annotation at all.
* Whatever `_verify_type_is_validatable` raises, if the return annotation is present
  but unsupported.

[▲ Back to top](#-table-of-contents)

---

### `_verify_type_is_validatable`

Shared final check behind both annotation validators above: confirms an annotation
can actually be decomposed by `simplibs-rules`' own typing engine, not just that it
exists.

**Parameters:**

* `annotated_type` (*Any*): The annotation to check.
* `func` (*Callable[..., Any]*): Used only for diagnostic messages.
* `param_name` (*str | None*): The parameter's name, for labeling; `None` means "this
  is the return annotation".

**Raises:**

* A structured `ParamError` (`UNSUPPORTED_ANNOTATION_TYPE`, wrapping `TypeError`) if
  `simplibs.rules.is_supported_annotation(annotated_type)` returns `False`.

[▲ Back to top](#-table-of-contents)

---

## Diagnostic raisers

Three small, single-purpose functions — each raises exactly one structured
`ParamError`, called from exactly the one place named below. Kept separate rather than
inlined so every failure path in `create_action`'s pipeline has its own clearly named,
independently readable diagnostic.

### `raise_action_instance_error`

Called by `create_action` (step 2) when `func` is an already-instantiated `Action`.
`error_name="ACTION_INSTANCE_NOT_ALLOWED"`, wraps `TypeError`.

### `raise_no_parameters`

Called by `resolve_param` when `func` has no parameters at all.
`error_name="NO_PARAMETERS_FOUND"`, wraps `TypeError`.

### `raise_main_param_not_found`

Called by `resolve_param` when an explicit `main_param` name matches nothing in
`func`'s signature. `error_name="MAIN_PARAM_NOT_FOUND"`, wraps `ValueError`.

[▲ Back to top](#-table-of-contents)

---

## `EMPTY`

A single shared constant — `inspect.Parameter.empty` — imported by every helper above
that needs to distinguish "no annotation/default given" from any real value
(including `None`, which is itself a meaningful annotation/default). Re-exported under
this name purely for readability at each call site (`if param.annotation is not
EMPTY:` reads better than repeating `inspect.Parameter.empty` everywhere).

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-create_action)
