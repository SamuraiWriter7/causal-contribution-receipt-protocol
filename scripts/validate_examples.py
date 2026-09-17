from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


REPO_ROOT = Path(__file__).resolve().parents[1]

PASS_DIR = REPO_ROOT / "examples" / "pass"
FAIL_DIR = REPO_ROOT / "examples" / "fail"

RECORD_INDEX_PATH = (
    REPO_ROOT
    / "examples"
    / "records"
    / "index.yaml"
)

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
    "causal-contribution-graph": (
        REPO_ROOT
        / "schemas"
        / "contribution-graph.schema.json"
    ),
    "causal-contribution-bundle": (
        REPO_ROOT
        / "schemas"
        / "contribution-bundle.schema.json"
    ),
    "causal-contribution-weight-assessment": (
        REPO_ROOT
        / "schemas"
        / "contribution-weight-assessment.schema.json"
    ),
}

EPSILON = 1e-9
COVERAGE_TOLERANCE = 0.0051


# ============================================================
# BASIC LOADING
# ============================================================


def load_json(path: Path) -> dict[str, Any]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_yaml(path: Path) -> Any:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)


def load_structured_file(path: Path) -> Any:
    suffix = path.suffix.lower()

    if suffix == ".json":
        return load_json(path)

    if suffix in {".yaml", ".yml"}:
        return load_yaml(path)

    raise ValueError(
        f"unsupported record file extension: {path.suffix}"
    )


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


def approximately_equal(
    a: float,
    b: float,
    tolerance: float = EPSILON,
) -> bool:
    return math.isclose(
        a,
        b,
        rel_tol=tolerance,
        abs_tol=tolerance,
    )


def approximately_equal_coverage(
    actual: float,
    declared: float,
) -> bool:
    return (
        abs(
            round(actual, 2)
            - declared
        )
        <= COVERAGE_TOLERANCE
    )


def duplicate_values(
    values: list[str],
) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return sorted(duplicates)


# ============================================================
# SCHEMA
# ============================================================


def load_validators(
) -> dict[str, Draft202012Validator]:
    validators: dict[
        str,
        Draft202012Validator,
    ] = {}

    print("=== SCHEMA VALIDATION ===")

    for protocol, schema_path in SCHEMA_PATHS.items():
        relative_path = schema_path.relative_to(
            REPO_ROOT
        )

        print()
        print(
            f"[load-schema] {relative_path}"
        )

        if not schema_path.exists():
            print(
                f"[fatal] schema not found: "
                f"{relative_path}"
            )
            raise SystemExit(1)

        try:
            schema = load_json(schema_path)
        except Exception as exc:
            print(
                f"[schema-load-error] {exc}"
            )
            raise SystemExit(1)

        try:
            Draft202012Validator.check_schema(
                schema
            )
        except SchemaError as exc:
            print(
                f"[schema-invalid] {exc.message}"
            )
            raise SystemExit(1)

        validators[protocol] = (
            Draft202012Validator(schema)
        )

        print(
            f"[schema-ok] protocol={protocol}"
        )

    return validators


