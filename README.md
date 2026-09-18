````markdown
# causal-contribution-receipt-protocol

A machine-readable protocol for tracing and evaluating causal contribution across humans, AI agents, data, and evidence for auditable attribution and value allocation.

**Current version: v0.5**

---

## Overview

The Causal Contribution Receipt Protocol (CCRP) provides a machine-readable structure for answering a difficult question:

> What actually contributed to an outcome, through what causal path, and with how much evidential support?

Modern AI systems increasingly produce outcomes through combinations of:

- humans
- AI agents
- datasets
- source material
- tools
- services
- auditors
- routers
- integrators
- multi-agent interactions

Traditional usage accounting can tell us:

```text
who ran
how long they ran
how many tokens they used
how much compute they consumed
````

But those measurements do not necessarily tell us:

```text
what actually mattered
```

This protocol separates:

```text
Work
≠
Contribution
```

and, equally importantly:

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
```

The protocol focuses on making contribution **observable, evidence-backed, structurally consistent, and auditable** before downstream economic or governance systems decide what rights or payments follow.

---

## Why This Protocol Exists

Consider two AI agents:

```text
Agent A
1,000,000 tokens
Produces mostly redundant reasoning

Agent B
300 tokens
Detects one critical false assumption
Prevents an incorrect final result
```

Traditional activity accounting may make Agent A appear more important.

Causal contribution analysis may reach the opposite conclusion.

The protocol therefore asks:

> What changed because a contributor was present?

rather than:

> How much activity did the contributor perform?

---

# Protocol Evolution

The protocol currently develops through five layers.

```text
v0.1
Individual Contribution Receipt
        ↓
v0.2
Interaction / Coalition Contribution
        ↓
v0.3
Contribution Graph
        ↓
v0.4
Cross-Record Consistency
        ↓
v0.5
Contribution Weight Assessment
```

Each version adds a different question.

| Version | Layer                                | Primary Question                                                   |
| ------- | ------------------------------------ | ------------------------------------------------------------------ |
| v0.1    | Individual Contribution Receipt      | Who contributed to this outcome?                                   |
| v0.2    | Interaction / Coalition Contribution | What value emerged between contributors?                           |
| v0.3    | Contribution Graph                   | How did contribution flow toward the outcome?                      |
| v0.4    | Cross-Record Consistency             | Do the independent records describe the same contribution context? |
| v0.5    | Contribution Weight Assessment       | How much relative contribution does the evidence support?          |

---

# v0.1 — Individual Contribution Receipt

v0.1 records one contributor's evidence-backed contribution to one identifiable outcome.

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

The receipt records five contribution-related dimensions:

```text
work
causal_impact
necessity
quality_impact
evidence_strength
```

Example:

```yaml
assessment:
  work: 0.12
  causal_impact: 0.82
  necessity: 0.74
  quality_impact: 0.91
  evidence_strength: 0.96
```

These dimensions are intentionally separate.

The protocol does not assume:

```text
more work
=
more contribution
```

### Schema

`schemas/causal-contribution-receipt.schema.json`

---

# v0.2 — Interaction / Coalition Contribution

Individual receipts are not enough when contributors create value together.

For example:

```text
A alone → small effect
B alone → small effect

A + B → large effect
```

The additional value may belong to the interaction itself.

v0.2 therefore represents contribution interactions such as:

```text
complementary
redundant
synergistic
substitutive
blocking
```

Conceptually:

```text
Contributor A
      \
       \
        → Interaction → Outcome
       /
      /
Contributor B
```

The protocol preserves:

```text
Individual Contribution
≠
Interaction Contribution
```

Interaction contribution is not automatically divided among individual participants.

### Schema

`schemas/contribution-interaction.schema.json`

---

# v0.3 — Contribution Graph

v0.3 connects contribution claims into a directed causal graph.

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

Example:

```text
Retriever Receipt ─┐
                   ├→ Interaction
Verifier Receipt ──┘
                        ↓
                    Evidence
                        ↓
                     Decision
                        ↓
                     Outcome
```

The graph allows the protocol to move from:

```text
isolated contribution claims
```

to:

```text
causal contribution structure
```

The graph validator checks properties such as:

* duplicate node identifiers
* dangling references
* invalid causal directions
* path continuity
* outcome termination
* graph assessment counts
* causal cycles

The default model is a DAG.

Unmodeled causal cycles are rejected.

### Schema

`schemas/contribution-graph.schema.json`

---

# v0.4 — Cross-Record Consistency

A graph can be internally valid while still referring to external records that contradict it.

v0.4 introduces the Contribution Bundle.

Its central question is:

> Do the graph, receipts, interactions, evidence, and outcome references actually tell the same story?

The validation stack becomes:

