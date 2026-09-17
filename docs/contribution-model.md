# Causal Contribution Receipt Protocol — Contribution Model

Version: v0.5

## 1. Overview

The Causal Contribution Receipt Protocol models contribution as a structured causal relationship between contributors, evidence, interactions, decisions, and identifiable outcomes.

Through v0.5, the model evolves through five layers:

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

The protocol is designed to answer progressively harder questions:

Who contributed?

Who contributed together?

How did contribution flow?

Do the records describe the same reality?

How much relative contribution does the evidence support?

The protocol does not assume that contribution is equivalent to work, compute usage, execution time, model size, or payment.

Its foundational distinction is:

Activity
≠
Contribution

and, through v0.5:

Contribution Weight
≠
Economic Entitlement

The model supports heterogeneous contributors including:

humans
AI agents
datasets
sources
tools
services
2. Why Contribution Is Not Work

Traditional usage accounting measures activity.

Examples include:

tokens consumed
GPU seconds
API requests
execution time
number of generated artifacts
human hours
storage usage
network usage

These measurements answer:

How much activity occurred?

They do not necessarily answer:

How much did that activity matter to the outcome?

Consider:

Agent A
work = 0.90

Agent B
work = 0.08

If Agent A produces a large amount of redundant reasoning while Agent B identifies the single false assumption that would otherwise invalidate the final result, Agent B may have substantially greater causal contribution.

Therefore:

Work Accounting
       ≠
Contribution Assessment

The protocol records work as one dimension of observation.

It does not use work as the definition of contribution.

This separation is important for both accuracy and incentives.

If resource consumption automatically increased contribution reward, systems could be incentivized to perform unnecessary computation.

Instead, the protocol asks:

What changed because this contributor participated?
3. v0.1 — Individual Contribution

v0.1 introduces the Causal Contribution Receipt.

Each receipt evaluates one contributor relative to one outcome.

The conceptual structure is:

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

A receipt does not attempt to solve all contribution problems.

Its role is narrower:

Record a machine-readable, evidence-backed claim about how one contributor affected one identifiable outcome.

4. Contribution Dimensions

v0.1 defines five normalized assessment dimensions.

Each value is represented between:

0.0
and
1.0

The dimensions are:

work
causal_impact
necessity
quality_impact
evidence_strength

These values are contextual observations or estimates.

They are not universal constants.

The protocol intentionally keeps them separate so that downstream evaluation policies do not become embedded into the base evidence layer.

5. Work

Example:

work: 0.12

work represents the normalized amount of activity or resource expenditure associated with the contributor.

It MAY reflect:

execution time
token consumption
computational cost
number of operations
API usage
human effort
data processing volume

A higher work value indicates greater activity within the chosen evaluation scope.

It MUST NOT independently determine contribution class or contribution weight.

For example:

High work
+
low downstream effect
=
possibly low contribution

while:

Low work
+
decisive downstream effect
=
possibly high contribution
6. Causal Impact

Example:

causal_impact: 0.82

causal_impact estimates the degree to which the contributor materially changed the formation, state, or content of the outcome.

Examples of high causal impact include:

changing the final decision
introducing decisive evidence
removing a false assumption
changing the selected architecture
altering the final conclusion
preventing an invalid result
blocking unsafe execution

Example:

Source Verifier
       ↓
rejects false source
       ↓
Reasoner stops using false evidence
       ↓
Final answer changes

This represents a strong causal path.

A contributor MAY have high causal impact even when the visible output is small.

7. Necessity

Example:

necessity: 0.74

necessity estimates how difficult it would have been to achieve comparable outcome quality without the contributor.

Examples of high necessity include:

unique primary evidence
unique human problem definition
irreplaceable specialist knowledge
critical audit function
unique tool capability

Necessity is distinct from causal impact.

For example:

Agent A had major causal impact,
but Agent B could easily have performed the same function.

Then:

causal_impact = high
necessity = lower

This distinction becomes especially important in multi-agent systems where several agents may be substitutable.

8. Quality Impact

Example:

quality_impact: 0.91

quality_impact estimates how much the contributor improved or preserved outcome quality.

Quality MAY include:

factual correctness
logical consistency
safety
usefulness
completeness
reliability
compliance
clarity

Quality impact can include prevented degradation.

For example:

Auditor
   ↓
detects critical error
   ↓
incorrect answer blocked

The Auditor may have high quality impact despite not generating the main artifact.

