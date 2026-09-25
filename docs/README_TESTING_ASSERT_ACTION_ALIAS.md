# 🧪 `assert_action_alias`

**Identity & Smoke-Test Verification for Alias Objects**

`assert_action_alias` is the dedicated helper for testing the many pure aliases this
library ships (`run_in_sequence`, `run_in_parallel`, `try_or_fallback`,
`guarded_action`, `pass_through`, ...). An alias here is never a wrapper, decorator, or
proxy — it's a direct reference assignment (`run_in_sequence = sequence`) — so testing
one requires verifying only two narrow facts, not re-running the canonical
implementation's own full contract battery.

## 💡 Table of Contents:
> * [⚙️ Architectural Principles](#-architectural-principles)
> * [🔍 Quick Usage Examples](#-quick-usage-examples)
> * [🛠️ Configuration & Parameters](#-configuration--parameters)
> * [📖 Real-World Example](#-real-world-example)

[⬅️ Back to main README](../README.md#-testing-utilities)

---

## ⚙️ Architectural Principles

* **The Two Invariants of an Alias:**
  1. **Memory identity** (`alias is canonical`) — proves zero overhead, zero
     wrapping, and 100% behavioral identity. If this passes, any test covering
     `canonical` transitively covers `alias`.
  2. **End-to-end smoke test** — one execution path confirming the alias module is
     cleanly importable, correctly exposed, and callable in a real pipeline context.
* **Atomic, Deliberately Lightweight:** This function does not test edge cases,
  invalid inputs, or pipeline combinations — those belong exclusively to the
  canonical implementation's own test file (e.g. `sequence`'s full contract lives in
  `test_sequence.py`, not here).
* **Optional Smoke Test:** The identity check always runs. The execution smoke test
  only runs when both `sample_action` and `expected_output` are supplied — an alias
  whose canonical form needs no construction arguments to demonstrate (rare in this
  library) can be checked on identity alone.

[▲ Back to Top](#-assert_action_alias)

---

## 🔍 Quick Usage Examples

```python
# 1. Full check: identity + smoke test
assert_action_alias(
    subtests,
    run_in_sequence, sequence,
    sample_action=run_in_sequence(steps=(strip, upper)),
    sample_input="  hi  ",
    expected_output="HI",
)

# 2. Identity only — no smoke test
assert_action_alias(subtests, pass_through, identity)
```

[▲ Back to Top](#-assert_action_alias)

---

## 🛠️ Configuration & Parameters

### Mandatory Parameters

* **`subtests`** (`Any`): The native pytest subtests fixture manager instance.
* **`alias`** (`Any`): The alias object under test (e.g. `run_in_sequence`).
* **`canonical`** (`Any`): The canonical implementation it should be identical to
  (e.g. `sequence`).

### Optional Parameters

* **`sample_action`** (`Action | None`): An `Action` constructed via `alias`, used for
  the smoke test.
* **`sample_input`** (`Any`): Data passed to `sample_action` during the smoke test.
* **`expected_output`** (`Any`, default `UNSET`): Expected result of
  `sample_action(sample_input)`. The smoke test only runs when this **and**
  `sample_action` are both given.
* **`verbose`** (`bool`, default `True`): Registers each check as an isolated pytest
  subtest.
* **`intro`** (`str`, default `""`): Prefix for generated subtest names.

```python
def assert_action_alias(
    subtests: Any,
    alias: Any,
    canonical: Any,
    *,
    sample_action: Action | None = None,
    sample_input: Any = None,
    expected_output: Any = UNSET,
    verbose: bool = True,
    intro: str = "",
) -> None: ...
```

**Under the hood:**

```python
# 1. Structural identity check
assert alias is canonical

# 2. Optional end-to-end smoke test
if sample_action is not None and expected_output is not UNSET:
    result = sample_action(sample_input)
    assert result == expected_output
```

[▲ Back to Top](#-assert_action_alias)

---

## 📖 Real-World Example

```python
"""Tests for the run_in_sequence alias."""
from simplibs.actions.containers.operators.aliases import run_in_sequence
from simplibs.actions.containers.operators import sequence

from simplibs.actions.testing import assert_action_alias


def test_run_in_sequence_is_a_true_alias(subtests):
    """Verify run_in_sequence is identical to sequence and works end to end."""
    assert_action_alias(
        subtests,
        run_in_sequence, sequence,
        sample_action=run_in_sequence(steps=(str.strip, str.upper)),
        sample_input="  hi  ",
        expected_output="HI",
        verbose=False,
    )
```

One call, per alias, replaces a hand-written `is` assertion plus a separate smoke
test — repeated across every alias this library (or a downstream user) exposes, it's
what keeps every alias provably in sync with its canonical implementation.

[▲ Back to Top](#-assert_action_alias)

---

[⬅️ Back to main README](../README.md#-testing-utilities)
