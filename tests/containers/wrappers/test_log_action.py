import pytest
from simplibs.actions.containers import log_action


def test_log_action_logs_data_without_prefix_and_returns_unchanged():
    # Arrange
    logged_messages = []
    logger = lambda msg: logged_messages.append(msg)
    action = log_action(logger=logger)

    # Act
    result = action({"key": "value"})

    # Assert
    assert result == {"key": "value"}
    assert logged_messages == [{"key": "value"}]


def test_log_action_logs_data_with_custom_message_prefix():
    # Arrange
    logged_messages = []
    logger = lambda msg: logged_messages.append(msg)
    action = log_action(logger=logger, message="Processing step")

    # Act
    result = action(42)

    # Assert
    assert result == 42
    assert logged_messages == ["Processing step: 42"]


def test_log_action_direct_call_curried():
    # Arrange
    logged_messages = []
    logger = lambda msg: logged_messages.append(msg)

    # Act
    result = log_action(logger=logger, message="Direct call")("data_stream")

    # Assert
    assert result == "data_stream"
    assert logged_messages == ["Direct call: 'data_stream'"]