9. Evidence Strength

Example:

evidence_strength: 0.96

evidence_strength describes the quality of the evidence supporting the contribution claim.

It does not describe the value of the contribution itself.

Evidence strength MAY depend on:

trace completeness
signed records
reproducible experiments
explicit downstream references
audit records
deterministic validation
counterfactual tests
independent verification
content digests

This distinction is important because a contributor may have:

high actual contribution
+
weak available evidence

The protocol should preserve that uncertainty rather than manufacture certainty.

10. Contribution Classes

v0.1 defines the following human-readable classes:

critical
high
medium
low
incidental

These classes summarize contribution assessment.

They are not universal mathematical thresholds.

Critical

The contributor appears central to correctness, safety, viability, or core outcome formation.

High

The contributor materially improves the outcome and has clear downstream significance.

Medium

The contributor provides meaningful but non-decisive value.

Low

The contributor has observable but limited influence.

Incidental

The contributor participated in the process but has little demonstrated effect on the outcome.

Contribution classes MUST NOT automatically determine:

ownership
entitlement
royalty
payment
11. Counterfactual Assessment

v0.1 introduces leave_one_out.

The method compares:

Baseline Outcome

with:

Outcome without Contributor i

Example:

A + B + C + D
→ quality 0.92

A + C + D
→ quality 0.67

The observed difference is:

0.92 - 0.67 = 0.25

A receipt may record:

counterfactual:
  method: leave_one_out

  baseline:
    quality_score: 0.92

  without_contributor:
    quality_score: 0.67

  observed_delta: 0.25

This supports a causal contribution claim.

It does not mean:

Contributor B = exactly 25% contribution

Counterfactual measurement is evidence, not absolute truth.

12. Why Leave-One-Out Is Not Enough

Contributors may interact.

Consider:

A alone → quality +0.01
B alone → quality +0.01

A + B → quality +0.30

Neither contributor appears important in isolation.

Together they create substantial additional value.

This means contribution may contain both:

Individual Contribution
+
Interaction Contribution

This limitation motivates v0.2.

13. v0.2 — Interaction and Coalition Contribution

v0.2 introduces the Contribution Interaction record.

Its purpose is to represent value that emerges from relationships among contributors.

Supported interaction types include:

complementary
redundant
synergistic
substitutive
blocking

The conceptual structure is:

Contributor A
      \
       \
        → Interaction → Outcome
       /
      /
Contributor B

For larger coalitions:

A
 \
B → Coalition Interaction → Outcome
 /
C

The protocol does not assume that interaction value belongs equally to coalition members.

For example:

A individual contribution = 0.20
B individual contribution = 0.18
A+B interaction contribution = distinct value

The interaction contribution remains separate until a downstream allocation method explicitly decides otherwise.

14. Complementarity

A complementary interaction occurs when contributors provide different capabilities that jointly form a useful result.

Example:

Retriever
    +
Verifier
    ↓
Reliable Evidence

Neither participant performs the other's role.

The value emerges through functional combination.

15. Redundancy

A redundant interaction occurs when multiple contributors provide overlapping capability.

Example:

Reasoner A
Reasoner B

may produce similar results.

Redundancy can improve resilience even when individual marginal effects are small.

A low marginal contribution does not necessarily mean the redundant contributor is useless.

It may provide:

reliability
fallback capacity
fault tolerance
independent confirmation
16. Synergy

A synergistic interaction occurs when the joint effect exceeds what would be expected from isolated contributions.

Example:

Retriever alone  → moderate result
Verifier alone   → limited result

Retriever + Verifier
        ↓
high-quality verified evidence

The additional effect is interaction contribution.

It should not automatically be assigned to one participant.

17. Substitution

A substitutive interaction describes contributors that can replace one another.

For example:

Primary Reasoner
Backup Reasoner

If replacing the primary with the backup preserves outcome quality, the primary may have high observed causal impact in one execution but relatively high substitutability.

This motivates distinguishing:

causal_impact
necessity
substitutability
18. Coalition Counterfactuals

v0.2 expands counterfactual reasoning beyond leave_one_out.

Examples include:

leave_group_out
pairwise_ablation
substitution_test

A coalition experiment may compare:

A + B + C

against:

without A+B

or:

A replaced by A'

These methods help expose interactions and substitution.

They still do not provide absolute causal truth.

19. v0.3 — Contribution Graph

Individual receipts and interaction records describe local claims.

