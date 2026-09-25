import inspect
from typing import Any, Callable
# Outers
from ..constants import EMPTY


def create_act(
    main_param: inspect.Parameter,
    other_params: list[inspect.Parameter],
    return_annotation: Any,
    func: Callable[..., Any],
) -> Callable[..., Any]:
    """Synthesize `act` — a thin wrapper carrying `func`'s own real signature.

    Args:
        main_param: `func`'s main parameter.
        other_params: `func`'s remaining parameters.
        return_annotation: `func`'s return annotation.
        func: The source function `act` ultimately calls.

    Returns:
        A real function with `func`'s exact parameter names, annotations,
        docstring, `__name__`, and defaults, plus one added keyword-only
        `_validate_call: bool = True` parameter that is accepted and
        silently dropped — never forwarded into `func` itself.
    """

    # 1. Prepare accumulators
    namespace: dict[str, Any] = {"__func__": func}
    all_params = [main_param, *other_params]
    params_entry: list[str] = []
    call_args: list[str] = []

    # 2. Walk through the parameters
    for index, param in enumerate(all_params):

        # 2.1 Prepare working variables
        param_name = param.name
        param_entry = param_name

        # 2.2 Add the annotation to the exec namespace, if present
        if param.annotation is not EMPTY:
            annotation_name = f"_annotation_{index}"
            namespace[annotation_name] = param.annotation
            param_entry += f": {annotation_name}"

        # 2.3 Add the default value to the exec namespace, if present
        if param.default is not EMPTY:
            default_name = f"_default_{index}"
            namespace[default_name] = param.default
            param_entry += f" = {default_name}"

        # 2.4 Record the parameter across both accumulators
        params_entry.append(param_entry)
        call_args.append(f"{param_name}={param_name}")

    # 3. Prepare the return annotation
    return_src = ""
    if return_annotation is not EMPTY:
        namespace["_return_annotation"] = return_annotation
        return_src = " -> _return_annotation"

    # 4. Build the source text
    source = (
        f"def act(*, {', '.join(params_entry)}, _validate_call: bool = True)"
        f"{return_src}:\n"
        f"    return __func__({', '.join(call_args)})"
    )

    # 5. Compile the function
    exec(source, namespace)
    generated_act = namespace["act"]

    # 6. Carry the source function's own docstring over onto act — act is
    #    just func wearing a thin validation/logging coat, so func's own
    #    documentation is the most accurate description available.
    generated_act.__doc__ = func.__doc__

    # 7. Carry the source function's own __name__ over onto act too —
    #    see design notes for why this matters and why "act" itself
    #    never appears here.
    generated_act.__name__ = func.__name__
    generated_act.__qualname__ = func.__name__

    # 8. Return the generated object
    return generated_act


_DESIGN_NOTES = """
# create_act — synthesizing act, the fully-typed core logic wrapper

## Why `func` itself never sees `_validate_call`
`func` is the caller's own business logic — written and understood with
no knowledge of `simplibs-validate`'s bypass mechanism. `act` is a
generated wrapper carrying `func`'s exact signature plus one addition:
`_validate_call`, accepted and immediately dropped, never passed into
`__func__(...)`. This keeps `func` reusable and testable on its own,
completely unaware that it has been wrapped at all.

## Why `_validate_call` must be a REAL parameter, not a `**kwargs` catch
`validate_call` (per its own documentation) looks for a parameter
literally named `_validate_call` in the decorated function's actual
signature via `inspect.signature` — not via some generic kwargs-catching
mechanism. A generic `def act(self, *args, **kwargs)` wrapper would
technically accept the flag, but would destroy the real, per-parameter
signature that `validate_call` and IDEs both rely on.

## Why `act.__doc__` is `func.__doc__`, verbatim, not a generated summary
`act` has no independent identity of its own — it is `func`, wearing a
thin, generated coat (extra parameter, static-method binding). Its
docstring should therefore describe what `func` does, not what `act`
mechanically does. This is a deliberate contrast with `create_call`/
`create_init_and_slots`, whose generated docstrings are authored fresh
(see `creators/_helpers/`) because *their* signatures genuinely differ
from `func`'s — `act`'s does not, beyond the one added bypass parameter.

## Why `act.__name__`/`__qualname__` are set to `func.__name__`, not left as `"act"`
Without this, every generated `act` — regardless of which source
function it wraps — would report the literal name `"act"` in
`inspect.signature()`, in `repr()`, and in tracebacks. A stack trace
through a `Guard`, a `Retry`, and a `Sequence` would show three frames
all named `act`, with nothing to distinguish which action actually
raised — a real loss of traceability for debugging, logging
(`log_this` derives its own logger and call-repr from the function it
wraps, so this also makes `log_this`'s own output correctly say
`guard(...)`/`retry(...)` instead of `act(...)` for every single
generated action), and any tooling that inspects a function by name.

Deliberately NOT set to something like `f"{func.__name__}.act"` — the
plain `func.__name__` is enough, and is in fact the more elegant choice
once you already know (from this very design note, and from the
docstring rationale above) that `act` is nothing more than `func` in a
thin coat: reusing `func`'s exact name says that implicitly, the same
way reusing `func`'s exact docstring does. Appending `.act` would
reintroduce, in the name itself, the same kind of redundant self-
reference that was deliberately left out of the docstring — "yes, this
is act, wrapping func" is already obvious from where you're looking; it
doesn't need to be repeated in every generated identifier too.

## Relationship to create_call
`create_call` builds `__call__`, which explicitly forwards its own
`_validate_call` into `self.act(..., _validate_call=_validate_call)`.
This file's half of the contract is simply: accept that flag, honor
`validate_call`'s bypass detection, and never leak it into `func`.
"""
