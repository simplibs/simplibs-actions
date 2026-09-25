from typing import Any, Callable, overload, ParamSpec, Concatenate, TypeVar
# Outers
from ..creator import create_action
from ..base_class import Action
# Annotations
P = ParamSpec("P")
R = TypeVar("R")
DataT = TypeVar("DataT")


@overload
def to_action(
    func: Callable[Concatenate[DataT, P], R], /
) -> Callable[P, Action]: ...


@overload
def to_action(
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
) -> Callable[[Callable[Concatenate[DataT, P], R]], Callable[P, Action]]: ...


def to_action(
    func: Callable[..., Any] | None = None,
    *,
    main_param: str | None = None,
    use_validations: bool = True,
    use_logging: bool = True,
    class_name: str | None = None,
) -> Any:
    """Decorator: turns an ordinary function into an `Action` subclass.

    Usable bare (`@to_action`) or configured (`@to_action(...)`).

    Args:
        func: The source function (passed automatically for the bare
            `@to_action` form).
        main_param: Name of the parameter to use as the main
            pipeline input.
        use_validations: Whether to apply `validate_call` to the
            generated methods.
        use_logging: Whether to apply `log_this` to the `act` method.
        class_name: Custom name for the generated Action class.

    Example:
        @to_action
        def process_user(data: dict, prefix: str = "USR") -> dict:
            ...

        # process_user is now an Action class
        action_instance = process_user(prefix="ADMIN")
        result = action_instance({"name": "Alice"})
    """

    # 1. Define the inner decorator that performs the actual conversion
    def decorator(fn: Callable[..., Any]) -> Callable[..., Action]:
        return create_action(
            fn,
            main_param=main_param,
            use_validations=use_validations,
            use_logging=use_logging,
            class_name=class_name,
        )

    # 2. Bare-decorator form (@to_action, no parentheses) — apply directly
    if func is not None:
        return decorator(func)

    # 3. Parametrized form (@to_action(...)) — return the decorator itself
    return decorator


_DESIGN_NOTES = """
# to_action — decorator entry point for create_action

## Why this exists alongside create_action, not instead of it
`create_action(func, ...)` is the real implementation — `to_action` is a
thin decorator-shaped front door over it, supporting both
`@to_action` and `@to_action(main_param=..., ...)` via the
`func is None` branch. Nothing here duplicates `create_action`'s logic;
`decorator()` just forwards every argument through unchanged.

## Why this file carries its own `@overload` pair, not just create_action's
`create_action` already has a `Concatenate`/`ParamSpec` overload giving
callers an accurate `Callable[P, Action]` hover instead of the generic
`type[Action]`. `to_action` needs its own pair because it is called
differently: bare (`@to_action`, a single positional function argument,
`/`-marked to keep it strictly positional) or parametrized
(`@to_action(...)`, no function yet, returning a decorator). A single
overload could not describe both shapes — the first overload matches the
bare form and returns `Callable[P, Action]` directly; the second matches
the parametrized form and returns a decorator function
(`Callable[[Callable[Concatenate[DataT, P], R]], Callable[P, Action]]`)
that itself produces `Callable[P, Action]` once applied. Both ultimately
resolve to the exact same hover quality `create_action` provides on its
own — this file's job is purely to preserve that through either calling
convention.

## Why `func: ... | None = None` in the real implementation
The real (non-overloaded) signature must accept `None` for `func` to
support the parametrized form at runtime — the overloads describe the
two valid call shapes precisely, but the actual implementation has to
handle the union of both, hence the runtime-only `if func is not None:`
branch deciding which behavior to run.
"""
