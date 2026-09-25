from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_invalid_predicate(condition: Any) -> NoReturn:
    """Raise a ParamError if the given condition is neither a Rule nor a Callable."""

    # 1. Raise structured ParamError wrapping a TypeError exception
    raise ParamError(
        error_name="INVALID_PREDICATE_TARGET",
        label="condition / rule",
        value=type(condition).__name__,
        problem=(
            f"Expected a Rule or Callable, got: {type(condition).__name__}.",
            "The passed object cannot be evaluated as a predicate or condition.",
        ),
        expected="A Rule instance or a callable function (Callable).",
        how_to_fix=(
            "Ensure that you pass a Rule object or a callable function returning a boolean as the condition.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_invalid_predicate — structured validation error helper

## Purpose
Provides a centralized, structured exception emitter when a non-predicate value
(neither a `Rule` instance nor a callable object) is supplied where a condition
is expected (e.g., in `guard` or `branch` containers).

## Target Code & Integration
- **Caller**: `as_predicate` helper in `containers/_helpers/as_predicate.py`.
- **Target Context**: Triggered during container setup/execution when normalizing
  input arguments passed as rules or conditional branches.

## Why a separate helper
Isolating exception construction keeps the core `as_predicate` resolution loop
lean, fast, and easy to read, while enforcing consistent structured error messaging
(`ParamError`) across the library.
"""