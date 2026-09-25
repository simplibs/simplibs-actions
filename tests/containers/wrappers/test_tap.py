import pytest
from simplibs.actions.containers import tap


def test_tap_executes_side_effect_and_returns_original_data():
    # Arrange
    side_effect_store = []

    def record_side_effect(data):
        side_effect_store.append(f"processed_{data}")

    action = tap(action=record_side_effect)

    # Act
    result = action("my_data")

    # Assert
    assert result == "my_data"
    assert side_effect_store == ["processed_my_data"]


def test_tap_discards_return_value_of_inner_action():
    # Arrange
    transform_func = lambda x: x * 999
    action = tap(action=transform_func)

    # Act
    result = action(10)

    # Assert
    assert result == 10


def test_tap_direct_call_curried():
    # Arrange
    captured = []
    capture_func = lambda x: captured.append(x)

    # Act
    result = tap(action=capture_func)("payload")

    # Assert
    assert result == "payload"
    assert captured == ["payload"]