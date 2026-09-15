from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

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
    "causal-contribution-graph": (
        REPO_ROOT
        / "schemas"
        / "contribution-graph.schema.json"
    ),
}


EPSILON = 1e-9


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


def approximately_equal(a: float, b: float) -> bool:
    return math.isclose(
        a,
        b,
        rel_tol=EPSILON,
        abs_tol=EPSILON,
    )


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


def print_schema_errors(errors: list[Any]) -> None:
    for error in errors:
        path = format_error_path(error)

        print(
            f"[schema-error] "
            f"{path}: {error.message}"
        )


# ---------------------------------------------------------------------------
# Semantic validation: Contribution Receipt
# ---------------------------------------------------------------------------


def validate_receipt_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    counterfactual = data.get("counterfactual")

    if isinstance(counterfactual, dict):
        baseline = counterfactual.get("baseline", {})
        without = counterfactual.get(
            "without_contributor",
            {},
        )

        baseline_score = baseline.get("quality_score")
        without_score = without.get("quality_score")
        observed_delta = counterfactual.get("observed_delta")

        if (
            isinstance(baseline_score, (int, float))
            and isinstance(without_score, (int, float))
            and isinstance(observed_delta, (int, float))
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
                    "counterfactual.observed_delta "
                    f"expected {expected_delta:.12g} "
                    f"but found {observed_delta}"
                )

    return errors


# ---------------------------------------------------------------------------
# Semantic validation: Contribution Interaction
# ---------------------------------------------------------------------------


def validate_interaction_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    contributors = data.get("contributors", [])

    contributor_ids: list[str] = []

    if isinstance(contributors, list):
        for contributor in contributors:
            if not isinstance(contributor, dict):
                continue

            contributor_id = contributor.get("contributor_id")

            if isinstance(contributor_id, str):
                contributor_ids.append(contributor_id)

    seen_contributors: set[str] = set()

    for contributor_id in contributor_ids:
        if contributor_id in seen_contributors:
            errors.append(
                f"duplicate contributor_id: {contributor_id}"
            )
        else:
            seen_contributors.add(contributor_id)

    counterfactual = data.get("counterfactual")

    if isinstance(counterfactual, dict):
        method = counterfactual.get("method")

        if (
            method in {
                "pairwise_ablation",
                "substitution_test",
            }
            and len(contributor_ids) != 2
        ):
            errors.append(
                f"{method} requires exactly 2 contributors "
                f"but found {len(contributor_ids)}"
            )

        baseline = counterfactual.get("baseline", {})
        comparison = counterfactual.get("comparison", {})

        baseline_score = baseline.get("quality_score")
        comparison_score = comparison.get("quality_score")
        observed_delta = counterfactual.get("observed_delta")

        if (
            isinstance(baseline_score, (int, float))
            and isinstance(comparison_score, (int, float))
            and isinstance(observed_delta, (int, float))
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
                    "counterfactual.observed_delta "
                    f"expected {expected_delta:.12g} "
                    f"but found {observed_delta}"
                )

    return errors


# ---------------------------------------------------------------------------
# Semantic validation: Contribution Graph
# ---------------------------------------------------------------------------


def duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)

    return sorted(duplicates)


