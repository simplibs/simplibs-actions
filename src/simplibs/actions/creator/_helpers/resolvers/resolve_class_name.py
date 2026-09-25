from typing import Any, Callable


def resolve_class_name(
    func: Callable[..., Any],
    class_name: str | None,
) -> str:
    """Resolve the generated class's name.

    Args:
        func: The source function.
        class_name: An explicit name to use instead of deriving
            one from `func.__name__`.

    Returns:
        `class_name`, if given; otherwise `func.__name__`
        converted from `snake_case` to `PascalCase`.
    """

    # 1. Use the override class name if explicitly provided
    if class_name is not None:
        return class_name

    # 2. Derive a PascalCase class name from the snake_case function name
    return "".join(
        part.capitalize()
        for part in func.__name__.split("_")
    )


_DESIGN_NOTES = """
# resolve_class_name — dynamic Action class naming resolver

## Purpose
Determines the name of the dynamically synthesized `Action` subclass
`create_action` builds. For an ordinary `def guard(data, rule): ...`,
`func.__name__` is a perfectly good source (`"guard"` -> `"Guard"`).

## Why `class_name` exists at all
It breaks down for anything without a meaningful `__name__` — a lambda's
`__name__` is the literal string `"<lambda>"`, which converts to garbage
(not even valid syntax as a class name), and a `functools.partial` has no
`__name__` attribute at all. `class_name` is not a convenience
for those cases — it is the only way `create_action` can be used at all.

## Why plain `str.split("_")` + `str.capitalize()`, not a regex
`snake_case` function names in this codebase are, by convention, plain
lowercase words joined by single underscores — no digits-glued-to-letters
edge cases, no leading/trailing underscores. A regex-based converter
would handle more exotic input, but nothing in this codebase produces
that input; the simple split/capitalize is exactly as capable as it
needs to be, and is far easier to read than a regex would be for the
same result.
"""
