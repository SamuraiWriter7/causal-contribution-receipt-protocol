````markdown
# Changelog

All notable changes to the Causal Contribution Receipt Protocol are documented in this file.

The protocol evolves incrementally from evidence-backed individual contribution records toward auditable relative contribution assessment.

The protocol intentionally maintains the following boundary:

```text
Contribution
≠
Attribution
≠
Entitlement
≠
Royalty Allocation
≠
Settlement
````

---

# v0.5 — Contribution Weight Assessment

## Added

### Contribution Weight Assessment

Added a new machine-readable layer for estimating relative contribution weight from validated contribution evidence.

New schema:

`schemas/contribution-weight-assessment.schema.json`

The assessment supports:

* contribution receipt subjects
* contribution interaction subjects
* contributor subjects
* estimated contribution weight
* lower and upper bounds
* confidence
* evidence references
* assessment basis
* unresolved contribution
* explicit assessment methods

Supported methods:

```text
evidence_weighted
counterfactual_marginal
coalition_adjusted
shapley_approximation
hybrid
```

---

### Explicit uncertainty representation

Contribution weight is no longer represented as false precision.

Each weight may include:

```text
lower_bound
estimated_weight
upper_bound
confidence
```

The semantic relationship is:

```text
lower_bound
<=
estimated_weight
<=
upper_bound
```

This allows weaker evidence to produce wider uncertainty ranges rather than artificially precise scores.

---

### Unresolved contribution

Added:

```yaml
unresolved_weight:
```

to preserve contribution that cannot currently be assigned with sufficient evidential support.

Normalized assessments follow:

```text
sum(known estimated weights)
+
unresolved_weight
=
1.0
```

This formalizes the principle:

```text
UNKNOWN
≠
ZERO
```

and prevents unknown contribution from being silently redistributed among known contributors.

---

### Interaction-aware weighting

Contribution Interaction weight remains distinguishable from individual contributor weight.

The protocol now explicitly rejects structures that absorb coalition contribution directly into one individual.

```text
Individual Weight
≠
Interaction Weight
```

---

### Shapley-assisted assessment

Added support for:

```text
shapley_approximation
```

as an optional relative contribution estimation method.

Shapley-derived values are treated as evidence-supported estimates rather than absolute causal truth.

The protocol explicitly preserves the distinction:

```text
Shapley Estimate
≠
Absolute Causal Truth
```

---

## Added Pass Examples

`examples/pass/basic-contribution-weight-assessment.example.yaml`

`examples/pass/coalition-adjusted-weight-assessment.example.yaml`

`examples/pass/partial-weight-assessment.example.yaml`

`examples/pass/shapley-assisted-weight-assessment.example.yaml`

These examples cover:

* basic evidence-weighted contribution
* multi-agent coalition contribution
* interaction weight preservation
* unresolved contribution
* uncertainty ranges
* partial causal evidence
* Shapley-assisted estimation

---

## Added Negative Cases

`examples/fail/weight-sum-exceeds-one.example.yaml`

Rejects known contribution weights whose total exceeds the available normalized contribution space.

---

`examples/fail/unknown-weight-forced-to-zero.example.yaml`

Rejects an assessment that sets:

```text
unresolved_weight = 0
```

when the referenced Contribution Bundle still contains unresolved causal evidence.

---

`examples/fail/interaction-weight-assigned-to-individual.example.yaml`

Rejects direct absorption of interaction contribution into an individual contribution subject.

---

`examples/fail/weight-implies-entitlement.example.yaml`

Rejects economic entitlement fields inside the Contribution Weight Assessment structure.

This preserves:

```text
Contribution Weight
≠
Economic Entitlement
```

---

`examples/fail/weight-outcome-mismatch.example.yaml`

Rejects a Weight Assessment whose declared outcome differs from the outcome represented by its referenced Contribution Bundle.

---

`examples/fail/unsupported-weight-method.example.yaml`

Rejects assessment methods outside the explicitly supported v0.5 method set.

---

## Validation

Extended:

`scripts/validate_examples.py`

with v0.5 Weight Assessment validation.

New semantic checks include:

* duplicate `weight_id`
* duplicate contribution subjects
* lower-bound consistency
* upper-bound consistency
* total estimated weight validation
* `known_weight` consistency
* `known_weight + unresolved_weight = 1.0`
* subject count consistency
* interaction subject count consistency
* interaction-to-individual absorption rejection

New cross-record checks include:

* Contribution Bundle resolution
* Bundle identity consistency
* Bundle protocol version consistency
* assessment outcome consistency
* contribution receipt subject membership
* contribution interaction subject membership
* contributor identity consistency
* unresolved Bundle evidence versus `unresolved_weight`

Contribution Bundles stored under:

`examples/pass/`

can now be resolved as:

```text
trace://contribution-bundles/bundle-001
trace://contribution-bundles/bundle-002
trace://contribution-bundles/bundle-003
```

for v0.5 cross-record validation.

---

## Documentation

Updated:

`docs/core-invariants.md`

to v0.5.

The invariant set now extends through:

```text
CCR-INV-032
```

New v0.5 invariants cover:

* Contribution Weight versus entitlement
* individual versus interaction weight
* unresolved contribution preservation
* evidence-backed weighting
* outcome scope
* Counterfactual and Shapley limitations
* evidential precision
* downstream economic boundary separation

Updated:

`docs/contribution-model.md`

to describe the complete model from individual Contribution Receipts through Contribution Weight Assessment.

Updated:

`README.md`

to expose the v0.1–v0.5 architecture, validation model, examples, protocol boundary, and current design principles.

---

## Core v0.5 Principle

```text
Evidence
   ↓
