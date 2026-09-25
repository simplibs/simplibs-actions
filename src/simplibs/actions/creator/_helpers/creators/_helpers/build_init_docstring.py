import inspect
# Inners
from ._describe_annotation import _describe_annotation


def build_init_docstring(
    params: list[inspect.Parameter]
) -> str:
    """Build a short, structural docstring for the generated `__init__` —
    one line per configuration parameter, with its type when known.

    Args:
        params: The "other" (non-main) parameters `__init__` accepts.

    Returns:
        A short docstring listing every parameter in `params`, with its
        type where known, or a one-line notice when there are none.
    """

    # 1. Handle the parameterless case explicitly
    if not params:
        return "No additional configuration parameters."

    # 2. Build one labeled line per parameter
    lines = ["Configure this action.", "", "Args:"]
    for param in params:
        param_type = _describe_annotation(param.annotation)
        label = f"{param.name} ({param_type})" if param_type else param.name
        lines.append(f"    {label}")

    # 3. Join into the final docstring
    return "\n".join(lines)


_DESIGN_NOTES = """
# build_init_docstring — generated docstring for the synthesized __init__

## Why `__init__` gets its own generated docstring, not `func`'s
`func`'s original docstring describes the *whole* function, including
the main parameter that `__init__` never sees (that one lives on
`__call__` instead — see `build_call_docstring.py`). Reusing
`func.__doc__` verbatim here would describe a parameter that doesn't
exist on this specific method and omit the fact that this method
configures the action rather than running it. This function instead
lists exactly the parameters `__init__` actually accepts, with their
types where known — a short, accurate, if minimal, structural summary
rather than a mismatched copy of `func`'s own docs. Mirrors
`build_call_docstring`'s identical reasoning for its own generated
`__call__` docstring.

## Cost of this addition
Negligible — every piece of data this function needs (`params`, their
names, annotations) was already being computed for the `exec` source
text itself in `create_init_and_slots`; this only adds one more pass
over the same list to render it as prose instead of code.
"""
