"""
Tests for raise_main_param_not_found — validation of explicit main_param name resolution.
"""
from simplibs.actions.creator._helpers.resolvers.validations.raise_main_param_not_found import (
    raise_main_param_not_found,
)
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _sample_func(data: dict) -> dict:
    """Dummy function used purely as a diagnostic target for the resolver."""
    return data


def test_raise_main_param_not_found(subtests):
    """Verify that a non-existent explicit main_param name raises a structured ParamError."""
    assert_exception_function(
        subtests,
        raise_main_param_not_found,
        invalid_params=("nonexistent_param", _sample_func),
        exception_type=ParamError,
        value="nonexistent_param",
        label="main parameter 'nonexistent_param'",
        expected=f"A parameter name that exists in function '{_sample_func.__qualname__}()'.",
        problem="was not found in the signature",
        how_to_fix="Check for typos in the parameter name",
        exception=ValueError,
    )