def build_node_map(
    nodes: list[Any],
) -> dict[str, dict[str, Any]]:
    node_map: dict[str, dict[str, Any]] = {}

    for node in nodes:
        if not isinstance(node, dict):
            continue

        node_id = node.get("node_id")

        if (
            isinstance(node_id, str)
            and node_id not in node_map
        ):
            node_map[node_id] = node

    return node_map


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
        and isinstance(node.get("node_id"), str)
    ]

    edge_ids = [
        edge["edge_id"]
        for edge in edges
        if isinstance(edge, dict)
        and isinstance(edge.get("edge_id"), str)
    ]

    path_ids = [
        path["path_id"]
        for path in paths
        if isinstance(path, dict)
        and isinstance(path.get("path_id"), str)
    ]

    for node_id in duplicate_values(node_ids):
        errors.append(
            f"duplicate node_id: {node_id}"
        )

    for edge_id in duplicate_values(edge_ids):
        errors.append(
            f"duplicate edge_id: {edge_id}"
        )

    for path_id in duplicate_values(path_ids):
        errors.append(
            f"duplicate path_id: {path_id}"
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

        edge_id = edge.get("edge_id", "<unknown>")
        source = edge.get("from")
        destination = edge.get("to")

        if isinstance(source, str) and source not in node_ids:
            errors.append(
                f"edge {edge_id} references unknown "
                f"source node: {source}"
            )

        if (
            isinstance(destination, str)
            and destination not in node_ids
        ):
            errors.append(
                f"edge {edge_id} references unknown "
                f"destination node: {destination}"
            )

    for path in paths:
        if not isinstance(path, dict):
            continue

        path_id = path.get("path_id", "<unknown>")
        path_node_ids = path.get("node_ids", [])

        if not isinstance(path_node_ids, list):
            continue

        for node_id in path_node_ids:
            if (
                isinstance(node_id, str)
                and node_id not in node_ids
            ):
                errors.append(
                    f"path {path_id} references unknown "
                    f"node: {node_id}"
                )

    return errors


def validate_graph_outcome(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    nodes = data.get("nodes", [])
    graph_outcome = data.get("outcome", {})

    outcome_ref = graph_outcome.get("outcome_ref")

    matching_outcome_nodes = [
        node
        for node in nodes
        if isinstance(node, dict)
        and node.get("node_type") == "outcome"
        and node.get("ref") == outcome_ref
    ]

    if not matching_outcome_nodes:
        errors.append(
            "graph outcome does not resolve to an "
            "outcome node with matching outcome_ref"
        )

    return errors


def validate_edge_directions(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    node_map = build_node_map(nodes)

    for edge in edges:
        if not isinstance(edge, dict):
            continue

        edge_id = edge.get("edge_id", "<unknown>")
        source_id = edge.get("from")
        destination_id = edge.get("to")
        relation = edge.get("relation")

        if (
            not isinstance(source_id, str)
            or not isinstance(destination_id, str)
        ):
            continue

        source = node_map.get(source_id)
        destination = node_map.get(destination_id)

        if source is None or destination is None:
            continue

        source_type = source.get("node_type")
        destination_type = destination.get("node_type")

        # Outcome is terminal in v0.3 causal graphs.
        if source_type == "outcome":
            errors.append(
                f"edge {edge_id} has invalid causal direction: "
                f"outcome node {source_id} cannot be a source"
            )
            continue

        if relation == "contributed_to":
            if destination_type != "outcome":
                errors.append(
                    f"invalid edge direction for contributed_to: "
                    f"{source_type} -> {destination_type}"
                )

        elif relation == "participates_in":
            if destination_type != "contribution_interaction":
                errors.append(
                    f"invalid edge direction for participates_in: "
                    f"{source_type} -> {destination_type}"
                )

            if source_type not in {
                "contributor",
                "contribution_receipt",
            }:
                errors.append(
                    "participates_in must originate from "
                    "contributor or contribution_receipt"
                )

        elif relation == "supported_by":
            if destination_type != "evidence":
                errors.append(
                    f"invalid edge direction for supported_by: "
                    f"{source_type} -> {destination_type}"
                )

        elif relation == "verified_by":
            if destination_type != "evidence":
                errors.append(
                    f"invalid edge direction for verified_by: "
                    f"{source_type} -> {destination_type}"
                )

        elif relation == "used_by":
            if source_type not in {
                "evidence",
                "decision",
                "contribution_receipt",
                "contribution_interaction",
                "unresolved_segment",
            }:
                errors.append(
                    f"invalid source type for used_by: "
                    f"{source_type}"
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
        (edge.get("from"), edge.get("to"))
        for edge in edges
        if isinstance(edge, dict)
        and isinstance(edge.get("from"), str)
        and isinstance(edge.get("to"), str)
    }

    graph_outcome_ref = (
        data.get("outcome", {}).get("outcome_ref")
    )

    for path in paths:
        if not isinstance(path, dict):
            continue

        path_id = path.get("path_id", "<unknown>")
        node_ids = path.get("node_ids", [])

        if not isinstance(node_ids, list):
            continue

        for index in range(len(node_ids) - 1):
            source = node_ids[index]
            destination = node_ids[index + 1]

            if (source, destination) not in directed_edges:
                errors.append(
                    f"path {path_id} is not contiguous: "
                    f"missing edge {source} -> {destination}"
                )

        if node_ids:
            final_node = node_map.get(node_ids[-1])

            if final_node is not None:
                if final_node.get("node_type") != "outcome":
                    errors.append(
                        f"path {path_id} does not terminate "
                        "at an outcome node"
                    )

                elif final_node.get("ref") != graph_outcome_ref:
                    errors.append(
                        f"path {path_id} terminates at an "
                        "outcome different from graph outcome"
                    )

    return errors


def find_cycle(
    data: dict[str, Any],
) -> list[str] | None:
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    node_map = build_node_map(nodes)

    adjacency: dict[str, list[str]] = {
        node_id: []
        for node_id in node_map
    }

    for edge in edges:
        if not isinstance(edge, dict):
            continue

        source = edge.get("from")
        destination = edge.get("to")

        if (
            isinstance(source, str)
            and isinstance(destination, str)
            and source in adjacency
            and destination in adjacency
        ):
            adjacency[source].append(destination)

    state: dict[str, int] = {
        node_id: 0
        for node_id in adjacency
    }

    stack: list[str] = []
    stack_index: dict[str, int] = {}

    def dfs(node_id: str) -> list[str] | None:
        state[node_id] = 1
        stack_index[node_id] = len(stack)
        stack.append(node_id)

        for neighbor in adjacency[node_id]:
            if state[neighbor] == 0:
                cycle = dfs(neighbor)

                if cycle is not None:
                    return cycle

            elif state[neighbor] == 1:
                start = stack_index[neighbor]

                return (
                    stack[start:]
                    + [neighbor]
                )

        stack.pop()
        stack_index.pop(node_id, None)
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

    assessment = data.get("graph_assessment")

    if not isinstance(assessment, dict):
        return errors

    edges = data.get("edges", [])
    nodes = data.get("nodes", [])

    status_counts = {
        "verified": 0,
        "partial": 0,
        "unresolved": 0,
    }

    for edge in edges:
        if not isinstance(edge, dict):
            continue

        status = edge.get("verification_status")

        if status in status_counts:
            status_counts[status] += 1

    unresolved_segment_count = sum(
        1
        for node in nodes
        if isinstance(node, dict)
        and node.get("node_type") == "unresolved_segment"
    )

    expected_fields = {
        "verified_edge_count": status_counts["verified"],
        "partial_edge_count": status_counts["partial"],
        "unresolved_edge_count": status_counts["unresolved"],
        "unresolved_segment_count": unresolved_segment_count,
    }

    for field, expected in expected_fields.items():
        actual = assessment.get(field)

        if actual is None:
            continue

        if actual != expected:
            errors.append(
                f"graph_assessment.{field} "
                f"expected {expected} but found {actual}"
            )

    return errors


def validate_graph_semantics(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    validators: list[
        Callable[[dict[str, Any]], list[str]]
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
        errors.extend(validator(data))

    return errors


# ---------------------------------------------------------------------------
# Semantic routing
# ---------------------------------------------------------------------------


SEMANTIC_VALIDATORS: dict[
    str,
    Callable[[dict[str, Any]], list[str]],
] = {
    "causal-contribution-receipt":
        validate_receipt_semantics,

    "causal-contribution-interaction":
        validate_interaction_semantics,

    "causal-contribution-graph":
        validate_graph_semantics,
}


def run_semantic_validation(
    protocol: str,
    data: dict[str, Any],
) -> list[str]:
    validator = SEMANTIC_VALIDATORS.get(protocol)

    if validator is None:
        return [
            f"no semantic validator registered "
            f"for protocol: {protocol}"
        ]

    return validator(data)


def print_semantic_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"[semantic-error] {error}")


# ---------------------------------------------------------------------------
# Example validation
# ---------------------------------------------------------------------------


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

        protocol, schema_validator = resolve_validator(
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

        if schema_validator is None:
            failures += 1
            print(
                "[routing-error] "
                f"unsupported protocol: {protocol}"
            )
            continue

        print(f"[protocol] {protocol}")

        schema_errors = collect_schema_errors(
            schema_validator,
            data,
        )

        if schema_errors:
            failures += 1
            print_schema_errors(schema_errors)
            continue

        print("[schema-ok]")

        if not isinstance(data, dict):
            failures += 1
            print(
                "[semantic-error] "
                "document root must be an object"
            )
            continue

        semantic_errors = run_semantic_validation(
            protocol,
            data,
        )

        if semantic_errors:
            failures += 1
            print_semantic_errors(semantic_errors)
            continue

        print("[semantic-ok]")

    return total, failures


def validate_fail_examples(
    validators: dict[str, Draft202012Validator],
) -> tuple[int, int, int, int]:
    total = 0
    harness_failures = 0
    expected_schema_failures = 0
    expected_semantic_failures = 0

    print()
    print("=== FAIL EXAMPLES ===")

    files = sorted(FAIL_DIR.glob("*.yaml"))

    if not files:
        print("[warning] no fail examples found")

        return (
            total,
            harness_failures,
            expected_schema_failures,
            expected_semantic_failures,
        )

    for path in files:
        total += 1

        relative_path = path.relative_to(REPO_ROOT)

        print()
        print(f"[validate-fail] {relative_path}")

        try:
            data = load_yaml(path)
        except Exception as exc:
            harness_failures += 1
            print(
                "[yaml-error] "
                f"invalid YAML prevents validation: {exc}"
            )
            continue

        protocol, schema_validator = resolve_validator(
            data,
            validators,
        )

        if protocol is None:
            harness_failures += 1
            print(
                "[routing-error] "
                "missing or invalid protocol identifier"
            )
            continue

        if schema_validator is None:
            harness_failures += 1
            print(
                "[routing-error] "
                f"unsupported protocol: {protocol}"
            )
            continue

        print(f"[protocol] {protocol}")

        schema_errors = collect_schema_errors(
            schema_validator,
            data,
        )

        if schema_errors:
            print_schema_errors(schema_errors)
            print("[expected-schema-failure]")

            expected_schema_failures += 1
            continue

        print("[schema-ok]")

        if not isinstance(data, dict):
            harness_failures += 1
            print(
                "[semantic-error] "
                "document root must be an object"
            )
            continue

        semantic_errors = run_semantic_validation(
            protocol,
            data,
        )

        if semantic_errors:
            print_semantic_errors(semantic_errors)
            print("[expected-semantic-failure]")

            expected_semantic_failures += 1
            continue

        harness_failures += 1

        print("[semantic-ok]")
        print(
            "[unexpected-pass] "
            "example was expected to fail validation"
        )

    return (
        total,
        harness_failures,
        expected_schema_failures,
        expected_semantic_failures,
    )


def print_summary(
    pass_total: int,
    pass_failures: int,
    fail_total: int,
    fail_harness_failures: int,
    expected_schema_failures: int,
    expected_semantic_failures: int,
) -> int:
    total_examples = pass_total + fail_total

    total_failures = (
        pass_failures
        + fail_harness_failures
    )

    print()
    print("=== SUMMARY ===")

    print(f"pass examples checked: {pass_total}")
    print(f"fail examples checked: {fail_total}")
    print(f"total examples checked: {total_examples}")

    print(
        "expected schema failures: "
        f"{expected_schema_failures}"
    )

    print(
        "expected semantic failures: "
        f"{expected_semantic_failures}"
    )

    print(
        "unexpected validation failures: "
        f"{total_failures}"
    )

    if total_failures:
        print("[validation-failed]")
        return 1

    print("[validation-ok]")
    print(
        "All pass examples passed schema and semantic "
        "validation, and all fail examples were rejected "
        "as expected."
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

    (
        fail_total,
        fail_harness_failures,
        expected_schema_failures,
        expected_semantic_failures,
    ) = validate_fail_examples(validators)

    return print_summary(
        pass_total=pass_total,
        pass_failures=pass_failures,
        fail_total=fail_total,
        fail_harness_failures=fail_harness_failures,
        expected_schema_failures=expected_schema_failures,
        expected_semantic_failures=expected_semantic_failures,
    )


if __name__ == "__main__":
    raise SystemExit(main())
