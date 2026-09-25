import pytest
from simplibs.actions.containers.wrappers.log_action import log_action
from simplibs.actions.containers.wrappers.aliases.log_step import log_step
from simplibs.actions.testing.assert_action_alias import assert_action_alias


def test_log_step_is_canonical_alias(subtests):
    # Arrange
    logged_messages = []
    logger = lambda msg: logged_messages.append(msg)
    action = log_step(logger=logger, message="Step")

    # Act & Assert
    assert_action_alias(
        subtests,
        alias=log_step,
        canonical=log_action,
        sample_action=action,
        sample_input="data_stream",
        expected_output="data_stream",
    )
    assert logged_messages == ["Step: 'data_stream'"]