def resolve_validator(
    data: Any,
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> tuple[
    str | None,
    Draft202012Validator | None,
]:
    if not isinstance(data, dict):
        return None, None

    protocol = data.get("protocol")

    if not isinstance(protocol, str):
        return None, None

    return (
        protocol,
        validators.get(protocol),
    )


def collect_schema_errors(
    validator: Draft202012Validator,
    data: Any,
) -> list[Any]:
    return sorted(
        validator.iter_errors(data),
        key=lambda error: (
            format_error_path(error),
            error.message,
        ),
    )


def print_schema_errors(
    errors: list[Any],
) -> None:
    for error in errors:
        print(
            "[schema-error] "
            f"{format_error_path(error)}: "
            f"{error.message}"
        )


# ============================================================
# RECORD RESOLVER
# ============================================================


@dataclass(frozen=True)
class ResolvedRecord:
    ref: str
    path: Path
    data: Any
    raw_bytes: bytes
    sha256: str


class RecordResolver:
    def __init__(
        self,
        index: dict[str, Path],
    ) -> None:
        self.index = index
        self.cache: dict[
            str,
            ResolvedRecord,
        ] = {}

    def resolve(
        self,
        ref: str,
    ) -> ResolvedRecord | None:
        if ref in self.cache:
            return self.cache[ref]

        path = self.index.get(ref)

        if path is None:
            return None

        if not path.exists():
            return None

        try:
            raw_bytes = path.read_bytes()
            data = load_structured_file(path)
        except Exception:
            return None

        digest = hashlib.sha256(
            raw_bytes
        ).hexdigest()

        record = ResolvedRecord(
            ref=ref,
            path=path,
            data=data,
            raw_bytes=raw_bytes,
            sha256=digest,
        )

        self.cache[ref] = record

        return record


def resolve_index_path(
    raw_path: str,
) -> Path:
    candidate = (
        REPO_ROOT
        / raw_path
    ).resolve()

    repo_root = REPO_ROOT.resolve()

    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(
            "record path escapes "
            f"repository root: {raw_path}"
        ) from exc

    return candidate


def auto_register_pass_bundles(
    index: dict[str, Path],
) -> int:
    """
    v0.5 Weight Assessments refer to v0.4 bundles through:

        trace://contribution-bundles/<bundle_id>

    Bundle examples live in examples/pass/, so register them
    automatically as locally resolvable records.
    """

    count = 0

    for path in sorted(
        PASS_DIR.glob("*.yaml")
    ):
        try:
            data = load_yaml(path)
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        if (
            data.get("protocol")
            != "causal-contribution-bundle"
        ):
            continue

        bundle_id = data.get("bundle_id")

        if not isinstance(bundle_id, str):
            continue

        ref = (
            "trace://contribution-bundles/"
            f"{bundle_id}"
        )

        if ref not in index:
            index[ref] = path.resolve()
            count += 1

    return count


def load_record_resolver(
) -> RecordResolver:
    print()
    print("=== RECORD RESOLVER ===")

    index: dict[str, Path] = {}

    if RECORD_INDEX_PATH.exists():
        try:
            index_data = load_yaml(
                RECORD_INDEX_PATH
            )
        except Exception as exc:
            print(
                f"[resolver-index-error] {exc}"
            )
            raise SystemExit(1)

        if not isinstance(
            index_data,
            dict,
        ):
            print(
                "[resolver-index-error] "
                "record index root must "
                "be an object"
            )
            raise SystemExit(1)

        records = index_data.get("records")

        if not isinstance(records, list):
            print(
                "[resolver-index-error] "
                "'records' must be an array"
            )
            raise SystemExit(1)

        for position, entry in enumerate(
            records
        ):
            if not isinstance(entry, dict):
                print(
                    "[resolver-index-error] "
                    f"records[{position}] "
                    "must be an object"
                )
                raise SystemExit(1)

            ref = entry.get("ref")
            raw_path = entry.get("path")

            if not isinstance(ref, str):
                print(
                    "[resolver-index-error] "
                    f"records[{position}].ref "
                    "must be a string"
                )
                raise SystemExit(1)

            if not isinstance(
                raw_path,
                str,
            ):
                print(
                    "[resolver-index-error] "
                    f"records[{position}].path "
                    "must be a string"
                )
                raise SystemExit(1)

            if ref in index:
                print(
                    "[resolver-index-error] "
                    f"duplicate record ref: {ref}"
                )
                raise SystemExit(1)

            try:
                index[ref] = (
                    resolve_index_path(
                        raw_path
                    )
                )
            except ValueError as exc:
                print(
                    "[resolver-index-error] "
                    f"{exc}"
                )
                raise SystemExit(1)

    else:
        print(
            "[resolver-warning] "
            "examples/records/index.yaml "
            "not found"
        )

    bundle_count = (
        auto_register_pass_bundles(
            index
        )
    )

    print(
        "[resolver-ok] "
        f"registered records: {len(index)}"
    )

    if bundle_count:
        print(
            "[resolver-bundles] "
            f"auto-registered: {bundle_count}"
        )

    return RecordResolver(index)


# ============================================================
# RECEIPT SEMANTICS
# ============================================================


def validate_receipt_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    counterfactual = data.get(
        "counterfactual"
    )

    if not isinstance(
        counterfactual,
        dict,
    ):
        return errors

    baseline = counterfactual.get(
        "baseline",
        {},
    )

    without = counterfactual.get(
        "without_contributor",
        {},
    )

    baseline_score = baseline.get(
        "quality_score"
    )

    without_score = without.get(
        "quality_score"
    )

    observed_delta = counterfactual.get(
        "observed_delta"
    )

    if (
        isinstance(
            baseline_score,
            (int, float),
        )
        and isinstance(
            without_score,
            (int, float),
        )
        and isinstance(
            observed_delta,
            (int, float),
        )
    ):
        expected_delta = (
            float(baseline_score)
            - float(without_score)
        )

        if not approximately_equal(
            expected_delta,
            float(observed_delta),
        ):
            errors.append(
                "counterfactual."
                "observed_delta "
                f"expected "
                f"{expected_delta:.12g} "
                f"but found "
                f"{observed_delta}"
            )

    return errors


# ============================================================
# INTERACTION SEMANTICS
# ============================================================


def validate_interaction_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    contributors = data.get(
        "contributors",
        [],
    )

    contributor_ids: list[str] = []

    if isinstance(contributors, list):
        for contributor in contributors:
            if not isinstance(
                contributor,
                dict,
            ):
                continue

            contributor_id = (
                contributor.get(
                    "contributor_id"
                )
            )

            if isinstance(
                contributor_id,
                str,
            ):
                contributor_ids.append(
                    contributor_id
                )

    for duplicate in duplicate_values(
        contributor_ids
    ):
        errors.append(
            "duplicate contributor_id: "
            f"{duplicate}"
        )

    counterfactual = data.get(
        "counterfactual"
    )

    if not isinstance(
        counterfactual,
        dict,
    ):
        return errors

    method = counterfactual.get(
        "method"
    )

    if (
        method
        in {
            "pairwise_ablation",
            "substitution_test",
        }
        and len(contributor_ids) != 2
    ):
        errors.append(
            f"{method} requires exactly "
            "2 contributors but found "
            f"{len(contributor_ids)}"
        )

    baseline = counterfactual.get(
        "baseline",
        {},
    )

    comparison = counterfactual.get(
        "comparison",
        {},
    )

    baseline_score = baseline.get(
        "quality_score"
    )

    comparison_score = comparison.get(
        "quality_score"
    )

    observed_delta = counterfactual.get(
        "observed_delta"
    )

    if (
        isinstance(
            baseline_score,
            (int, float),
        )
        and isinstance(
            comparison_score,
            (int, float),
        )
        and isinstance(
            observed_delta,
            (int, float),
        )
    ):
        expected_delta = (
            float(baseline_score)
            - float(comparison_score)
        )

        if not approximately_equal(
            expected_delta,
            float(observed_delta),
        ):
            errors.append(
                "counterfactual."
                "observed_delta "
                f"expected "
                f"{expected_delta:.12g} "
                f"but found "
                f"{observed_delta}"
            )

    return errors


# ============================================================
# GRAPH SEMANTICS
# ============================================================


def build_node_map(
    nodes: list[Any],
) -> dict[str, dict[str, Any]]:
    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for node in nodes:
        if not isinstance(node, dict):
            continue

        node_id = node.get("node_id")

        if (
            isinstance(node_id, str)
            and node_id not in result
        ):
            result[node_id] = node

    return result


def validate_graph_ids(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    paths = data.get("paths", [])

    node_ids = [
        node["node_id"]
        for node in nodes
        if isinstance(node, dict)
        and isinstance(
            node.get("node_id"),
            str,
        )
    ]

    edge_ids = [
        edge["edge_id"]
        for edge in edges
        if isinstance(edge, dict)
        and isinstance(
            edge.get("edge_id"),
            str,
        )
    ]

    path_ids = [
        path["path_id"]
        for path in paths
        if isinstance(path, dict)
        and isinstance(
            path.get("path_id"),
            str,
        )
    ]

    for value in duplicate_values(
        node_ids
    ):
        errors.append(
            f"duplicate node_id: {value}"
        )

    for value in duplicate_values(
        edge_ids
    ):
        errors.append(
            f"duplicate edge_id: {value}"
        )

    for value in duplicate_values(
        path_ids
    ):
        errors.append(
            f"duplicate path_id: {value}"
        )

    return errors


def validate_graph_references(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    paths = data.get("paths", [])

    node_map = build_node_map(nodes)
    node_ids = set(node_map)

    for edge in edges:
        if not isinstance(edge, dict):
            continue

        edge_id = edge.get(
            "edge_id",
            "<unknown>",
        )

        source = edge.get("from")
        destination = edge.get("to")

        if (
            isinstance(source, str)
            and source not in node_ids
        ):
            errors.append(
                f"edge {edge_id} "
                "references unknown "
                f"source node: {source}"
            )

        if (
            isinstance(
                destination,
                str,
            )
            and destination
            not in node_ids
        ):
            errors.append(
                f"edge {edge_id} "
                "references unknown "
                "destination node: "
                f"{destination}"
            )

    for path in paths:
        if not isinstance(path, dict):
            continue

        path_id = path.get(
            "path_id",
            "<unknown>",
        )

        path_nodes = path.get(
            "node_ids",
            [],
        )

        if not isinstance(
            path_nodes,
            list,
        ):
            continue

        for node_id in path_nodes:
            if (
                isinstance(node_id, str)
                and node_id
                not in node_ids
            ):
                errors.append(
                    f"path {path_id} "
                    "references unknown "
                    f"node: {node_id}"
                )

    return errors


def validate_graph_outcome(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    outcome = data.get(
        "outcome",
        {},
    )

    outcome_ref = outcome.get(
        "outcome_ref"
    )

    matching = [
        node
        for node in data.get(
            "nodes",
            [],
        )
        if isinstance(node, dict)
        and node.get("node_type")
        == "outcome"
        and node.get("ref")
        == outcome_ref
    ]

    if not matching:
        errors.append(
            "graph outcome does not "
            "resolve to an outcome node "
            "with matching outcome_ref"
        )

    return errors


def validate_edge_directions(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    node_map = build_node_map(
        data.get("nodes", [])
    )

    for edge in data.get(
        "edges",
        [],
    ):
        if not isinstance(edge, dict):
            continue

        edge_id = edge.get(
            "edge_id",
            "<unknown>",
        )

        source_id = edge.get("from")
        destination_id = edge.get("to")
        relation = edge.get("relation")

        if (
            not isinstance(
                source_id,
                str,
            )
            or not isinstance(
                destination_id,
                str,
            )
        ):
            continue

        source = node_map.get(
            source_id
        )

        destination = node_map.get(
            destination_id
        )

        if (
            source is None
            or destination is None
        ):
            continue

        source_type = source.get(
            "node_type"
        )

        destination_type = (
            destination.get(
                "node_type"
            )
        )

        if source_type == "outcome":
            errors.append(
                f"edge {edge_id} has "
                "invalid causal direction: "
                f"outcome node {source_id} "
                "cannot be a source"
            )
            continue

        if relation == "contributed_to":
            if (
                destination_type
                != "outcome"
            ):
                errors.append(
                    "invalid edge direction "
                    "for contributed_to: "
                    f"{source_type} -> "
                    f"{destination_type}"
                )

        elif relation == "participates_in":
            if (
                destination_type
                != "contribution_interaction"
            ):
                errors.append(
                    "invalid edge direction "
                    "for participates_in: "
                    f"{source_type} -> "
                    f"{destination_type}"
                )

            if source_type not in {
                "contributor",
                "contribution_receipt",
            }:
                errors.append(
                    "participates_in must "
                    "originate from "
                    "contributor or "
                    "contribution_receipt"
                )

        elif relation == "supported_by":
            if (
                destination_type
                != "evidence"
            ):
                errors.append(
                    "invalid edge direction "
                    "for supported_by: "
                    f"{source_type} -> "
                    f"{destination_type}"
                )

        elif relation == "verified_by":
            if (
                destination_type
                != "evidence"
            ):
                errors.append(
                    "invalid edge direction "
                    "for verified_by: "
                    f"{source_type} -> "
                    f"{destination_type}"
                )

    return errors


def validate_graph_paths(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    paths = data.get("paths", [])

    node_map = build_node_map(nodes)

    directed_edges = {
        (
            edge.get("from"),
            edge.get("to"),
        )
        for edge in edges
        if isinstance(edge, dict)
        and isinstance(
            edge.get("from"),
            str,
        )
        and isinstance(
            edge.get("to"),
            str,
        )
    }

    graph_outcome_ref = (
        data.get(
            "outcome",
            {},
        ).get(
            "outcome_ref"
        )
    )

    for path in paths:
        if not isinstance(path, dict):
            continue

        path_id = path.get(
            "path_id",
            "<unknown>",
        )

        node_ids = path.get(
            "node_ids",
            [],
        )

        if not isinstance(
            node_ids,
            list,
        ):
            continue

        for index in range(
            len(node_ids) - 1
        ):
            source = node_ids[index]
            destination = (
                node_ids[index + 1]
            )

            if (
                source,
                destination,
            ) not in directed_edges:
                errors.append(
                    f"path {path_id} is "
                    "not contiguous: "
                    "missing edge "
                    f"{source} -> "
                    f"{destination}"
                )

        if node_ids:
            final_node = node_map.get(
                node_ids[-1]
            )

            if final_node is not None:
                if (
                    final_node.get(
                        "node_type"
                    )
                    != "outcome"
                ):
                    errors.append(
                        f"path {path_id} "
                        "does not terminate "
                        "at an outcome node"
                    )

                elif (
                    final_node.get("ref")
                    != graph_outcome_ref
                ):
                    errors.append(
                        f"path {path_id} "
                        "terminates at an "
                        "outcome different "
                        "from graph outcome"
                    )

    return errors


def find_cycle(
    data: dict[str, Any],
) -> list[str] | None:
    node_map = build_node_map(
        data.get("nodes", [])
    )

    adjacency: dict[
        str,
        list[str],
    ] = {
        node_id: []
        for node_id in node_map
    }

    for edge in data.get(
        "edges",
        [],
    ):
        if not isinstance(edge, dict):
            continue

        source = edge.get("from")
        destination = edge.get("to")

        if (
            isinstance(source, str)
            and isinstance(
                destination,
                str,
            )
            and source in adjacency
            and destination
            in adjacency
        ):
            adjacency[source].append(
                destination
            )

    state = {
        node_id: 0
        for node_id in adjacency
    }

    stack: list[str] = []
    stack_index: dict[str, int] = {}

    def dfs(
        node_id: str,
    ) -> list[str] | None:
        state[node_id] = 1

        stack_index[node_id] = (
            len(stack)
        )

        stack.append(node_id)

        for neighbor in adjacency[
            node_id
        ]:
            if state[neighbor] == 0:
                cycle = dfs(neighbor)

                if cycle is not None:
                    return cycle

            elif state[neighbor] == 1:
                start = stack_index[
                    neighbor
                ]

                return (
                    stack[start:]
                    + [neighbor]
                )

        stack.pop()

        stack_index.pop(
            node_id,
            None,
        )

        state[node_id] = 2

        return None

    for node_id in adjacency:
        if state[node_id] != 0:
            continue

        cycle = dfs(node_id)

        if cycle is not None:
            return cycle

    return None


def validate_graph_cycles(
    data: dict[str, Any],
) -> list[str]:
    cycle = find_cycle(data)

    if cycle is None:
        return []

    return [
        "causal cycle detected: "
        + " -> ".join(cycle)
    ]


def validate_graph_assessment(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    assessment = data.get(
        "graph_assessment"
    )

    if not isinstance(
        assessment,
        dict,
    ):
        return errors

    status_counts = {
        "verified": 0,
        "partial": 0,
        "unresolved": 0,
    }

    for edge in data.get(
        "edges",
        [],
    ):
        if not isinstance(edge, dict):
            continue

        status = edge.get(
            "verification_status"
        )

        if status in status_counts:
            status_counts[status] += 1

    unresolved_segments = sum(
        1
        for node in data.get(
            "nodes",
            [],
        )
        if isinstance(node, dict)
        and node.get("node_type")
        == "unresolved_segment"
    )

    expected = {
        "verified_edge_count":
            status_counts["verified"],
        "partial_edge_count":
            status_counts["partial"],
        "unresolved_edge_count":
            status_counts["unresolved"],
        "unresolved_segment_count":
            unresolved_segments,
    }

    for field, expected_value in (
        expected.items()
    ):
        actual = assessment.get(field)

        if actual is None:
            continue

        if actual != expected_value:
            errors.append(
                f"graph_assessment."
                f"{field} expected "
                f"{expected_value} "
                f"but found {actual}"
            )

    return errors


def validate_graph_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    validators: list[
        Callable[
            [dict[str, Any]],
            list[str],
        ]
    ] = [
        validate_graph_ids,
        validate_graph_references,
        validate_graph_outcome,
        validate_edge_directions,
        validate_graph_paths,
        validate_graph_cycles,
        validate_graph_assessment,
    ]

    for validator in validators:
        errors.extend(
            validator(data)
        )

    return errors


# ============================================================
# BUNDLE SEMANTICS
# ============================================================


def validate_bundle_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    refs: list[str] = []

    graph_ref = data.get(
        "graph_ref",
        {},
    )

    if isinstance(graph_ref, dict):
        ref = graph_ref.get("ref")

        if isinstance(ref, str):
            refs.append(ref)

    receipt_refs = data.get(
        "receipt_refs",
        [],
    )

    if isinstance(
        receipt_refs,
        list,
    ):
        for entry in receipt_refs:
            if not isinstance(
                entry,
                dict,
            ):
                continue

            ref = entry.get("ref")

            if isinstance(ref, str):
                refs.append(ref)

            if (
                entry.get(
                    "record_type"
                )
                != "contribution_receipt"
            ):
                errors.append(
                    "receipt_refs entry "
                    "must declare "
                    "record_type="
                    "contribution_receipt"
                )

    interaction_refs = data.get(
        "interaction_refs",
        [],
    )

    if isinstance(
        interaction_refs,
        list,
    ):
        for entry in interaction_refs:
            if not isinstance(
                entry,
                dict,
            ):
                continue

            ref = entry.get("ref")

            if isinstance(ref, str):
                refs.append(ref)

            if (
                entry.get(
                    "record_type"
                )
                != "contribution_interaction"
            ):
                errors.append(
                    "interaction_refs entry "
                    "must declare "
                    "record_type="
                    "contribution_interaction"
                )

    evidence_refs = data.get(
        "evidence_refs",
        [],
    )

    if isinstance(
        evidence_refs,
        list,
    ):
        for entry in evidence_refs:
            if not isinstance(
                entry,
                dict,
            ):
                continue

            ref = entry.get("ref")

            if isinstance(ref, str):
                refs.append(ref)

    for duplicate in duplicate_values(
        refs
    ):
        errors.append(
            "duplicate bundle reference: "
            f"{duplicate}"
        )

    return errors


# ============================================================
# v0.5 WEIGHT SEMANTICS
# ============================================================


def validate_weight_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    weights = data.get(
        "weights",
        [],
    )

    if not isinstance(weights, list):
        return errors

    weight_ids: list[str] = []
    subject_refs: list[str] = []

    estimated_total = 0.0
    interaction_count = 0

    for entry in weights:
        if not isinstance(entry, dict):
            continue

        weight_id = entry.get(
            "weight_id"
        )

        if isinstance(weight_id, str):
            weight_ids.append(weight_id)

        subject_ref = entry.get(
            "subject_ref"
        )

        if isinstance(subject_ref, str):
            subject_refs.append(
                subject_ref
            )

        subject_type = entry.get(
            "subject_type"
        )

        if (
            subject_type
            == "contribution_interaction"
        ):
            interaction_count += 1

        estimated = entry.get(
            "estimated_weight"
        )

        lower = entry.get(
            "lower_bound"
        )

        upper = entry.get(
            "upper_bound"
        )

        if isinstance(
            estimated,
            (int, float),
        ):
            estimated_total += float(
                estimated
            )

        if (
            isinstance(
                lower,
                (int, float),
            )
            and isinstance(
                estimated,
                (int, float),
            )
            and isinstance(
                upper,
                (int, float),
            )
        ):
            if (
                float(lower)
                > float(estimated)
                + EPSILON
            ):
                errors.append(
                    f"{weight_id}: "
                    "lower_bound exceeds "
                    "estimated_weight"
                )

            if (
                float(estimated)
                > float(upper)
                + EPSILON
            ):
                errors.append(
                    f"{weight_id}: "
                    "estimated_weight exceeds "
                    "upper_bound"
                )

        interaction_adjustment = (
            entry.get(
                "interaction_adjustment"
            )
        )

        if isinstance(
            interaction_adjustment,
            dict,
        ):
            applied = (
                interaction_adjustment.get(
                    "applied"
                )
            )

            if (
                applied is True
                and subject_type
                != "contribution_interaction"
            ):
                errors.append(
                    "interaction contribution "
                    "MUST NOT be assigned "
                    "directly to an individual "
                    "contribution subject: "
                    f"{weight_id}"
                )

            if applied is False:
                if (
                    "adjustment"
                    in interaction_adjustment
                    or "interaction_refs"
                    in interaction_adjustment
                ):
                    errors.append(
                        f"{weight_id}: "
                        "interaction_adjustment "
                        "declares adjustment data "
                        "while applied=false"
                    )

    for duplicate in duplicate_values(
        weight_ids
    ):
        errors.append(
            f"duplicate weight_id: {duplicate}"
        )

    for duplicate in duplicate_values(
        subject_refs
    ):
        errors.append(
            "duplicate contribution "
            f"weight subject: {duplicate}"
        )

    if (
        estimated_total
        > 1.0 + EPSILON
    ):
        errors.append(
            "estimated contribution "
            "weight sum exceeds 1.0: "
            f"{estimated_total:.12g}"
        )

    summary = data.get(
        "assessment_summary",
        {},
    )

    if isinstance(summary, dict):
        known_weight = summary.get(
            "known_weight"
        )

        if isinstance(
            known_weight,
            (int, float),
        ):
            if not approximately_equal(
                estimated_total,
                float(known_weight),
            ):
                errors.append(
                    "assessment_summary."
                    "known_weight expected "
                    f"{estimated_total:.12g} "
                    f"but found "
                    f"{known_weight}"
                )

        subject_count = summary.get(
            "subject_count"
        )

        if (
            isinstance(
                subject_count,
                int,
            )
            and subject_count
            != len(weights)
        ):
            errors.append(
                "assessment_summary."
                "subject_count expected "
                f"{len(weights)} "
                f"but found "
                f"{subject_count}"
            )

        declared_interaction_count = (
            summary.get(
                "interaction_subject_count"
            )
        )

        if (
            isinstance(
                declared_interaction_count,
                int,
            )
            and declared_interaction_count
            != interaction_count
        ):
            errors.append(
                "assessment_summary."
                "interaction_subject_count "
                f"expected "
                f"{interaction_count} "
                f"but found "
                f"{declared_interaction_count}"
            )

    unresolved_weight = data.get(
        "unresolved_weight"
    )

    if isinstance(
        unresolved_weight,
        (int, float),
    ):
        total = (
            estimated_total
            + float(unresolved_weight)
        )

        if not approximately_equal(
            total,
            1.0,
        ):
            errors.append(
                "known contribution weight "
                "+ unresolved_weight "
                "must equal 1.0: "
                f"found {total:.12g}"
            )

    return errors


# ============================================================
# SEMANTIC ROUTING
# ============================================================


SEMANTIC_VALIDATORS: dict[
    str,
    Callable[
        [dict[str, Any]],
        list[str],
    ],
] = {
    "causal-contribution-receipt":
        validate_receipt_semantics,

    "causal-contribution-interaction":
        validate_interaction_semantics,

    "causal-contribution-graph":
        validate_graph_semantics,

    "causal-contribution-bundle":
        validate_bundle_semantics,

    "causal-contribution-weight-assessment":
        validate_weight_semantics,
}


def run_semantic_validation(
    protocol: str,
    data: dict[str, Any],
) -> list[str]:
    validator = (
        SEMANTIC_VALIDATORS.get(
            protocol
        )
    )

    if validator is None:
        return [
            "no semantic validator "
            "registered for protocol: "
            f"{protocol}"
        ]

    return validator(data)


def print_semantic_errors(
    errors: list[str],
) -> None:
    for error in errors:
        print(
            f"[semantic-error] {error}"
        )


# ============================================================
# CROSS-RECORD HELPERS
# ============================================================


def record_protocol(
    record: Any,
) -> str | None:
    if not isinstance(record, dict):
        return None

    value = record.get("protocol")

    if isinstance(value, str):
        return value

    return None


def record_version(
    record: Any,
) -> str | None:
    if not isinstance(record, dict):
        return None

    value = record.get(
        "protocol_version"
    )

    if isinstance(value, str):
        return value

    return None


def record_id(
    record: Any,
) -> str | None:
    if not isinstance(record, dict):
        return None

    protocol = record_protocol(
        record
    )

    fields = {
        "causal-contribution-receipt":
            "receipt_id",

        "causal-contribution-interaction":
            "interaction_id",

        "causal-contribution-graph":
            "graph_id",

        "causal-contribution-bundle":
            "bundle_id",

        "causal-contribution-weight-assessment":
            "assessment_id",
    }

    field = fields.get(protocol)

    if field is None:
        return None

    value = record.get(field)

    if isinstance(value, str):
        return value

    return None


def record_outcome_id(
    record: Any,
) -> str | None:
    if not isinstance(record, dict):
        return None

    outcome = record.get("outcome")

    if not isinstance(outcome, dict):
        outcome = record.get(
            "outcome_ref"
        )

    if not isinstance(
        outcome,
        dict,
    ):
        return None

    value = outcome.get(
        "outcome_id"
    )

    if isinstance(value, str):
        return value

    return None


def receipt_contributor_id(
    record: Any,
) -> str | None:
    if not isinstance(record, dict):
        return None

    contributor = record.get(
        "contributor"
    )

    if not isinstance(
        contributor,
        dict,
    ):
        return None

    value = contributor.get(
        "contributor_id"
    )

    if isinstance(value, str):
        return value

    return None


def interaction_contributor_ids(
    record: Any,
) -> set[str]:
    result: set[str] = set()

    if not isinstance(record, dict):
        return result

    contributors = record.get(
        "contributors",
        [],
    )

    if not isinstance(
        contributors,
        list,
    ):
        return result

    for contributor in contributors:
        if not isinstance(
            contributor,
            dict,
        ):
            continue

        contributor_id = (
            contributor.get(
                "contributor_id"
            )
        )

        if isinstance(
            contributor_id,
            str,
        ):
            result.add(
                contributor_id
            )

    return result


def collect_bundle_ref_entries(
    bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    entries: list[
        dict[str, Any]
    ] = []

    graph = bundle.get(
        "graph_ref"
    )

    if isinstance(graph, dict):
        entries.append(graph)

    for field in (
        "receipt_refs",
        "interaction_refs",
        "evidence_refs",
    ):
        values = bundle.get(
            field,
            [],
        )

        if not isinstance(
            values,
            list,
        ):
            continue

        for value in values:
            if isinstance(
                value,
                dict,
            ):
                entries.append(
                    value
                )

    return entries


def get_entry_ref(
    entry: dict[str, Any],
) -> str | None:
    ref = entry.get("ref")

    if isinstance(ref, str):
        return ref

    return None


def validate_declared_digest(
    entry: dict[str, Any],
    resolved: ResolvedRecord,
) -> str | None:
    digest = entry.get("digest")

    if not isinstance(digest, dict):
        return None

    algorithm = digest.get(
        "algorithm"
    )

    declared_value = digest.get(
        "value"
    )

    if algorithm != "sha256":
        return (
            "unsupported digest "
            f"algorithm for "
            f"{resolved.ref}: "
            f"{algorithm}"
        )

    if not isinstance(
        declared_value,
        str,
    ):
        return (
            "invalid digest value "
            f"for {resolved.ref}"
        )

    if (
        declared_value.lower()
        != resolved.sha256.lower()
    ):
        return (
            "digest mismatch for "
            f"{resolved.ref}"
        )

    return None


# ============================================================
# v0.4 BUNDLE CROSS-RECORD
# ============================================================


def validate_bundle_cross_records(
    bundle: dict[str, Any],
    resolver: RecordResolver,
) -> list[str]:
    errors: list[str] = []

    bundle_outcome = bundle.get(
        "outcome_ref",
        {},
    )

    expected_outcome_id = (
        bundle_outcome.get(
            "outcome_id"
        )
        if isinstance(
            bundle_outcome,
            dict,
        )
        else None
    )

    graph_entry = bundle.get(
        "graph_ref",
        {},
    )

    receipt_entries = bundle.get(
        "receipt_refs",
        [],
    )

    interaction_entries = bundle.get(
        "interaction_refs",
        [],
    )

    all_entries = (
        collect_bundle_ref_entries(
            bundle
        )
    )

    resolved_by_ref: dict[
        str,
        ResolvedRecord,
    ] = {}

    unresolved_refs: list[str] = []

    for entry in all_entries:
        ref = get_entry_ref(entry)

        if ref is None:
            continue

        resolved = resolver.resolve(
            ref
        )

        if resolved is None:
            unresolved_refs.append(
                ref
            )
            continue

        resolved_by_ref[ref] = (
            resolved
        )

        digest_error = (
            validate_declared_digest(
                entry,
                resolved,
            )
        )

        if digest_error is not None:
            errors.append(
                digest_error
            )

    total_refs = len(all_entries)
    resolved_count = len(
        resolved_by_ref
    )

    if total_refs > 0:
        reference_coverage = (
            resolved_count
            / total_refs
        )

        digest_count = sum(
            1
            for entry in all_entries
            if isinstance(
                entry.get("digest"),
                dict,
            )
        )

        digest_coverage = (
            digest_count
            / total_refs
        )

    else:
        reference_coverage = 1.0
        digest_coverage = 1.0

    assessment = bundle.get(
        "bundle_assessment"
    )

    if isinstance(
        assessment,
        dict,
    ):
        declared_reference = (
            assessment.get(
                "reference_coverage"
            )
        )

        if isinstance(
            declared_reference,
            (int, float),
        ):
            if not approximately_equal_coverage(
                reference_coverage,
                float(
                    declared_reference
                ),
            ):
                errors.append(
                    "bundle_assessment."
                    "reference_coverage "
                    f"expected "
                    f"{round(reference_coverage, 2):.2f} "
                    f"but found "
                    f"{declared_reference}"
                )

        declared_digest = (
            assessment.get(
                "digest_coverage"
            )
        )

        if isinstance(
            declared_digest,
            (int, float),
        ):
            if not approximately_equal_coverage(
                digest_coverage,
                float(declared_digest),
            ):
                errors.append(
                    "bundle_assessment."
                    "digest_coverage "
                    f"expected "
                    f"{round(digest_coverage, 2):.2f} "
                    f"but found "
                    f"{declared_digest}"
                )

        declared_unresolved = (
            assessment.get(
                "unresolved_reference_count"
            )
        )

        if (
            isinstance(
                declared_unresolved,
                int,
            )
            and declared_unresolved
            != len(unresolved_refs)
        ):
            errors.append(
                "bundle_assessment."
                "unresolved_reference_count "
                f"expected "
                f"{len(unresolved_refs)} "
                f"but found "
                f"{declared_unresolved}"
            )

    graph_ref = (
        graph_entry.get("ref")
        if isinstance(
            graph_entry,
            dict,
        )
        else None
    )

    graph_record: (
        ResolvedRecord | None
    ) = None

    if isinstance(graph_ref, str):
        graph_record = (
            resolved_by_ref.get(
                graph_ref
            )
        )

        if graph_record is None:
            errors.append(
                "unresolved graph "
                f"reference: {graph_ref}"
            )

    resolved_receipts: dict[
        str,
        ResolvedRecord,
    ] = {}

    if isinstance(
        receipt_entries,
        list,
    ):
        for entry in receipt_entries:
            if not isinstance(
                entry,
                dict,
            ):
                continue

            ref = get_entry_ref(
                entry
            )

            if ref is None:
                continue

            resolved = (
                resolved_by_ref.get(
                    ref
                )
            )

            if resolved is None:
                errors.append(
                    "unresolved external "
                    f"reference: {ref}"
                )
                continue

            resolved_receipts[
                ref
            ] = resolved

            if (
                record_protocol(
                    resolved.data
                )
                !=
                "causal-contribution-receipt"
            ):
                errors.append(
                    "record type mismatch "
                    f"for {ref}: expected "
                    "causal-contribution-receipt"
                )
                continue

            actual_id = record_id(
                resolved.data
            )

            declared_id = entry.get(
                "record_id"
            )

            if (
                isinstance(
                    declared_id,
                    str,
                )
                and actual_id
                != declared_id
            ):
                errors.append(
                    "receipt reference "
                    "identity mismatch: "
                    f"expected "
                    f"{declared_id} "
                    f"but resolved "
                    f"{actual_id}"
                )

            actual_version = (
                record_version(
                    resolved.data
                )
            )

            declared_version = (
                entry.get(
                    "protocol_version"
                )
            )

            if (
                isinstance(
                    declared_version,
                    str,
                )
                and actual_version
                != declared_version
            ):
                errors.append(
                    f"receipt {actual_id} "
                    "version mismatch: "
                    f"expected "
                    f"{declared_version} "
                    f"but found "
                    f"{actual_version}"
                )

            actual_contributor = (
                receipt_contributor_id(
                    resolved.data
                )
            )

            declared_contributor = (
                entry.get(
                    "contributor_id"
                )
            )

            if (
                isinstance(
                    declared_contributor,
                    str,
                )
                and actual_contributor
                != declared_contributor
            ):
                errors.append(
                    f"receipt {actual_id} "
                    "contributor mismatch: "
                    f"expected "
                    f"{declared_contributor} "
                    f"but found "
                    f"{actual_contributor}"
                )

            actual_outcome = (
                record_outcome_id(
                    resolved.data
                )
            )

            declared_outcome = (
                entry.get(
                    "outcome_id"
                )
            )

            if (
                isinstance(
                    declared_outcome,
                    str,
                )
                and actual_outcome
                != declared_outcome
            ):
                errors.append(
                    f"receipt {actual_id} "
                    "declared outcome "
                    "mismatch: expected "
                    f"{declared_outcome} "
                    f"but found "
                    f"{actual_outcome}"
                )

            if (
                isinstance(
                    expected_outcome_id,
                    str,
                )
                and actual_outcome
                != expected_outcome_id
            ):
                errors.append(
                    f"receipt {actual_id} "
                    "outcome mismatch: "
                    f"expected "
                    f"{expected_outcome_id} "
                    f"but found "
                    f"{actual_outcome}"
                )

    resolved_interactions: dict[
        str,
        ResolvedRecord,
    ] = {}

    if isinstance(
        interaction_entries,
        list,
    ):
        for entry in (
            interaction_entries
        ):
            if not isinstance(
                entry,
                dict,
            ):
                continue

            ref = get_entry_ref(
                entry
            )

            if ref is None:
                continue

            resolved = (
                resolved_by_ref.get(
                    ref
                )
            )

            if resolved is None:
                errors.append(
                    "unresolved external "
                    f"reference: {ref}"
                )
                continue

            resolved_interactions[
                ref
            ] = resolved

            if (
                record_protocol(
                    resolved.data
                )
                !=
                "causal-contribution-interaction"
            ):
                errors.append(
                    "record type mismatch "
                    f"for {ref}: expected "
                    "causal-contribution-"
                    "interaction"
                )
                continue

            actual_id = record_id(
                resolved.data
            )

            declared_id = entry.get(
                "record_id"
            )

            if (
                isinstance(
                    declared_id,
                    str,
                )
                and actual_id
                != declared_id
            ):
                errors.append(
                    "interaction reference "
                    "identity mismatch: "
                    f"expected "
                    f"{declared_id} "
                    f"but resolved "
                    f"{actual_id}"
                )

            actual_version = (
                record_version(
                    resolved.data
                )
            )

            declared_version = (
                entry.get(
                    "protocol_version"
                )
            )

            if (
                isinstance(
                    declared_version,
                    str,
                )
                and actual_version
                != declared_version
            ):
                errors.append(
                    f"interaction "
                    f"{actual_id} "
                    "version mismatch: "
                    f"expected "
                    f"{declared_version} "
                    f"but found "
                    f"{actual_version}"
                )

            actual_outcome = (
                record_outcome_id(
                    resolved.data
                )
            )

            declared_outcome = (
                entry.get(
                    "outcome_id"
                )
            )

            if (
                isinstance(
                    declared_outcome,
                    str,
                )
                and actual_outcome
                != declared_outcome
            ):
                errors.append(
                    f"interaction "
                    f"{actual_id} "
                    "declared outcome "
                    "mismatch: expected "
                    f"{declared_outcome} "
                    f"but found "
                    f"{actual_outcome}"
                )

            if (
                isinstance(
                    expected_outcome_id,
                    str,
                )
                and actual_outcome
                != expected_outcome_id
            ):
                errors.append(
                    f"interaction "
                    f"{actual_id} "
                    "outcome mismatch: "
                    f"expected "
                    f"{expected_outcome_id} "
                    f"but found "
                    f"{actual_outcome}"
                )

    if graph_record is not None:
        graph_data = (
            graph_record.data
        )

        if (
            record_protocol(
                graph_data
            )
            !=
            "causal-contribution-graph"
        ):
            errors.append(
                "record type mismatch "
                f"for {graph_ref}: expected "
                "causal-contribution-graph"
            )

        graph_outcome = (
            record_outcome_id(
                graph_data
            )
        )

        if (
            isinstance(
                expected_outcome_id,
                str,
            )
            and graph_outcome
            != expected_outcome_id
        ):
            errors.append(
                "graph outcome mismatch: "
                f"expected "
                f"{expected_outcome_id} "
                f"but found "
                f"{graph_outcome}"
            )

        graph_nodes = (
            graph_data.get(
                "nodes",
                [],
            )
            if isinstance(
                graph_data,
                dict,
            )
            else []
        )

        if isinstance(
            graph_nodes,
            list,
        ):
            for node in graph_nodes:
                if not isinstance(
                    node,
                    dict,
                ):
                    continue

                node_type = node.get(
                    "node_type"
                )

                node_ref = node.get(
                    "ref"
                )

                if not isinstance(
                    node_ref,
                    str,
                ):
                    continue

                if (
                    node_type
                    == "contribution_receipt"
                ):
                    if (
                        node_ref
                        not in resolved_receipts
                    ):
                        errors.append(
                            "graph references "
                            "receipt not resolved "
                            "by bundle: "
                            f"{node_ref}"
                        )

                elif (
                    node_type
                    ==
                    "contribution_interaction"
                ):
                    if (
                        node_ref
                        not in
                        resolved_interactions
                    ):
                        errors.append(
                            "graph references "
                            "interaction not "
                            "resolved by bundle: "
                            f"{node_ref}"
                        )

        errors.extend(
            validate_graph_interaction_membership(
                graph_data=graph_data,
                resolved_receipts=(
                    resolved_receipts
                ),
                resolved_interactions=(
                    resolved_interactions
                ),
            )
        )

    errors.extend(
        validate_bundle_compatibility(
            bundle=bundle,
            graph_record=graph_record,
            receipt_records=list(
                resolved_receipts.values()
            ),
            interaction_records=list(
                resolved_interactions.values()
            ),
        )
    )

    return errors


def validate_graph_interaction_membership(
    graph_data: dict[str, Any],
    resolved_receipts: dict[
        str,
        ResolvedRecord,
    ],
    resolved_interactions: dict[
        str,
        ResolvedRecord,
    ],
) -> list[str]:
    errors: list[str] = []

    nodes = graph_data.get(
        "nodes",
        [],
    )

    edges = graph_data.get(
        "edges",
        [],
    )

    if not isinstance(nodes, list):
        return errors

    if not isinstance(edges, list):
        return errors

    node_map = build_node_map(nodes)

    for node in nodes:
        if not isinstance(node, dict):
            continue

        if (
            node.get("node_type")
            !=
            "contribution_interaction"
        ):
            continue

        interaction_node_id = (
            node.get("node_id")
        )

        interaction_ref = (
            node.get("ref")
        )

        if (
            not isinstance(
                interaction_node_id,
                str,
            )
            or not isinstance(
                interaction_ref,
                str,
            )
        ):
            continue

        resolved_interaction = (
            resolved_interactions.get(
                interaction_ref
            )
        )

        if (
            resolved_interaction
            is None
        ):
            continue

        actual_members = (
            interaction_contributor_ids(
                resolved_interaction.data
            )
        )

        graph_members: set[str] = (
            set()
        )

        incoming_receipt_refs: (
            set[str]
        ) = set()

        for edge in edges:
            if not isinstance(
                edge,
                dict,
            ):
                continue

            if (
                edge.get("relation")
                != "participates_in"
            ):
                continue

            if (
                edge.get("to")
                != interaction_node_id
            ):
                continue

            source_id = edge.get(
                "from"
            )

            if not isinstance(
                source_id,
                str,
            ):
                continue

            source_node = (
                node_map.get(
                    source_id
                )
            )

            if source_node is None:
                continue

            source_type = (
                source_node.get(
                    "node_type"
                )
            )

            if (
                source_type
                == "contributor"
            ):
                contributor_id = (
                    source_node.get(
                        "contributor_id"
                    )
                )

                if isinstance(
                    contributor_id,
                    str,
                ):
                    graph_members.add(
                        contributor_id
                    )

            elif (
                source_type
                ==
                "contribution_receipt"
            ):
                receipt_ref = (
                    source_node.get(
                        "ref"
                    )
                )

                if not isinstance(
                    receipt_ref,
                    str,
                ):
                    continue

                incoming_receipt_refs.add(
                    receipt_ref
                )

                resolved_receipt = (
                    resolved_receipts.get(
                        receipt_ref
                    )
                )

                if (
                    resolved_receipt
                    is None
                ):
                    continue

                contributor_id = (
                    receipt_contributor_id(
                        resolved_receipt.data
                    )
                )

                if isinstance(
                    contributor_id,
                    str,
                ):
                    graph_members.add(
                        contributor_id
                    )

        if (
            graph_members
            != actual_members
        ):
            interaction_id = (
                record_id(
                    resolved_interaction.data
                )
            )

            errors.append(
                f"interaction "
                f"{interaction_id} "
                "contributor membership "
                "mismatch: graph="
                f"{sorted(graph_members)} "
                "record="
                f"{sorted(actual_members)}"
            )

        individual_refs = (
            resolved_interaction.data.get(
                "individual_receipt_refs"
            )
        )

        if isinstance(
            individual_refs,
            list,
        ):
            declared_receipts = {
                value
                for value
                in individual_refs
                if isinstance(
                    value,
                    str,
                )
            }

            if (
                incoming_receipt_refs
                and declared_receipts
                != incoming_receipt_refs
            ):
                interaction_id = (
                    record_id(
                        resolved_interaction.data
                    )
                )

                errors.append(
                    f"interaction "
                    f"{interaction_id} "
                    "receipt membership "
                    "mismatch: graph="
                    f"{sorted(incoming_receipt_refs)} "
                    "record="
                    f"{sorted(declared_receipts)}"
                )

    return errors


def validate_bundle_compatibility(
    bundle: dict[str, Any],
    graph_record: (
        ResolvedRecord | None
    ),
    receipt_records: list[
        ResolvedRecord
    ],
    interaction_records: list[
        ResolvedRecord
    ],
) -> list[str]:
    errors: list[str] = []

    compatibility = bundle.get(
        "compatibility"
    )

    if not isinstance(
        compatibility,
        dict,
    ):
        return errors

    graph_versions = (
        compatibility.get(
            "graph_versions"
        )
    )

    receipt_versions = (
        compatibility.get(
            "receipt_versions"
        )
    )

    interaction_versions = (
        compatibility.get(
            "interaction_versions"
        )
    )

    if (
        graph_record is not None
        and isinstance(
            graph_versions,
            list,
        )
    ):
        version = record_version(
            graph_record.data
        )

        if version not in graph_versions:
            errors.append(
                "incompatible graph "
                f"version: {version}"
            )

    if isinstance(
        receipt_versions,
        list,
    ):
        for record in receipt_records:
            version = record_version(
                record.data
            )

            if (
                version
                not in receipt_versions
            ):
                errors.append(
                    "incompatible receipt "
                    f"version: {version}"
                )

    if isinstance(
        interaction_versions,
        list,
    ):
        for record in (
            interaction_records
        ):
            version = record_version(
                record.data
            )

            if (
                version
                not in
                interaction_versions
            ):
                errors.append(
                    "incompatible "
                    "interaction version: "
                    f"{version}"
                )

    return errors


# ============================================================
# v0.5 WEIGHT CROSS-RECORD
# ============================================================


def ref_entry_map(
    entries: Any,
) -> dict[str, dict[str, Any]]:
    result: dict[
        str,
        dict[str, Any],
    ] = {}

    if not isinstance(entries, list):
        return result

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        ref = entry.get("ref")

        if isinstance(ref, str):
            result[ref] = entry

    return result


def validate_weight_cross_records(
    assessment: dict[str, Any],
    resolver: RecordResolver,
) -> list[str]:
    errors: list[str] = []

    bundle_ref_block = (
        assessment.get(
            "bundle_ref",
            {},
        )
    )

    if not isinstance(
        bundle_ref_block,
        dict,
    ):
        return [
            "weight assessment "
            "bundle_ref is invalid"
        ]

    bundle_ref = (
        bundle_ref_block.get(
            "ref"
        )
    )

    if not isinstance(
        bundle_ref,
        str,
    ):
        return [
            "weight assessment "
            "bundle_ref.ref is invalid"
        ]

    resolved_bundle = (
        resolver.resolve(
            bundle_ref
        )
    )

    if resolved_bundle is None:
        return [
            "unresolved contribution "
            f"bundle reference: "
            f"{bundle_ref}"
        ]

    bundle = resolved_bundle.data

    if not isinstance(bundle, dict):
        return [
            "resolved contribution "
            "bundle is not an object"
        ]

    if (
        bundle.get("protocol")
        !=
        "causal-contribution-bundle"
    ):
        errors.append(
            "weight assessment "
            "bundle_ref resolved to "
            "unexpected protocol: "
            f"{bundle.get('protocol')}"
        )

        return errors

    declared_bundle_id = (
        bundle_ref_block.get(
            "bundle_id"
        )
    )

    actual_bundle_id = (
        bundle.get("bundle_id")
    )

    if (
        isinstance(
            declared_bundle_id,
            str,
        )
        and declared_bundle_id
        != actual_bundle_id
    ):
        errors.append(
            "weight assessment "
            "bundle identity mismatch: "
            f"expected "
            f"{declared_bundle_id} "
            f"but resolved "
            f"{actual_bundle_id}"
        )

    declared_version = (
        bundle_ref_block.get(
            "protocol_version"
        )
    )

    actual_version = bundle.get(
        "protocol_version"
    )

    if (
        isinstance(
            declared_version,
            str,
        )
        and declared_version
        != actual_version
    ):
        errors.append(
            "weight assessment "
            "bundle version mismatch: "
            f"expected "
            f"{declared_version} "
            f"but found "
            f"{actual_version}"
        )

    digest_error = (
        validate_declared_digest(
            bundle_ref_block,
            resolved_bundle,
        )
    )

    if digest_error is not None:
        errors.append(
            digest_error
        )

    assessment_outcome = (
        assessment.get(
            "outcome_ref",
            {},
        )
    )

    bundle_outcome = (
        bundle.get(
            "outcome_ref",
            {},
        )
    )

    assessment_outcome_id = (
        assessment_outcome.get(
            "outcome_id"
        )
        if isinstance(
            assessment_outcome,
            dict,
        )
        else None
    )

    bundle_outcome_id = (
        bundle_outcome.get(
            "outcome_id"
        )
        if isinstance(
            bundle_outcome,
            dict,
        )
        else None
    )

    if (
        isinstance(
            assessment_outcome_id,
            str,
        )
        and assessment_outcome_id
        != bundle_outcome_id
    ):
        errors.append(
            "weight assessment "
            "outcome mismatch: "
            f"expected "
            f"{assessment_outcome_id} "
            "but referenced bundle "
            "contains "
            f"{bundle_outcome_id}"
        )

    receipt_entries = ref_entry_map(
        bundle.get(
            "receipt_refs",
            [],
        )
    )

    interaction_entries = (
        ref_entry_map(
            bundle.get(
                "interaction_refs",
                [],
            )
        )
    )

    bundle_contributors = {
        entry.get("contributor_id")
        for entry
        in receipt_entries.values()
        if isinstance(
            entry.get(
                "contributor_id"
            ),
            str,
        )
    }

    weights = assessment.get(
        "weights",
        [],
    )

    if isinstance(weights, list):
        for weight in weights:
            if not isinstance(
                weight,
                dict,
            ):
                continue

            weight_id = weight.get(
                "weight_id",
                "<unknown>",
            )

            subject_ref = weight.get(
                "subject_ref"
            )

            subject_type = weight.get(
                "subject_type"
            )

            contributor_id = (
                weight.get(
                    "contributor_id"
                )
            )

            if not isinstance(
                subject_ref,
                str,
            ):
                continue

            if (
                subject_type
                == "contribution_receipt"
            ):
                receipt_entry = (
                    receipt_entries.get(
                        subject_ref
                    )
                )

                if receipt_entry is None:
                    errors.append(
                        f"{weight_id}: "
                        "contribution receipt "
                        "subject is not present "
                        "in referenced bundle: "
                        f"{subject_ref}"
                    )

                    continue

                bundle_contributor = (
                    receipt_entry.get(
                        "contributor_id"
                    )
                )

                if (
                    isinstance(
                        contributor_id,
                        str,
                    )
                    and isinstance(
                        bundle_contributor,
                        str,
                    )
                    and contributor_id
                    != bundle_contributor
                ):
                    errors.append(
                        f"{weight_id}: "
                        "contributor mismatch: "
                        f"expected "
                        f"{bundle_contributor} "
                        f"but found "
                        f"{contributor_id}"
                    )

            elif (
                subject_type
                ==
                "contribution_interaction"
            ):
                if (
                    subject_ref
                    not in
                    interaction_entries
                ):
                    errors.append(
                        f"{weight_id}: "
                        "contribution interaction "
                        "subject is not present "
                        "in referenced bundle: "
                        f"{subject_ref}"
                    )

            elif (
                subject_type
                == "contributor"
            ):
                if not isinstance(
                    contributor_id,
                    str,
                ):
                    errors.append(
                        f"{weight_id}: "
                        "contributor subject "
                        "requires contributor_id"
                    )

                elif (
                    contributor_id
                    not in
                    bundle_contributors
                ):
                    errors.append(
                        f"{weight_id}: "
                        "contributor is not "
                        "represented by the "
                        "referenced bundle: "
                        f"{contributor_id}"
                    )

    bundle_assessment = (
        bundle.get(
            "bundle_assessment",
            {},
        )
    )

    bundle_has_unresolved = False

    if isinstance(
        bundle_assessment,
        dict,
    ):
        unresolved_count = (
            bundle_assessment.get(
                "unresolved_reference_count"
            )
        )

        reference_coverage = (
            bundle_assessment.get(
                "reference_coverage"
            )
        )

        if (
            isinstance(
                unresolved_count,
                int,
            )
            and unresolved_count > 0
        ):
            bundle_has_unresolved = (
                True
            )

        if (
            isinstance(
                reference_coverage,
                (int, float),
            )
            and float(
                reference_coverage
            )
            < 1.0 - EPSILON
        ):
            bundle_has_unresolved = (
                True
            )

    unresolved_weight = (
        assessment.get(
            "unresolved_weight"
        )
    )

    if (
        bundle_has_unresolved
        and isinstance(
            unresolved_weight,
            (int, float),
        )
        and float(
            unresolved_weight
        )
        <= EPSILON
    ):
        errors.append(
            "unresolved contribution "
            "forced to zero while "
            "referenced bundle contains "
            "unresolved causal evidence"
        )

    return errors


# ============================================================
# CROSS-RECORD ROUTING
# ============================================================


def run_cross_record_validation(
    protocol: str,
    data: dict[str, Any],
    resolver: RecordResolver,
) -> list[str]:
    if (
        protocol
        == "causal-contribution-bundle"
    ):
        return (
            validate_bundle_cross_records(
                data,
                resolver,
            )
        )

    if (
        protocol
        ==
        "causal-contribution-weight-assessment"
    ):
        return (
            validate_weight_cross_records(
                data,
                resolver,
            )
        )

    return []


def protocol_has_cross_record_validation(
    protocol: str,
) -> bool:
    return protocol in {
        "causal-contribution-bundle",
        "causal-contribution-weight-assessment",
    }


def print_cross_record_errors(
    errors: list[str],
) -> None:
    for error in errors:
        print(
            "[cross-record-error] "
            f"{error}"
        )


# ============================================================
# PASS EXAMPLES
# ============================================================


def validate_pass_examples(
    validators: dict[
        str,
        Draft202012Validator,
    ],
    resolver: RecordResolver,
) -> tuple[int, int]:
    total = 0
    failures = 0

    print()
    print("=== PASS EXAMPLES ===")

    files = sorted(
        PASS_DIR.glob("*.yaml")
    )

    if not files:
        print(
            "[warning] no pass "
            "examples found"
        )

        return (
            total,
            failures,
        )

    for path in files:
        total += 1

        relative_path = (
            path.relative_to(
                REPO_ROOT
            )
        )

        print()
        print(
            f"[validate-pass] "
            f"{relative_path}"
        )

        try:
            data = load_yaml(path)
        except Exception as exc:
            failures += 1

            print(
                f"[yaml-error] {exc}"
            )

            continue

        (
            protocol,
            schema_validator,
        ) = resolve_validator(
            data,
            validators,
        )

        if protocol is None:
            failures += 1

            print(
                "[routing-error] "
                "missing or invalid "
                "protocol identifier"
            )

            continue

        if schema_validator is None:
            failures += 1

            print(
                "[routing-error] "
                "unsupported protocol: "
                f"{protocol}"
            )

            continue

        print(
            f"[protocol] {protocol}"
        )

        schema_errors = (
            collect_schema_errors(
                schema_validator,
                data,
            )
        )

        if schema_errors:
            failures += 1

            print_schema_errors(
                schema_errors
            )

            continue

        print("[schema-ok]")

        if not isinstance(data, dict):
            failures += 1

            print(
                "[semantic-error] "
                "document root must "
                "be an object"
            )

            continue

        semantic_errors = (
            run_semantic_validation(
                protocol,
                data,
            )
        )

        if semantic_errors:
            failures += 1

            print_semantic_errors(
                semantic_errors
            )

            continue

        print("[semantic-ok]")

        if (
            protocol_has_cross_record_validation(
                protocol
            )
        ):
            cross_errors = (
                run_cross_record_validation(
                    protocol,
                    data,
                    resolver,
                )
            )

            if cross_errors:
                failures += 1

                print_cross_record_errors(
                    cross_errors
                )

                continue

            print("[cross-record-ok]")

    return (
        total,
        failures,
    )


# ============================================================
# FAIL EXAMPLES
# ============================================================


def validate_fail_examples(
    validators: dict[
        str,
        Draft202012Validator,
    ],
    resolver: RecordResolver,
) -> tuple[
    int,
    int,
    int,
    int,
    int,
]:
    total = 0
    harness_failures = 0

    expected_schema_failures = 0
    expected_semantic_failures = 0
    expected_cross_record_failures = 0

    print()
    print("=== FAIL EXAMPLES ===")

    files = sorted(
        FAIL_DIR.glob("*.yaml")
    )

    for path in files:
        total += 1

        relative_path = (
            path.relative_to(
                REPO_ROOT
            )
        )

        print()
        print(
            f"[validate-fail] "
            f"{relative_path}"
        )

        try:
            data = load_yaml(path)
        except Exception as exc:
            harness_failures += 1

            print(
                "[yaml-error] "
                "invalid YAML prevents "
                f"validation: {exc}"
            )

            continue

        (
            protocol,
            schema_validator,
        ) = resolve_validator(
            data,
            validators,
        )

        if protocol is None:
            harness_failures += 1

            print(
                "[routing-error] "
                "missing or invalid "
                "protocol identifier"
            )

            continue

        if schema_validator is None:
            harness_failures += 1

            print(
                "[routing-error] "
                "unsupported protocol: "
                f"{protocol}"
            )

            continue

        print(
            f"[protocol] {protocol}"
        )

        schema_errors = (
            collect_schema_errors(
                schema_validator,
                data,
            )
        )

        if schema_errors:
            print_schema_errors(
                schema_errors
            )

            print(
                "[expected-schema-failure]"
            )

            expected_schema_failures += 1
            continue

        print("[schema-ok]")

        if not isinstance(data, dict):
            harness_failures += 1

            print(
                "[semantic-error] "
                "document root must "
                "be an object"
            )

            continue

        semantic_errors = (
            run_semantic_validation(
                protocol,
                data,
            )
        )

        if semantic_errors:
            print_semantic_errors(
                semantic_errors
            )

            print(
                "[expected-semantic-failure]"
            )

            expected_semantic_failures += 1
            continue

        print("[semantic-ok]")

        if (
            protocol_has_cross_record_validation(
                protocol
            )
        ):
            cross_errors = (
                run_cross_record_validation(
                    protocol,
                    data,
                    resolver,
                )
            )

            if cross_errors:
                print_cross_record_errors(
                    cross_errors
                )

                print(
                    "[expected-cross-record-failure]"
                )

                expected_cross_record_failures += 1
                continue

            print("[cross-record-ok]")

        harness_failures += 1

        print(
            "[unexpected-pass] "
            "example was expected "
            "to fail validation"
        )

    return (
        total,
        harness_failures,
        expected_schema_failures,
        expected_semantic_failures,
        expected_cross_record_failures,
    )


# ============================================================
# SUMMARY
# ============================================================


def print_summary(
    pass_total: int,
    pass_failures: int,
    fail_total: int,
    fail_harness_failures: int,
    expected_schema_failures: int,
    expected_semantic_failures: int,
    expected_cross_record_failures: int,
) -> int:
    total_examples = (
        pass_total
        + fail_total
    )

    total_failures = (
        pass_failures
        + fail_harness_failures
    )

    print()
    print("=== SUMMARY ===")

    print(
        "pass examples checked: "
        f"{pass_total}"
    )

    print(
        "fail examples checked: "
        f"{fail_total}"
    )

    print(
        "total examples checked: "
        f"{total_examples}"
    )

    print(
        "expected schema failures: "
        f"{expected_schema_failures}"
    )

    print(
        "expected semantic failures: "
        f"{expected_semantic_failures}"
    )

    print(
        "expected cross-record failures: "
        f"{expected_cross_record_failures}"
    )

    print(
        "unexpected validation failures: "
        f"{total_failures}"
    )

    if total_failures:
        print(
            "[validation-failed]"
        )

        return 1

    print("[validation-ok]")

    print(
        "All pass examples validated "
        "successfully, and all fail "
        "examples were rejected at "
        "the expected validation layer."
    )

    return 0


# ============================================================
# MAIN
# ============================================================


def main() -> int:
    print(
        "=== Causal Contribution "
        "Receipt Protocol Validation ==="
    )

    validators = load_validators()

    resolver = (
        load_record_resolver()
    )

    (
        pass_total,
        pass_failures,
    ) = validate_pass_examples(
        validators,
        resolver,
    )

    (
        fail_total,
        fail_harness_failures,
        expected_schema_failures,
        expected_semantic_failures,
        expected_cross_record_failures,
    ) = validate_fail_examples(
        validators,
        resolver,
    )

    return print_summary(
        pass_total=pass_total,
        pass_failures=pass_failures,
        fail_total=fail_total,
        fail_harness_failures=(
            fail_harness_failures
        ),
        expected_schema_failures=(
            expected_schema_failures
        ),
        expected_semantic_failures=(
            expected_semantic_failures
        ),
        expected_cross_record_failures=(
            expected_cross_record_failures
        ),
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
