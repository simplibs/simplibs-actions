import pytest
from simplibs.exception.exceptions import ParamError
from simplibs.actions.containers import lambda_action


def test_lambda_action_executes_raw_callable():
    # Arrange
    strip_func = lambda s: s.strip()
    action = lambda_action(func=strip_func)

    # Act
    result = action("  hello world  ")

    # Assert
    assert result == "hello world"


def test_lambda_action_works_with_builtin_functions():
    # Arrange
    action = lambda_action(func=len)

    # Act
    result = action([1, 2, 3, 4, 5])

    # Assert
    assert result == 5


def test_lambda_action_direct_call_curried():
    # Arrange & Act
    result = lambda_action(func=str.upper)("python")

    # Assert
    assert result == "PYTHON"


def test_lambda_action_sync_call_raises_for_async_function():
    """Verify that calling __call__ synchronously on an async function raises ParamError."""

    async def _async_strip(s: str) -> str:
        return s.strip()

    action = lambda_action(func=_async_strip)

    with pytest.raises(ParamError):
        action("  hello world  ")


@pytest.mark.asyncio
async def test_lambda_action_acall_supports_async_function():
    """Verify that acall directly awaits an async coroutine function."""

    async def _async_strip(s: str) -> str:
        return s.strip()

    action = lambda_action(func=_async_strip)

    result = await action.acall("  hello world  ")
    assert result == "hello world"


@pytest.mark.asyncio
async def test_lambda_action_acall_bridges_sync_function_via_thread():
    """Verify that acall safely runs a sync function via to_thread worker."""
    sync_func = lambda s: s.upper()
    action = lambda_action(func=sync_func)

    result = await action.acall("python")
    assert result == "PYTHON"


def test_lambda_action_is_async_property():
    """Verify that lambda_action instances expose a dynamic is_async property."""
    sync_action = lambda_action(func=lambda x: x)
    assert sync_action.is_async is False

    async def _async_func(x):
        return x

    async_action = lambda_action(func=_async_func)
    assert async_action.is_async is True