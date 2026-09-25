"""
Tests for create_init_and_slots — synthesized __init__ plus matching __slots__.
"""
import inspect

from simplibs.actions.creator._helpers.creators.create_init_and_slots import create_init_and_slots


def _sample(data: dict, prefix: str = "USR", suffix: str = "END") -> dict:
    return data


def test_create_init_and_slots_with_no_params():
    """Verify that an empty parameter list yields empty slots and a no-op __init__."""
    init, slots = create_init_and_slots([])

    assert slots == ()

    dummy_cls = type("Dummy", (object,), {"__slots__": slots, "__init__": init})
    instance = dummy_cls()

    assert instance is not None


def test_create_init_and_slots_binds_params_with_defaults():
    """Verify that __init__ assigns each parameter onto its matching slot, honoring defaults."""
    params = list(inspect.signature(_sample).parameters.values())[1:]  # prefix, suffix
    init, slots = create_init_and_slots(params)

    assert slots == ("prefix", "suffix")

    dummy_cls = type("Dummy", (object,), {"__slots__": slots, "__init__": init})

    default_instance = dummy_cls()
    assert default_instance.prefix == "USR"
    assert default_instance.suffix == "END"

    custom_instance = dummy_cls(prefix="ADMIN", suffix="STOP")
    assert custom_instance.prefix == "ADMIN"
    assert custom_instance.suffix == "STOP"


def test_create_init_and_slots_docstring_lists_params():
    """Verify that the generated __init__ carries a docstring listing its parameters."""
    params = list(inspect.signature(_sample).parameters.values())[1:]
    init, _ = create_init_and_slots(params)

    assert "prefix" in init.__doc__
    assert "suffix" in init.__doc__
