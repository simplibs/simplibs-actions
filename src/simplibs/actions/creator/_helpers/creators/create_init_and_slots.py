import inspect
from typing import Any, Callable
# Outers
from ..constants import EMPTY
# Inners
from ._helpers import build_init_docstring


def create_init_and_slots(
    params: list[inspect.Parameter],
) -> tuple[Callable, tuple[str, ...]]:
    """Synthesize `__init__` (via `exec`) with a real signature matching
    `params`, plus the matching `__slots__` tuple.

    Args:
        params: The "other" (non-main) parameters — i.e. everything the
            generated Action's constructor should accept.

    Returns:
        A `(init, slots)` pair: `init` is a real function carrying
        `params`' own names, annotations, defaults, and a generated
        docstring listing each one; `slots` is the matching `__slots__`
        tuple for the generated class.
    """

    # 1. Prepare accumulators
    namespace: dict[str, Any] = {}
    params_entry: list[str] = ["self"]
    if params:
        params_entry.append("*")
    slot_names: list[str] = []
    assignments: list[str] = []

    # 2. Walk through the parameters
    for index, param in enumerate(params):

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

        # 2.4 Record the parameter across all three accumulators
        params_entry.append(param_entry)
        slot_names.append(param_name)
        assignments.append(f"    self.{param_name} = {param_name}")

    # 3. Build the source text
    source = (
        f"def __init__({', '.join(params_entry)}):\n"
        + ("\n".join(assignments) or "    pass")
    )

    # 4. Compile the function
    exec(source, namespace)
    generated_init = namespace["__init__"]

    # 5. Attach a generated docstring listing each configuration parameter
    generated_init.__doc__ = build_init_docstring(params)

    # 6. Return the generated objects
    return generated_init, tuple(slot_names)


_DESIGN_NOTES = """
# create_init_and_slots — synthesizing a real __init__ via exec

## Why exec-based codegen, not a generic **kwargs constructor
A generic `def __init__(self, **kwargs): ...` would accept anything and
assign it onto `self` — but it destroys the real, inspectable signature
this whole approach exists to provide. Writing out real source text and
`exec`-ing it is the same technique `dataclasses` uses to synthesize
`__init__`.

## The `("\\n".join(assignments) or "    pass")` fallback
Without it, a parameterless Action (e.g. `identity`) would synthesize
`def __init__(self):\\n` with nothing indented underneath — an
`IndentationError` at `exec` time. `or "    pass"` guarantees the
generated body is always syntactically valid.

## Why annotations/defaults are injected via namespace entries
`_annotation_{index}`/`_default_{index}` hold the actual Python objects
in the `exec` namespace, referenced by name — not `repr()`'d into the
source text, since most annotations/defaults used here (`Rule`
instances, arbitrary objects) have no `repr()` that would `eval()` back
into the same object.

## Where the generated docstring comes from
`build_init_docstring` (in `creators/_helpers/`) does the actual work —
see its own design notes for why this docstring is authored fresh rather
than copied from `func`, unlike `act` (see `create_act.py`'s notes for
that contrast).
"""
