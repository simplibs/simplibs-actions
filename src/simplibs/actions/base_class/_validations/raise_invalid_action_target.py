from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_invalid_action_target(obj: Any) -> NoReturn:
    """Raises a ParamError when an object cannot be resolved into an Action.

    Args:
        obj: The candidate target object that failed resolution checks.

    Raises:
        ParamError: Unconditionally raised with diagnostic context.
    """
    raise ParamError(
        error_name="INVALID_ACTION_TARGET",
        label="action target candidate",
        value=type(obj).__name__,
        problem=(
            f"Object of type '{type(obj).__name__}' cannot be converted into an Action.",
            "Action resolution expects an Action instance, a Rule, or any Callable.",
        ),
        expected="An Action instance, a Rule, or a callable function/object.",
        how_to_fix=(
            "Ensure you pass a valid callable entity to the operator or resolution helper.",
            "If passing a custom class or object, ensure it is callable (implements __call__) "
            "or inherits from Action / Rule.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_invalid_action_target — Action Resolution Failure Diagnostic

## Purpose
Provides a standard, highly diagnostic `ParamError` exception when an object
passed to `Action.resolve_action` or compositional operators (`|`, `>>`) cannot
be converted into a valid `Action` instance.

---

## 1. Unified Exception Interface

By delegating invalid resolution reporting to a dedicated function, all
composition and resolution entry points share identical error diagnostics,
labels, and remediation instructions.

---

## 2. Dynamic Type Inspection

Reflects the actual type of the received `obj` in the diagnostic message to
give clear feedback to the developer about what unsupported type was provided.
"""