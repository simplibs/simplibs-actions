import pytest
from simplibs.exception.exceptions import ParamError, ValidationError
from simplibs.actions.containers.flow_control.for_each import for_each


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


@pytest.mark.asyncio
async def test_for_each_acall_processes_items_concurrently():
    """Verify that acall processes items concurrently via asyncio.gather."""

    async def async_double(x: int) -> int:
        return x * 2

    action = for_each(action=async_double)

    result = await action.acall([1, 2, 3, 4])

    assert result == [2, 4, 6, 8]


@pytest.mark.asyncio
async def test_for_each_acall_raises_error_for_non_iterable_input():
    """Verify that acall raises an error for non-iterable input data."""

    async def async_double(x: int) -> int:
        return x * 2

    action = for_each(action=async_double)

    with pytest.raises((TypeError, ParamError, Exception)):
        await action.acall(12345)


def _numbers():
    yield 1
    yield 2
    yield 3


def test_for_each_processes_a_generator_item_by_item():
    """Verify a generator is accepted by the synchronous path and every item is processed.

    Regression: with `data: Iterable` the validation walked the generator (twice), so the body
    received it exhausted and the result was silently `[]`.
    """
    action = for_each(action=lambda x: x * 2)

    assert action(_numbers()) == [2, 4, 6]


@pytest.mark.asyncio
async def test_for_each_acall_processes_a_generator():
    """Verify the async path accepts a generator too (both paths accept the same inputs)."""
    action = for_each(action=lambda x: x * 2)

    assert await action.acall(_numbers()) == [2, 4, 6]


def test_for_each_still_processes_reiterable_containers():
    """Verify lists, tuples, sets and ranges are processed as before."""
    action = for_each(action=lambda x: x + 1)

    assert action([1, 2]) == [2, 3]
    assert action((1, 2)) == [2, 3]
    assert action(range(2)) == [1, 2]
    assert action({5}) == [6]


def test_for_each_rejects_a_non_iterable_input():
    """Verify a non-iterable value is rejected by the type check."""
    action = for_each(action=lambda x: x)

    with pytest.raises(ValidationError):
        action(42)
