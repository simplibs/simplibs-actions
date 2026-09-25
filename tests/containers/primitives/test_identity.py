import pytest
from simplibs.actions.containers import identity


def test_identity_returns_input_data_unchanged():
    # Arrange
    action = identity()

    # Act
    result_int = action(42)
    result_str = action("hello")
    result_list = action([1, 2, 3])

    # Assert
    assert result_int == 42
    assert result_str == "hello"
    assert result_list == [1, 2, 3]


def test_identity_preserves_object_identity():
    # Arrange
    action = identity()
    complex_object = {"key": "value"}

    # Act
    result = action(complex_object)

    # Assert
    assert result is complex_object


def test_identity_direct_call_curried():
    # Arrange & Act
    result = identity()("test_value")

    # Assert
    assert result == "test_value"