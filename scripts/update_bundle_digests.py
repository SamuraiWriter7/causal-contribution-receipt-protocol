from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = REPO_ROOT / "examples" / "pass"

RECORD_INDEX_PATH = (
    REPO_ROOT
    / "examples"
    / "records"
    / "index.yaml"
)

BUNDLE_PROTOCOL = "causal-contribution-bundle"

REFERENCE_FIELDS = (
    "receipt_refs",
    "interaction_refs",
    "evidence_refs",
)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def write_yaml(
    path: Path,
    data: Any,
) -> None:
    with path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as file:
        yaml.safe_dump(
            data,
            file,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        )


def resolve_repo_path(raw_path: str) -> Path:
    repo_root = REPO_ROOT.resolve()
    candidate = (REPO_ROOT / raw_path).resolve()

    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(
            f"path escapes repository root: {raw_path}"
        ) from exc

    return candidate


def load_record_index() -> dict[str, Path]:
    if not RECORD_INDEX_PATH.exists():
        raise FileNotFoundError(
            "record index not found: "
            "examples/records/index.yaml"
        )

    data = load_yaml(RECORD_INDEX_PATH)

    if not isinstance(data, dict):
        raise ValueError(
            "record index root must be an object"
        )

    records = data.get("records")

    if not isinstance(records, list):
        raise ValueError(
            "record index must contain a 'records' array"
        )

    index: dict[str, Path] = {}

    for position, entry in enumerate(records):
        if not isinstance(entry, dict):
            raise ValueError(
                f"records[{position}] must be an object"
            )

        ref = entry.get("ref")
        raw_path = entry.get("path")

        if not isinstance(ref, str):
            raise ValueError(
                f"records[{position}].ref "
                "must be a string"
            )

        if not isinstance(raw_path, str):
            raise ValueError(
                f"records[{position}].path "
                "must be a string"
            )

        if ref in index:
            raise ValueError(
                f"duplicate record ref: {ref}"
            )

        index[ref] = resolve_repo_path(
            raw_path
        )

    return index


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def iter_reference_entries(
    bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    graph_ref = bundle.get("graph_ref")

    if isinstance(graph_ref, dict):
        entries.append(graph_ref)

    for field in REFERENCE_FIELDS:
        values = bundle.get(field, [])

        if not isinstance(values, list):
            continue

        for value in values:
            if isinstance(value, dict):
                entries.append(value)

    return entries


def update_reference_digest(
    entry: dict[str, Any],
    record_index: dict[str, Path],
) -> tuple[bool, str]:
    """
    Update only an already-existing digest.

    Returns:
        (changed, status)
    """

    ref = entry.get("ref")

    if not isinstance(ref, str):
        return False, "invalid-ref"

    digest_block = entry.get("digest")

    # Important:
    # Missing digest is intentional in partial bundles.
    # Do not automatically add one.
    if not isinstance(digest_block, dict):
        return False, "no-digest"

    algorithm = digest_block.get("algorithm")

    if algorithm != "sha256":
        return False, "unsupported-algorithm"

    record_path = record_index.get(ref)

    if record_path is None:
        return False, "unresolved-ref"

    if not record_path.exists():
        return False, "missing-file"

    actual_digest = sha256_file(
        record_path
    )

    current_digest = digest_block.get("value")

    if current_digest == actual_digest:
        return False, "already-current"

    digest_block["value"] = actual_digest

    return True, "updated"


def update_bundle(
    bundle_path: Path,
    record_index: dict[str, Path],
) -> tuple[int, int, int]:
    data = load_yaml(bundle_path)

    if not isinstance(data, dict):
        raise ValueError(
            f"{bundle_path}: root must be an object"
        )

    if data.get("protocol") != BUNDLE_PROTOCOL:
        return 0, 0, 0

    changed_count = 0
    skipped_count = 0
    unresolved_count = 0

    print()
    print(
        "[bundle] "
        f"{bundle_path.relative_to(REPO_ROOT)}"
    )

    for entry in iter_reference_entries(
        data
    ):
        ref = entry.get(
            "ref",
            "<missing-ref>",
        )

        changed, status = (
            update_reference_digest(
                entry,
                record_index,
            )
        )

        if changed:
            changed_count += 1

            print(
                f"[digest-updated] {ref}"
            )

            continue

        if status == "already-current":
            print(
                f"[digest-current] {ref}"
            )

        elif status == "no-digest":
            skipped_count += 1

            print(
                f"[digest-skipped] "
                f"{ref}: digest not declared"
            )

        elif status == "unresolved-ref":
            unresolved_count += 1

            print(
                f"[digest-unresolved] "
                f"{ref}: ref not registered"
            )

        elif status == "missing-file":
            unresolved_count += 1

            print(
                f"[digest-unresolved] "
                f"{ref}: fixture file missing"
            )

        elif status == "unsupported-algorithm":
            raise ValueError(
                f"{bundle_path}: unsupported "
                f"digest algorithm for {ref}"
            )

        elif status == "invalid-ref":
            raise ValueError(
                f"{bundle_path}: invalid ref"
            )

    if changed_count:
        write_yaml(
            bundle_path,
            data,
        )

        print(
            "[bundle-updated] "
            f"digests={changed_count}"
        )

    else:
        print("[bundle-unchanged]")

    return (
        changed_count,
        skipped_count,
        unresolved_count,
    )


def find_pass_bundles() -> list[Path]:
    bundles: list[Path] = []

    for path in sorted(
        PASS_DIR.glob("*.yaml")
    ):
        try:
            data = load_yaml(path)
        except Exception as exc:
            raise ValueError(
                f"failed to read {path}: {exc}"
            ) from exc

        if (
            isinstance(data, dict)
            and data.get("protocol")
            == BUNDLE_PROTOCOL
        ):
            bundles.append(path)

    return bundles


def main() -> int:
    print(
        "=== Update Contribution Bundle Digests ==="
    )

    print(
        "record index: "
        "examples/records/index.yaml"
    )

    try:
        record_index = (
            load_record_index()
        )
    except Exception as exc:
        print(
            f"[fatal] {exc}"
        )

        return 1

    print(
        "[record-index-ok] "
        f"registered records: "
        f"{len(record_index)}"
    )

    try:
        bundles = find_pass_bundles()
    except Exception as exc:
        print(f"[fatal] {exc}")
        return 1

    if not bundles:
        print(
            "[warning] "
            "no pass contribution bundles found"
        )

        return 0

    total_changed = 0
    total_skipped = 0
    total_unresolved = 0

    for bundle_path in bundles:
        try:
            (
                changed,
                skipped,
                unresolved,
            ) = update_bundle(
                bundle_path,
                record_index,
            )
        except Exception as exc:
            print(
                "[fatal] "
                f"{bundle_path.relative_to(REPO_ROOT)}: "
                f"{exc}"
            )

            return 1

        total_changed += changed
        total_skipped += skipped
        total_unresolved += unresolved

    print()
    print("=== SUMMARY ===")

    print(
        f"bundles checked: {len(bundles)}"
    )

    print(
        f"digests updated: {total_changed}"
    )

    print(
        "references without declared digest: "
        f"{total_skipped}"
    )

    print(
        "unresolved digest references: "
        f"{total_unresolved}"
    )

    if total_unresolved:
        print(
            "[digest-update-warning] "
            "Some declared digests could not "
            "be resolved."
        )

        return 1

    print("[digest-update-ok]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
