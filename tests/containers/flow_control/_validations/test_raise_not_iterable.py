"""
Tests for raise_not_iterable — validation of for_each input data.
"""
import pytest

from simplibs.actions.containers.flow_control._validations.raise_not_iterable import raise_not_iterable
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


@pytest.mark.parametrize("non_iterable", [42, 3.14, None])
def test_raise_not_iterable(subtests, non_iterable):
    """Verify that a non-iterable for_each input raises a structured ParamError."""
    assert_exception_function(
        subtests,
        raise_not_iterable,
        invalid_params=(non_iterable,),
        exception_type=ParamError,
        value=type(non_iterable).__name__,
        label="for_each data",
        expected="An iterable object (e.g., list, tuple, set, generator).",
        problem="for_each requires an iterable object",
        how_to_fix="Pass a collection or iterable data structure",
        exception=TypeError,
    )
