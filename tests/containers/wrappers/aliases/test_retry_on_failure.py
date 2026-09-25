import pytest
from simplibs.actions.containers.wrappers.retry import retry
from simplibs.actions.containers.wrappers.aliases.retry_on_failure import retry_on_failure
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_retry_on_failure_is_canonical_alias(subtests):
    # Arrange
    double = lambda x: x * 2
    action = retry_on_failure(action=double, attempts=2)

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=retry_on_failure,
        canonical=retry,
        sample_action=action,
        sample_input=10,
        expected_output=20,
    )