import inspect
from typing import Any, Callable
from simplibs.sentinels import EMPTY
# Outers
from ..validations import raise_async_action_requires_acall_error
# Inners
from ._helpers import build_call_docstring


def create_call(
    main_param: inspect.Parameter,
    other_params: list[inspect.Parameter],
    return_annotation: Any,
    is_async: bool,
) -> tuple[Callable[..., Any], Callable[..., Any] | None]:
    """Synthesize `__call__` — and, for an async-sourced action, `acall` too.

    Args:
        main_param: The parameter that becomes the sole real argument
            (besides `self`) on both generated entry points.
        other_params: The remaining parameters, read off `self` (already
            bound there by the generated `__init__`) and forwarded into
            `self.act(...)`.
        return_annotation: The source function's return annotation, used
            to annotate both generated methods' return type and docstring.
        is_async: Whether `act` (built by `create_act`, from the same
            source function) is a native `async def`. Determines both
            which entry points are generated and how `__call__` behaves.

    Returns:
        A `(call, acall)` pair.
        * For a synchronous source (`is_async=False`): `call` is the
          familiar real `__call__`, delegating straight into
          `self.act(...)`; `acall` is `None` — the class inherits
          `Action`'s own default `acall` (a to-thread bridge over
          `__call__`), exactly as before this feature existed.
        * For an async source (`is_async=True`): `call` still exists
          (every `Action` must satisfy the base class's abstract
          `__call__`), but raises immediately — calling it would
          otherwise silently return an un-awaited coroutine instead of
          the real result. `acall` is a real, generated `async def`
          that `await`s `self.act(...)` directly, with no thread hop.
    """

    # 1. Prepare accumulators shared by both generated entry points
    namespace: dict[str, Any] = {}
    main_name = main_param.name
    call_param = main_name
    act_arguments = [f"{main_name}={main_name}"]

    # 2. Prepare the main parameter
    if main_param.annotation is not EMPTY:
        annotation_name = "_main_annotation"
        namespace[annotation_name] = main_param.annotation
        call_param += f": {annotation_name}"

    # 3. Add the parameters already bound on the instance
    for param in other_params:
        act_arguments.append(f"{param.name}=self.{param.name}")

    # 4. Forward the validation bypass flag
    act_arguments.append("_validate_call=_validate_call")

    # 5. Prepare the return annotation
    call_return = ""
    if return_annotation is not EMPTY:
        namespace["_return_annotation"] = return_annotation
        call_return = " -> _return_annotation"

    # 6. Generate the shared docstring text once — same parameter/return
    #    description fits both __call__ and acall equally well
    docstring = build_call_docstring(main_param, return_annotation)

    # 7. Synchronous source function — unchanged behavior, no acall generated
    if not is_async:
        source = (
            f"def __call__(self, {call_param}, *, _validate_call: bool = True)"
            f"{call_return}:\n"
            f"    return self.act({', '.join(act_arguments)})"
        )
        exec(source, namespace)
        generated_call = namespace["__call__"]
        generated_call.__doc__ = docstring
        return generated_call, None

    # 8. Async source function — __call__ raises; acall does the real work.
    #    Two separate exec namespaces so each function only carries what
    #    it actually needs in scope.
    call_namespace = dict(namespace)
    call_namespace["_raise_async_action_requires_acall_error"] = raise_async_action_requires_acall_error
    call_source = (
        f"def __call__(self, {call_param}, *, _validate_call: bool = True){call_return}:\n"
        f"    return _raise_async_action_requires_acall_error(self)"
    )
    exec(call_source, call_namespace)
    generated_call = call_namespace["__call__"]
    generated_call.__doc__ = (
        f"{docstring}\n\n"
        "Raises:\n"
        "    This action wraps an async source function — use `await acall(...)` instead."
    )

    acall_namespace = dict(namespace)
    acall_source = (
        f"async def acall(self, {call_param}, *, _validate_call: bool = True){call_return}:\n"
        f"    return await self.act({', '.join(act_arguments)})"
    )
    exec(acall_source, acall_namespace)
    generated_acall = acall_namespace["acall"]
    generated_acall.__doc__ = docstring

    # 9. Return both — create_action assigns acall onto the class only when not None
    return generated_call, generated_acall


_DESIGN_NOTES = """
# create_call — synthesizing __call__ (and acall, for async sources)

## Why __call__/acall only take `main_param`, never the other parameters
Those other parameters were already bound onto `self` by the generated
`__init__` at construction time. Both entry points read them back off
`self` and forward them into `self.act(...)` alongside `main_param`, so
the caller only ever has to supply the one value that actually changes
per invocation.

## `_validate_call` is forwarded here, not consumed
Both generated entry points accept `_validate_call` and pass it straight
through into `self.act(..., _validate_call=_validate_call)` — neither
decides anything with it itself. See `create_act.py`'s own design notes
for what happens to the flag once it arrives there.

## Why this is `__call__`, not `execute`
`Action.__call__` is the sole abstract entry point — for an Action, being
callable IS the whole point. Generating `__call__` directly here means a
`create_action`-built class satisfies `Action`'s contract with no extra
indirection.

## Why an async-sourced action's `__call__` raises, rather than returning a coroutine
`act` for an async source is itself `async def` (see `create_act.py`).
If `__call__` simply did `return self.act(...)`, calling `action(data)`
would silently hand back an un-awaited coroutine object instead of the
real result — no exception, just a value that compares unequal to
everything and eventually triggers a distant, confusing "coroutine was
never awaited" warning at garbage-collection time, far from the actual
mistake. Raising immediately, via the dedicated
`raise_async_action_requires_acall_error`, turns that into one clear
diagnostic exactly at the call site that got it wrong — the same
philosophy this whole ecosystem applies everywhere else a misuse is
detectable up front instead of left to surface confusingly downstream.

## Why `is_async` is a passed-in flag, not re-detected here
`create_act.py` already computes `inspect.iscoroutinefunction(func)` for
its own `def`/`async def` choice. This file needs the identical answer
for the identical reason (the source function's own nature), but
receives it as a parameter from `create_action` rather than importing
`func` itself and re-deriving it — this file has never needed to know
`func` directly (it only ever worked with parameter/annotation data),
and keeping it that way means `create_call` stays focused purely on
shaping `__call__`/`acall`'s own signatures, with zero risk of the two
generators ever disagreeing about whether a given source is async.

## Two separate `exec` namespaces for the async branch
`call_namespace` and `acall_namespace` are independent copies of the
shared setup (`namespace`), rather than one dict both functions are
`exec`'d into together. Each generated function only needs its own
pieces (`__call__` needs the raise-helper, `acall` needs none of that);
keeping them separate avoids one function accidentally picking up a name
meant for the other, and keeps each `exec` call's namespace legible on
its own.

## Where the generated docstring comes from
`build_call_docstring` (in `creators/_helpers/`) does the actual work —
see its own design notes for why this docstring is authored fresh rather
than copied from `func`, unlike `act` (see `create_act.py`'s notes for
that contrast). For an async source, the same generated text is reused
for both `__call__` (with an appended note pointing at `acall`) and
`acall` itself — the parameter/return description is identical either
way; only the calling convention differs.
"""