v0.3 connects them into a Contribution Graph.

The graph asks:

Through what path did contribution reach the outcome?

A graph may contain:

contributor
contribution_receipt
contribution_interaction
evidence
decision
unresolved_segment
outcome

Example:

Human Problem Definition
        ↓
Receipt
        ↓
Evidence
        ↓
Architecture Decision
        ↓
Outcome

Or:

Retriever Receipt ─┐
                   ├→ Interaction → Evidence → Decision → Outcome
Verifier Receipt ──┘

The graph moves the protocol beyond isolated contribution records.

20. From Execution Trace to Contribution Graph

The model can be understood as a progression:

Execution Trace
      ↓
Dependency Trace
      ↓
Causal Evidence
      ↓
Contribution Receipt
      ↓
Interaction Record
      ↓
Contribution Graph
Execution Trace

Records what happened.

Agent B executed source verification.
Dependency Trace

Records who used the result.

Agent C consumed Agent B's verification output.
Causal Evidence

Estimates whether the dependency mattered.

Without Agent B, false evidence survives.
Contribution Receipt

Records one contributor's contribution claim.

Interaction Record

Records joint contribution among multiple contributors.

Contribution Graph

Connects those claims into a causal structure leading toward the outcome.

21. Unresolved Causal Segments

Real systems rarely provide perfect evidence.

The protocol therefore includes unresolved_segment.

Example:

Known Evidence
     ↓
Unresolved Segment
     ↓
Known Decision
     ↓
Outcome

An unresolved segment means:

We know part of the causal path exists,
but we cannot currently verify it completely.

It does not mean:

The causal effect was zero.

This principle becomes central in v0.5.

22. UNKNOWN Is Not ZERO

The protocol distinguishes:

unknown

from:

zero

Suppose available evidence explains:

75% of normalized contribution space

The remaining 25% should not automatically be assigned to known contributors.

Instead:

known = 0.75
unresolved = 0.25

This prevents artificial certainty.

The rule is:

UNKNOWN
≠
ZERO

and:

UNKNOWN
≠
automatic redistribution
23. v0.4 — Cross-Record Consistency

A Contribution Graph may be internally valid while still referring to external records that contradict it.

v0.4 therefore introduces the Contribution Bundle.

The bundle asks:

Do all referenced records describe the same contribution context?

The validation stack becomes:

Schema
  ↓
Semantic Validation
  ↓
Graph Validation
  ↓
Cross-Record Validation

A bundle connects:

Contribution Graph
Contribution Receipts
Contribution Interactions
Evidence
Outcome
24. Outcome Consistency

A valid bundle normally preserves:

Bundle Outcome
      =
Graph Outcome
      =
Receipt Outcomes
      =
Interaction Outcomes

For example:

outcome-401

should remain the same across the contribution records describing that evaluation context.

A mismatch such as:

Bundle  → outcome-401
Receipt → outcome-999

must be surfaced.

25. Contributor Consistency

The protocol also checks identity consistency.

For example:

Graph says:
Receipt X → Contributor A

Resolved Receipt X says:
Contributor B

This is inconsistent.

The validator should report the disagreement rather than silently choosing one version.

26. Interaction Membership Consistency

Suppose the graph claims:

Retriever + Verifier
        ↓
Interaction X

while the resolved interaction record claims:

Retriever + Reasoner
        ↓
Interaction X

The records do not describe the same coalition.

v0.4 rejects this mismatch.

27. Content Digests

v0.4 may use SHA-256 digests to identify exact record content.

Example:

digest:
  algorithm: sha256
  value: "..."

A digest verifies:

This exact serialized record

not:

Any record with approximately the same meaning

Therefore:

Same semantic meaning
≠
Same raw-content digest

if whitespace, serialization, or content changes.

This provides record identity rather than semantic equivalence.

28. Partial Evidence Can Still Be Valid

A Contribution Bundle does not need to pretend that every reference is available.

For example:

reference_coverage = 0.86
unresolved_reference_count = 1

may still represent a valid partial contribution context.

The important requirement is that missing information be explicit.

Therefore:

partial
≠
invalid

but:

hidden missing evidence
=
invalid confidence
29. v0.5 — Contribution Weight Assessment

v0.5 introduces relative contribution weight estimation.

The central question becomes:

Given the validated evidence, records, interactions, and unresolved segments, how much relative contribution does the evidence support for each contribution subject?

The model adds:

Contribution Bundle
        ↓
