from typing import NoReturn
from simplibs.exception import ParamError


def raise_invalid_attempts(attempts: int) -> NoReturn:
    """Raise ParamError if retry attempts count is less than 1."""

    # 1. Raise structured ParamError wrapping a ValueError exception
    raise ParamError(
        error_name="INVALID_RETRY_ATTEMPTS",
        label="attempts",
        value=attempts,
        problem=(
            f"Invalid attempt count: {attempts}.",
            "Retry attempts count must be at least 1.",
        ),
        expected="An integer greater than or equal to 1.",
        how_to_fix=(
            "Set the attempts parameter to a value of at least 1.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_invalid_attempts — structured validation error helper for retry

## Purpose
Provides a centralized, structured exception emitter when an invalid `attempts`
count (< 1) is passed to the `retry` container.

## Target Code & Integration
- **Caller**: `retry` container in `containers/wrappers/retry.py`.
- **Target Context**: Triggered as an early parameter validation guard before entering
  the execution loop.

## Exception Standard
Wraps a `ValueError` inside a structured `ParamError`, providing clear diagnostic
details (received value, expected range, and fix instructions).
"""