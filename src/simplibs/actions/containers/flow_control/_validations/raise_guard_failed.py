from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_guard_failed(data: Any) -> NoReturn:
    """Raise a ParamError when a guard condition fails and rule lacks build_exception."""

    # 1. Raise structured ParamError wrapping a ValueError exception
    raise ParamError(
        error_name="GUARD_CONDITION_FAILED",
        label="guard data",
        value=data,
        problem=(
            f"Guard condition failed for value: {data!r}.",
            "Input data did not satisfy the required hard gate criteria.",
        ),
        expected="Data satisfying the defined rule condition (Rule).",
        how_to_fix=(
            "Adjust input data to satisfy the rule condition.",
            "Verify the evaluation logic of the tested predicate.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_guard_failed — structured validation error helper for guard

## Purpose
Provides a centralized, structured exception emitter when a `guard` condition
fails for the input data and the evaluated `rule` does not provide its own
custom `build_exception` method.

## Target Code & Integration
- **Caller**: `guard` container in `containers/flow_control/guard.py`.
- **Target Context**: Triggered as the fallback error path during runtime
  data evaluation in a hard gate.

## Exception Standard
Wraps a `ValueError` inside a structured `ParamError`, providing clear diagnostic
details (actual data value, expected rule match, and fix suggestions).
"""