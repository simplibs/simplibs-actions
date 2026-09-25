"""
Tests for build_call_docstring — generated docstring for the synthesized __call__.
"""
import inspect

from simplibs.actions.creator._helpers.creators._helpers.build_call_docstring import build_call_docstring


def _annotated(data: dict) -> list:
    return [data]


def _unannotated(data):
    return data


def test_build_call_docstring_includes_param_type_and_return_type():
    """Verify that both the main param's type and the return type appear when known."""
    main_param = inspect.signature(_annotated).parameters["data"]
    return_annotation = inspect.signature(_annotated).return_annotation

    docstring = build_call_docstring(main_param, return_annotation)

    assert "data (dict)" in docstring
    assert "Returns:" in docstring
    assert "list" in docstring


def test_build_call_docstring_omits_returns_section_when_unannotated():
    """Verify that no 'Returns:' section is added when the return annotation is EMPTY."""
    main_param = inspect.signature(_unannotated).parameters["data"]
    return_annotation = inspect.signature(_unannotated).return_annotation

    docstring = build_call_docstring(main_param, return_annotation)

    assert "data" in docstring
    assert "Returns:" not in docstring