Contribution
   ↓
Interaction
   ↓
Graph
   ↓
Cross-Record Validation
   ↓
Weight Assessment
```

The protocol stops before:

```text
Attribution
   ↓
Entitlement
   ↓
Royalty Allocation
   ↓
Settlement
```

---

# v0.4 — Cross-Record Consistency and Provenance

## Added

### Contribution Bundle

Added:

`schemas/contribution-bundle.schema.json`

to connect Contribution Graphs with external Contribution Receipts, Contribution Interactions, evidence records, and outcome references.

The central question introduced in v0.4 is:

> Do independently stored contribution records actually describe the same contribution context?

---

### Cross-record validation

Added validation across:

```text
Graph
Receipt
Interaction
Evidence
Outcome
```

Checks include:

* record resolution
* outcome consistency
* contributor consistency
* interaction membership consistency
* receipt reference consistency
* protocol version compatibility
* graph-to-record consistency

---

### Content provenance

Added optional SHA-256 digest pinning for referenced records.

Where a digest is declared:

```text
Declared Digest
       =
SHA-256 of exact referenced content
```

This allows a Bundle to identify the exact record content that was validated.

---

### Partial provenance

Added support for explicitly incomplete evidence sets.

A Bundle may declare:

```text
reference_coverage
digest_coverage
unresolved_reference_count
```

Partial evidence is not automatically invalid.

Missing evidence must instead remain explicit.

---

## Added Resolver Registry

Added:

`examples/records/index.yaml`

to map logical trace references to local fixture files.

Record fixtures are organized under:

`examples/records/graphs/`

`examples/records/receipts/`

`examples/records/interactions/`

`examples/records/evidence/`

---

## Added Pass Examples

`examples/pass/consistent-contribution-bundle.example.yaml`

`examples/pass/multi-agent-contribution-bundle.example.yaml`

`examples/pass/partial-evidence-bundle.example.yaml`

These demonstrate:

* fully consistent contribution records
* multi-agent contribution bundles
* interaction membership
* exact digest validation
* intentionally unresolved evidence

---

## Added Negative Cases

Added cross-record failure cases for:

* outcome mismatch
* contributor mismatch
* interaction member mismatch
* missing external records
* receipt reference mismatch
* digest mismatch

Representative files include:

`examples/fail/cross-record-outcome-mismatch.example.yaml`

`examples/fail/cross-record-contributor-mismatch.example.yaml`

`examples/fail/interaction-member-mismatch.example.yaml`

`examples/fail/missing-external-record.example.yaml`

`examples/fail/receipt-ref-mismatch.example.yaml`

`examples/fail/record-digest-mismatch.example.yaml`

---

## Added Digest Maintenance Tool

Added:

`scripts/update_bundle_digests.py`

The script:

* resolves records from `examples/records/index.yaml`
* calculates SHA-256 over raw record bytes
* updates already-declared digests in pass Bundles
* preserves partial provenance
* does not automatically add missing digests
* does not modify fail examples
* rejects unsafe path traversal

Recommended workflow:

```bash
python scripts/update_bundle_digests.py
python scripts/validate_examples.py
```

---

## Validation

Extended:

`scripts/validate_examples.py`

with resolver-backed Cross-Record Validation.

The validation architecture became:

```text
Schema
  ↓
