"""
Tests for to_action — decorator turning an ordinary function into an Action subclass.
"""
from simplibs.actions.base_class import Action
from simplibs.actions.decorator.to_action import to_action


def test_to_action_bare_decorator_creates_working_action_subclass():
    """Verify that @to_action (no parentheses) turns a function into a usable Action subclass."""

    @to_action
    def process_user(data: dict, prefix: str = "USR") -> dict:
        """Prefix-tag a user record."""
        return {**data, "prefix": prefix}

    assert issubclass(process_user, Action)

    instance = process_user(prefix="ADMIN")
    result = instance({"name": "Alice"})

    assert result == {"name": "Alice", "prefix": "ADMIN"}


def test_to_action_parametrized_form_honors_class_name():
    """Verify that @to_action(...) accepts configuration and applies a custom class_name."""

    @to_action(class_name="CustomAction")
    def do_thing(data: dict) -> dict:
        return data

    assert do_thing.__name__ == "CustomAction"

    instance = do_thing()
    assert instance({"x": 1}) == {"x": 1}


def test_to_action_instance_is_directly_callable():
    """Verify that the resulting Action instance is invoked directly as `instance(data)`."""

    @to_action
    def double(data: int) -> int:
        return data * 2

    action_instance = double()

    assert action_instance(21) == 42


def test_to_action_main_param_override():
    """Verify that @to_action(main_param=...) picks a non-first parameter as the pipeline input."""

    @to_action(main_param="note")
    def combine(data: dict, note: str = "") -> str:
        return f"{note}:{data}"

    action_instance = combine(data={"x": 1})

    assert action_instance("tag") == "tag:{'x': 1}"
