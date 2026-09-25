# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-09-25

### ✨ Added

#### Core `Action` Class

* `Action` — abstract base class for every pipeline step; `__call__` is its sole
  abstract method
* Operator-based composition: `>>`/`then` (sequence), `&` (parallel), `|` (fallback),
  plus their reflected counterparts (`__rrshift__`, `__rand__`, `__ror__`) so a
  `simplibs-rules` `Rule` composes directly with an `Action` on either side
  (`rule >> action`, `rule & action`, ...)
* `Action.resolve_action` — the single normalization point converting an `Action`, a
  `Rule`, or any plain callable into a real `Action` instance
* `__not_rule__` hook, preventing `Rule.__and__`/`__or__` from silently absorbing an
  `Action` as a plain boolean predicate

#### Dynamic Action Construction

* `create_action()` — builds a fully-typed `Action` subclass from an ordinary function
  via `exec`-based codegen, mirroring `dataclasses`' own `__init__` synthesis technique
* `@to_action` — the decorator front door over `create_action`, usable bare
  (`@to_action`) or parametrized (`@to_action(main_param=..., class_name=..., ...)`)
* `use_validations` — wraps the generated `__init__`/`__call__`/`act` with
  `simplibs-validate`'s `validate_call`, and exposes `_input_type`/`_output_type`
  introspection on the resulting class
* `use_logging` — wraps `act` with `simplibs-validate`'s `log_this` for
  entry/exit/timing/exception logging
* `main_param` — selects any parameter (not just the first) as the pipeline's main
  input; every other parameter becomes constructor configuration
* Automatic peeling of any pre-existing `@validate_call`/`@log_this` layers on the
  source function, at any depth or interleaving order, before re-wrapping
  (`unwrap_log_this_and_validate_call`)
* Structured, `simplibs-exception`-style diagnostics for every misuse case:
  unsupported parameter kinds (`*args`/`**kwargs`/positional-only), missing or
  unsupported type annotations, an already-instantiated `Action` passed back into
  `create_action`, and an unresolvable `main_param` name

#### Built-in Containers

* **Flow control**: `guard` (hard gate), `branch` (soft conditional), `for_each`
  (per-item mapping over an iterable)
* **Operators**: `sequence`, `parallel`, `fallback`, plus their self-flattening
  variants `SequenceCompose`/`ParallelCompose` (what `>>`/`&` actually build under the
  hood, keeping chained compositions flat instead of nesting)
* **Primitives**: `identity`, `constant`
* **Wrappers**: `lambda_action`, `tap`, `retry`, `log_action`
* Descriptive aliases for every container above (`guarded_action`, `conditional_action`,
  `apply_to_each`, `run_in_sequence`, `run_in_parallel`, `try_or_fallback`,
  `pass_through`, `replace_with`, `callable_action`, `run_side_effect`,
  `retry_on_failure`, `log_step`) — each a true identity alias (`alias = canonical`),
  never a wrapper or copy

#### Testing Ecosystem

* `simplibs.actions.testing` — a dedicated testing package, mirroring
  `simplibs-exception`'s and `simplibs-rules`' own testing toolkits
* `assert_action()` — master orchestrator auditing any `Action`'s deterministic
  execution contract in one call: valid-input output correctness, invalid-input raise
  behavior, `_input_type`/`_output_type` declaration, and (opt-in) constructor
  misuse guarding
* `assert_action_output`, `assert_action_raises`, `assert_action_io_types`,
  `assert_action_construction` — the individually reusable blades behind
  `assert_action`
* `assert_action_alias()` — lightweight identity + end-to-end smoke-test verification
  for every alias in this library

#### Dependencies

* `simplibs-rules` — the `Rule` abstraction actions compose with directly, and the
  engine behind `guard`'s condition checking
* `simplibs-validate` — `validate_call`/`log_this`, applied to every generated
  `Action`
* `simplibs-exception` — structured diagnostic cards, and the testing primitives
  `assert_action` is built on
* `simplibs-types` — `tuple_not_empty`, used as the annotation on `sequence`'s
  `steps` and `parallel`'s `branches`

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)