Semantic
  ↓
Graph
  ↓
Cross-Record
```

---

## Core v0.4 Principle

```text
Internally valid record
≠
cross-record consistent system
```

v0.4 verifies that records not only validate individually but also agree with one another.

---

# v0.3 — Contribution Graph

## Added

### Contribution Graph schema

Added:

`schemas/contribution-graph.schema.json`

to represent causal and evidential relationships among contribution records.

Supported node concepts include:

```text
contributor
contribution_receipt
contribution_interaction
evidence
decision
outcome
unresolved_segment
```

Supported relationship concepts include:

```text
produced
supported_by
used_by
participates_in
influenced
verified_by
blocked_by
contributed_to
```

---

### Directed contribution paths

Added explicit paths connecting contribution subjects to identifiable outcomes.

The graph represents:

```text
Contributor / Receipt
        ↓
Evidence / Interaction
        ↓
Decision
        ↓
Outcome
```

---

### Unresolved causal segments

Added:

```text
unresolved_segment
```

to represent known gaps in causal evidence.

This establishes the foundation for the later v0.5 principle:

```text
UNKNOWN
≠
ZERO
```

---

## Added Graph Validation

Added semantic checks for:

* duplicate node IDs
* duplicate edge IDs
* duplicate path IDs
* dangling node references
* invalid edge directions
* path continuity
* outcome termination
* causal cycles
* graph assessment count consistency

Contribution Graphs are acyclic by default.

---

## Added Pass Examples

`examples/pass/linear-contribution-graph.example.yaml`

`examples/pass/interaction-contribution-graph.example.yaml`

`examples/pass/partial-evidence-graph.example.yaml`

---

## Added Negative Cases

Added failure examples for:

* dangling node references
* duplicate node IDs
* invalid edge direction
* causal cycles
* graph assessment count mismatch

Representative files include:

`examples/fail/dangling-node-reference.example.yaml`

`examples/fail/duplicate-node-id.example.yaml`

`examples/fail/invalid-edge-direction.example.yaml`

`examples/fail/causal-cycle.example.yaml`

`examples/fail/graph-assessment-count-mismatch.example.yaml`

---

## Core v0.3 Principle

Contribution is not merely a set of isolated scores.

It can be represented as a causal structure:

```text
Contribution
     ↓
Causal Path
     ↓
