from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_not_iterable(data: Any) -> NoReturn:
    """Raise a ParamError when data provided to for_each is not iterable."""

    # 1. Raise structured ParamError wrapping a TypeError exception
    raise ParamError(
        error_name="NOT_ITERABLE_DATA",
        label="for_each data",
        value=type(data).__name__,
        problem=(
            f"for_each requires an iterable object, got: {type(data).__name__}.",
            "The passed object does not support iteration (missing __iter__).",
        ),
        expected="An iterable object (e.g., list, tuple, set, generator).",
        how_to_fix=(
            "Pass a collection or iterable data structure into the for_each container.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_not_iterable — structured validation error helper for for_each

## Purpose
Provides a centralized, structured exception emitter when non-iterable data
is passed to the `for_each` container.

## Target Code & Integration
- **Caller**: `for_each` container in `containers/flow_control/for_each.py`.
- **Target Context**: Triggered when `iter(data)` fails during collection processing.

## Exception Standard
Wraps a `TypeError` inside a structured `ParamError`, clearly indicating that an
iterable object was expected and specifying the received type.
"""