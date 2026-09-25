import inspect
from typing import Any, Callable, NoReturn
from simplibs.exception import ParamError


def raise_no_parameters(func: Callable[..., Any]) -> NoReturn:
    """Raise ParamError if the function has no parameters to serve as main input."""

    # 1. Raise structured ParamError wrapping a TypeError exception
    raise ParamError(
        error_name="NO_PARAMETERS_FOUND",
        label="function parameters",
        value=None,
        problem=(
            f"Function '{func.__qualname__}()' has no input parameters defined.",
            "The Action architecture requires at least one parameter to serve as the main payload input.",
        ),
        expected="A function with at least one input parameter.",
        how_to_fix=(
            f"Add at least one input parameter to function '{func.__qualname__}()'.",
            "Example: def my_function(main_data: dict) -> bool:",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_no_parameters — Parameter Presence Validation Helper

## Purpose
Provides a structured exception emitter when a function without any parameters is passed to
`create_action`.

## Integration
- **Caller**: `resolve_param` in `_create_action/resolvers/resolve_param.py`.
- Emits a structured `ParamError` wrapping a `TypeError`.
"""