import inspect
from typing import Any, Callable
# Outers
from ..constants import EMPTY
# Inners
from ._helpers import build_call_docstring


def create_call(
    main_param: inspect.Parameter,
    other_params: list[inspect.Parameter],
    return_annotation: Any,
) -> Callable[..., Any]:
    """Synthesize `__call__` — the Action's single pipeline entry point.

    Args:
        main_param: The parameter that becomes `__call__`'s only real
            argument (besides `self`).
        other_params: The remaining parameters, read off `self` (already
            bound there by the generated `__init__`) and forwarded into
            `self.act(...)`.
        return_annotation: The source function's return annotation, used
            to annotate `__call__`'s own return type and docstring.

    Returns:
        A real `__call__` function taking `main_param` (plus a
        `_validate_call` bypass flag) and delegating to `self.act(...)`,
        carrying a generated docstring describing its parameter and
        return type.
    """

    # 1. Prepare accumulators
    namespace: dict[str, Any] = {}
    main_name = main_param.name
    call_param = main_name
    call_return = ""
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
    if return_annotation is not EMPTY:
        namespace["_return_annotation"] = return_annotation
        call_return = " -> _return_annotation"

    # 6. Build the source text
    source = (
        f"def __call__(self, {call_param}, *, _validate_call: bool = True)"
        f"{call_return}:\n"
        f"    return self.act({', '.join(act_arguments)})"
    )

    # 7. Compile the function
    exec(source, namespace)
    generated_call = namespace["__call__"]

    # 8. Attach a generated docstring describing the parameter/return type
    generated_call.__doc__ = build_call_docstring(main_param, return_annotation)

    # 9. Return the generated function
    return generated_call


_DESIGN_NOTES = """
# create_call — synthesizing __call__, the single pipeline entry point

## Why __call__ only takes `main_param`, never the other parameters
Those other parameters were already bound onto `self` by the generated
`__init__` at construction time. `__call__` reads them back off `self`
and forwards them into `self.act(...)` alongside `main_param`, so the
caller only ever has to supply the one value that actually changes per
invocation.

## `_validate_call` is forwarded here, not consumed
`__call__` accepts `_validate_call` and passes it straight through into
`self.act(..., _validate_call=_validate_call)` — it does not decide
anything with it itself. See `create_act.py`'s own design notes for what
happens to the flag once it arrives there.

## Why this is `__call__`, not `execute`
`Action.__call__` is the sole abstract entry point — for an Action, being
callable IS the whole point. Generating `__call__` directly here means a
`create_action`-built class satisfies `Action`'s contract with no extra
indirection.

## Where the generated docstring comes from
`build_call_docstring` (in `creators/_helpers/`) does the actual work —
see its own design notes for why this docstring is authored fresh rather
than copied from `func`, unlike `act` (see `create_act.py`'s notes for
that contrast).
"""
