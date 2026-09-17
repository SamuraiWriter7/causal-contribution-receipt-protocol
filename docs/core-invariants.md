# Causal Contribution Receipt Protocol — Core Invariants

Version: v0.5

## 1. Purpose

The Causal Contribution Receipt Protocol provides a machine-readable structure for recording, connecting, validating, and evaluating evidence-backed causal contribution to identifiable outcomes.

Through v0.5, the protocol defines five progressively connected layers:

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

The protocol distinguishes contribution from activity, identity, ownership, attribution, entitlement, royalty allocation, payment, and settlement.

The central principle remains:

Work performed is not equivalent to contribution created.

A contributor MAY consume substantial resources while having little causal effect on an outcome.

A contributor MAY also perform very little work while having a decisive effect on quality, safety, correctness, usefulness, or final feasibility.

The protocol therefore preserves evidence and causal structure before downstream systems apply economic, legal, governance, or allocation rules.

2. Terminology
Contributor

An entity whose participation in an outcome is being evaluated.

Examples include:

human
agent
dataset
source
tool
service
Outcome

The result relative to which contribution is evaluated.

Examples include:

generated answer
system design
research summary
decision
software artifact
audited result

Contribution MUST NOT be interpreted independently of its outcome.

Contribution Receipt

A record describing one contributor's evidence-backed contribution to one outcome.

Introduced in v0.1.

Contribution Interaction

A record describing contribution that emerges from the relationship among two or more contributors.

Introduced in v0.2.

Interaction contribution MAY be:

complementary
redundant
synergistic
substitutive
blocking
Contribution Graph

A directed graph connecting contributors, receipts, interactions, evidence, decisions, unresolved segments, and outcomes.

Introduced in v0.3.

The graph represents how contribution evidence and causal claims flow toward an outcome.

Contribution Bundle

A cross-record container linking a graph with its receipts, interactions, evidence, and outcome references.

Introduced in v0.4.

The bundle allows records to be validated not only individually, but also against one another.

Contribution Weight Assessment

A structured estimate of the relative contribution represented by known contribution subjects within a declared outcome and assessment scope.

Introduced in v0.5.

A contribution weight is an estimate.

It is not an ownership share, entitlement ratio, royalty percentage, or payment instruction.

Evidence

Traceable information supporting a contribution claim.

Evidence MAY include:

source inputs
generated outputs
execution traces
decisions
downstream usage
audit records
counterfactual measurements
comparison records
interaction traces
Counterfactual Assessment

An evaluation of what changes when a contributor or group of contributors is removed, replaced, or otherwise altered in an evaluated process.

Supported methods through v0.5 include examples such as:

leave_one_out
leave_group_out
pairwise_ablation
substitution_test

Counterfactual results are evidence.

They are not absolute causal truth.

Unresolved Contribution

Contribution that cannot currently be assigned to a known subject with sufficient evidential support.

Unresolved contribution MUST remain distinguishable from zero contribution.

3. Core Invariants
v0.1 — Individual Contribution
CCR-INV-001 — Every Contribution Receipt MUST reference an outcome

A contribution has meaning only relative to an identifiable result.

A receipt without an outcome is invalid.

Contributor
    ↓
Contribution
    ↓
Outcome

The protocol MUST NOT record contribution as an isolated property of an entity.

CCR-INV-002 — Every Contribution Receipt MUST identify exactly one contributor

Each Contribution Receipt evaluates one contributor relative to one outcome.

A contributor MAY be a human, agent, dataset, source, tool, or service.

If multiple contributors are being evaluated individually, separate receipts SHOULD be issued.

Outcome
 ├─ Receipt A → Contributor A
 ├─ Receipt B → Contributor B
 └─ Receipt C → Contributor C

This keeps individual contribution claims independently auditable.

Multi-contributor effects belong to Contribution Interaction records rather than being hidden inside one individual receipt.

CCR-INV-003 — Work MUST NOT be treated as equivalent to contribution

Resource consumption alone MUST NOT determine causal contribution.

Measurements of work MAY include:

inference time
token usage
GPU usage
API calls
execution duration
storage usage
network usage

However:

High Work
≠
High Contribution

and:

Low Work
≠
Low Contribution

Example:

Agent A
1,000,000 tokens
No material effect on final result

Agent B
300 tokens
Detects critical false evidence
Prevents incorrect final output

