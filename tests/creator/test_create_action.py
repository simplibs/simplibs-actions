"""
Tests for create_action — dynamically building an Action subclass from an ordinary function.
"""
import functools
import logging

import pytest

from simplibs.actions.base_class import Action
from simplibs.actions.creator.create_action import create_action
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.exceptions import ParamError, ValidationError


def _greet(data: dict, prefix: str = "Hi") -> str:
    """Greet using data['name']."""
    return f"{prefix}, {data['name']}!"


# ==============================================================================
# 1. BUILDING THE CLASS
# ==============================================================================

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


def test_create_action_supports_callable_without_name_via_class_name():
    """Verify a functools.partial (no __name__) works when class_name is given — as documented."""
    Tagged = create_action(functools.partial(_greet, prefix="Yo"), class_name="Tagged")

    assert Tagged.__name__ == "Tagged"
    assert Tagged()({"name": "Ann"}) == "Yo, Ann!"


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


# ==============================================================================
# 2. VALIDATIONS & TYPE INTROSPECTION
# ==============================================================================

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


# ==============================================================================
# 3. LOGGING (use_logging)
# ==============================================================================

def test_create_action_logs_under_the_source_functions_module(caplog):
    """Verify records go to the logger of the module the source function lives in.

    Regression: the exec-generated `act` used to have no __module__, so log_this logged every
    generated action under a logger literally named "unknown" — invisible to an application's own
    logging configuration.
    """
    Greet = create_action(_greet)

    with caplog.at_level(logging.DEBUG):
        Greet()({"name": "Bob"})

    logger_names = {record.name for record in caplog.records}
    assert _greet.__module__ in logger_names
    assert "unknown" not in logger_names


def test_create_action_logs_even_without_validations(caplog):
    """Verify use_validations=False does not change where (or whether) records are written."""

    def _loose(data, note="x"):
        return data, note

    Loose = create_action(_loose, use_validations=False)

    with caplog.at_level(logging.DEBUG):
        Loose()(1)

    logger_names = {record.name for record in caplog.records}
    assert _loose.__module__ in logger_names
    assert "unknown" not in logger_names


def test_create_action_use_logging_false_writes_no_records(caplog):
    """Verify use_logging=False switches logging off for that action."""
    Greet = create_action(_greet, use_logging=False)

    with caplog.at_level(logging.DEBUG):
        Greet()({"name": "Bob"})

    own_records = [r for r in caplog.records if r.name in (_greet.__module__, "unknown")]
    assert own_records == []


def test_create_action_logging_shortens_large_values(caplog):
    """Verify a large argument is written as a short record (log_this shortens by default)."""

    def _count(data: list) -> int:
        return len(data)

    Count = create_action(_count)

    with caplog.at_level(logging.DEBUG):
        assert Count()(list(range(500))) == 500

    assert "(500 items)" in caplog.text
    assert "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...]" in caplog.text


@pytest.mark.parametrize(
    "flags",
    [
        {},
        {"use_logging": False},
        {"use_validations": False},
        {"use_validations": False, "use_logging": False},
    ],
)
def test_create_action_generated_act_carries_source_module(flags):
    """Verify the generated `act` keeps the source function's module, whatever wrapping is applied."""
    Greet = create_action(_greet, **flags)

    assert Greet.act.__module__ == _greet.__module__


# ==============================================================================
# 4. ASYNC SOURCE
# ==============================================================================

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


@pytest.mark.asyncio
async def test_create_action_async_source_logs_under_the_source_functions_module(caplog):
    """Verify the async path is logged under the source function's module too."""

    async def _async_greet(data: dict, prefix: str = "Hi") -> str:
        return f"{prefix}, {data['name']}!"

    AsyncGreet = create_action(_async_greet)

    with caplog.at_level(logging.DEBUG):
        await AsyncGreet().acall({"name": "Bob"})

    logger_names = {record.name for record in caplog.records}
    assert _async_greet.__module__ in logger_names
    assert "unknown" not in logger_names


# ==============================================================================
# 5. NAMING OF THE GENERATED METHODS
# ==============================================================================

def test_create_action_methods_are_named_after_the_class():
    """Verify the generated entry points carry `<ClassName>.<method>` as __qualname__."""
    Greet = create_action(_greet)

    assert Greet.__init__.__qualname__ == "Greet.__init__"
    assert Greet.__call__.__qualname__ == "Greet.__call__"


def test_create_action_honors_class_name_in_method_names():
    """Verify an explicit class_name is what the methods are named after."""
    Greeting = create_action(_greet, class_name="Greeting")

    assert Greeting.__call__.__qualname__ == "Greeting.__call__"


def test_create_action_act_keeps_source_function_name():
    """Verify `act` is NOT renamed after the class — it mirrors the source function."""
    Greet = create_action(_greet)

    assert Greet.act.__name__ == "_greet"


@pytest.mark.asyncio
async def test_create_action_async_acall_is_named_after_the_class():
    """Verify the generated acall of an async source is named too."""

    async def _async_greet(data: dict, prefix: str = "Hi") -> str:
        return f"{prefix}, {data['name']}!"

    AsyncGreet = create_action(_async_greet)

    assert AsyncGreet.acall.__qualname__ == "AsyncGreet.acall"


def test_create_action_validation_error_names_the_action():
    """Verify a wrong main input reports WHICH action failed."""
    Greet = create_action(_greet)

    with pytest.raises(ValidationError) as excinfo:
        Greet()(42)

    assert "Greet.__call__" in str(excinfo.value)


# ==============================================================================
# 6. create_action VALIDATES ITS OWN ARGUMENTS (@validate_call)
# ==============================================================================

def test_create_action_rejects_wrongly_typed_option():
    """Verify a wrongly typed option is a structured ValidationError, not silently truthy."""
    with pytest.raises(ValidationError):
        create_action(_greet, use_logging="no")  # type: ignore[arg-type]


def test_create_action_validation_can_be_bypassed():
    """Verify `_validate_call=False` skips the check of create_action's own arguments."""
    Greet = create_action(_greet, use_logging="no", _validate_call=False)  # type: ignore[arg-type]

    assert issubclass(Greet, Action)


def test_create_action_rejects_non_callable():
    """Verify a non-callable `func` is a structured ValidationError, not a raw TypeError."""
    with pytest.raises(ValidationError):
        create_action(42)  # type: ignore[arg-type]