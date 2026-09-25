from typing import Any
# Outers
from ...constants import EMPTY


def _describe_annotation(annotation: Any) -> str | None:
    """Best-effort, human-readable name for an annotation, or `None` if
    there isn't one (`EMPTY`) to describe.

    Args:
        annotation: A parameter's or return value's raw annotation, as
            returned by `inspect.signature`.

    Returns:
        `annotation.__name__` when available (plain types, most typing
        generics); otherwise `str(annotation)`; `None` if `annotation`
        is `EMPTY`.
    """
    if annotation is EMPTY:
        return None
    return getattr(annotation, "__name__", None) or str(annotation)


_DESIGN_NOTES = """
# _describe_annotation — shared, best-effort annotation-to-text helper

## Purpose
`build_call_docstring` and `build_init_docstring` both need the same
thing: turn a raw annotation into a short, readable label for a
generated docstring line — without needing to know or care what kind of
annotation it actually is. This is the one shared place that logic
lives, rather than being duplicated in each caller.

## Why "best-effort", not a proper type-formatting engine
`annotation.__name__` covers the common cases well — plain types (`int`,
`str`, a custom class) and most typing generics (`list[int].__name__` is
`"list"` via `types.GenericAlias` proxying). It is deliberately lossy for
anything more elaborate: `list[int]` renders as just `"list"`, not
`"list[int]"`; a `Union`/`|` type or an `Annotated[...]` construct falls
through to `str(annotation)`, which is readable but verbose. A fully
faithful renderer would need to special-case every shape `IsTyping`
itself understands — disproportionate effort for what is, in the end,
one line of hover text, not a type-checking surface. Good enough here
means "better than nothing," not "as precise as the real annotation."

## Why leading underscore, unlike its two callers
This helper is never meant to be imported or used outside
`build_call_docstring`/`build_init_docstring` — it has no independent
identity as a public building block the way `resolve_param` or
`create_act` do. The leading underscore signals that directly, even
though it lives in its own file for the same "one thing per file"
reasons as the rest of this codebase.
"""
