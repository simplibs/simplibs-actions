"""
Tests for raise_guard_failed — validation of guard hard-gate failures without a build_exception fallback.
"""
import pytest

from simplibs.actions.containers.flow_control._validations.raise_guard_failed import raise_guard_failed
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


@pytest.mark.parametrize("failing_data", [-5, "bad", None, (1, 2)])
def test_raise_guard_failed(subtests, failing_data):
    """Verify that a guard failure raises a structured ParamError carrying the offending data."""
    assert_exception_function(
        subtests,
        raise_guard_failed,
        invalid_params=(failing_data,),
        exception_type=ParamError,
        value=failing_data,
        label="guard data",
        expected="Data satisfying the defined rule condition (Rule).",
        problem="Guard condition failed for value",
        how_to_fix="Adjust input data to satisfy the rule condition.",
        exception=ValueError,
    )
