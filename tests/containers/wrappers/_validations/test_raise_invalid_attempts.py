"""
Tests for raise_invalid_attempts — validation of retry attempt counts.
"""
import pytest

from simplibs.actions.containers.wrappers._validations.raise_invalid_attempts import raise_invalid_attempts
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


@pytest.mark.parametrize("invalid_attempts", [0, -1, -100])
def test_raise_invalid_attempts(subtests, invalid_attempts):
    """Verify that an attempts count below 1 raises a structured ParamError."""
    assert_exception_function(
        subtests,
        raise_invalid_attempts,
        invalid_params=(invalid_attempts,),
        exception_type=ParamError,
        value=invalid_attempts,
        label="attempts",
        expected="An integer greater than or equal to 1.",
        problem="Invalid attempt count",
        how_to_fix="Set the attempts parameter to a value of at least 1.",
        exception=ValueError,
    )
