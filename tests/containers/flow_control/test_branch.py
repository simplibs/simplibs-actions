import pytest
from simplibs.actions.containers import branch


def test_branch_executes_then_branch_when_condition_is_true():
    # Arrange
    is_even = lambda x: x % 2 == 0
    double = lambda x: x * 2
    zero = lambda x: 0

    action = branch(condition=is_even, then_branch=double, else_branch=zero)

    # Act
    result = action(4)

    # Assert
    assert result == 8


def test_branch_executes_else_branch_when_condition_is_false():
    # Arrange
    is_even = lambda x: x % 2 == 0
    double = lambda x: x * 2
    zero = lambda x: 0

    action = branch(condition=is_even, then_branch=double, else_branch=zero)

    # Act
    result = action(5)

    # Assert
    assert result == 0


def test_branch_passes_data_unchanged_when_condition_fails_and_no_else_branch():
    # Arrange
    is_positive = lambda x: x > 0
    double = lambda x: x * 2

    action = branch(condition=is_positive, then_branch=double)

    # Act
    result = action(-10)

    # Assert
    assert result == -10


def test_branch_direct_call_without_currying():
    # Arrange
    is_positive = lambda x: x > 0
    double = lambda x: x * 2
    negate = lambda x: -x

    # Act - prvním voláním se vytvoří akce, druhým se předají data
    result_true = branch(condition=is_positive, then_branch=double, else_branch=negate)(10)
    result_false = branch(condition=is_positive, then_branch=double, else_branch=negate)(-5)

    # Assert
    assert result_true == 20
    assert result_false == 5