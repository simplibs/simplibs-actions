import inspect
from typing import Any
# Inners
from ._describe_annotation import _describe_annotation


def build_call_docstring(
    main_param: inspect.Parameter,
    return_annotation: Any
) -> str:
    """Build a short, structural docstring for the generated `__call__` —
    parameter name/type and return type, whenever they are known.

    Args:
        main_param: The parameter `__call__` exposes as its own single
            argument.
        return_annotation: The source function's return annotation.

    Returns:
        A short docstring naming `main_param` (with its type, if known)
        and the return type (if known).
    """

    # 1. Describe the main parameter, with its type if known
    param_type = _describe_annotation(main_param.annotation)
    param_label = f"{main_param.name} ({param_type})" if param_type else main_param.name

    # 2. Build the base docstring lines
    lines = [
        "Run this action's main pipeline step.",
        "",
        "Args:",
        f"    {param_label}: the pipeline input.",
    ]

    # 3. Append the return type section, if known
    return_type = _describe_annotation(return_annotation)
    if return_type:
        lines += ["", "Returns:", f"    {return_type}"]

    # 4. Join into the final docstring
    return "\n".join(lines)


_DESIGN_NOTES = """
# build_call_docstring — generated docstring for the synthesized __call__

## Why the generated docstring is authored, not copied from `func`
Unlike `act` (see `create_act.py`'s own notes — its signature is
`func`'s own, unchanged, so copying `func.__doc__` verbatim stays
accurate), `__call__`'s signature genuinely differs from `func`'s: it
exposes only the main parameter, not the full set `func` originally
declared. Copying `func`'s docstring here could describe parameters that
no longer appear on this specific method, or omit the bypass flag that
now does. This function instead generates a short, structural
description (parameter name/type, return type) directly from the data
`create_call` already has on hand — accurate for what this specific
method actually accepts, at the cost of being far less rich than a
hand-written docstring.

## Why this is intentionally minimal
Best-effort hover information when the source data allows it, not a
substitute for reading `func`'s own documentation — still available via
the class's own `__doc__`, copied from `func.__doc__` in `create_action`
itself. A caller who wants the full picture reads the class docstring;
this one answers a narrower, mechanical question: "what do I pass to
`(...)`, and what do I get back?"
"""
