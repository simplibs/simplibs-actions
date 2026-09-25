from .create_act import create_act
from .create_call import create_call
from .create_init_and_slots import create_init_and_slots


_DESIGN_NOTES = """
# Action Factory Method Creators Sub-Package

## Purpose
Low-level code generators that dynamically synthesize class methods (`__init__`, `__call__`,
`act`) and `__slots__` attributes for new `Action` types inside `create_action`.

## Internal Components Registry

| Component               | Type     | Description                                                                     |
| :---------------------- | :------- | :------------------------------------------------------------------------------ |
| `create_act`            | Function | Synthesizes the core `act` method executing the underlying wrapped function.    |
| `create_call`           | Function | Synthesizes the `__call__` method binding runtime payload to `act`.             |
| `create_init_and_slots` | Function | Synthesizes `__init__` constructor and `__slots__` tuple for state storage.     |
"""