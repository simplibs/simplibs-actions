import inspect
from typing import Any, Callable, overload, ParamSpec, Concatenate, TypeVar
from simplibs.validate import validate_call, log_this
# Outers
from ..base_class import Action
# Inners
from ._helpers.resolvers import (
    resolve_class_name,
    resolve_param,
    unwrap_log_this_and_validate_call,
)
from ._helpers.creators import (
    create_init_and_slots,
    create_call,
    create_act,
)
from ._helpers.validations import (
    validate_param_kinds,
    validate_params_annotations,
    validate_return_annotations,
    raise_action_instance_error,
)
# Annotations
P = ParamSpec("P")
R = TypeVar("R")
DataT = TypeVar("DataT")


# ============================================================================
# Typing overloads — resolved at type-check time only, never executed.
# ============================================================================

@overload
def create_action(
    func: type[Action],
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
    _validate_call: bool = True,
) -> type[Action]: ...


@overload
def create_action(
    func: Callable[Concatenate[DataT, P], R],
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
    _validate_call: bool = True,
) -> Callable[P, Action]: ...


# ============================================================================
# Actual implementation
# ============================================================================

@validate_call
def create_action(
    func: Callable[..., Any],
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
    _validate_call: bool = True,
) -> Any:
    """Dynamically build an Action subclass from an ordinary function.

    Args:
        func: The source function to wrap into an Action class. Its
            first parameter (or `main_param`, if given) becomes the
            Action's main pipeline input (`__call__`/`acall`); every
            other parameter becomes a constructor (`__init__`)
            parameter. If `func` is already an `Action` subclass, it is
            returned unchanged; if it is an `Action` instance, a
            diagnostic error is raised instead. If `func` already
            carries `@validate_call` and/or `@log_this` layers (in any
            order or depth), they are peeled off first — see the design
            notes below. If `func` is a native `async def`, the
            resulting class is async-native too — see the design notes
            for exactly what that changes.
        main_param: Name of the parameter to use as the main
            pipeline input. Defaults to `None`, meaning "the first
            parameter".
        use_validations: If `True`, requires `func` to be fully annotated
            (every parameter and the return value) and wraps
            `act`/`__init__`/`__call__` (and `acall`, for an async
            source) with `validate_call`; the resulting class also
            carries `_input_type`/`_output_type` introspection
            attributes. If `False`, no annotation is required and no
            validation is applied — a fast, low-friction path for
            prototypes.
        use_logging: If `True`, wraps `act` with `log_this` on top of
            `validate_call` (entry/exit/timing/exception logging).
            Records go to the logger of the module the source function
            lives in (`func.__module__`), and `log_this` shortens large
            arguments and results, so logging a list-returning action is
            safe. Pass `False` to turn logging off for this action.
        class_name: Explicit name for the generated class.
            Defaults to `func.__name__` converted from `snake_case` to
            `PascalCase`. Required for callables with no usable
            `__name__` (lambdas, `functools.partial`).
        _validate_call: Internal bypass switch for the `@validate_call`
            decorator applied to `create_action` itself — not part of
            the function's own behavior.

    Returns:
        A new `Action` subclass whose instances are constructed with
        every parameter of `func` except the main one
        (`MyAction(other_param=...)`), and called with the main
        parameter alone — synchronously (`instance(main_value)`) for a
        `def` source, or via `await instance.acall(main_value)` for an
        `async def` source (whose synchronous `__call__` raises instead
        — see the design notes).
    """

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
    _is_async = inspect.iscoroutinefunction(_func)

    # 7. Validate the received annotations, if requested
    if use_validations:
        validate_params_annotations(_params, _func)
        validate_return_annotations(_return_annotation, _func)

    # 8. Build the pieces of the class dict
    init, slots = create_init_and_slots(_other_params)
    call, acall = create_call(_main_param, _other_params, _return_annotation, _is_async)
    act = create_act(_main_param, _other_params, _return_annotation, _func)

    # 9. Name the generated methods after the class, so diagnostics say which action
    #    failed. Must stay BEFORE validate_call (step 10): functools.wraps copies
    #    __qualname__ at wrap time, and validate_call builds its error context from it.
    init.__qualname__ = f"{_class_name}.__init__"
    call.__qualname__ = f"{_class_name}.__call__"
    if acall is not None:
        acall.__qualname__ = f"{_class_name}.acall"

    # 10. Apply validation to the generated methods
    if use_validations:
        init = validate_call(init)
        call = validate_call(call)
        act = validate_call(act)
        if acall is not None:
            acall = validate_call(acall)

    # 11. Apply logging
    if use_logging:
        act = log_this(act)

    # 12. Turn act into a static method
    act = staticmethod(act)

    # 13. Assemble the class dict
    attrs: dict[str, Any] = {
        "__doc__": _func.__doc__,
        "__slots__": slots,
        "__init__": init,
        "__call__": call,
        "act": act,
        "is_async": _is_async,
        "_main_name": _main_param.name,
    }

    # 14. Only an async source generates its own acall — a synchronous
    #      class inherits Action's own default (to-thread bridge) instead.
    if acall is not None:
        attrs["acall"] = acall

    # 15. Add I/O type introspection attributes, only when validated
    if use_validations:
        attrs["_input_type"] = _main_param.annotation
        attrs["_output_type"] = _return_annotation

    # 16. Build the class
    # noinspection PyTypeChecker
    return type(
        _class_name,
        (Action,),
        attrs
    )


