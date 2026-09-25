import pytest
from simplibs.actions.containers import lambda_action


def test_lambda_action_executes_raw_callable():
    # Arrange
    strip_func = lambda s: s.strip()
    action = lambda_action(func=strip_func)

    # Act
    result = action("  hello world  ")

    # Assert
    assert result == "hello world"


def test_lambda_action_works_with_builtin_functions():
    # Arrange
    action = lambda_action(func=len)

    # Act
    result = action([1, 2, 3, 4, 5])

    # Assert
    assert result == 5


def test_lambda_action_direct_call_curried():
    # Arrange & Act
    result = lambda_action(func=str.upper)("python")

    # Assert
    assert result == "PYTHON"