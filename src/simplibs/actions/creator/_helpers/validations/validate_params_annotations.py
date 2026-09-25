import inspect
from typing import Any, Callable
from simplibs.exception import ParamError
# Outers
from ..constants import EMPTY
# Inners
from ._verify_type_is_validatable import _verify_type_is_validatable


def validate_params_annotations(
    params: list[inspect.Parameter],
    func: Callable[..., Any],
) -> None:
    """Validates that all parameters have explicit type annotations and that types are supported."""

    # 1. Iterate through parameters to ensure presence and validity of type annotations
    for param in params:
        if param.annotation is EMPTY:
            raise ParamError(
                error_name="MISSING_PARAM_ANNOTATION",
                label=f"parameter '{param.name}'",
                value=None,
                problem=(
                    f"Parameter '{param.name}' in function '{func.__qualname__}()' ",
                    "does not have a type annotation defined.",
                ),
                expected="An explicit type annotation (e.g., 'data: dict').",
                how_to_fix=(
                    f"Add a type annotation to parameter '{param.name}' in function '{func.__qualname__}()'.",
                    "Example: def my_function(data: dict) -> bool:",
                ),
                exception=TypeError,
            )

        # 2. Verify that the parameter type annotation is validatable
        _verify_type_is_validatable(param.annotation, func, param_name=param.name)


_DESIGN_NOTES = """
# validate_params_annotations — parameter annotation presence & validity checker

## Purpose
Ensures strict type contract compliance by requiring every function parameter passed to
`create_action` to feature an explicit, validatable type annotation.
"""