_DESIGN_NOTES = """
# create_action — synthesizing Action classes from functions

## Structure of `_helpers/`
This function is deliberately thin — it orchestrates, it does not
implement. Each real piece of work lives in its own file under
`_helpers/`:
* `resolvers/` — `resolve_param` (splits the signature into main +
  the rest), `resolve_class_name` (names the generated class),
  `unwrap_log_this_and_validate_call` (normalizes `func` down to its
  true underlying callable — see its own design notes for why this is
  needed and how it handles arbitrary decorator stacking).
* `creators/` — `create_init_and_slots`, `create_call`, `create_act`
  (the three `exec`-based codegen functions that build the actual class
  members, each backed by its own `_helpers/` for anything beyond the
  bare codegen itself — see `creators/_helpers/`).
* `validations/` — parameter-kind and annotation checks, plus the
  `raise_*` diagnostic helpers, written in `simplibs-exception` style.

## The two Action-input cases, and why they are handled differently
`func` already being an `Action` **class** is a legitimate, idempotent
case — returning it unchanged mirrors a common Python idiom
(`pathlib.Path(Path(x))` being a safe no-op).

`func` being an `Action` **instance** is different — its configuration is
already bound, so `raise_action_instance_error` turns that into a clear,
actionable error instead of silently misreading the instance's generated
`__call__` signature as fresh constructor configuration.

## Why step 3 is now a single call, not inline logic
The unwrap-until-stable loop previously lived directly in this function's
body. Moved to its own file (`resolvers/unwrap_log_this_and_validate_call.py`)
for two reasons: it keeps this function reading as a clean, linear
pipeline (each step is one clearly-named call), and it gives that logic
room for its own, deeper design notes (the interleaved-stacking argument
for why a fixed-point loop is needed, rather than one pass of each
unwrap function) without bloating this file's own notes with something
that isn't really about `create_action`'s own orchestration.

## `_is_async` — one detection, shared by generators and class attributes
`inspect.iscoroutinefunction(_func)` is computed exactly once, on the
already-unwrapped source function, and passed into `create_call` as a
plain flag. It is also explicitly injected into the generated class dictionary 
as `is_async`, ensuring that the resulting `Action` subclass cleanly overrides 
the base class default (`False`) when generated from an `async def` source.
`create_act` performs the identical check independently on
the same `_func` (see its own design notes for why the duplication is
intentional) — both generators are working from the same, single
unwrapped source, so there is no risk of the two ever disagreeing about
whether this particular action is async.

## What actually differs for an async source, end to end
* `act` (from `create_act`) becomes `async def`, `await`-ing `__func__`.
* `__call__` (from `create_call`) still exists — the abstract contract
  on `Action` requires it — but raises immediately rather than silently
  returning an un-awaited coroutine.
* `acall` (also from `create_call`) is a real, generated coroutine
  function, assigned onto the class in 14 above. For a
  synchronous source, `acall` stays `None` here and the class simply
  inherits `Action`'s own default implementation (the to-thread bridge)
  — nothing new needs assembling for the overwhelming majority of
  actions, which remain purely synchronous exactly as before this
  feature existed.
* `use_validations`/`use_logging` apply uniformly either way — `acall`
  gets the same `validate_call` wrapping `call`/`act`/`init` already
  receive, whenever it exists at all.

## `_input_type`/`_output_type` — conditional on `use_validations`
These are only ever set inside the `if use_validations:` branch, after
`validate_params_annotations`/`validate_return_annotations` have already
guaranteed every annotation is real and supported. Unaffected by whether
the source is sync or async — the main parameter's annotation and the
return annotation mean the same thing either way.

## Logging — which logger, and what is written
`use_logging=True` wraps `act` with `log_this`, which logs through
`logging.getLogger(<module of the wrapped function>)`. `create_act` copies
the source function's `__module__` onto the generated `act` (an `exec`-built
function has none, and `log_this` would fall back to a logger named
`"unknown"`), so records appear under the module where the source function
lives and follow the application's own logging configuration. `log_this`
also shortens large arguments and results by default (see its own
`max_items`), which is why list-returning actions no longer need
`use_logging=False`. `use_logging=False` remains the switch for an action
that must not be logged at all (sensitive data, extremely frequent calls).

## Why the generated methods are named here, not inside their creators
`__init__`, `__call__` and `acall` are named `<ClassName>.<method>` in step 9. Left
alone, an exec-built function is called just `__call__`, so `validate_call`'s error
context reads `Function __call__()` — identical for every action in a pipeline, with
nothing to say which step received bad data. Only this function knows the class name
(`resolve_class_name`); `create_call`/`create_init_and_slots` work from parameters
alone, so naming happens here rather than widening their signatures.

`act` is deliberately different: `create_act` gives it `func`'s own name and module,
because `act` IS `func` in a thin coat (see its design notes), and `log_this` reads
its output from those. Two sources of truth, two places: `act` mirrors the function,
the entry points mirror the class.

Only `__qualname__` is set, never `__module__`: a module prefix would claim the class
lives where the source function does, which it does not.

## Why `create_action` decorates itself with `@validate_call`
Dogfooding — `create_action`'s own parameters are exactly the kind of
plain, fully-typed parameters `validate_call` is meant to check.
`_validate_call` on `create_action` itself is the same bypass hook every
other `validate_call`-decorated function in this ecosystem carries.

## What this file deliberately leaves to containers themselves
`create_action` gives an async-sourced action's own `act`/`acall` a
correct, efficient async path. It does NOT — and structurally cannot —
make a container like `sequence`/`parallel`/`fallback` correctly await
its OWN child steps concurrently or without unnecessary thread hops;
that requires knowing what those containers actually do with their
children, which is bespoke per container. See `sequence.py`/
`parallel.py`/`fallback.py`'s own design notes for their hand-written
`acall` overrides, and `Action.py`'s design notes for why its own
default `acall` is deliberately not asked to handle that case either.
"""