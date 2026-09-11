from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


REPO_ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = (
    REPO_ROOT
    / "schemas"
    / "causal-contribution-receipt.schema.json"
)

PASS_DIR = REPO_ROOT / "examples" / "pass"
FAIL_DIR = REPO_ROOT / "examples" / "fail"


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


def validate_schema(schema: dict[str, Any]) -> Draft202012Validator:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        print("[schema-invalid]")
        print(f"  {exc.message}")
        sys.exit(1)

    print("[schema-ok]")
    return Draft202012Validator(schema)


def validate_pass_examples(
    validator: Draft202012Validator,
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

        print()
        print(f"[validate-pass] {path.relative_to(REPO_ROOT)}")

        try:
            data = load_yaml(path)
        except Exception as exc:
            failures += 1
            print(f"[yaml-error] {exc}")
            continue

        errors = sorted(
            validator.iter_errors(data),
            key=lambda error: list(error.absolute_path),
        )

        if errors:
            failures += 1

            for error in errors:
                error_path = format_error_path(error)
                print(
                    f"[schema-error] "
                    f"{error_path}: {error.message}"
                )
        else:
            print("[schema-ok]")

    return total, failures


def validate_fail_examples(
    validator: Draft202012Validator,
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

        print()
        print(f"[validate-fail] {path.relative_to(REPO_ROOT)}")

        try:
            data = load_yaml(path)
        except Exception as exc:
            failures += 1
            print(f"[yaml-error] {exc}")
            continue

        errors = sorted(
            validator.iter_errors(data),
            key=lambda error: list(error.absolute_path),
        )

        if not errors:
            failures += 1
            print(
                "[unexpected-pass] "
                "example was expected to fail validation"
            )
            continue

        print("[expected-failure]")

        for error in errors:
            error_path = format_error_path(error)
            print(
                f"[schema-error] "
                f"{error_path}: {error.message}"
            )

    return total, failures


def main() -> int:
    print("=== Causal Contribution Receipt Protocol Validation ===")
    print(
        "schema: "
        "schemas/causal-contribution-receipt.schema.json"
    )

    if not SCHEMA_PATH.exists():
        print(f"[fatal] schema not found: {SCHEMA_PATH}")
        return 1

    schema = load_json(SCHEMA_PATH)
    validator = validate_schema(schema)

    pass_total, pass_failures = validate_pass_examples(validator)
    fail_total, fail_failures = validate_fail_examples(validator)

    total_examples = pass_total + fail_total
    total_failures = pass_failures + fail_failures

    print()
    print("=== SUMMARY ===")
    print(f"pass examples checked: {pass_total}")
    print(f"fail examples checked: {fail_total}")
    print(f"total examples checked: {total_examples}")

    if total_failures:
        print(f"[validation-failed] failures: {total_failures}")
        return 1

    print("[validation-ok]")
    print(
        "All pass examples validated successfully and "
        "all fail examples were rejected as expected."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
