from typing import Any, Sequence
from simplibs.sentinels import UNSET, UnsetType
from simplibs.exception import ValidationError
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
    verbose: bool = True,
    intro: str = "",
    deep_check: bool = True,
) -> None:
    """Master orchestrator for testing an Action's deterministic execution contract.

    Runs the battery of checks any Action instance should satisfy — whether one of this
    library's own containers (guard, sequence, parallel, fallback, retry, tap, ...) or one
    built by a downstream user via @to_action/create_action in their own code. Mirrors the
    Facade pattern already established by simplibs-rules' assert_rule_contract and
    simplibs-exception's assert_exception_function: one call, fed with data, exercises
    every deterministic corner of the contract.

    An Action instance is directly callable, so most of the actual value-execution checking
    here is delegated straight to simplibs-exception's own testing primitives rather than
    reimplemented.

    What this deliberately does NOT do: assert anything about business-logic correctness
    beyond the exact valid/invalid value pairs supplied — no generic tool can infer that.
    It is expected to be supplied by the caller here, or covered by additional, focused
    tests written alongside this call — not folded into the generic contract.

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
            construction. Defaults to ValidationError (see assert_action_construction's
            own design notes for why). Only used when action_class + invalid_init_params
            are given.
        verbose: If True, registers individual checks as isolated pytest subtests.
        intro: Optional prefix string added to the generated subtest identity name.
        deep_check: If True, additionally verifies _input_type/_output_type declaration
            and (if action_class + invalid_init_params are given) the constructor's
            ParamError guard.
    """
    assert isinstance(action, Action), (
        f"assert_action expects an Action instance, got {type(action).__name__}."
    )

    action_name = type(action).__name__
    prefix = f"{intro}[{action_name}] " if intro == "" else f"{intro} "

    # 1. Valid inputs -> expected outputs
    if valid_values:
        if expected_outputs is None:
            raise ValueError("expected_outputs is required whenever valid_values is given.")

        assert_action_output(
            subtests,
            action,
            valid_values,
            expected_outputs,
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
every deterministic corner of the contract.

---

## 1. What Is (and Isn't) Deterministic Here

Unlike a Rule, whose is_valid()/validate()/build_exception() triad is entirely mechanical
given valid/invalid values, an Action wraps arbitrary business logic — there is no generic
way to know what output a given input SHOULD produce. So this tool splits cleanly:

* **Fully generic / mechanical** (checked automatically): the object really is an Action;
  invalid inputs actually raise; _input_type/_output_type are declared when the caller
  expects them to be; a misconfigured constructor raises ParamError.
* **Business-logic-specific** (must be supplied by the caller): what each valid input
  should produce (`expected_outputs`), and which invalid input should trigger which
  exception (`expected_exception_type`).

This is exactly the boundary discussed before building this tool: it saves the
boilerplate around calling/raising/subtesting, but the actual "is this the right answer"
truth table is inherently the caller's to provide.

## 2. Toolkit Reuse Over Reimplementation

Because an Action instance is directly callable (`action(data)`), the negative-path check
(`assert_action_raises`) is a near-direct pass-through to simplibs-exception's own
`assert_function_raises` — no raise/type-check logic is duplicated here. Only the
positive-path output check (`assert_action_output`) needed a purpose-built blade, since
none of the existing testing primitives in this ecosystem check a return value against an
expectation (they only check "does/doesn't raise").

## 3. deep_check Scope

Consistent with assert_rule_contract and assert_exception_function's own deep_check split:
the basic execution contract (valid inputs succeed with the right output, invalid inputs
raise) always runs. deep_check additionally gates:
  - _input_type/_output_type declaration checks (meaningless for actions built with
    use_validations=False, so this is opt-in rather than assumed).
  - the optional constructor ParamError sweep (opt-in via action_class +
    invalid_init_params, mirroring assert_rule_param_error's own opt-in design for
    exactly the same reason: not every action has constructor parameters worth
    misuse-testing).

## 4. Fail-Fast Type Guard

Asserts isinstance(action, Action) immediately, before any check runs — same rationale as
assert_rule_contract and assert_rule_is_valid: a misuse of this helper itself should
produce one clear error, not a cascade of confusing subtest failures deep inside a loop.

## 5. Scope Boundary — What Comes Next, Deliberately Not Here

The pipeline-level type-compatibility linter sketched earlier (inspect_pipeline,
assert_pipeline_compatible) is a different tool solving a different problem — checking
that a whole composed pipeline's steps fit together, not that one action's own contract
holds. It stays a separate, later addition; assert_action only ever looks at one action
at a time.
"""