```text
Schema Validation
        ↓
Semantic Validation
        ↓
Graph Validation
        ↓
Cross-Record Validation
```

v0.4 verifies relationships including:

```text
Bundle Outcome
      =
Graph Outcome
      =
Receipt Outcome
      =
Interaction Outcome
```

It also checks:

* external record resolution
* contributor consistency
* receipt identity consistency
* interaction membership
* protocol version compatibility
* graph-to-record consistency
* optional SHA-256 content digests
* declared reference coverage
* unresolved references

### Exact content identity

Where a SHA-256 digest is declared:

```text
same meaning
≠
same serialized content
```

The digest identifies the exact record bytes being validated.

### Schema

`schemas/contribution-bundle.schema.json`

---

# v0.5 — Contribution Weight Assessment

v0.5 asks the next question:

> Given the validated contribution evidence, how much relative contribution does the evidence support?

A Weight Assessment can represent:

```yaml
estimated_weight: 0.32
lower_bound: 0.25
upper_bound: 0.39
confidence: 0.84
```

This is an **estimate**, not absolute causal truth.

The protocol explicitly preserves uncertainty.

---

## Known and Unresolved Contribution

A central v0.5 principle is:

```text
UNKNOWN
≠
ZERO
```

If only 80% of normalized contribution can currently be explained:

```text
Known Contribution = 0.80
Unresolved         = 0.20
```

the unresolved 20% must not automatically be redistributed among known contributors.

Normalized assessments use:

```text
sum(known estimated weights)
+
unresolved_weight
=
1.0
```

Example:

```text
Retriever     0.22
Verifier      0.24
Reasoner      0.26
Interaction   0.18
Unresolved    0.10
────────────────
Total         1.00
```

---

## Supported Weight Assessment Methods

v0.5 currently supports:

```text
evidence_weighted
counterfactual_marginal
coalition_adjusted
shapley_approximation
hybrid
```

No method is declared universally correct.

The method is recorded explicitly because contribution estimates depend on:

* available evidence
* causal assumptions
* evaluated coalition space
* outcome metric
* substitutability
* interaction effects
* uncertainty
* assessment scope

---

## Shapley Values Are Evidence, Not Truth

Shapley-style estimation can be useful for multi-agent contribution analysis.

However:

```text
Shapley Estimate
≠
Absolute Causal Truth
```

Results may depend on:

* sampled coalitions
* utility functions
* omitted contributors
* substitution effects
* model randomness
* measurement quality

v0.5 therefore treats Shapley-derived values as structured estimation evidence.

---

## Interaction Weight Remains Separate

Suppose:

```text
Retriever contribution = 0.22
Verifier contribution  = 0.24
Reasoner contribution  = 0.26
Coalition interaction  = 0.18
```

The protocol does not silently convert this into:

```text
Verifier contribution = 0.42
```

by absorbing coalition value into an individual.

Instead:

```text
Individual Weight
≠
Interaction Weight
```

remains explicit.

### Schema

`schemas/contribution-weight-assessment.schema.json`

---

# Contribution Dimensions

The protocol uses several distinct concepts because contribution is not one-dimensional.

## Work

How much activity or resource expenditure occurred?

Possible indicators:

```text
tokens
execution time
GPU usage
API usage
human effort
```

## Causal Impact

How much did the contributor materially change the outcome?

## Necessity

How difficult would comparable outcome quality have been without the contributor?

## Quality Impact

How much did the contributor improve or preserve correctness, safety, reliability, usefulness, or other outcome quality?

## Evidence Strength

How strong is the evidence supporting the contribution claim?

## Substitutability

How easily could another contributor have performed the same function?

These dimensions must not be silently collapsed into one concept.

---

# Counterfactual Evaluation

The protocol supports counterfactual evidence such as:

```text
leave_one_out
leave_group_out
pairwise_ablation
substitution_test
```

Example:

```text
Baseline:
A + B + C + D
→ quality 0.92

Without B:
A + C + D
→ quality 0.67

Observed delta:
0.25
```

This provides evidence that B mattered.

It does **not** prove:

```text
B contributed exactly 25%
```

because interactions, substitutions, randomness, routing changes, and measurement uncertainty may affect the result.

---

# Humans, AI, Data, and Tools in One Model

The protocol is intentionally contributor-type neutral.

An outcome might be produced through:

```text
Human
  ↓
Problem Definition

Dataset
  ↓
Primary Evidence

Retriever Agent
  ↓
Evidence Discovery

Verifier Agent
  ↓
Evidence Validation

Reasoner Agent
  ↓
Reasoning

Auditor
  ↓
Error Prevention

Integrator
  ↓
Final Outcome
```

The final generator does not automatically receive full contribution credit.