Weight Assessment

A Weight Assessment MAY evaluate:

contribution_receipt
contribution_interaction
contributor

depending on assessment scope.

30. Contribution Weight Is an Estimate

A contribution weight is not absolute truth.

Example:

estimated_weight: 0.32
lower_bound: 0.25
upper_bound: 0.39
confidence: 0.84

This means:

The available evidence supports an estimate around 0.32 within the declared assessment model.

It does not mean:

The true metaphysical contribution is exactly 32%.

Contribution is often partially observable and method-dependent.

The protocol therefore supports uncertainty explicitly.

31. Weight Bounds

Each weight may include:

lower_bound
estimated_weight
upper_bound

with the semantic rule:

lower_bound
<=
estimated_weight
<=
upper_bound

Wide bounds can represent weak or incomplete evidence.

Narrow bounds should require stronger evidential support.

This prevents false precision.

32. Confidence

confidence represents confidence in the Weight Assessment.

It is not the same as contribution magnitude.

For example:

estimated_weight = 0.40
confidence = 0.55

means:

The current estimate is large, but the evidence supporting the estimate is uncertain.

By contrast:

estimated_weight = 0.15
confidence = 0.98

means:

The estimated contribution is smaller, but the evidence supporting that estimate is strong.

33. Known and Unresolved Weight

For normalized v0.5 assessments:

sum(known estimated weights)
+
unresolved_weight
=
1.0

Example:

Human Problem Setter   0.36
Agent Architect        0.39
Unresolved             0.25
──────────────────────────
Total                  1.00

The unresolved_weight field is not an error bucket.

It represents contribution that cannot currently be assigned with sufficient evidential support.

This preserves:

UNKNOWN ≠ ZERO
34. Why Weight Should Not Always Sum to Known Contributors

A conventional allocation system may normalize known contributors so that they sum to 100%.

For example:

Observed:
A = 0.40
B = 0.30
C = 0.15

Known total = 0.85

A naive normalization might transform this into:

A = 0.4706
B = 0.3529
C = 0.1765

so that known contributors sum to 1.0.

The protocol deliberately avoids this when 0.15 remains unresolved.

Instead:

A = 0.40
B = 0.30
C = 0.15
Unresolved = 0.15

This is more honest about the evidence.

35. Weight Assessment Methods

v0.5 supports multiple estimation approaches.

Examples include:

evidence_weighted
counterfactual_marginal
coalition_adjusted
shapley_approximation
hybrid

No single method is declared universally correct.

Different domains may require different methods.

The method used should therefore be explicit.

36. Evidence-Weighted Assessment

An evidence-weighted approach may consider fields such as:

causal_impact
necessity
quality_impact
evidence_strength
substitutability

The protocol does not prescribe one universal formula.

A domain-specific implementation may define one.

For example:

Safety system
→ necessity and quality impact may receive greater emphasis

Research provenance
→ evidence strength may receive greater emphasis

Agent orchestration
→ causal impact and substitutability may receive greater emphasis

The base protocol records the factors and the resulting estimate without claiming one universal weighting rule.

37. Counterfactual Marginal Assessment

A counterfactual marginal method estimates how much the outcome changes when a contributor is removed or replaced.

Conceptually:

Marginal Impact_i
=
Baseline Quality
-
Quality Without i

This is useful but incomplete.

It may fail when:

contributors are substitutable
contributors interact strongly
routing changes after removal
model randomness changes execution
coalition structure changes

Counterfactual values therefore remain supporting evidence rather than absolute truth.

38. Coalition-Adjusted Assessment

Coalition-adjusted weighting preserves both individual and interaction contribution.

Example:

Retriever     0.22
Verifier      0.24
Reasoner      0.26
Interaction   0.18
Unresolved    0.10

The key property is:

Interaction Weight
≠
Individual Weight

The 0.18 interaction value should not automatically become:

Retriever +0.06
Verifier  +0.06
Reasoner  +0.06

unless an explicit downstream allocation policy decides to do that.

The Contribution Weight Assessment layer does not make that allocation decision automatically.

39. Shapley-Assisted Assessment

Shapley-style methods can help estimate relative marginal contribution across many possible coalitions.

Conceptually, Shapley analysis asks:

On average, how much additional value does contributor i create when joining different possible coalitions?

This can be useful for multi-agent systems.

However:

Shapley Value
≠
Absolute Causal Truth

because results depend on:

