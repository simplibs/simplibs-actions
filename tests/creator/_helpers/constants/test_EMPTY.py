"""
Tests for EMPTY — the shared sentinel marking "no annotation/default given" in inspect signatures.
"""
import inspect

from simplibs.actions.creator._helpers.constants.EMPTY import EMPTY


def test_empty_is_inspect_parameter_empty():
    """Verify that EMPTY is exactly inspect.Parameter.empty, not just an equal-looking value."""
    assert EMPTY is inspect.Parameter.empty


def test_empty_matches_unannotated_parameter():
    """Verify that a real unannotated/default-less parameter's fields compare equal to EMPTY."""

    def _sample(data):
        return data

    param = inspect.signature(_sample).parameters["data"]

    assert param.annotation is EMPTY
    assert param.default is EMPTY
