"""
Tests for create_action — dynamically building an Action subclass from an ordinary function.
"""
import pytest
from simplibs.exception.exceptions import ParamError
from simplibs.actions.base_class import Action
from simplibs.actions.creator.create_action import create_action
from simplibs.exception.exceptions import ParamError
from simplibs.exception.testing import assert_exception_function


def _greet(data: dict, prefix: str = "Hi") -> str:
    """Greet using data['name']."""
    return f"{prefix}, {data['name']}!"


def test_create_action_builds_working_action_class():
    """Verify that create_action builds a usable Action subclass around a plain function."""
    Greet = create_action(_greet)

    assert issubclass(Greet, Action)

    instance = Greet(prefix="Hello")
    assert instance({"name": "Bob"}) == "Hello, Bob!"


def test_create_action_default_class_name_and_parameter_defaults():
    """Verify the derived PascalCase class name and that func's own defaults are honored."""
    Greet = create_action(_greet)

    assert Greet.__name__ == "Greet"

    instance = Greet()
    assert instance({"name": "Ann"}) == "Hi, Ann!"


def test_create_action_honors_class_name_override():
    """Verify that an explicit class_name overrides the derived one."""
    Greeting = create_action(_greet, class_name="Greeting")
    assert Greeting.__name__ == "Greeting"


def test_create_action_honors_main_param_override():
    """Verify that an explicit main_param selects a different pipeline input."""

    def _combine(data: dict, note: str = "") -> str:
        return f"{note}:{data}"

    Combine = create_action(_combine, main_param="note")
    instance = Combine(data={"x": 1})
    assert instance("tag") == "tag:{'x': 1}"


def test_create_action_passes_through_existing_action_subclass():
    """Verify that an already-built Action subclass is returned unchanged."""
    Greet = create_action(_greet)
    assert create_action(Greet) is Greet


def test_create_action_rejects_action_instance(subtests):
    """Verify that passing an already-instantiated Action (not a class) raises a structured ParamError."""
    Greet = create_action(_greet)
    instance = Greet()

    assert_exception_function(
        subtests,
        create_action,
        invalid_params=(instance,),
        exception_type=ParamError,
        label="func",
        exception=TypeError,
    )


def test_create_action_use_validations_false_skips_annotation_requirement():
    """Verify that use_validations=False allows an unannotated function through, with no type introspection."""

    def _loose(data, note="x"):
        return data, note

    Loose = create_action(_loose, use_validations=False)

    instance = Loose(note="y")
    assert instance(1) == (1, "y")
    assert not hasattr(Loose, "_input_type")


def test_create_action_use_validations_true_requires_annotations(subtests):
    """Verify that use_validations=True (default) rejects a function with a missing annotation."""

    def _loose(data, note: str = "x") -> tuple:
        return data, note

    assert_exception_function(
        subtests,
        create_action,
        invalid_params=(_loose,),
        exception_type=ParamError,
        label="parameter 'data'",
        exception=TypeError,
    )


def test_create_action_exposes_input_output_type_introspection():
    """Verify that _input_type/_output_type are exposed when use_validations=True (the default)."""
    Greet = create_action(_greet)

    assert Greet._input_type is dict
    assert Greet._output_type is str


def test_create_action_async_source_builds_async_action_class():
    """Verify that create_action with an async function builds an async-native Action class."""

    async def _async_greet(data: dict, prefix: str = "Hi") -> str:
        return f"{prefix}, {data['name']}!"

    AsyncGreet = create_action(_async_greet)

    assert issubclass(AsyncGreet, Action)
    assert AsyncGreet._input_type is dict
    assert AsyncGreet._output_type is str

    instance = AsyncGreet(prefix="Hello")

    # Calling synchronously via __call__ must raise ParamError
    with pytest.raises(ParamError):
        instance({"name": "Bob"})


@pytest.mark.asyncio
async def test_create_action_async_source_executes_via_acall():
    """Verify that an async Action created via create_action executes properly via acall."""

    async def _async_greet(data: dict, prefix: str = "Hi") -> str:
        return f"{prefix}, {data['name']}!"

    AsyncGreet = create_action(_async_greet)
    instance = AsyncGreet(prefix="Hello")

    result = await instance.acall({"name": "Bob"})
    assert result == "Hello, Bob!"