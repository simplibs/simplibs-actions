"""
Tests for unwrap_log_this_and_validate_call — peeling pre-existing @validate_call/@log_this layers.

NOTE: assumes `log_this` is importable from `simplibs.validate` alongside `validate_call`
(per the ecosystem's completed tools list). Adjust the import if `log_this` actually lives
at a different path.
"""
from simplibs.validate import log_this, validate_call

from simplibs.actions.creator._helpers.resolvers.unwrap_log_this_and_validate_call import (
    unwrap_log_this_and_validate_call,
)


def _plain(data: dict) -> dict:
    return data


def test_unwrap_returns_plain_function_unchanged():
    """Verify that a function carrying neither decorator is returned unchanged (same object)."""
    assert unwrap_log_this_and_validate_call(_plain) is _plain


def test_unwrap_peels_single_validate_call_layer():
    """Verify that a single @validate_call layer is peeled off down to the raw function."""
    wrapped = validate_call(_plain)
    assert unwrap_log_this_and_validate_call(wrapped) is _plain


def test_unwrap_peels_single_log_this_layer():
    """Verify that a single @log_this layer is peeled off down to the raw function."""
    wrapped = log_this(_plain)
    assert unwrap_log_this_and_validate_call(wrapped) is _plain


def test_unwrap_peels_interleaved_layers_in_any_order():
    """Verify that interleaved @validate_call/@log_this layers, in any order/depth, are all peeled off."""
    wrapped = log_this(validate_call(log_this(_plain)))
    assert unwrap_log_this_and_validate_call(wrapped) is _plain
