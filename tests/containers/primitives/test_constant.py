import pytest
from simplibs.actions.containers import constant


def test_constant_returns_configured_value_and_ignores_data():
    # Arrange
    action = constant(value=42)

    # Act
    result_int = action(100)
    result_str = action("string_input")
    result_none = action(None)

    # Assert
    assert result_int == 42
    assert result_str == 42
    assert result_none == 42


def test_constant_works_with_complex_objects():
    # Arrange
    fixed_payload = {"status": "ok", "code": 200}
    action = constant(value=fixed_payload)

    # Act
    result = action("trigger_data")

    # Assert
    assert result == fixed_payload
    assert result is fixed_payload


def test_constant_direct_call_curried():
    # Arrange & Act
    result = constant(value="fixed_output")("any_input")

    # Assert
    assert result == "fixed_output"