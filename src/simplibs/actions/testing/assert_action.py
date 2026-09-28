import inspect
from typing import Any, Sequence
from simplibs.sentinels import UNSET, UnsetType
from simplibs.exception import ParamError, ValidationError
# Outers
from ..base_class import Action
# Inners
from .asserts.assert_action_output import assert_action_output
from .asserts.assert_action_raises import assert_action_raises
from .asserts.assert_action_io_types import assert_action_io_types
from .asserts.assert_action_construction import assert_action_construction


def assert_action(
    subtests: Any,
    action: Action,
    *,
    valid_values: list[Any] | None = None,
    expected_outputs: list[Any] | None = None,
    invalid_values: list[Any] | None = None,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] | None = None,
    expected_input_type: Any | UnsetType = UNSET,
    expected_output_type: Any | UnsetType = UNSET,
    action_class: type[Action] | None = None,
    invalid_init_params: list[tuple[tuple[Any, ...], dict[str, Any]]] | None = None,
    construction_exception_type: type[Exception] | Sequence[type[Exception] | None] = ValidationError,
    is_async: bool | None = None,
    verbose: bool = True,
    intro: str = "",
    deep_check: bool = True,
) -> None:
    """Master orchestrator for testing an Action's deterministic execution contract.

    Runs the battery of checks any Action instance should satisfy — whether one of this
    library's own containers (guard, sequence, parallel, fallback, retry, tap, ...) or one
    built by a downstream user via @to_action/create_action in their own code. Supports
    both sync and native async def actions.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        action: The Action instance under test.
        valid_values: Inputs expected to be accepted by the action.
        expected_outputs: Outputs expected for each entry in valid_values, index-matched
            (required whenever valid_values is given).
        invalid_values: Inputs expected to raise when passed to the action.
        expected_exception_type: If provided, asserted against each exception raised for
            invalid_values. Can be a single exception class or a Sequence matching
            invalid_values index-by-index (use None to skip specific indices).
        expected_input_type: If provided (not UNSET), asserted against the action class's
            declared _input_type. Only checked when deep_check is True.
        expected_output_type: If provided (not UNSET), asserted against the action class's
            declared _output_type. Only checked when deep_check is True.
        action_class: Optional — the Action subclass itself (as opposed to `action`, an
            instance of it). Only needed together with invalid_init_params.
        invalid_init_params: Optional list of (args, kwargs) pairs, each expected to raise
            on construction via action_class(*args, **kwargs). Requires action_class, and
            is only run when deep_check is True.
        construction_exception_type: Asserted against each exception raised on
            construction. Defaults to ValidationError. Only used when action_class +
            invalid_init_params are given.
        is_async: Explicit flag specifying whether the action is async. If None, auto-detected.
        verbose: If True, registers individual checks as isolated pytest subtests.
        intro: Optional prefix string added to the generated subtest identity name.
        deep_check: If True, additionally verifies _input_type/_output_type declaration
            and constructor parameter validation.
    """
    assert isinstance(action, Action), (
        f"assert_action expects an Action instance, got {type(action).__name__}."
    )

    action_name = type(action).__name__
    prefix = f"{intro}[{action_name}] " if intro == "" else f"{intro} "

    if is_async is None:
        is_async = getattr(action, "is_async", False)

    # 1. Valid inputs -> expected outputs
    if valid_values:
        if expected_outputs is None:
            raise ValueError("expected_outputs is required whenever valid_values is given.")

        assert_action_output(
            subtests,
            action,
            valid_values,
            expected_outputs,
            is_async=is_async,
            verbose=verbose,
            intro=prefix,
        )

    # 2. Invalid inputs -> expected exceptions
    if invalid_values:
        assert_action_raises(
            subtests,
            action,
            invalid_values,
            expected_exception_type=expected_exception_type,
            is_async=is_async,
            verbose=verbose,
            intro=prefix,
        )

    # 3. Optional deep structural checks
    if deep_check:
        assert_action_io_types(
            subtests,
            action,
            expected_input_type=expected_input_type,
            expected_output_type=expected_output_type,
            verbose=verbose,
            intro=prefix,
        )

        # Sync-misuse guard check for async actions
        if is_async and valid_values:
            assert_action_raises(
                subtests,
                action,
                [valid_values[0]],
                expected_exception_type=ParamError,
                is_async=False,
                verbose=verbose,
                intro=f"{prefix}[sync_misuse_guard] ",
            )

        if action_class is not None and invalid_init_params:
            assert_action_construction(
                subtests,
                action_class,
                invalid_init_params,
                expected_exception_type=construction_exception_type,
                verbose=verbose,
                intro=prefix,
            )


