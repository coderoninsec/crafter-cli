import os
from typing import Any, Callable, Iterable

CheckHandler = Callable[[dict[str, Any], str], tuple[bool, str | None]]


def _normalize_output(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    return str(output)


def _get_check_type(check: Any) -> str | None:
    if not isinstance(check, dict):
        return None
    check_type = check.get("type")
    return check_type if isinstance(check_type, str) and check_type.strip() else None


def _check_always_pass(check: dict[str, Any], output: str) -> tuple[bool, str | None]:
    return True, None


def _check_output_equals(check: dict[str, Any], output: str) -> tuple[bool, str | None]:
    expected = check.get("value")
    if expected is None:
        return False, "Check 'output_equals' requires 'value'"
    if output.strip() == str(expected).strip():
        return True, None
    return False, f"Output must equal {str(expected).strip()!r}"


def _check_output_not_equals(
    check: dict[str, Any], output: str
) -> tuple[bool, str | None]:
    expected = check.get("value")
    if expected is None:
        return False, "Check 'output_not_equals' requires 'value'"
    if output.strip() != str(expected).strip():
        return True, None
    return False, f"Output must not equal {str(expected).strip()!r}"


def _check_output_contains(
    check: dict[str, Any], output: str
) -> tuple[bool, str | None]:
    expected = check.get("value")
    if expected is None:
        return False, "Check 'output_contains' requires 'value'"
    needle = str(expected)
    if needle in output:
        return True, None
    return False, f"Output must contain {needle!r}"


def _check_output_length_greater(
    check: dict[str, Any], output: str
) -> tuple[bool, str | None]:
    minimum = check.get("value")
    try:
        threshold = int(minimum)
    except (TypeError, ValueError):
        return False, "Check 'output_length_greater' requires numeric 'value'"

    if len(output) > threshold:
        return True, None
    return False, f"Output length must be greater than {threshold}"


def _check_file_contains(check: dict[str, Any], output: str) -> tuple[bool, str | None]:
    path = check.get("path")
    expected = check.get("content")

    if not path:
        return False, "Check 'file_contains' requires 'path'"
    if expected is None:
        return False, "Check 'file_contains' requires 'content'"
    if not os.path.exists(path):
        return False, f"File not found: {path}"

    try:
        with open(path) as f:
            content = f.read()
    except OSError as exc:
        return False, f"Could not read file {path}: {exc}"

    if str(expected) in content:
        return True, None
    return False, f"File {path!r} must contain {str(expected)!r}"


CHECK_HANDLERS: dict[str, CheckHandler] = {
    "always_pass": _check_always_pass,
    "output_equals": _check_output_equals,
    "output_not_equals": _check_output_not_equals,
    "output_contains": _check_output_contains,
    "output_length_greater": _check_output_length_greater,
    "file_contains": _check_file_contains,
}


def evaluate(checks: Iterable[Any] | None, output: Any) -> tuple[bool, str | None]:
    normalized_output = _normalize_output(output)

    if checks is None:
        return True, None

    for index, check in enumerate(checks, start=1):
        check_type = _get_check_type(check)
        if check_type is None:
            return False, f"Check #{index} is missing a valid 'type'"

        handler = CHECK_HANDLERS.get(check_type)
        if handler is None:
            return False, f"Unsupported check type: {check_type}"

        passed, error = handler(check, normalized_output)
        if not passed:
            prefix = f"Check #{index} ({check_type}) failed"
            return False, f"{prefix}: {error}" if error else prefix

    return True, None
