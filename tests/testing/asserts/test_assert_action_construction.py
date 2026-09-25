"""
Tests for assert_action_construction — checking that bad construction args raise an exception.

Constructor kwargs are type-checked by the synthesized __init__'s own validate_call wrapping
(when use_validations=True), which raises ValidationError for a wrong-typed value — not
ParamError. ValidationError is therefore assert_action_construction's default
expected_exception_type; anything else (e.g. ParamError) can still be passed explicitly for
actions with hand-written constructor guards.
"""
import pytest
from simplibs.exception import ValidationError

from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.asserts.assert_action_construction import assert_action_construction


@to_action
def _greet(data: dict, prefix: str) -> str:
    return f"{prefix}, {data['name']}!"


def test_assert_action_construction_passes_for_actually_invalid_params(subtests):
    """Verify that a wrong-typed constructor kwarg (raising ValidationError) passes the check."""
    assert_action_construction(
        subtests,
        _greet,
        invalid_init_params=[((), {"prefix": 123})],
        verbose=False,
    )


def test_assert_action_construction_fails_for_valid_params(subtests):
    """Verify that construction args which do NOT raise are treated as a failure."""
    with pytest.raises(BaseException):
        assert_action_construction(
            subtests,
            _greet,
            invalid_init_params=[((), {"prefix": "Hi"})],
            verbose=False,
        )


def test_assert_action_construction_sweeps_multiple_entries(subtests):
    """Verify that every entry in invalid_init_params is checked, not just the first."""
    assert_action_construction(
        subtests,
        _greet,
        invalid_init_params=[
            ((), {"prefix": 123}),
            ((), {"prefix": 4.5}),
        ],
        verbose=False,
    )


def test_assert_action_construction_honors_explicit_exception_type(subtests):
    """Verify that an explicit expected_exception_type overrides the ValidationError default."""
    assert_action_construction(
        subtests,
        _greet,
        invalid_init_params=[((), {"prefix": 123})],
        expected_exception_type=ValidationError,
        verbose=False,
    )
