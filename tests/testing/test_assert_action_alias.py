import pytest
from simplibs.actions.containers import sequence
from simplibs.actions.containers.operators.aliases import run_in_sequence
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_assert_alias_passes_for_valid_alias(subtests):
    # Arrange
    double = lambda x: x * 2
    increment = lambda x: x + 1
    action = run_in_sequence(steps=(double, increment))

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=run_in_sequence,
        canonical=sequence,
        sample_action=action,
        sample_input=5,
        expected_output=11,
    )


def test_assert_alias_fails_when_identity_mismatches(subtests):
    # Arrange
    def fake_sequence(*args, **kwargs):
        return sequence(*args, **kwargs)

    # Act & Assert
    with pytest.raises(AssertionError) as exc_info:
        assert_action_alias(
            subtests,
            alias=fake_sequence,
            canonical=sequence,
            verbose=False,
        )

    assert "is not the exact same object" in str(exc_info.value)


def test_assert_alias_fails_when_smoke_test_output_mismatches(subtests):
    # Arrange
    double = lambda x: x * 2
    action = run_in_sequence(steps=(double,))

    # Act & Assert
    with pytest.raises(AssertionError) as exc_info:
        assert_action_alias(
            subtests,
            alias=run_in_sequence,
            canonical=sequence,
            sample_action=action,
            sample_input=5,
            expected_output=999,  # Incorrect expectation
            verbose=False,
        )

    assert "did not match expected output" in str(exc_info.value)