Agent B MAY have substantially higher causal contribution despite performing less work.

CCR-INV-004 — Contribution claims MUST include evidence references

A contribution claim MUST contain traceable evidence.

A self-declared statement such as:

"I made an important contribution."

is insufficient.

Evidence SHOULD allow an auditor to reconstruct at least part of the following relationship:

Input
  ↓
Contributor Action
  ↓
Recorded Output or Decision
  ↓
Downstream Use
  ↓
Outcome

Contribution without evidence MUST NOT be treated as verified contribution.

CCR-INV-005 — Counterfactual measurements MUST NOT be treated as absolute causal truth

A counterfactual experiment estimates what might have occurred under a different condition.

For example:

Baseline:
A + B + C + D → quality 0.92

Without B:
A + C + D → quality 0.67

Observed delta:
0.25

The value 0.25 is evidence of causal significance.

It MUST NOT automatically be interpreted as:

B contributed exactly 25%

Interaction effects, substitution effects, stochastic model behavior, evaluator uncertainty, measurement error, and incomplete observations MAY affect the result.

CCR-INV-006 — Contribution classification MUST NOT directly imply payment entitlement

Contribution classes MAY include:

critical
high
medium
low
incidental

These classes summarize contribution assessment.

However:

critical
≠
payment entitlement

and:

critical
≠
fixed royalty percentage

Contribution classification MUST NOT directly create an economic claim.

CCR-INV-007 — Contribution, Attribution, Entitlement, and Settlement MUST remain separate

The protocol MUST preserve the following distinction:

Contribution
    ≠
Attribution
    ≠
Entitlement
    ≠
Settlement

These layers answer different questions.

Contribution

What materially affected the outcome?

Attribution

To whom or what should that contribution be associated?

Entitlement

Does that attributed contribution create a valid right to receive value?

Settlement

What value is actually transferred, to whom, when, and under what rules?

Contribution records MAY be consumed by downstream systems.

They MUST NOT silently perform downstream economic or legal decisions themselves.

v0.2 — Interaction and Coalition Contribution
CCR-INV-008 — Interaction contribution MUST NOT be automatically assigned to any single contributor

Some value emerges from the relationship among contributors rather than from one contributor in isolation.

For example:

Agent A alone → moderate result
Agent B alone → moderate result

Agent A + Agent B
        ↓
substantially better result

The additional effect MAY be interaction contribution.

It MUST NOT automatically be assigned entirely to Agent A or Agent B.

CCR-INV-009 — Coalition contribution MUST remain distinguishable from individual contribution

The protocol MUST preserve:

Individual Contribution
        ≠
Coalition Contribution

A coalition MAY produce value that is not reducible to the sum of independently observed individual effects.

For example:

A = 0.20 individual effect
B = 0.18 individual effect
A+B = additional interaction effect

The interaction effect MUST remain separately representable until an explicit downstream allocation method is applied.

CCR-INV-010 — Substitutability MUST be distinguished from causal impact

A contributor MAY have substantial causal effect while still being replaceable.

Therefore:

High Causal Impact
≠
Low Substitutability

and:

Replaceable Contributor
≠
No Contribution

Contribution assessment MUST NOT collapse replaceability, necessity, and causal effect into one hidden concept.

CCR-INV-011 — Counterfactual absence MUST NOT be assumed equivalent to real-world non-existence

Removing a contributor in an experiment does not necessarily recreate a world in which that contributor never existed.

Removal MAY affect:

routing
timing
substitute selection
context availability
model behavior
coalition structure

Counterfactual absence MUST therefore be treated as an experimental condition rather than a perfect reconstruction of reality.

CCR-INV-012 — Interaction claims MUST include evidence involving all claimed contributors

An interaction claim involving contributors A and B MUST contain evidence that supports an interaction involving both A and B.

Evidence showing only A's isolated behavior is insufficient to prove an A+B interaction claim.

The protocol SHOULD support reconstruction such as:

Contributor A
     \
      → Interaction Evidence → Outcome
     /
Contributor B
v0.3 — Contribution Graph
CCR-INV-013 — All graph references MUST resolve within the graph

Every graph edge and declared graph path MUST reference known graph nodes.

A graph MUST reject dangling structural references.

Known Node
   ↓
Known Node

is valid.

Known Node
   ↓
Unknown Node

