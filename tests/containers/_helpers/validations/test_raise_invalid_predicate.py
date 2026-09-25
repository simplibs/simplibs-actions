"""
Tests for raise_invalid_predicate — validation of guard/branch condition targets.
"""
import pytest

from simplibs.actions.containers._helpers.validations.raise_invalid_predicate import raise_invalid_predicate
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


@pytest.mark.parametrize("invalid_condition", [42, "not-a-rule", None, []])
def test_raise_invalid_predicate(subtests, invalid_condition):
    """Verify that a non-Rule, non-Callable condition raises a structured ParamError."""
    assert_exception_function(
        subtests,
        raise_invalid_predicate,
        invalid_params=(invalid_condition,),
        exception_type=ParamError,
        value=type(invalid_condition).__name__,
        label="condition / rule",
        expected="A Rule instance or a callable function (Callable).",
        problem="cannot be evaluated as a predicate or condition",
        how_to_fix="Ensure that you pass a Rule object or a callable function",
        exception=TypeError,
    )
