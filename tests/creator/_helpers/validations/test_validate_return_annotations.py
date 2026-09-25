"""
Tests for validate_return_annotations — validation that the source function's return value is annotated.
"""
import inspect

from simplibs.actions.creator._helpers.validations.validate_return_annotations import validate_return_annotations
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _annotated_return_func(data: dict) -> dict:
    """Dummy function with an explicit return annotation."""
    return data


def _missing_return_func(data: dict):
    """Dummy function with no return annotation at all."""
    return data


def test_validate_return_annotations(subtests):
    """Verify that a function missing its return type annotation raises a structured ParamError."""
    good_return = inspect.signature(_annotated_return_func).return_annotation
    bad_return = inspect.signature(_missing_return_func).return_annotation

    assert_exception_function(
        subtests,
        validate_return_annotations,
        invalid_params=(bad_return, _missing_return_func),
        valid_params=(good_return, _annotated_return_func),
        exception_type=ParamError,
        value=None,
        label="return annotation",
        expected="An explicit return type annotation (e.g., '-> dict').",
        problem="does not have a return type annotation defined",
        how_to_fix="Add a return type annotation",
        exception=TypeError,
    )
