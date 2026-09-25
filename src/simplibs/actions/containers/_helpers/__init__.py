from .as_action import as_action
from .as_predicate import as_predicate


_DESIGN_NOTES = """
# Action Container Helpers Sub-Package

## Purpose
Internal resolution and adaptation helpers used across action containers to normalize
arbitrary runnables into unified `Action` instances and condition inputs into executable predicates.

## Internal Components Registry

| Component      | Type     | Description                                                                     |
| :------------- | :------- | :------------------------------------------------------------------------------ |
| `as_action`    | Alias    | Direct shorthand for `Action.resolve_action` to normalize runnables to Actions. |
| `as_predicate` | Function | Normalizes `Rule` instances or callables into unified boolean-returning methods.|
"""