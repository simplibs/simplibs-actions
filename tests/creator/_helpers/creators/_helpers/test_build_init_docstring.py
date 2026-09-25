"""
Tests for build_init_docstring — generated docstring for the synthesized __init__.
"""
import inspect

from simplibs.actions.creator._helpers.creators._helpers.build_init_docstring import build_init_docstring


def _configured(data: dict, prefix: str = "USR", suffix=None) -> dict:
    return data


def test_build_init_docstring_lists_each_param_with_known_type():
    """Verify that every configuration parameter is listed, with its type when known."""
    params = list(inspect.signature(_configured).parameters.values())[1:]  # prefix, suffix

    docstring = build_init_docstring(params)

    assert "prefix (str)" in docstring
    assert "suffix" in docstring
    assert "Args:" in docstring


def test_build_init_docstring_handles_empty_param_list():
    """Verify that an empty parameter list yields the dedicated no-configuration notice."""
    docstring = build_init_docstring([])

    assert docstring == "No additional configuration parameters."
