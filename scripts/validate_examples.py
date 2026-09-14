from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


REPO_ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = REPO_ROOT / "examples" / "pass"
FAIL_DIR = REPO_ROOT / "examples" / "fail"


SCHEMA_PATHS = {
    "causal-contribution-receipt": (
        REPO_ROOT
        / "schemas"
        / "causal-contribution-receipt.schema.json"
    ),
    "causal-contribution-interaction": (
        REPO_ROOT
        / "schemas"
        / "contribution-interaction.schema.json"
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def format_error_path(error: Any) -> str:
    if not error.absolute_path:
        return "<root>"

    parts: list[str] = []

    for part in error.absolute_path:
        if isinstance(part, int):
            parts.append(f"[{part}]")
        else:
            if parts:
                parts.append(".")
            parts.append(str(part))

    return "".join(parts)


def load_validators() -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}

    print("=== SCHEMA VALIDATION ===")

    for protocol, schema_path in SCHEMA_PATHS.items():
        relative_path = schema_path.relative_to(REPO_ROOT)

        print()
        print(f"[load-schema] {relative_path}")

        if not schema_path.exists():
            print(f"[fatal] schema not found: {relative_path}")
            raise SystemExit(1)

        try:
            schema = load_json(schema_path)
        except Exception as exc:
            print(f"[schema-load-error] {exc}")
            raise SystemExit(1)

        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            print(f"[schema-invalid] {exc.message}")
            raise SystemExit(1)

        validators[protocol] = Draft202012Validator(schema)

        print(f"[schema-ok] protocol={protocol}")

    return validators


def resolve_validator(
    data: Any,
    validators: dict[str, Draft202012Validator],
) -> tuple[str | None, Draft202012Validator | None]:
    if not isinstance(data, dict):
        return None, None

    protocol = data.get("protocol")

    if not isinstance(protocol, str):
        return None, None

    return protocol, validators.get(protocol)


def print_schema_errors(
    validator: Draft202012Validator,
    data: Any,
) -> list[Any]:
    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: (
            list(error.absolute_path),
            error.message,
        ),
    )

    for error in errors:
        path = format_error_path(error)
        print(f"[schema-error] {path}: {error.message}")

    return errors


def validate_pass_examples(
    validators: dict[str, Draft202012Validator],
) -> tuple[int, int]:
    total = 0
    failures = 0

    print()
    print("=== PASS EXAMPLES ===")

    files = sorted(PASS_DIR.glob("*.yaml"))

    if not files:
        print("[warning] no pass examples found")
        return total, failures

    for path in files:
        total += 1

        relative_path = path.relative_to(REPO_ROOT)

        print()
        print(f"[validate-pass] {relative_path}")

        try:
            data = load_yaml(path)
        except Exception as exc:
            failures += 1
            print(f"[yaml-error] {exc}")
            continue

        protocol, validator = resolve_validator(
            data,
            validators,
        )

        if protocol is None:
            failures += 1
            print(
                "[routing-error] "
                "missing or invalid protocol identifier"
            )
            continue

        if validator is None:
            failures += 1
            print(
                "[routing-error] "
                f"unsupported protocol: {protocol}"
            )
            continue

        print(f"[protocol] {protocol}")

        errors = print_schema_errors(
            validator,
            data,
        )

        if errors:
            failures += 1
            continue

        print("[schema-ok]")

    return total, failures


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
) -> tuple[int, int]:
    total = 0
    failures = 0

    print()
    print("=== FAIL EXAMPLES ===")

    files = sorted(FAIL_DIR.glob("*.yaml"))

    if not files:
        print("[warning] no fail examples found")
        return total, failures

    for path in files:
        total += 1

        relative_path = path.relative_to(REPO_ROOT)

        print()
        print(f"[validate-fail] {relative_path}")

        try:
            data = load_yaml(path)
        except Exception as exc:
            failures += 1
            print(
                "[yaml-error] "
                f"invalid YAML prevents schema test: {exc}"
            )
            continue

        protocol, validator = resolve_validator(
            data,
            validators,
        )

        if protocol is None:
            failures += 1
            print(
                "[routing-error] "
                "missing or invalid protocol identifier"
            )
            continue

        if validator is None:
            failures += 1
            print(
                "[routing-error] "
                f"unsupported protocol: {protocol}"
            )
            continue

        print(f"[protocol] {protocol}")

        errors = print_schema_errors(
            validator,
            data,
        )

        if not errors:
            failures += 1
            print(
                "[unexpected-pass] "
                "example was expected to fail validation"
            )
            continue

        print("[expected-failure]")

    return total, failures


def print_summary(
    pass_total: int,
    pass_failures: int,
    fail_total: int,
    fail_failures: int,
) -> int:
    total_examples = pass_total + fail_total
    total_failures = pass_failures + fail_failures

    print()
    print("=== SUMMARY ===")
    print(f"pass examples checked: {pass_total}")
    print(f"fail examples checked: {fail_total}")
    print(f"total examples checked: {total_examples}")
    print(f"validation failures: {total_failures}")

    if total_failures:
        print("[validation-failed]")
        return 1

    print("[validation-ok]")
    print(
        "All pass examples validated successfully and "
        "all fail examples were rejected as expected."
    )

    return 0


def main() -> int:
    print(
        "=== Causal Contribution Receipt Protocol "
        "Validation ==="
    )

    validators = load_validators()

    pass_total, pass_failures = validate_pass_examples(
        validators
    )

    fail_total, fail_failures = validate_fail_examples(
        validators
    )

    return print_summary(
        pass_total,
        pass_failures,
        fail_total,
        fail_failures,
    )


if __name__ == "__main__":
    raise SystemExit(main())