is structurally invalid.

External record resolution is handled by the v0.4 Cross-Record layer.

CCR-INV-014 — Graph contribution paths MUST remain scoped to one declared outcome

A Contribution Graph represents causal structure relative to one declared outcome.

Graph paths MUST NOT silently combine unrelated outcomes into one causal chain.

Derived-outcome or multi-outcome models require explicit future semantics rather than implicit mixing.

CCR-INV-015 — Graph interaction membership MUST resolve to known contribution subjects

A graph MUST NOT claim participation in an interaction from an unknown graph subject.

Where a Contribution Receipt participates in an interaction, the corresponding receipt node MUST exist in the graph.

Cross-record verification of the actual external interaction record is performed in v0.4.

CCR-INV-016 — Contribution Graphs MUST NOT contain attribution or settlement edges

The Contribution Graph represents contribution structure.

It MUST NOT introduce edge semantics that silently perform downstream economic or ownership decisions.

Examples of prohibited contribution-graph shortcuts include:

contributed_to
    ↓
owns

contributed_to
    ↓
is_entitled_to

contributed_to
    ↓
must_be_paid

Contribution flow and economic flow MUST remain separate.

CCR-INV-017 — Contribution paths MUST be directionally valid

Causal and evidential relationships MUST respect defined direction semantics.

For example:

Contribution
    ↓
Outcome

MAY be valid.

But:

Outcome
    ↓
caused earlier Contribution

MUST NOT be accepted as an ordinary forward causal path.

The graph validator MUST reject directionally invalid relationships.

CCR-INV-018 — Cyclic causal claims MUST be rejected unless explicitly modeled as feedback

v0.3 Contribution Graphs are acyclic by default.

For example:

A → B → C → A

MUST be rejected.

A future protocol MAY explicitly support feedback structures.

Such feedback MUST be represented with explicit semantics rather than being interpreted as an ordinary causal DAG.

v0.4 — Cross-Record Consistency
CCR-INV-019 — Every external record required for cross-record validation MUST resolve

A Contribution Bundle MAY reference:

Contribution Graphs
Contribution Receipts
Contribution Interactions
Evidence records

Records required to validate a claim MUST resolve to identifiable content.

An unresolved reference MUST NOT silently be treated as verified.

Partial evidence MAY remain valid when explicitly represented as unresolved.

CCR-INV-020 — Contribution records connected within one Bundle MUST maintain outcome consistency

Where a Bundle claims that records describe one contribution context:

Bundle Outcome
      =
Graph Outcome
      =
Receipt Outcome
      =
Interaction Outcome

unless a future protocol explicitly defines a derived-outcome relationship.

Cross-record outcome mismatch MUST be rejected.

CCR-INV-021 — Graph-declared contributor identity MUST match referenced Receipt identity

If a graph or Bundle associates a Contribution Receipt with contributor A, the resolved Receipt MUST identify contributor A.

Declared Contributor
        =
Resolved Receipt Contributor

Identity disagreement MUST be surfaced as inconsistency rather than silently corrected.

CCR-INV-022 — Interaction membership in the graph MUST be consistent with the referenced Interaction record

If a graph represents:

A + B → Interaction X

but the resolved Interaction record declares:

A + C → Interaction X

the records are inconsistent.

The validator MUST reject the mismatch.

CCR-INV-023 — A record digest MUST identify the exact content validated when a digest is present

Where a SHA-256 digest is declared, validation MUST compare it against the exact referenced record content according to the protocol's digest procedure.

In v0.4 fixtures, the digest may be computed from raw record bytes.

Therefore:

Same semantic meaning
≠
Same digest

if the actual serialized content differs.

Digest validation provides content identity, not semantic equivalence.

CCR-INV-024 — Cross-record consistency MUST NOT imply economic entitlement

A fully consistent Contribution Bundle proves only that the checked contribution records are structurally and referentially coherent under the protocol.

It does NOT prove:

ownership
entitlement
royalty percentage
payment obligation
settlement finality

Therefore:

Valid Bundle
≠
Economic Entitlement
v0.5 — Contribution Weight Assessment
CCR-INV-025 — Contribution Weight MUST NOT directly imply economic entitlement

A Contribution Weight estimates relative contribution within a defined assessment scope.

For example:

Contributor A
estimated_weight = 0.35

MUST NOT automatically mean:

Contributor A owns 35%

or:

Contributor A must receive 35% of payment

Contribution Weight is evidential assessment.

Economic entitlement belongs to a downstream layer.

CCR-INV-026 — Individual contribution weight MUST remain distinguishable from interaction contribution weight

The protocol MUST preserve:

Individual Weight
      ≠
Interaction Weight

If a coalition contributes additional value:

A individual contribution
B individual contribution
A+B interaction contribution

the interaction contribution MUST remain separately representable.

It MUST NOT be silently absorbed into an individual's weight.

CCR-INV-027 — Unknown contribution MUST NOT be automatically redistributed among known contributors

If available evidence supports:

Known Contribution = 0.80

the remaining:

0.20

MUST NOT automatically be redistributed among known contributors.

Instead:

unresolved_weight: 0.20

MAY be retained.

Therefore:

UNKNOWN
≠
ZERO

and:

UNKNOWN
≠
automatic redistribution

This invariant prevents false precision.

CCR-INV-028 — Weight assessment MUST identify the evidence or records on which it is based

A Weight Assessment MUST NOT consist only of unexplained numbers.

Each weight entry MUST reference evidence or contribution records supporting the estimate.

A system SHOULD be able to reconstruct:

Evidence
   ↓
Contribution Record
   ↓
Assessment Basis
   ↓
Weight Estimate
CCR-INV-029 — A contribution weight MUST be interpreted only within its declared outcome and assessment scope

A weight has meaning only relative to:

an outcome
a contribution bundle
an assessment method
the available evidence
the evaluated subject set

A weight derived for outcome-A MUST NOT be silently reused as the weight for outcome-B.

Therefore:

Weight Assessment Outcome
        =
Referenced Bundle Outcome

is required unless future protocol semantics explicitly define another relationship.

CCR-INV-030 — Counterfactual or Shapley-derived values MUST NOT be treated as absolute causal truth

v0.5 MAY use methods such as:

counterfactual_marginal
coalition_adjusted
shapley_approximation
hybrid

However:

Shapley Estimate
≠
Absolute Causal Truth

and:

Counterfactual Delta
≠
Guaranteed True Contribution Percentage

Such methods provide structured evidence for estimation.

Their assumptions, sampled coalition space, metric choice, uncertainty, and substitution behavior MAY affect the result.

CCR-INV-031 — Weight precision MUST NOT exceed the evidential precision available to the assessment

Contribution Weight is an estimate.

The protocol SHOULD represent uncertainty using structures such as:

lower_bound
estimated_weight
upper_bound
confidence

For example:

lower_bound      = 0.25
estimated_weight = 0.32
upper_bound      = 0.39
confidence       = 0.84

is preferable to claiming unjustified precision such as:

0.3217461892

when the available evidence cannot support that precision.

Weak evidence SHOULD increase uncertainty rather than create artificial certainty.

CCR-INV-032 — Contribution Weight, Attribution, Entitlement, Royalty Allocation, and Settlement MUST remain separate

v0.5 extends contribution evaluation but does not collapse downstream layers.

The protocol MUST preserve:

Contribution Evidence
        ↓
Contribution Assessment
        ↓
Contribution Weight
        ↓
────────────────────────
Downstream Boundary
────────────────────────
        ↓
Attribution
        ↓
Entitlement
        ↓
Royalty Allocation
        ↓
Settlement

Therefore:

Contribution Weight
≠
Attribution Ownership

Contribution Weight
≠
Entitlement

Contribution Weight
≠
Royalty Allocation

Contribution Weight
≠
Settlement

A downstream system MAY consume a Weight Assessment.

It MUST apply its own explicit rules before creating economic rights or transfers.

4. Weight Conservation and Unresolved Contribution

For normalized v0.5 assessments, the protocol uses the following semantic relationship:

sum(known estimated weights)
+
unresolved_weight
=
1.0

For example:

Contributor A       0.34
Contributor B       0.46
Unresolved          0.20
────────────────────────
Total               1.00

This rule does not claim that reality is perfectly divisible into exact percentages.

It defines a normalized accounting surface for the assessment.

The unresolved_weight field exists specifically to prevent a system from pretending that all contribution has been fully explained.

5. Separation of Observation, Estimation, and Allocation

The protocol separates three stages.

Observation
    ↓
Estimation
    ↓
Allocation
Observation

