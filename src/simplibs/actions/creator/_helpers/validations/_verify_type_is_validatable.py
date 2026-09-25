from typing import Any, Callable
from simplibs.exception import ParamError
from simplibs.rules import is_supported_annotation


def _verify_type_is_validatable(
    annotated_type: Any,
    func: Callable[..., Any],
    param_name: str | None = None,
) -> None:
    """Verifies whether the given type annotation is supported by the validation subsystem."""

    # 1. Verify if the annotation is supported by rules subsystem
    if not is_supported_annotation(annotated_type):
        label_text = f"parameter '{param_name}'" if param_name else "return value"
        location_text = f"parameter '{param_name}'" if param_name else "return value"

        # 2. Raise structured ParamError for unsupported type annotations
        raise ParamError(
            error_name="UNSUPPORTED_ANNOTATION_TYPE",
            label=label_text,
            value=annotated_type,
            problem=(
                f"Type annotation {annotated_type!r} for {location_text} "
                f"in function '{func.__qualname__}()' is not supported.",
                "The validation subsystem cannot validate this specific type structure.",
            ),
            expected="A supported Python type annotation (e.g., str, int, list[str], Union, etc.).",
            how_to_fix=(
                f"Update the type annotation for {location_text} to a supported type.",
                "Ensure you are not using incompatible or unsupported complex meta-types.",
            ),
            exception=TypeError,
        )


_DESIGN_NOTES = """
# _verify_type_is_validatable — type annotation support checker

## Purpose
Internal helper used during `create_action` factory execution to guarantee that parameter
or return value annotations can be evaluated by `simplibs.rules`.

## Target Integration
- **Callers**: `validate_params_annotations` and `validate_return_annotations`.
- **Target Context**: Prevents constructing Action classes with unsupported or unvalidatable
  typing structures before runtime execution.
"""