utility function
coalition space
sampled permutations
model stochasticity
measurement quality
substitutability
omitted contributors
evaluation scope

For large systems, exact Shapley computation may also be prohibitively expensive.

v0.5 therefore supports:

shapley_approximation

rather than treating exact Shapley computation as mandatory.

40. Interaction Weight Must Remain Separate

Consider:

Retriever individual weight = 0.22
Verifier individual weight  = 0.24
Reasoner individual weight  = 0.26
Coalition interaction       = 0.18

If the 0.18 is hidden inside the Verifier's weight:

Verifier = 0.42

the system loses the distinction between:

value produced by Verifier

and:

value produced by the coalition structure

This distinction is especially important in AI systems where orchestration itself may create substantial value.

41. Contribution Weight and Outcome Scope

A weight is only meaningful inside its declared assessment context.

For example:

Agent A contribution weight
for Outcome X

does not automatically imply the same weight for:

Outcome Y

Even if the same contributor participates in both.

Contribution Weight therefore depends on:

Contributor / Subject
+
Outcome
+
Evidence
+
Method
+
Coalition Structure
+
Assessment Scope

A weight should never be interpreted without these surrounding conditions.

42. Observation, Estimation, and Allocation

The protocol separates three stages:

Observation
    ↓
Estimation
    ↓
Allocation
Observation

What happened?

Examples:

execution trace
decision trace
evidence reference
interaction trace
counterfactual result
Estimation

What contribution does the evidence support?

Examples:

causal impact
necessity
quality impact
substitutability
interaction contribution
contribution weight
uncertainty
Allocation

What economic or legal consequence follows?

Examples:

attribution
ownership
entitlement
royalty
payment
settlement

The Causal Contribution Receipt Protocol through v0.5 covers Observation and Contribution Estimation.

It intentionally stops before economic Allocation.

43. Contribution Weight Is Not Entitlement

This boundary is fundamental.

Suppose:

Contributor A
estimated_weight = 0.35

This does not mean:

Contributor A owns 35%

or:

Contributor A receives 35% of revenue

or:

Contributor A has a legal claim to 35%

The correct relationship is:

Contribution Weight
        ↓
possible downstream input
        ↓
Attribution Policy
        ↓
Entitlement Policy
        ↓
Royalty Allocation
        ↓
Settlement

Each transition requires additional rules.

44. Cost and Contribution Remain Separate

A future economic system may distinguish:

Cost Recovery
+
Contribution Reward

Conceptually:

Payment_i
=
CostRecovery_i
+
ContributionReward_i

Cost recovery MAY compensate actual resource expenditure.

Contribution reward MAY depend on verified outcome contribution.

This prevents the incentive:

More wasteful computation
→ more reward

Instead, an efficient contribution may have:

low resource use
+
high outcome effect
=
high contribution

This is compatible with energy-efficient and dynamically routed AI systems.

45. Humans, Data, and AI in the Same Model

The contribution model intentionally treats heterogeneous subjects under one structural framework.

Example:

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
Integration

Auditor
  ↓
Error Prevention

Integrator
  ↓
Final Outcome

The final generator MUST NOT automatically receive full contribution credit.

Upstream contribution may include:

problem definition
evidence creation
constraint design
verification
error prevention
routing
integration

The model therefore supports both active computation and non-computational contribution.

46. Human Problem Definition as Contribution

A human may contribute by defining:

the problem
success conditions
constraints
values
priorities
exclusions
evaluation criteria

For example:

Human Problem Definition
        ↓
Architecture Search
        ↓
Agent Coordination
        ↓
System Design

The human may perform little computational work while having very high causal significance.

The protocol can represent this without forcing all contribution into the final AI generator.

47. Datasets and Sources as Contribution

A dataset or source may materially affect an outcome without performing active computation.

Example:

Primary Source
      ↓
Verified Evidence
      ↓
Reasoning
      ↓
Outcome

If removing the source significantly changes the result, the source may have meaningful causal contribution.

This enables future contribution systems to recognize upstream information resources rather than only execution agents.

48. Auditors and Error Prevention

Contribution does not require visible artifact generation.

An auditor may contribute by preventing an invalid result.

Example:

Candidate Output
      ↓
Auditor
      ↓
Critical Error Detected
      ↓
Output Blocked
      ↓
Corrected Outcome

Traditional activity accounting may undervalue this role.

Causal contribution analysis can represent it directly.