Outcome
```

---

# v0.2 — Interaction and Coalition Contribution

## Added

### Contribution Interaction schema

Added:

`schemas/contribution-interaction.schema.json`

to represent contribution that emerges between multiple contributors.

Supported interaction types:

```text
complementary
redundant
synergistic
substitutive
blocking
```

---

### Coalition contribution

Added explicit representation of coalition-level contribution.

The protocol now distinguishes:

```text
Individual Contribution
≠
Coalition Contribution
```

Interaction value is not automatically assigned to one participant.

---

### Interaction assessment

Added interaction assessment dimensions including:

```text
joint_effect
synergy
dependency
evidence_strength
```

---

### Extended counterfactual methods

Added support for:

```text
leave_group_out
pairwise_ablation
substitution_test
```

These allow the protocol to evaluate relationships that cannot be captured by individual `leave_one_out` tests.

---

## Added Pass Examples

`examples/pass/synergistic-agent-interaction.example.yaml`

`examples/pass/substitutive-agent-interaction.example.yaml`

`examples/pass/coalition-contribution.example.yaml`

---

## Added Negative Cases

Added interaction failure examples for:

* missing contributors
* missing evidence
* invalid interaction scores
* improper assignment of coalition value to individuals

Representative files include:

`examples/fail/interaction-missing-contributors.example.yaml`

`examples/fail/interaction-missing-evidence.example.yaml`

`examples/fail/invalid-interaction-score.example.yaml`

`examples/fail/individual-claims-coalition-value.example.yaml`

---

## Core v0.2 Principle

```text
A alone
+
B alone
```

does not always explain:

```text
A + B together
```

Interaction itself may contribute value.

---

# v0.1 — Individual Contribution Receipt

## Added

### Initial protocol

Introduced the Causal Contribution Receipt Protocol.

The initial version records one contributor's evidence-backed contribution to one identifiable outcome.

Core structure:

```text
Contributor
    ↓
Role
    ↓
Evidence
    ↓
Assessment
    ↓
Optional Counterfactual
    ↓
Contribution Class
    ↓
Outcome
```

---

### Initial schema

Added:

`schemas/causal-contribution-receipt.schema.json`

The schema supports contributor types including:

```text
human
agent
dataset
source
tool
service
```

---

### Contribution assessment dimensions

Introduced:

```text
work
causal_impact
necessity
quality_impact
evidence_strength
```

The protocol established the foundational distinction:

```text
Work
≠
Contribution
```

---

### Individual counterfactual assessment

Added optional:

```text
leave_one_out
```

counterfactual measurement.

The protocol records observed outcome changes without treating those measurements as absolute causal truth.

---

### Contribution classes

Added:

```text
critical
high
medium
low
incidental
```

Contribution classes are descriptive.

They do not directly establish economic entitlement.

---

## Added Pass Examples

`examples/pass/critical-agent-contribution.example.yaml`

`examples/pass/human-problem-definition.example.yaml`

`examples/pass/dataset-evidence-contribution.example.yaml`

---

## Added Negative Cases

Added initial invalid examples for:

* missing outcome
* missing evidence
* invalid assessment ranges
* contribution directly implying settlement

Representative files include:

`examples/fail/missing-outcome.example.yaml`

`examples/fail/missing-evidence.example.yaml`

`examples/fail/invalid-assessment-range.example.yaml`

`examples/fail/contribution-implies-settlement.example.yaml`

---

## Added Documentation

Added:

`docs/core-invariants.md`

Added:

`docs/contribution-model.md`

---

## Core v0.1 Principle

> Measure what changed because a contributor was present, not merely how much activity the contributor performed.

---

# Protocol Progression

The protocol evolution through v0.5 can be summarized as:

```text
v0.1
Who contributed?
    ↓
Individual Contribution Receipt

v0.2
What value emerged between contributors?
    ↓
Contribution Interaction

v0.3
How did contribution flow?
    ↓
Contribution Graph

v0.4
Do the records agree?
    ↓
Cross-Record Consistency

v0.5
How much relative contribution
does the evidence support?
    ↓
Contribution Weight Assessment
```

The next downstream questions remain intentionally separate:

```text
Who or what should receive attribution?

Does that attribution create entitlement?

How should value be allocated?

How should settlement occur?
```

Those questions are outside the responsibility of the Causal Contribution Receipt Protocol through v0.5.

```
```
