"""
Tests for the guards of assert_action and assert_action_alias against checks that would silently never run.
"""
from contextlib import contextmanager

import pytest

from simplibs.actions.base_class import Action
from simplibs.actions.containers import sequence
from simplibs.actions.decorator.to_action import to_action
from simplibs.actions.testing.assert_action import assert_action
from simplibs.actions.testing.assert_action_alias import assert_action_alias


@to_action
def _double(data: int) -> int:
    return data * 2


class _NativeAsyncDouble(Action):
    """Native-async action: __call__ is the misuse guard, acall does the work."""

    is_async = True

    def __call__(self, data, /):
        raise RuntimeError("use acall")

    async def acall(self, data, /):
        return data * 2


class _RecordingSubtests:
    """Records the names of the subtests."""

    def __init__(self) -> None:
        self.names: list[str] = []

    @contextmanager
    def test(self, name: str):
        self.names.append(name)
        yield


# ==============================================================================
# assert_action
# ==============================================================================

def test_assert_action_rejects_expected_outputs_without_valid_values(subtests):
    with pytest.raises(ValueError, match="expected_outputs"):
        assert_action(subtests, _double(), expected_outputs=[2], verbose=False)


def test_assert_action_rejects_expected_input_type_with_deep_check_false(subtests):
    with pytest.raises(ValueError, match="expected_input_type"):
        assert_action(subtests, _double(), expected_input_type=int, deep_check=False, verbose=False)


def test_assert_action_rejects_expected_output_type_with_deep_check_false(subtests):
    with pytest.raises(ValueError, match="expected_output_type"):
        assert_action(subtests, _double(), expected_output_type=int, deep_check=False, verbose=False)


def test_assert_action_deep_check_false_alone_is_still_valid(subtests):
    """Verify that only the combination with an option that would not run is a mistake."""
    assert_action(subtests, _double(), valid_values=[2], expected_outputs=[4], deep_check=False, verbose=False)


# ==============================================================================
# assert_action_alias
# ==============================================================================

def test_alias_rejects_sample_action_without_expected_output(subtests):
    with pytest.raises(ValueError, match="together"):
        assert_action_alias(subtests, alias=sequence, canonical=sequence, sample_action=_double(), verbose=False)


def test_alias_rejects_expected_output_without_sample_action(subtests):
    with pytest.raises(ValueError, match="together"):
        assert_action_alias(subtests, alias=sequence, canonical=sequence, expected_output=4, verbose=False)


def test_alias_identity_only_is_still_valid(subtests):
    assert_action_alias(subtests, alias=sequence, canonical=sequence, verbose=False)


def test_alias_smoke_run_goes_through_acall_for_an_async_action():
    """Verify that a native-async sample action is run through acall (its __call__ would fail)."""
    assert_action_alias(
        _RecordingSubtests(),
        alias=sequence,
        canonical=sequence,
        sample_action=_NativeAsyncDouble(),
        sample_input=5,
        expected_output=10,
        verbose=False,
    )


def test_alias_subtest_names_carry_the_alias_name_and_intro():
    subtests = _RecordingSubtests()

    assert_action_alias(
        subtests,
        alias=sequence,
        canonical=sequence,
        sample_action=_double(),
        sample_input=3,
        expected_output=6,
        intro="case 1: ",
    )

    name = getattr(sequence, "__name__", type(sequence).__name__)
    assert subtests.names == [
        f"case 1: [{name}] test_alias_is_canonical",
        f"case 1: [{name}] test_smoke_run",
    ]
