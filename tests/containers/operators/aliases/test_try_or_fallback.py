import pytest
from simplibs.actions.containers.operators.fallback import fallback
from simplibs.actions.containers.operators.aliases.try_or_fallback import try_or_fallback
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_try_or_fallback_is_canonical_alias(subtests):
    # Arrange
    failing_action = lambda x: 1 / 0
    fallback_action = lambda x: x * 2
    action = try_or_fallback(action=failing_action, on_error=fallback_action)

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=try_or_fallback,
        canonical=fallback,
        sample_action=action,
        sample_input=5,
        expected_output=10,
    )