What evidence exists?

Examples:

execution trace
decision record
counterfactual delta
interaction trace
downstream effect
Estimation

What relative contribution does the available evidence support?

Examples:

causal impact
necessity
quality impact
substitutability
contribution weight
uncertainty range
Allocation

What economic, legal, or governance consequence follows?

Examples:

attribution
entitlement
royalty percentage
payment
settlement

The Causal Contribution Receipt Protocol through v0.5 covers Observation and Contribution Estimation.

It does not define economic Allocation.

6. Evidence Before Weight

The protocol follows this structural order:

Trace
  ↓
Evidence
  ↓
Individual Contribution
  ↓
Interaction Contribution
  ↓
Contribution Graph
  ↓
Cross-Record Validation
  ↓
Contribution Weight Assessment

Only after these layers MAY downstream systems perform operations such as:

Attribution
  ↓
Entitlement
  ↓
Royalty Allocation
  ↓
Settlement

A Weight Assessment SHOULD NOT be produced from identity, compute cost, payment destination, model size, or resource consumption alone.

7. Human and Machine Contributions

The protocol MUST NOT assume that the final generator is the primary contributor.

An outcome MAY result from a structure such as:

Human
  ↓
Problem Definition

Dataset
  ↓
Primary Evidence

Agent A
  ↓
Retrieval

Agent B
  ↓
Verification

Agent C
  ↓
Reasoning

Auditor
  ↓
Error Prevention

Integrator
  ↓
Final Output

Each component MAY have independently meaningful contribution.

Contribution MAY also emerge through interaction:

Human + Agent
Dataset + Verifier
Retriever + Reasoner
Multiple Agents + Auditor

Humans, AI agents, datasets, and evidence sources SHOULD be representable under the same causal contribution framework without assuming that computation itself creates priority.

8. Minimality Principle

A contribution record SHOULD contain only information necessary to support and audit its contribution claim.

The protocol SHOULD NOT require disclosure of:

complete private reasoning
hidden chain-of-thought
model internals
proprietary prompts
unrelated personal information
unnecessary full-content copies

Where possible, implementations SHOULD prefer:

reference
hash
decision record
result delta
evidence identifier
structured assessment

over unnecessary replication of underlying content.

The protocol is intended to make contribution auditable without requiring total internal transparency.

9. Non-Goals Through v0.5

Through v0.5, the protocol does not define:

legal ownership
copyright status
identity proofing
economic entitlement
royalty percentages
payment instructions
currency
payment rails
settlement finality
tax treatment
contractual rights
dispute adjudication
universal contribution formula
universally correct Shapley model
globally authoritative contribution ranking

v0.5 supports contribution weight estimation.

It does not define how that weight becomes money, rights, ownership, or legal obligation.

10. Version Boundaries
v0.1 Boundary

The defining question is:

Can a system record a machine-readable, evidence-backed claim describing how one contributor affected one identifiable outcome?

v0.2 Boundary

The defining question is:

Can a system represent contribution that emerges from interactions or coalitions without pretending that all value belongs to one individual contributor?

v0.3 Boundary

The defining question is:

Can a system represent the path through which contribution evidence and causal claims flow toward an outcome?

v0.4 Boundary

The defining question is:

Can a system verify that independently stored contribution records actually describe a consistent contribution context?

v0.5 Boundary

The defining question is:

Can a system estimate relative contribution weight while preserving uncertainty, interaction effects, unresolved contribution, and the boundary between contribution and economic entitlement?

If yes, v0.5 has completed its responsibility.

Everything beyond that boundary belongs to downstream attribution, entitlement, allocation, governance, legal, or settlement systems.

11. Architectural Summary

The protocol through v0.5 can be summarized as:

Who contributed?
        ↓
v0.1 Receipt

Who contributed together?
        ↓
v0.2 Interaction

How did contribution flow?
        ↓
v0.3 Graph

Do the records describe the same reality?
        ↓
v0.4 Cross-Record Validation

How much relative contribution does the evidence support?
        ↓
v0.5 Weight Assessment

Who owns what?
Who is entitled to what?
How much value should be transferred?
        ↓
NOT DEFINED HERE

The protocol intentionally stops before economic allocation.

Its responsibility is to make contribution increasingly observable, auditable, comparable, and structurally explicit without pretending that measurement automatically creates ownership or payment rights.