49. Relationship to Dynamic Shoal AI

Dynamic Shoal AI provides a useful environment for contribution analysis because participants are structurally separated.

A temporary shoal may contain:

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

The system can observe:

who was activated
what they received
what they produced
who consumed their output
what changed downstream
which interaction occurred
what remained unresolved

This creates better conditions for causal contribution analysis than a completely opaque monolithic process.

The Causal Contribution Receipt Protocol does not require Dynamic Shoal AI.

The two architectures are simply complementary.

50. Why Multi-Agent Systems Make Contribution More Observable

In a monolithic model, many internal operations are compressed into one execution.

In a multi-agent architecture, roles may become explicit:

Retrieval
Verification
Reasoning
Audit
Integration

This creates discrete contribution nodes.

As a result:

Execution
becomes
Structure

and:

Structure
becomes
Auditable Contribution Evidence

This does not automatically make attribution easy.

But it makes the causal structure more observable.

51. Evidence Before Weight

The protocol follows this order:

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

Weight should therefore be considered a later-stage estimate.

It should not be inferred directly from:

identity
model size
execution cost
token count
payment destination
visibility
final output ownership
52. Weight Precision and Evidence Precision

The precision of a contribution estimate should reflect the precision of its evidence.

If the evidence is weak, the system should not produce unjustifiably precise numbers.

For example:

Evidence strength = moderate
Causal path = partially unresolved

should favor:

estimated_weight = 0.39
range = 0.27–0.48
confidence = 0.68

rather than:

estimated_weight = 0.391728614

The latter may create an illusion of certainty unsupported by the evidence.

53. Why Uncertainty Is a First-Class Property

Uncertainty is not a defect to be hidden.

It provides useful structural information.

For example:

Contributor A
weight estimate = high
confidence = low

may indicate:

missing traces
insufficient coalition tests
unknown substitutes
incomplete evidence
unresolved causal segments

A downstream system can then decide whether to:

collect more evidence
run more counterfactual tests
request human review
delay allocation

Therefore uncertainty itself can guide future validation.

54. Contribution Graph to Weight Assessment

The complete v0.5 conceptual pipeline is:

Contributor
    ↓
Contribution Receipt
    ↓
Interaction Records
    ↓
Contribution Graph
    ↓
Contribution Bundle
    ↓
Cross-Record Validation
    ↓
Weight Assessment

This pipeline transforms raw activity into progressively more structured contribution evidence.

55. Example: Research Answer

Consider:

Retriever
Verifier
Reasoner

working together.

Observed individual contribution might support:

Retriever  = 0.22
Verifier   = 0.24
Reasoner   = 0.26

The coalition may also create:

Interaction = 0.18

while some contribution remains unresolved:

Unresolved = 0.10

The normalized assessment becomes:

Retriever     0.22
Verifier      0.24
Reasoner      0.26
Interaction   0.18
Unresolved    0.10
────────────────
Total         1.00

This structure preserves both individual and structural contribution.

56. Example: Partial System Design Evidence

Suppose a human defines the problem and an AI architect produces the final system design.

Available evidence supports:

Human Problem Setter = 0.36
Agent Architect      = 0.39

but part of the causal path remains unresolved.

Instead of normalizing:

0.36 + 0.39

to 100%, the protocol preserves:

Human Problem Setter = 0.36
Agent Architect      = 0.39
Unresolved           = 0.25

This is a more conservative and auditable representation.

57. Example: Shapley-Assisted Estimation

A multi-agent system may sample many coalitions.

For example:

{Retriever}
{Verifier}
{Reasoner}
{Retriever, Verifier}
{Retriever, Reasoner}
{Verifier, Reasoner}
{Retriever, Verifier, Reasoner}

The evaluator may estimate marginal contribution across these combinations.

This can support:

Retriever = 0.21
Verifier  = 0.27
Reasoner  = 0.30

while separately preserving interaction and unresolved contribution.

The Shapley-derived values remain estimates under the tested coalition model.

58. Economic Systems May Consume Contribution Weight

A future value-allocation system MAY use:

Contribution Weight

as one input among several.

Other inputs may include:

contract terms
ownership
licensing
identity
cost recovery
legal rights
policy
risk
tax
jurisdiction

Therefore:

Final Allocation
≠
Contribution Weight alone

This separation is necessary to avoid confusing causal contribution with legal or economic rights.

59. Relationship to Royalty Systems

A downstream royalty system may eventually use the structure:

Trace
  ↓
Contribution
  ↓
Weight
  ↓
Attribution
  ↓
Entitlement
  ↓
Allocation
  ↓
Royalty
  ↓
Settlement

The Causal Contribution Receipt Protocol currently covers:

Trace-adjacent Evidence
Contribution
Interaction
Graph
Cross-Record Validation
Weight

It intentionally stops before:

Attribution ownership
Entitlement
Royalty allocation
Settlement

This keeps contribution measurement reusable across many economic and governance systems.

60. Why the Protocol Stops Before Payment

If Contribution Weight directly created payment, circular reasoning could emerge.

For example:

Contributor receives 40%
therefore
Contributor must have contributed 40%

or:

Contribution Weight is 40%
therefore
Contributor must receive 40%

Both are structurally unsafe assumptions.

The protocol instead preserves a boundary:

Measurement
    ↓
Decision Boundary
    ↓
Allocation
61. Contribution as a Causal Surface

Through v0.5, contribution can be understood as a causal surface rather than a single number.

The surface includes:

individual effects
interaction effects
substitution
necessity
quality impact
counterfactual evidence
uncertainty
unresolved contribution

A scalar weight is therefore only a summary projection of a richer causal structure.

The richer evidence should remain available for audit.

62. No Universal Contribution Formula

The protocol does not define:

Contribution =
0.3 × causal_impact
+
0.2 × necessity
+
...

as a universal rule.

Such formulas may be domain-specific.

A safety-critical system may value:

error prevention
necessity
quality preservation

more strongly.

A research provenance system may value:

evidence strength
source originality
downstream influence

more strongly.

The protocol therefore separates:

evidence structure

from:

evaluation policy
63. Model Independence

The protocol does not depend on a particular AI model, vendor, or architecture.

It can be applied to:

large language models
small local models
multi-agent systems
human-AI collaboration
tool-using agents
data pipelines
hybrid systems

The contribution structure exists above the model layer.

This allows the same protocol to survive changes in underlying model technology.

64. Minimality Principle

Contribution analysis SHOULD expose enough information to support audit without requiring unnecessary disclosure.

The protocol SHOULD prefer:

reference
digest
decision record
evidence identifier
result delta
structured assessment

over unnecessary disclosure of:

complete private reasoning
hidden chain-of-thought
proprietary prompts
model internals
unrelated personal information

Contribution auditing should not require total internal transparency.

65. v0.5 Contribution Model Summary

The complete model can be summarized as:

                       ┌──────────────────┐
                       │   Contributor    │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Contribution     │
                       │ Receipt          │
                       └────────┬─────────┘
                                │
               ┌────────────────┴────────────────┐
               │                                 │
               ▼                                 ▼
      ┌──────────────────┐             ┌──────────────────┐
      │ Individual       │             │ Interaction /    │
      │ Contribution     │             │ Coalition        │
      └────────┬─────────┘             └────────┬─────────┘
               │                                 │
               └────────────────┬────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Contribution     │
                       │ Graph            │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Contribution     │
                       │ Bundle           │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Cross-Record     │
                       │ Validation       │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Contribution     │
                       │ Weight           │
                       │ Assessment       │
                       └────────┬─────────┘
                                │
                                ▼
                    ─────────────────────────
                         Protocol Boundary
                    ─────────────────────────
                                │
                                ▼
                       Attribution
                                │
                                ▼
                       Entitlement
                                │
                                ▼
                       Royalty Allocation
                                │
                                ▼
                       Settlement
66. Design Principle

The protocol can be summarized by several progressively stronger statements.

v0.1:

Measure what changed because a contributor was present, not merely how much activity the contributor performed.

v0.2:

Preserve value that emerges from interactions instead of forcing all contribution into individuals.

v0.3:

Represent contribution as a causal path rather than isolated claims.

v0.4:

Verify that independently stored contribution records describe a consistent reality.

v0.5:

Estimate relative contribution without pretending that uncertainty is zero or that contribution automatically creates economic rights.

Or more compactly:

Activity tells us who worked.

Trace tells us what happened.

Causal evidence tells us what mattered.

Interaction tells us what emerged between contributors.

Graph tells us how contribution flowed.

Cross-record validation tells us whether the records agree.

Weight tells us how much relative contribution the evidence supports.

Downstream systems decide what rights or payments follow.

That separation is the foundation of the Causal Contribution Receipt Protocol through v0.5.
