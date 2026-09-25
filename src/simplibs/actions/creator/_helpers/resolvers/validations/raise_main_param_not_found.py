import inspect
from typing import Any, Callable, NoReturn
from simplibs.exception import ParamError


def raise_main_param_not_found(
    main_name: str,
    func: Callable[..., Any],
) -> NoReturn:
    """Raise ParamError if the specified main parameter name is not found in the function signature."""

    # 1. Raise structured ParamError wrapping a ValueError exception
    raise ParamError(
        error_name="MAIN_PARAM_NOT_FOUND",
        label=f"main parameter '{main_name}'",
        value=main_name,
        problem=(
            f"Parameter with name '{main_name}' was not found in the signature of function '{func.__qualname__}()'.",
        ),
        expected=f"A parameter name that exists in function '{func.__qualname__}()'.",
        how_to_fix=(
            f"Check for typos in the parameter name '{main_name}'.",
            "Ensure the value passed as main parameter name matches an exact parameter name in the function.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_main_param_not_found — Parameter Resolution Validation Helper

## Purpose
Provides a structured exception emitter when an explicit `main_param_name` is passed to
`create_action`, but no matching parameter exists in the target function signature.

## Integration
- **Caller**: `resolve_param` in `_create_action/resolvers/resolve_param.py`.
- Emits a structured `ParamError` wrapping a `ValueError`.
"""