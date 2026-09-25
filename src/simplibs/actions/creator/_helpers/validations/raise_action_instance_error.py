from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_action_instance_error(instance: Any) -> NoReturn:
    """Raise ParamError when an already instantiated Action is passed to create_action."""

    # 1. Raise structured ParamError wrapping a TypeError exception
    raise ParamError(
        error_name="ACTION_INSTANCE_NOT_ALLOWED",
        label="func",
        value=type(instance).__name__,
        problem=(
            f"Received an instantiated Action '{type(instance).__name__}' object.",
            "create_action expects an uninstantiated callable, function, or class type, not an instance.",
        ),
        expected="A function, callable object, or uninstantiated Action class type.",
        how_to_fix=(
            "Pass the raw function or class type directly instead of an already instantiated object.",
            "Example: use `MyAction` instead of `MyAction()`.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_action_instance_error — validation helper for create_action

## Purpose
Provides a clear diagnostic error when a caller accidentally passes an instantiated `Action`
object to `create_action` (or `@to_action`), preventing invalid double-wrapping.
"""