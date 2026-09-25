from .resolve_class_name import resolve_class_name
from .resolve_param import resolve_param
from .unwrap_log_this_and_validate_call import unwrap_log_this_and_validate_call


_DESIGN_NOTES = """
# Action Factory Resolvers Sub-Package

## Purpose
Inspection helpers that analyze input signatures and source functions to
resolve dynamic Action class names, separate payload parameters from
initialization parameters, and normalize a source function down to the
one truly underneath any pre-existing `@validate_call`/`@log_this`
decoration.

## Internal Components Registry

| Component                          | Type     | Description                                                                       |
| :---------------------------------- | :------- | :---------------------------------------------------------------------------------|
| `resolve_class_name`                | Function | Resolves dynamic class name via override or `snake_case` -> `PascalCase` rules.   |
| `resolve_param`                     | Function | Separates signature into primary main payload input and auxiliary init params.    |
| `unwrap_log_this_and_validate_call` | Function | Peels off any pre-existing `@validate_call`/`@log_this` layers, any order/depth.  |
"""
