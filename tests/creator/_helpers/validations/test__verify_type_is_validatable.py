"""
Tests for _verify_type_is_validatable — validation gate for supported annotation types.

NOTE: `is_supported_annotation` (from the rules subsystem) decides what counts as
"supported" here. `dict` is used as an obviously-supported baseline and a bare
literal `42` (not a type at all) as an obviously-unsupported one. If the real
decomposition engine treats something more subtle as unsupported (a specific
typing construct, say), swap the invalid fixture for that instead.
"""
from simplibs.actions.creator._helpers.validations._verify_type_is_validatable import _verify_type_is_validatable
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _sample_func(data: dict) -> dict:
    """Dummy function used purely as a diagnostic target."""
    return data


def test__verify_type_is_validatable_param(subtests):
    """Verify that an unsupported parameter annotation raises a structured ParamError."""
    assert_exception_function(
        subtests,
        _verify_type_is_validatable,
        invalid_params=(42, _sample_func, "data"),
        valid_params=(dict, _sample_func, "data"),
        exception_type=ParamError,
        value=42,
        label="parameter 'data'",
        expected="A supported Python type annotation (e.g., str, int, list[str], Union, etc.).",
        problem="is not supported",
        how_to_fix="Update the type annotation",
        exception=TypeError,
    )


def test__verify_type_is_validatable_return(subtests):
    """Verify that an unsupported return-value annotation (no param_name) raises a structured ParamError."""
    assert_exception_function(
        subtests,
        _verify_type_is_validatable,
        invalid_params=(42, _sample_func),
        valid_params=(dict, _sample_func),
        exception_type=ParamError,
        value=42,
        label="return value",
        expected="A supported Python type annotation (e.g., str, int, list[str], Union, etc.).",
        problem="is not supported",
        how_to_fix="Update the type annotation",
        exception=TypeError,
    )
