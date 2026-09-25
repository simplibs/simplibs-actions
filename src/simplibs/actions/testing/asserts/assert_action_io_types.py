from typing import Any
from simplibs.sentinels import UNSET, UnsetType
from simplibs.exception.testing import maybe_subtest
# Outers
from ...base_class import Action


def assert_action_io_types(
    subtests: Any,
    action: Action,
    *,
    expected_input_type: Any | UnsetType = UNSET,
    expected_output_type: Any | UnsetType = UNSET,
    verbose: bool = True,
    intro: str = "",
) -> None:
    """Verify that the action's class exposes _input_type/_output_type, and optionally match them.

    Only meaningful for actions built with use_validations=True (create_action's default).
    An action deliberately built with use_validations=False has no _input_type/_output_type
    at all — this blade treats their absence as a plain assertion failure rather than
    silently skipping, since a caller invoking assert_action's deep_check has implicitly
    asserted that type introspection should be available for this particular action.

    Args:
        subtests: The native pytest subtests fixture manager instance.
        action: The Action instance under test.
        expected_input_type: If provided (not UNSET), asserted against
            type(action)._input_type.
        expected_output_type: If provided (not UNSET), asserted against
            type(action)._output_type.
        verbose: Enables isolated pytest subtest tracking for each checked field.
        intro: Optional prefix string added to generated subtest identity names.
    """
    action_cls = type(action)

    with maybe_subtest(subtests, name=f"{intro}test_input_type_declared", verbose=verbose):
        assert hasattr(action_cls, "_input_type"), (
            f"{action_cls.__name__} has no _input_type — was it built with use_validations=True?"
        )

    with maybe_subtest(subtests, name=f"{intro}test_output_type_declared", verbose=verbose):
        assert hasattr(action_cls, "_output_type"), (
            f"{action_cls.__name__} has no _output_type — was it built with use_validations=True?"
        )

    if expected_input_type is not UNSET:
        with maybe_subtest(subtests, name=f"{intro}test_input_type_matches", verbose=verbose):
            assert action_cls._input_type == expected_input_type, (
                f"Expected _input_type {expected_input_type!r}, got {action_cls._input_type!r}."
            )

    if expected_output_type is not UNSET:
        with maybe_subtest(subtests, name=f"{intro}test_output_type_matches", verbose=verbose):
            assert action_cls._output_type == expected_output_type, (
                f"Expected _output_type {expected_output_type!r}, got {action_cls._output_type!r}."
            )


_DESIGN_NOTES = """
# assert_action_io_types (Type Introspection Contract Blade)

## Purpose
Verifies the static type-introspection surface create_action exposes when
use_validations=True: the _input_type/_output_type class attributes that a downstream
tool (like the future pipeline-compatibility linter) would rely on.

## Why This Is Opt-In Content, Not Always Silently Skipped
An action built with use_validations=False legitimately has no _input_type/_output_type.
Rather than treating their absence as "not applicable, skip quietly", this blade treats
it as a failure — because assert_action only calls this blade at all when deep_check is
True, which the caller controls. If someone runs deep_check against a use_validations=False
action, that mismatch (expecting introspection where none exists) is exactly the kind of
thing worth surfacing loudly rather than swallowing.

## UNSET Sentinel Reuse
Uses simplibs-sentinels' UNSET (rather than None) to distinguish "not checked" from
"expected to be None" — consistent with how UNSET is used throughout
simplibs-exception's own testing primitives (assert_exception_fields, etc.).
"""
