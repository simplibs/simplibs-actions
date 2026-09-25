from typing import Any, Callable
from simplibs.exception import ParamError
# Outers
from ..constants import EMPTY
# Inners
from ._verify_type_is_validatable import _verify_type_is_validatable


def validate_return_annotations(
    return_annotation: Any,
    func: Callable[..., Any],
) -> None:
    """Validates that return value has an explicit type annotation and that the type is supported."""

    # 1. Check if return type annotation is defined
    if return_annotation is EMPTY:
        raise ParamError(
            error_name="MISSING_RETURN_ANNOTATION",
            label="return annotation",
            value=None,
            problem=(
                f"Function '{func.__qualname__}()' does not have a return type annotation defined.",
            ),
            expected="An explicit return type annotation (e.g., '-> dict').",
            how_to_fix=(
                f"Add a return type annotation to function '{func.__qualname__}()'.",
                "Example: def my_function(data: dict) -> bool:",
            ),
            exception=TypeError,
        )

    # 2. Verify that the return type annotation is validatable
    _verify_type_is_validatable(return_annotation, func)


_DESIGN_NOTES = """
# validate_return_annotations — return annotation presence & validity checker

## Purpose
Ensures strict type contract compliance by requiring every wrapped Action function to
explicitly declare a validatable return type annotation.
"""