Upstream contribution can include:

* problem definition
* original evidence
* source creation
* verification
* architecture decisions
* constraint design
* error prevention
* routing
* integration

---

# Observation → Estimation → Allocation

The architecture separates three stages.

```text
Observation
    ↓
Estimation
    ↓
Allocation
```

## Observation

What happened?

```text
execution traces
decisions
evidence references
interaction traces
counterfactual measurements
```

## Estimation

What relative contribution does the evidence support?

```text
causal impact
necessity
quality impact
interaction contribution
contribution weight
uncertainty
```

## Allocation

What rights or economic consequences follow?

```text
attribution
ownership
entitlement
royalty
payment
settlement
```

The Causal Contribution Receipt Protocol through v0.5 covers **Observation and Contribution Estimation**.

It intentionally stops before economic Allocation.

---

# Protocol Boundary

The most important boundary is:

```text
Contribution Evidence
        ↓
Contribution Assessment
        ↓
Contribution Weight
        ↓
────────────────────────
Protocol Boundary
────────────────────────
        ↓
Attribution
        ↓
Entitlement
        ↓
Royalty Allocation
        ↓
Settlement
```

Therefore:

```text
Contribution Weight
≠
Ownership

Contribution Weight
≠
Entitlement

Contribution Weight
≠
Royalty Percentage

Contribution Weight
≠
Settlement Instruction
```

A downstream system may use contribution weight as an input.

It must apply additional explicit policy before creating economic or legal consequences.

---

# Validation

Install the validator dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the complete example suite:

```bash
python scripts/validate_examples.py
```

The validator covers all protocol versions from v0.1 through v0.5.

Expected high-level validation pipeline:

```text
Schema
  ↓
Semantic
  ↓
Graph
  ↓
Cross-Record
  ↓
Weight Assessment
```

Pass examples must validate successfully.

Fail examples must be rejected at their intended validation layer.

---

# Digest Maintenance

v0.4 bundles may pin exact external records with SHA-256 digests.

After intentionally changing a referenced pass fixture, update declared pass-example digests with:

```bash
python scripts/update_bundle_digests.py
```

Then run:

```bash
python scripts/validate_examples.py
```

The digest updater:

* updates only already-declared digests
* preserves intentionally partial provenance
* does not add missing digest blocks
* does not modify fail examples

---

# Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── validate.yml
│
├── docs/
│   ├── contribution-model.md
│   └── core-invariants.md
│
├── examples/
│   ├── pass/
│   ├── fail/
│   └── records/
│       ├── graphs/
│       ├── receipts/
│       ├── interactions/
│       ├── evidence/
│       └── index.yaml
│
├── schemas/
│   ├── causal-contribution-receipt.schema.json
│   ├── contribution-interaction.schema.json
│   ├── contribution-graph.schema.json
│   ├── contribution-bundle.schema.json
│   └── contribution-weight-assessment.schema.json
│
├── scripts/
│   ├── update_bundle_digests.py
│   └── validate_examples.py
│
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

---

# Pass Examples

## v0.1

`examples/pass/critical-agent-contribution.example.yaml`

`examples/pass/human-problem-definition.example.yaml`

`examples/pass/dataset-evidence-contribution.example.yaml`

## v0.2

`examples/pass/synergistic-agent-interaction.example.yaml`

`examples/pass/substitutive-agent-interaction.example.yaml`

`examples/pass/coalition-contribution.example.yaml`

## v0.3

`examples/pass/linear-contribution-graph.example.yaml`

`examples/pass/interaction-contribution-graph.example.yaml`

`examples/pass/partial-evidence-graph.example.yaml`

## v0.4

`examples/pass/consistent-contribution-bundle.example.yaml`

`examples/pass/multi-agent-contribution-bundle.example.yaml`

`examples/pass/partial-evidence-bundle.example.yaml`

## v0.5

`examples/pass/basic-contribution-weight-assessment.example.yaml`

`examples/pass/coalition-adjusted-weight-assessment.example.yaml`

`examples/pass/partial-weight-assessment.example.yaml`

`examples/pass/shapley-assisted-weight-assessment.example.yaml`

---

# v0.5 Negative Cases

v0.5 includes explicit negative cases for important protocol boundaries.

### Excess total weight

`examples/fail/weight-sum-exceeds-one.example.yaml`

Rejects contribution weights whose normalized total exceeds the available contribution space.

### UNKNOWN forced to zero

`examples/fail/unknown-weight-forced-to-zero.example.yaml`

Rejects a complete known allocation when the referenced contribution bundle still contains unresolved causal evidence.

### Interaction assigned to individual

`examples/fail/interaction-weight-assigned-to-individual.example.yaml`

