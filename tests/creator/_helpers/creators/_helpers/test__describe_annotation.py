"""
Tests for _describe_annotation — best-effort human-readable naming of a raw annotation.
"""
from simplibs.actions.creator._helpers.constants.EMPTY import EMPTY
from simplibs.actions.creator._helpers.creators._helpers._describe_annotation import _describe_annotation


def test_describe_annotation_returns_none_for_empty():
    """Verify that EMPTY (no annotation given) describes as None."""
    assert _describe_annotation(EMPTY) is None


def test_describe_annotation_uses_dunder_name_for_plain_types():
    """Verify that plain types are described via their __name__."""
    assert _describe_annotation(int) == "int"
    assert _describe_annotation(dict) == "dict"


def test_describe_annotation_falls_back_to_str_for_nameless_constructs():
    """Verify that a typing construct with no __name__ falls back to str(annotation)."""
    union_annotation = int | str
    assert _describe_annotation(union_annotation) == str(union_annotation)
