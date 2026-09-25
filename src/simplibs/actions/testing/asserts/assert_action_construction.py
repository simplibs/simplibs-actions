from typing import Any, Callable, Sequence
from simplibs.exception import ValidationError
from simplibs.exception.testing import assert_function_raises
# Outers
from ...base_class import Action


def assert_action_construction(
    subtests: Any,
    action_class: type[Action],
    invalid_init_params: list[tuple[tuple[Any, ...], dict[str, Any]]],
    *,
    expected_exception_type: type[Exception] | Sequence[type[Exception] | None] = ValidationError,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that the action class constructor rejects bad configuration with an exception.

    Mirrors simplibs-rules' assert_rule_param_error: sweeps a list of deliberately bad
    (args, kwargs) construction attempts and confirms each one raises the expected exception.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        action_class: The Action subclass under test — called as
            `action_class(*args, **kwargs)` for each entry in invalid_init_params.
        invalid_init_params: A list of (args, kwargs) pairs, each expected to raise on
            construction.
        expected_exception_type: Asserted against each exception raised on construction.
            Defaults to ValidationError, since a wrong-typed constructor kwarg is rejected
            by the synthesized __init__'s own validate_call wrapping (when
            use_validations=True) — not by a hand-written ParamError guard. Can be a
            single exception class (applied to every entry) or a Sequence matching
            invalid_init_params index-by-index (use None to skip specific indices).
        verbose: Enables isolated pytest subtest tracking for each checked call.
        intro: Optional prefix string added to generated subtest identity names.

    Raises:
        ValueError: If a Sequence expected_exception_type doesn't match invalid_init_params
            in length.
    """
    is_sequence = (
        isinstance(expected_exception_type, Sequence)
        and not isinstance(expected_exception_type, type)
    )

    if is_sequence and len(expected_exception_type) != len(invalid_init_params):
        raise ValueError(
            "expected_exception_type sequence must have the same length as invalid_init_params."
        )

    def make_invalid_call(
        call_args: tuple[Any, ...],
        call_kwargs: dict[str, Any],
    ) -> Callable[[], None]:
        def _call() -> None:
            action_class(*call_args, **call_kwargs)
        return _call

    for index, (args, kwargs) in enumerate(invalid_init_params):
        current_type = expected_exception_type[index] if is_sequence else expected_exception_type

        assert_function_raises(
            subtests,
            make_invalid_call(args, kwargs),
            invalid_params=(),
            exception_type=current_type,
            verbose=verbose,
            intro=f"{intro}test_action_construction_#index_{index}_",
        )


_DESIGN_NOTES = """
# assert_action_construction (Constructor Guard Contract Blade)

## Purpose
Verifies that an action class's synthesized __init__ rejects invalid configuration
arguments — the Action-level counterpart to simplibs-rules' assert_rule_param_error,
reusing the exact same closure-binding technique and the same underlying
assert_function_raises primitive.

## Why ValidationError, Not ParamError, Is the Default
An earlier revision hardcoded exception_type=ParamError here, copying
assert_rule_param_error's assumption verbatim. That assumption doesn't transfer: a Rule
constructor validates its OWN configuration by hand and raises ParamError for that. An
Action's synthesized __init__, when use_validations=True, is wrapped in @validate_call
exactly like every other generated method — a wrong-typed kwarg is caught by that
wrapping and raises ValidationError, the same way a wrong-typed call argument does.
ParamError is reserved for create_action's own dedicated misuse guards (e.g. passing an
already-instantiated Action into create_action), not for per-parameter type checking on
a normally-constructed instance. expected_exception_type is still overridable for the
rare action whose __init__ does its own hand-written validation instead.

## Why This Is Opt-In (action_class + invalid_init_params), Not Always Run
Not every action has constructor parameters worth misuse-testing — plenty of
containers (identity, tap wrapping a no-arg action, ...) take no configuration
parameters at all, so there is nothing to sweep. Mirroring assert_rule_contract's
own opt-in design for exactly the same reason (see assert_rule_param_error's
_DESIGN_NOTES), this blade only runs from assert_action when the caller explicitly
supplies both action_class and a non-empty invalid_init_params list.

## Class, Not Instance
Unlike every other assert_action_* blade, this one operates on the action CLASS
rather than an already-constructed instance — construction is exactly the thing
under test here, so there is nothing to call it on beforehand.
"""
