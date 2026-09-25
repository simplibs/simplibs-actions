import pytest
from simplibs.actions.containers import retry


def test_retry_succeeds_on_first_attempt():
    # Arrange
    calls = 0

    def successful_action(data):
        nonlocal calls
        calls += 1
        return data * 2

    action = retry(action=successful_action, attempts=3)

    # Act
    result = action(5)

    # Assert
    assert result == 10
    assert calls == 1


def test_retry_succeeds_after_transient_failures():
    # Arrange
    attempts_count = 0

    def flaky_action(data):
        nonlocal attempts_count
        attempts_count += 1
        if attempts_count < 3:
            raise ValueError("Temporary failure")
        return f"success_{data}"

    action = retry(action=flaky_action, attempts=3, exceptions=(ValueError,))

    # Act
    result = action("test")

    # Assert
    assert result == "success_test"
    assert attempts_count == 3


def test_retry_raises_last_exception_when_all_attempts_fail():
    # Arrange
    attempts_count = 0

    def always_fails(data):
        nonlocal attempts_count
        attempts_count += 1
        raise KeyError(f"Failed attempt {attempts_count}")

    action = retry(action=always_fails, attempts=3, exceptions=(KeyError,))

    # Act & Assert
    with pytest.raises(KeyError) as exc_info:
        action("payload")

    assert "Failed attempt 3" in str(exc_info.value)
    assert attempts_count == 3


def test_retry_raises_for_invalid_attempts_value():
    # Act & Assert
    with pytest.raises(Exception):
        retry(action=lambda x: x, attempts=0)("any_data")


def test_retry_direct_call_curried():
    # Arrange & Act
    result = retry(action=lambda x: x + 1, attempts=2)(10)

    # Assert
    assert result == 11