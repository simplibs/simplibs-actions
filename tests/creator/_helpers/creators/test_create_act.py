"""
Tests for create_act — synthesized `act` carrying func's own real signature.
"""
import functools
import inspect

import pytest

from simplibs.actions.creator._helpers.creators.create_act import create_act


def _sample(data: dict, prefix: str = "USR") -> dict:
    """Prefix-tag a data dict."""
    return {**data, "prefix": prefix}


def _build_act(func):
    """Run create_act over func's own signature."""
    signature = inspect.signature(func)
    params = list(signature.parameters.values())
    return create_act(params[0], params[1:], signature.return_annotation, func)


def test_create_act_calls_source_function_directly():
    """Verify that act carries func's exact signature (no extra `self`) and calls func directly."""
    act = _build_act(_sample)

    result = act(data={"name": "Alice"}, prefix="ADMIN")

    assert result == {"name": "Alice", "prefix": "ADMIN"}


def test_create_act_honors_default_values():
    """Verify that act preserves func's own default values for non-main parameters."""
    act = _build_act(_sample)

    assert act(data={"name": "Bob"}) == {"name": "Bob", "prefix": "USR"}


def test_create_act_carries_func_metadata():
    """Verify that act inherits func's docstring and __name__/__qualname__/__module__ (never 'act'/None)."""
    act = _build_act(_sample)

    assert act.__doc__ == _sample.__doc__
    assert act.__name__ == "_sample"
    assert act.__qualname__ == "_sample"
    assert act.__module__ == _sample.__module__


def test_create_act_module_is_not_none():
    """Verify act is never left without a module.

    An exec-built function has __module__ = None; log_this then falls back to a logger literally
    named "unknown", so every generated action would log where no application configures anything.
    """
    assert _build_act(_sample).__module__ is not None


def test_create_act_supports_callable_without_name():
    """Verify a callable with no __name__ (functools.partial) does not break create_act.

    Such an act keeps the generated name "act"; it still carries the callable's module.
    """
    base = functools.partial(_sample, prefix="X")

    act = _build_act(base)

    assert act(data={"a": 1}) == {"a": 1, "prefix": "X"}
    assert act.__name__ == "act"
    assert act.__module__ == base.__module__


@pytest.mark.asyncio
async def test_create_act_supports_async_source_function():
    """Verify that create_act generates an async def act for an async source function."""

    async def _async_sample(data: dict, prefix: str = "USR") -> dict:
        """Async prefix-tag a data dict."""
        return {**data, "prefix": prefix}

    act = _build_act(_async_sample)

    assert inspect.iscoroutinefunction(act)

    result = await act(data={"name": "Alice"}, prefix="ADMIN")
    assert result == {"name": "Alice", "prefix": "ADMIN"}


def test_create_act_async_metadata():
    """Verify that async act preserves docstring and __name__/__qualname__/__module__ of async source function."""

    async def _async_sample(data: dict, prefix: str = "USR") -> dict:
        """Async prefix-tag a data dict."""
        return {**data, "prefix": prefix}

    act = _build_act(_async_sample)

    assert act.__doc__ == _async_sample.__doc__
    assert act.__name__ == "_async_sample"
    assert act.__qualname__ == "_async_sample"
    assert act.__module__ == _async_sample.__module__
