"""
Tests for validate_params_annotations — validation that every source function parameter is annotated.
"""
import inspect

from simplibs.actions.creator._helpers.validations.validate_params_annotations import validate_params_annotations
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _annotated_func(data: dict, prefix: str = "USR") -> dict:
    """Dummy function where every parameter carries a type annotation."""
    return data


def _missing_annotation_func(data, prefix: str = "USR") -> dict:
    """Dummy function whose 'data' parameter has no type annotation."""
    return data


def test_validate_params_annotations(subtests):
    """Verify that a parameter missing its type annotation raises a structured ParamError."""
    bad_params = list(inspect.signature(_missing_annotation_func).parameters.values())
    good_params = list(inspect.signature(_annotated_func).parameters.values())

    assert_exception_function(
        subtests,
        validate_params_annotations,
        invalid_params=(bad_params, _missing_annotation_func),
        valid_params=(good_params, _annotated_func),
        exception_type=ParamError,
        value=None,
        label="parameter 'data'",
        expected="An explicit type annotation (e.g., 'data: dict').",
        problem="does not have a type annotation defined",
        how_to_fix="Add a type annotation to parameter",
        exception=TypeError,
    )
