import pytest
from simplibs.rules import Rule
from simplibs.actions.containers._helpers.as_predicate import as_predicate


class DummyRule(Rule):
    def is_valid(self, data: int) -> bool:
        return data > 0

    def build_exception(self, data, context=""):
        return ValueError(f"Rule failed for {data}: {context}")


def test_as_predicate_extracts_is_valid_from_rule_instance():
    # Arrange
    rule = DummyRule()

    # Act
    predicate = as_predicate(rule)

    # Assert
    assert predicate(10) is True
    assert predicate(-5) is False
    assert predicate == rule.is_valid


def test_as_predicate_returns_plain_callable_as_is():
    # Arrange
    is_even = lambda x: x % 2 == 0

    # Act
    predicate = as_predicate(is_even)

    # Assert
    assert predicate(4) is True
    assert predicate(5) is False
    assert predicate is is_even


def test_as_predicate_raises_exception_for_invalid_predicate():
    # Arrange
    invalid_predicate = "not_a_callable_or_rule"

    # Act & Assert
    with pytest.raises(Exception):
        as_predicate(invalid_predicate)