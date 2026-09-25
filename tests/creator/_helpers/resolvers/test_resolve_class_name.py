"""
Tests for resolve_class_name — deriving the generated Action class's name.
"""
from simplibs.actions.creator._helpers.resolvers.resolve_class_name import resolve_class_name


def _process_user_data():
    return None


def test_resolve_class_name_derives_pascal_case_from_snake_case():
    """Verify that a snake_case function name is converted into PascalCase."""
    assert resolve_class_name(_process_user_data, None) == "ProcessUserData"


def test_resolve_class_name_single_word():
    """Verify that a single-word function name converts to a single capitalized word."""

    def parallel():
        return None

    assert resolve_class_name(parallel, None) == "Parallel"


def test_resolve_class_name_honors_explicit_override():
    """Verify that an explicit class_name always wins over the derived one."""
    assert resolve_class_name(_process_user_data, "CustomName") == "CustomName"
