import inspect
from typing import Callable
# Inners
from .validations import raise_no_parameters, raise_main_param_not_found


def resolve_param(
    params: list[inspect.Parameter],
    main_name: str | None,
    func: Callable,
) -> tuple[inspect.Parameter, list[inspect.Parameter]]:
    """Split `params` into the main pipeline parameter and the rest.

    Args:
        params: The full parameter list of `func`, as returned by
            `inspect.signature(func).parameters.values()`.
        main_name: Name of the parameter to treat as the main pipeline
            input. `None` means "use the first parameter".
        func: The source function — used only for diagnostic messages.

    Returns:
        A `(main_param, other_params)` tuple.
    """

    # 1. Ensure at least one parameter is defined on the function
    if not params:
        raise_no_parameters(func)

    # 2. Default resolution: use the first positional parameter as main
    if main_name is None:
        return params[0], params[1:]

    # 3. Initialize parameter mapping containers
    main_param = None
    other_params = []

    # 4. Separate the main parameter (matching main_name) from the rest
    for param in params:
        if param.name == main_name:
            main_param = param
        else:
            other_params.append(param)

    # 5. Verify that the requested main parameter name was actually found
    if main_param is None:
        raise_main_param_not_found(main_name, func)

    # 6. Return the resolved main parameter and the remaining ones
    # noinspection PyTypeChecker
    return main_param, other_params


_DESIGN_NOTES = """
# resolve_param — parameter separation helper

## Purpose
Every generated Action needs its parameters divided into exactly two
groups: the one main pipeline input (`__call__`'s only parameter) and
everything else (`__init__`'s parameters). This is the single place that
decision gets made, so `create_action` itself never has to reason about
"which parameter is main" more than once.

## Why the fast path skips straight to `params[0]`
When `main_name` is `None` (the common case — most functions written for
`create_action`/`to_action` don't bother naming their main parameter
explicitly), there is no need to walk the full parameter list at all —
`params[0]`/`params[1:]` is a plain slice, cheaper and simpler than the
loop below it. The loop only runs when a caller actually asks for a
specific named parameter to be main.

## Error delegation
Both failure cases delegate to dedicated raise-helpers in `validations/`
(`raise_no_parameters`, `raise_main_param_not_found`) rather than raising
inline — kept consistent with the `simplibs-exception`-based error style
used across the rest of the ecosystem, rather than ad-hoc `TypeError`/
`ValueError` calls scattered through this file.
"""