Rejects direct absorption of coalition interaction value into an individual contribution subject.

### Weight implies entitlement

`examples/fail/weight-implies-entitlement.example.yaml`

Rejects economic entitlement fields inside the Contribution Weight Assessment schema.

### Outcome mismatch

`examples/fail/weight-outcome-mismatch.example.yaml`

Rejects a Weight Assessment whose declared outcome differs from the referenced Contribution Bundle.

### Unsupported method

`examples/fail/unsupported-weight-method.example.yaml`

Rejects assessment methods outside the explicitly supported v0.5 method set.

---

# Core Invariants

The protocol currently defines 32 core invariants.

See:

`docs/core-invariants.md`

They cover:

```text
CCR-INV-001–007
Individual Contribution

CCR-INV-008–012
Interaction / Coalition Contribution

CCR-INV-013–018
Contribution Graph

CCR-INV-019–024
Cross-Record Consistency

CCR-INV-025–032
Contribution Weight Assessment
```

Important examples include:

```text
Work MUST NOT equal Contribution.

Interaction Contribution MUST NOT be
automatically assigned to one contributor.

UNKNOWN contribution MUST NOT be
automatically redistributed.

Contribution Weight MUST NOT directly
create economic entitlement.
```

---

# Contribution Model

For the conceptual model behind the schemas and invariants, see:

`docs/contribution-model.md`

The model explains:

* why contribution differs from work
* causal impact
* necessity
* quality impact
* evidence strength
* counterfactual evaluation
* coalition contribution
* substitutability
* contribution graphs
* unresolved causal segments
* cross-record consistency
* contribution weight
* Shapley-assisted estimation
* uncertainty
* economic boundary separation

---

# Design Principles

## Evidence before allocation

```text
Trace
  ↓
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
Weight
```

Only then should downstream systems consider:

```text
Attribution
  ↓
Entitlement
  ↓
Royalty Allocation
  ↓
Settlement
```

## UNKNOWN is not ZERO

Missing causal knowledge must not be silently converted into known allocation.

## Interaction is not Individual

Value emerging from a coalition should remain distinguishable from individual contribution.

## Precision must follow evidence

Weak evidence should produce greater uncertainty, not more decimal places.

## Model independence

The protocol is not tied to a specific AI vendor or model architecture.

It may be applied to:

* human-AI collaboration
* multi-agent systems
* local AI models
* large language models
* tool-using agents
* data pipelines
* hybrid systems

## Minimal disclosure

Contribution audit should not require disclosure of complete private reasoning or hidden chain-of-thought.

References, hashes, evidence identifiers, decisions, and measurable deltas should be preferred where sufficient.

---

# Relationship to Multi-Agent Systems

The protocol is especially useful where work is structurally divided among specialized agents.

For example:

```text
Router
  ↓
Retriever
Verifier
Reasoner
Specialist
Auditor
  ↓
Integrator
  ↓
Outcome
```

Such architectures make it easier to observe:

```text
who participated
what each participant received
what each participant produced
who used the output
which interactions mattered
what changed downstream
what remains unresolved
```

This creates a stronger basis for contribution analysis than simple execution accounting.

---

# What v0.5 Does Not Define

v0.5 does **not** define:

* legal ownership
* copyright status
* identity proofing
* payment entitlement
* royalty percentages
* payment instructions
* currency
* payment rails
* settlement finality
* tax treatment
* contractual rights
* dispute adjudication
* universal contribution formula
* universally correct Shapley model
* globally authoritative contribution ranking

These belong to downstream or separate protocols.

---

# Architectural Summary

```text
Who contributed?
        ↓
v0.1
Contribution Receipt

Who contributed together?
        ↓
v0.2
Contribution Interaction

How did contribution flow?
        ↓
v0.3
Contribution Graph

Do the records describe
the same contribution context?
        ↓
v0.4
Cross-Record Validation

How much relative contribution
does the evidence support?
        ↓
v0.5
Contribution Weight Assessment

Who owns what?
Who is entitled to what?
How much value should move?
        ↓
Out of scope
```

---

# Current Design Principle

The protocol can be summarized as:

> Measure what changed because a contributor was present, not merely how much activity the contributor performed.

And through v0.5:

> Estimate relative contribution without pretending that uncertainty is zero, coalition value belongs to one individual, or contribution automatically creates economic rights.

More compactly:

```text
Activity tells us who worked.

Trace tells us what happened.

Evidence tells us what can be supported.

Contribution tells us what mattered.

Interaction tells us what emerged between contributors.

Graph tells us how contribution flowed.

Cross-record validation tells us whether the records agree.

Weight tells us how much relative contribution the evidence supports.

Downstream systems decide what rights or payments follow.
```

```
```
