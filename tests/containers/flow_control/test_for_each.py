import pytest
from simplibs.actions.containers import for_each


def test_for_each_applies_action_to_every_item_in_list():
    # Arrange
    double = lambda x: x * 2
    action = for_each(action=double)

    # Act
    result = action([1, 2, 3, 4])

    # Assert
    assert result == [2, 4, 6, 8]


def test_for_each_works_with_empty_iterable():
    # Arrange
    double = lambda x: x * 2
    action = for_each(action=double)

    # Act
    result = action([])

    # Assert
    assert result == []


def test_for_each_works_with_sets_tuples_and_ranges():
    # Arrange
    square = lambda x: x ** 2
    action = for_each(action=square)

    # Act & Assert - Set input
    result_set = action({1, 2, 3})
    assert sorted(result_set) == [1, 4, 9]

    # Act & Assert - Tuple input
    result_tuple = action((1, 2, 3))
    assert result_tuple == [1, 4, 9]

    # Act & Assert - Range input
    result_range = action(range(1, 4))
    assert result_range == [1, 4, 9]


def test_for_each_raises_error_for_non_iterable_input():
    # Arrange
    double = lambda x: x * 2
    action = for_each(action=double)

    # Act & Assert
    with pytest.raises((TypeError, Exception)):
        action(12345)


def test_for_each_direct_call_without_currying():
    # Arrange
    to_upper = lambda s: s.upper()

    # Act
    result = for_each(action=to_upper)(["apple", "banana"])

    # Assert
    assert result == ["APPLE", "BANANA"]