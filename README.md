# 🔗 `simplibs-actions`

[![PyPI](https://img.shields.io/pypi/v/simplibs-actions)](https://pypi.org/project/simplibs-actions/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-actions/blob/main/LICENSE)

**Turn ordinary functions into composable pipeline steps — chain them with `>>`, `&`, and `|`.**

A lightweight Python library for building `Action` objects: single-purpose pipeline steps
that chain into sequences, run in parallel, and fall back on failure using plain Python
operators — no pipeline framework, no DSL, no boilerplate. Any function becomes an `Action`
with one decorator, complete with type-checked construction and calls, structured
diagnostics on failure, and its own dedicated testing toolkit.

```python
from simplibs.actions import to_action

@to_action
def strip(data: str) -> str:
    return data.strip()

@to_action
def shout(data: str) -> str:
    return data.upper() + "!"

pipeline = strip() >> shout()
pipeline("  hello  ")   # -> "HELLO!"
```

> `simplibs-actions` is the pipeline layer of the ecosystem, built directly on
> [`simplibs-rules`](https://pypi.org/project/simplibs-rules/) (conditions),
> [`simplibs-validate`](https://pypi.org/project/simplibs-validate/) (`validate_call`,
> `log_this`), and [`simplibs-exception`](https://pypi.org/project/simplibs-exception/)
> (structured diagnostics) — see [Related libraries](#-related-libraries) below.

---

## 🧭 The Core Philosophy

Most pipeline/workflow tooling forces a choice: write ad-hoc chains of `if`/`try` calls
scattered through your codebase, or adopt a heavy orchestration framework with its own
configuration language. `simplibs-actions` takes neither route. An `Action` is nothing
more than a plain function with a real signature — `create_action`/`@to_action` wraps it
once, and from then on it composes with the same three operators every function in this
library composes with:

```python
step_a >> step_b >> step_c     # sequence — thread output into the next input
step_a & step_b & step_c       # parallel — same input, every branch, one flat tuple out
step_a | step_b                # fallback — try step_a; on failure, run step_b instead
```

Every generated `Action` keeps the function's own signature intact — its parameters are
still individually annotated, still individually type-checked at call time (via
`simplibs-validate`'s `validate_call`), and still individually documented, rather than
being flattened into an opaque `(*args, **kwargs)` wrapper. Because that generation is
itself a well-defined, mechanical process, the library ships its own testing tool
(`assert_action`) that audits the *entire* contract of any `Action` — this library's own
containers, or any `Action` a downstream library builds — with one function call.

---

## 📦 Installation

```bash
pip install simplibs-actions
```

---

## 🚀 Quick Start in 60 Seconds

### Level 1: Turning a function into an Action

```python
from simplibs.actions import to_action

@to_action
def double(data: int) -> int:
    return data * 2

action = double()
action(21)   # -> 42
```

### Level 2: Composing Actions

```python
from simplibs.actions import to_action

@to_action
def strip(data: str) -> str:
    return data.strip()

@to_action
def upper(data: str) -> str:
    return data.upper()

@to_action
def lower(data: str) -> str:
    return data.lower()

# Sequence: thread output into the next input
pipeline = strip() >> upper()
pipeline("  hi  ")                        # -> "HI"

# Parallel: same input, every branch, one flat tuple out
both = upper() & lower()
both("Hi")                                 # -> ("HI", "hi")

# Fallback: try the left side; on failure, run the right side instead
safe = risky_parse() | default_value(value=None)
safe(raw_input)
```

`Rule` instances from `simplibs-rules` compose the same way — `is_integer >> add_one`
verifies the rule first, then continues with the action.

### Level 3: Testing an Action

```python
from simplibs.actions.testing import assert_action

def test_double_contract(subtests):
    assert_action(
        subtests,
        double(),
        valid_values=[21],
        expected_outputs=[42],
        invalid_values=["not-a-number"],
        expected_exception_type=ValidationError,
    )
```

One call audits the full deterministic contract: valid inputs produce the right output,
invalid inputs raise the right exception, and (by default) the generated class carries
correct `_input_type`/`_output_type` introspection.

---

## 🛠️ Architecture & Package Structure

```
src/simplibs/actions/
├── base_class/              ◄── Abstract base class Action — __call__, operators, resolve_action
├── containers/               ◄── Every built-in Action
│   ├── flow_control/          ◄── guard, branch, for_each
│   ├── operators/               ◄── sequence, parallel, fallback, compose_class/ (self-flattening)
│   ├── primitives/               ◄── identity, constant
│   └── wrappers/                  ◄── lambda_action, tap, retry, log_action
├── creator/                   ◄── create_action — dynamically builds Action classes from functions
├── decorator/                  ◄── to_action — the decorator interface for create_action
└── testing/                     ◄── assert_action, assert_action_alias
```

---

## 🧩 The `Action` Class

Every action in this library — hand-written or generated — is an `Action`. It defines
the one mandatory contract (`__call__`) and provides full operator-based composition out
of the box.

```python
class Action(ABC):

    @abstractmethod
    def __call__(self, data: Any, /) -> Any:
        """Run this action over `data` and return the result."""
        raise NotImplementedError

    def then(self, next_step: Any) -> "Action":
        """Chains this action with a subsequent action, rule, or callable."""
        ...

    def __and__(self, other: Any) -> "Action":
        """Executes actions in parallel over identical input data."""
        ...

    def __or__(self, other: Any) -> "Action":
        """Fallback handling: executes `other` if this action fails."""
        ...

    @staticmethod
    def resolve_action(obj: Any) -> "Action":
        """Convert an Action, a Rule, or a plain callable into an Action instance."""
        ...
```

➡️ Full method-by-method reference: [README_ACTION](https://github.com/simplibs/simplibs-actions/blob/main/docs/README_ACTION.md)

---

## 📖 Built-in Containers

Every built-in `Action` is exposed as a `@to_action`-generated class, constructed with
its own configuration parameters and called with one main input value.

| Container       | Package        | Description                                                                                                        |
|-----------------|----------------|--------------------------------------------------------------------------------------------------------------------|
| `guard`         | `flow_control` | Hard gate — passes data through, or raises, based on a `Rule`/condition.                                           |
| `branch`        | `flow_control` | Soft conditional — runs one of two actions based on a condition, no error either way.                              |
| `for_each`      | `flow_control` | Applies an action to every item of an iterable, collecting the results.                                            |
| `sequence`      | `operators`    | Chains any number of steps left to right. Self-flattening variant: `SequenceCompose`.                              |
| `parallel`      | `operators`    | Runs N actions over the same input, returning a flat tuple of results. Self-flattening variant: `ParallelCompose`. |
| `fallback`      | `operators`    | Tries one action; on failure, runs another or returns the original data.                                           |
| `identity`      | `primitives`   | No-op — returns data unchanged.                                                                                    |
| `constant`      | `primitives`   | Ignores data, always returns a fixed value.                                                                        |
| `lambda_action` | `wrappers`     | Adapts a raw callable into an Action.                                                                              |
| `tap`           | `wrappers`     | Runs an action for its side effect; always returns the original data.                                              |
| `retry`         | `wrappers`     | Retries an action up to N times on failure.                                                                        |
| `log_action`    | `wrappers`     | Logs the data flowing through one pipeline point, unchanged.                                                       |

Every container above also ships under a more descriptive alias (`guarded_action`,
`run_in_sequence`, `pass_through`, ...) — see the full list in the containers reference.

➡️ [README_CONTAINERS](https://github.com/simplibs/simplibs-actions/blob/main/docs/README_CONTAINERS.md)

---

## 🏗️ Creating Actions

Any function becomes an `Action` two ways: the decorator (everyday use), or the
function it wraps (when you need to build one dynamically):

```python
from simplibs.actions import to_action, create_action

@to_action
def greet(data: dict, prefix: str = "Hi") -> str:
    return f"{prefix}, {data['name']}!"

# Equivalent, without the decorator:
Greet = create_action(greet)
```

`create_action` fully annotates, validates, and documents the generated class's
`__init__`/`__call__`/`act` — nothing about the source function's own signature is lost
or flattened into `(*args, **kwargs)`.

➡️ [README_CREATOR](https://github.com/simplibs/simplibs-actions/blob/main/docs/README_CREATOR.md) — `create_action` and every internal resolver/generator it's built from
➡️ [README_DECOTATOR](https://github.com/simplibs/simplibs-actions/blob/main/docs/README_DECOTATOR.md) — `to_action`, the decorator interface

---

## 🧪 Testing Utilities

`simplibs-actions` includes its own contract-testing tools, so this library's containers
— and any `Action` a downstream library builds on top of it — can be audited with one
function call instead of a hand-written test module per action:

```python
from simplibs.actions.testing import assert_action

# Full deterministic contract: valid/invalid execution, type introspection, construction guard
assert_action(
    subtests,
    my_action,
    valid_values=[...], expected_outputs=[...],
    invalid_values=[...], expected_exception_type=SomeError,
)
```

➡️ [README_TESTING_ASSERT_ACTION](https://github.com/simplibs/simplibs-actions/blob/main/docs/README_TESTING_ASSERT_ACTION.md)
➡️ [README_TESTING_ASSERT_ACTION_ALIAS](https://github.com/simplibs/simplibs-actions/blob/main/docs/README_TESTING_ASSERT_ACTION_ALIAS.md) — identity + smoke-test verification for alias objects

---

## ⚠️ Exceptions

Every diagnostic this library raises — a rejected constructor argument, a type
mismatch on call, an unsupported source-function signature — is a structured
[`simplibs.exception`](https://pypi.org/project/simplibs-exception/) card
(`ParamError`, `ValidationError`, ...), not a bare `TypeError`/`ValueError` traceback.
Validation failures on a generated `Action`'s own parameters (constructor or call) go
through [`simplibs-validate`](https://pypi.org/project/simplibs-validate/)'s
`validate_call`, using the same annotation-decomposition engine as
[`simplibs-rules`](https://pypi.org/project/simplibs-rules/).

---

## 🔗 Related libraries

* **[`simplibs-rules`](https://pypi.org/project/simplibs-rules/)** — the `Rule`
  abstraction actions compose with directly (`rule >> action`, `rule & action`, ...)
  and the engine behind `guard`'s condition checking.
* **[`simplibs-validate`](https://pypi.org/project/simplibs-validate/)** —
  `validate_call`/`log_this`, applied to every generated `Action`'s `__init__`/
  `__call__`/`act`.
* **[`simplibs-exception`](https://pypi.org/project/simplibs-exception/)** — the
  structured diagnostic cards every failure in this library raises, and the testing
  primitives (`assert_function_raises`, `assert_exception_function`) `assert_action`
  is built on.
* **[`simplibs-types`](https://pypi.org/project/simplibs-types/)** — reusable
  validated types (like `tuple_not_empty`) used as annotations on several built-in
  containers (`sequence`'s `steps`, `parallel`'s `branches`).

`simplibs-actions` is, in turn, the foundation other `simplibs` libraries build their
own domain-specific actions on top of — each ships ready-made `Action`s for its own
area alongside its standalone functions.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common engineering philosophy:

* **Dyslexia-friendly:** 
We actively minimize cognitive load. Code is atomized into small, self-contained units, 
files are named directly after the logical task they perform, 
and explanations describe *why* something is designed, not just *what* it is.
* **Programmer's Zen:** 
Nothing should be missing, and nothing should be superfluous. 
We value clean execution paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:** 
We actively anticipate edge cases and failure modes so that only safe operational paths remain. 
Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:** 
Find the most direct path to the goal in as few operational steps as possible 
without taking shortcuts on safety, readability, or completeness.
* **Code as Craft:** 
Code should be pleasant to look at, readable at a glance, and evoke structural harmony. 
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. 
We strongly believe in community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---

[▲ Back to Top](#-simplibs-actions)
