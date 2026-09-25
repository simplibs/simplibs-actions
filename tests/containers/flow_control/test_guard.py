import pytest
from simplibs.actions.containers import guard


class DummyRule:
    def __init__(self, should_pass: bool):
        self.should_pass = should_pass

    def __call__(self, data):
        return self.should_pass

    def build_exception(self, data, context=""):
        return ValueError(f"Rule failed for {data}: {context}")


def test_guard_passes_data_unchanged_when_rule_holds():
    # Arrange
    is_positive = lambda x: x > 0
    action = guard(rule=is_positive)

    # Act
    result = action(42)

    # Assert
    assert result == 42


def test_guard_raises_exception_when_plain_callable_rule_fails():
    # Arrange
    is_positive = lambda x: x > 0
    action = guard(rule=is_positive)

    # Act & Assert
    with pytest.raises(Exception):
        action(-5)


def test_guard_uses_rule_build_exception_when_available():
    # Arrange
    failing_rule = DummyRule(should_pass=False)
    action = guard(rule=failing_rule)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        action("test_data")

    assert "Rule failed for test_data" in str(exc_info.value)


def test_guard_direct_call_without_currying():
    # Arrange
    is_non_empty = lambda s: len(s) > 0

    # Act
    result = guard(rule=is_non_empty)("hello")

    # Assert
    assert result == "hello"

    # Act & Assert
    with pytest.raises(Exception):
        guard(rule=is_non_empty)("")