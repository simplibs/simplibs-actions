import pytest
from simplibs.actions.containers._helpers.as_action import as_action
from simplibs.actions.base_class import Action
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_as_action_is_direct_alias_of_action_resolve_action(subtests):
    # Act & Assert
    assert_action_alias(
        subtests,
        alias=as_action,
        canonical=Action.resolve_action,
    )


def test_as_action_resolves_callable_into_action():
    # Arrange
    double = lambda x: x * 2

    # Act
    resolved = as_action(double)

    # Assert
    assert isinstance(resolved, Action)
    assert resolved(5) == 10