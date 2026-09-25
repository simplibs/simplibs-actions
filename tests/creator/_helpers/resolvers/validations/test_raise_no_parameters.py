"""
Tests for raise_no_parameters — validation that a source function has at least one parameter.
"""
from simplibs.actions.creator._helpers.resolvers.validations.raise_no_parameters import raise_no_parameters
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _no_param_func() -> None:
    """Dummy zero-parameter function used purely as a diagnostic target for the resolver."""
    return None


def test_raise_no_parameters(subtests):
    """Verify that a parameterless function raises a structured ParamError."""
    assert_exception_function(
        subtests,
        raise_no_parameters,
        invalid_params=(_no_param_func,),
        exception_type=ParamError,
        value=None,
        label="function parameters",
        expected="A function with at least one input parameter.",
        problem="has no input parameters defined",
        how_to_fix="Add at least one input parameter",
        exception=TypeError,
    )
