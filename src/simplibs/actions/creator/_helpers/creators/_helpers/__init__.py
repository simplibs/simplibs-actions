from ._describe_annotation import _describe_annotation
from .build_call_docstring import build_call_docstring
from .build_init_docstring import build_init_docstring


_DESIGN_NOTES = """
# create_action Docstring-Building Helpers Sub-Package

## Purpose
Generates short, structural docstrings for the synthesized `__call__`
and `__init__` methods `create_call`/`create_init_and_slots` produce —
each method's signature genuinely differs from the source function's
own, so neither can simply reuse `func.__doc__` the way `create_act`
does for `act` (see `create_act.py`'s own design notes for that
contrast).

## Internal Components Registry

| Component               | Type     | Description                                                                          |
| :------------------------ | :------- | :-------------------------------------------------------------------------------- |
| `_describe_annotation`     | Function | Shared, best-effort annotation-to-text conversion used by both builders below.    |
| `build_call_docstring`     | Function | Generates the docstring for the synthesized `__call__`.                           |
| `build_init_docstring`     | Function | Generates the docstring for the synthesized `__init__`.                           |
"""