_DESIGN_NOTES = """
# assert_action (Master Action Contract Orchestrator)

## Purpose
The single entry point for testing any Action instance — this library's own containers
(guard, sequence, parallel, fallback, retry, tap, ...) and, equally, any action a
downstream user builds via @to_action/create_action in their own code. Mirrors the
Facade pattern already established by assert_rule_contract (simplibs-rules) and
assert_exception_function (simplibs-exception): one call, fed with data, exercises
every deterministic corner of the contract. Fully supports both synchronous actions
and native async def actions.

---

## 1. What Is (and Isn't) Deterministic Here

Unlike a Rule, whose is_valid()/validate()/build_exception() triad is entirely mechanical
given valid/invalid values, an Action wraps arbitrary business logic — there is no generic
way to know what output a given input SHOULD produce. So this tool splits cleanly:

* **Fully generic / mechanical** (checked automatically): the object really is an Action;
  invalid inputs actually raise; _input_type/_output_type are declared when the caller
  expects them to be; a misconfigured constructor raises ValidationError/ParamError.
* **Business-logic-specific** (must be supplied by the caller): what each valid input
  should produce (`expected_outputs`), and which invalid input should trigger which
  exception (`expected_exception_type`).

This saves the boilerplate around calling, raising, subtesting, and async event-loop
orchestration, while leaving the actual "is this the right answer" truth table
inherently to the caller to provide.

## 2. Sync & Native Async Dual Support

With native async support (`acall`), `assert_action` auto-detects whether the target
action is async (or respects the explicit `is_async` override). Both positive-path outputs
(`assert_action_output`) and negative-path exceptions (`assert_action_raises`) transparently
execute through the async channel (`acall`) when testing an async action, isolating
event-loop execution cleanly via `asyncio.run`.

## 3. Sync-Misuse Guard Verification for Async Actions

Calling an async action directly via standard synchronous `__call__` (`action(data)`) is a
contract violation that must raise `ParamError` (via `raise_async_action_requires_acall_error`).
When `deep_check` is enabled and `valid_values` are provided for an async action, `assert_action`
automatically verifies this misuse guard against a sample input (`is_async=False`), ensuring
the Action enforces its async boundary strictly.

## 4. Toolkit Reuse Over Reimplementation

Because negative execution paths are wrapped inside zero-arg callable closures, the
negative-path check (`assert_action_raises`) relies directly on `simplibs-exception`'s own
`assert_function_raises` primitive — no raise/type-check logic is duplicated here.

## 5. deep_check Scope

Consistent with assert_rule_contract and assert_exception_function's own deep_check split:
the basic execution contract (valid inputs succeed with the right output, invalid inputs
raise) always runs. deep_check additionally gates:
  - _input_type/_output_type declaration checks (meaningless for actions built with
    use_validations=False, so this is opt-in rather than assumed).
  - the optional constructor parameter sweep (opt-in via action_class +
    invalid_init_params, mirroring assert_rule_param_error's own opt-in design for
    exactly the same reason: not every action has constructor parameters worth
    misuse-testing).

## 6. Fail-Fast Type Guard

Asserts isinstance(action, Action) immediately, before any check runs — same rationale as
assert_rule_contract and assert_rule_is_valid: a misuse of this helper itself should
produce one clear error, not a cascade of confusing subtest failures deep inside a loop.

## 7. Scope Boundary — What Comes Next, Deliberately Not Here

The pipeline-level type-compatibility linter (inspect_pipeline, assert_pipeline_compatible)
is a different tool solving a different problem — checking that a whole composed
pipeline's steps fit together, not that one action's own contract holds. It stays a
separate, later addition; assert_action only ever looks at one action at a time.
"""