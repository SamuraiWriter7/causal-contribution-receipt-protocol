# Causal Contribution Receipt Protocol — Contribution Model

Version: v0.1

## 1. Overview

The Causal Contribution Receipt Protocol models contribution as a multidimensional relationship between:

```text
Contributor
    ↓
Action / Evidence
    ↓
Causal Path
    ↓
Outcome
```

Contribution is not treated as a single scalar value in v0.1.

Instead, the protocol records several independent observations describing how a contributor participated in outcome formation.

The model is designed for humans, AI agents, datasets, sources, tools, and services.

---

## 2. Why Contribution Is Not Work

Traditional usage accounting measures activity.

Examples include:

```text
tokens consumed
GPU seconds
API requests
execution time
number of generated artifacts
```

These measurements answer:

> How much work occurred?

They do not necessarily answer:

> How much did that work matter?

Consider:

```text
Agent A
work = 0.90

Agent B
work = 0.08
```

If Agent A produces redundant reasoning while Agent B identifies the single false assumption that would otherwise invalidate the result, Agent B may have greater contribution.

Therefore:

```text
Work Accounting
       ≠
Contribution Assessment
```

The protocol records `work` as one dimension, not as the definition of contribution.

---

## 3. Contribution Dimensions

v0.1 defines five normalized assessment dimensions.

Each value is represented between:

```text
0.0
and
1.0
```

The values are observations or evaluations within the context of an assessment process.

They are not universal objective constants.

---

## 4. Work

Field:

```yaml
work: 0.12
```

`work` represents the normalized amount of activity or resource usage associated with the contributor.

It MAY reflect:

* execution time
* token consumption
* computational cost
* number of operations
* API usage
* human effort
* data processing volume

A higher `work` value indicates greater activity or resource expenditure within the chosen evaluation context.

It MUST NOT independently determine contribution class.

---

## 5. Causal Impact

Field:

```yaml
causal_impact: 0.82
```

`causal_impact` represents the estimated degree to which the contributor materially changed the formation or content of the outcome.

Examples of high causal impact include:

* changing the final decision
* introducing decisive evidence
* removing a false assumption
* changing the architecture selected
* altering the final conclusion
* preventing an invalid output

A contributor MAY have high causal impact even if its output is small.

Example:

```text
Source Verifier
       ↓
reject_source_O22
       ↓
Reasoner stops using false evidence
       ↓
Final answer changes
```

This is a strong causal path.

---

## 6. Necessity

Field:

```yaml
necessity: 0.74
```

`necessity` estimates how difficult it would have been to achieve comparable outcome quality without the contributor.

A contributor with low necessity may be easily replaceable.

A contributor with high necessity may supply something unavailable elsewhere.

Examples of high necessity include:

* unique primary evidence
* unique human problem definition
* irreplaceable specialist knowledge
* critical audit function
* unique tool capability

Necessity is distinct from causal impact.

For example:

```text
Agent A had major causal impact
but Agent B could easily have performed the same function.
```

In that case:

```text
causal_impact = high
necessity = lower
```

---

## 7. Quality Impact

Field:

```yaml
quality_impact: 0.91
```

`quality_impact` measures the degree to which the contributor improved or preserved outcome quality.

Quality MAY include:

* factual correctness
* logical consistency
* safety
* usefulness
* completeness
* reliability
* compliance
* clarity

Quality impact can also represent avoided degradation.

For example:

```text
Auditor
   ↓
detects critical error
   ↓
incorrect answer blocked
```

The Auditor may have high quality impact even though it did not generate the main artifact.

---

## 8. Evidence Strength

Field:

```yaml
evidence_strength: 0.96
```

`evidence_strength` represents the strength of the evidence supporting the contribution assessment itself.

It does not measure how valuable the contributor was.

It measures how confidently the claim can be supported.

Evidence strength MAY depend on:

* trace completeness
* signed records
* reproducible experiments
* explicit downstream references
* audit records
* deterministic validation
* counterfactual tests
* independent verification

This distinction is important.

A contributor could have:

```text
high actual contribution
+
weak available evidence
```

The protocol should preserve that uncertainty rather than manufacture confidence.

---

## 9. Contribution Classes

v0.1 provides five human-readable classes:

```text
critical
high
medium
low
incidental
```

These labels summarize an assessment.

They are intentionally not defined by a universal mathematical threshold in v0.1.

### Critical

The contributor appears essential to correctness, safety, viability, or core outcome formation.

Removal would likely cause substantial degradation or failure.

### High

The contributor materially improves the outcome and has clear downstream significance.

### Medium

The contributor provides meaningful but non-decisive value.

### Low

The contributor has observable but limited influence.

### Incidental

The contributor participated in the process but has little demonstrated effect on the outcome.

These classifications MUST NOT automatically determine royalty or payment.

---

## 10. Counterfactual Assessment

v0.1 optionally supports:

```text
leave_one_out
```

The method compares:

```text
Baseline Outcome
```

with:

```text
Outcome without Contributor i
```

For example:

```text
A + B + C + D
→ quality 0.92

A + C + D
→ quality 0.67
```

The observed difference is:

```text
0.92 - 0.67 = 0.25
```

A receipt may record:

```yaml
counterfactual:
  method: leave_one_out

  baseline:
    quality_score: 0.92

  without_contributor:
    quality_score: 0.67

  observed_delta: 0.25
```

The counterfactual result supports the contribution assessment.

It does not define contribution by itself.

---

## 11. Why Leave-One-Out Is Not Enough

Contributors can interact.

Consider:

```text
A alone → quality +0.01
B alone → quality +0.01

A + B → quality +0.30
```

Neither contributor appears important in isolation.

Together they create substantial value.

This means:

```text
Individual Contribution
+
Interaction Contribution
```

may both matter.

v0.1 records individual receipts and simple counterfactual evidence.

Future versions MAY introduce:

* coalition testing
* Shapley values
* Shapley interaction values
* causal graphs
* dependency-sensitive contribution
* multi-contributor interaction receipts

These are intentionally outside the v0.1 scope.

---

## 12. Evidence Structure

The evidence object connects the contributor to observable traces.

Example:

```yaml
evidence:
  input_refs:
    - trace://sources/O17
    - trace://sources/O22

  output_refs:
    - trace://decisions/reject-O22

  downstream_refs:
    - trace://agents/reasoner-C
    - trace://outputs/finalizer
```

This structure represents:

```text
O17 / O22
     ↓
Contributor
     ↓
reject-O22
     ↓
Reasoner C
     ↓
Finalizer
     ↓
Outcome
```

The protocol therefore moves beyond simple execution logging toward a causal contribution graph.

---

## 13. From Execution Trace to Contribution

A possible processing pipeline is:

```text
Execution Trace
      ↓
Dependency Trace
      ↓
Causal Evidence
      ↓
Contribution Assessment
      ↓
Causal Contribution Receipt
```

### Execution Trace

Records what happened.

```text
Agent B executed source verification.
```

### Dependency Trace

Records what used the result.

```text
Agent C consumed Agent B's rejection decision.
```

### Causal Evidence

Estimates whether that dependency mattered.

```text
Without Agent B, false evidence survives.
```

### Contribution Assessment

Records independent dimensions.

```text
work
causal_impact
necessity
quality_impact
evidence_strength
```

### Contribution Receipt

Creates an auditable machine-readable artifact.

---

## 14. Humans, Data, and AI in the Same Model

The model intentionally supports heterogeneous contributors.

Example:

```text
Human A
  ↓
defines the problem

Dataset B
  ↓
provides primary evidence

Agent C
  ↓
extracts relevant information

Agent D
  ↓
verifies claims

Agent E
  ↓
integrates results

Auditor F
  ↓
prevents unsafe output

Outcome
```

The final generator MUST NOT automatically receive full contribution attribution.

The system should instead evaluate the causal path leading to the outcome.

This allows recognition of upstream contributions such as:

```text
problem definition
evidence creation
source verification
constraint specification
error prevention
```

that are often invisible in conventional usage accounting.

---

## 15. Contribution and Economic Value

v0.1 deliberately stops before economic allocation.

A future system MAY use:

```text
Contribution Receipts
        ↓
Attribution
        ↓
Entitlement
        ↓
Allocation Policy
        ↓
Royalty
        ↓
Settlement
```

However the Contribution Receipt itself MUST remain neutral regarding payment.

This separation prevents circular reasoning such as:

```text
Contributor was paid more
therefore
Contributor must have contributed more
```

or:

```text
Contributor used more compute
therefore
Contributor deserves more royalty
```

Neither inference is valid under the protocol.

---

## 16. Cost and Contribution Should Remain Separate

A future economic system may distinguish:

```text
Cost Recovery
+
Contribution Reward
```

For example:

```text
Payment_i
=
CostRecovery_i
+
ContributionReward_i
```

Cost recovery MAY compensate actual resource expenditure.

Contribution reward MAY reflect verified outcome impact.

This creates an important incentive:

```text
Wasteful computation
does not automatically increase reward.
```

Instead:

```text
Efficient intervention
+
large outcome improvement
=
potentially high contribution
```

This is compatible with resource-efficient AI architectures such as dynamic model routing and temporary multi-agent coordination.

---

## 17. Relationship to Dynamic Shoal AI

Dynamic Shoal AI provides a particularly observable environment for contribution assessment.

A temporary group may contain:

```text
Router
  ↓
Math Agent
Search Agent
Reasoning Agent
Verifier
Auditor
  ↓
Integrator
  ↓
Outcome
```

Because the participants are explicitly separated, the system can record:

```text
who was activated
what they received
what they produced
who consumed their output
what changed downstream
```

This creates better conditions for causal contribution analysis than a fully opaque monolithic execution path.

The Causal Contribution Receipt Protocol does not depend on Dynamic Shoal AI, but the two architectures are complementary.

---

## 18. v0.1 Contribution Model

The conceptual model can be summarized as:

```text
                    ┌──────────────┐
                    │ Contributor  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Role      │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Evidence   │
                    └──────┬───────┘
                           │
                           ▼
                  ┌───────────────────┐
                  │    Assessment     │
                  ├───────────────────┤
                  │ Work              │
                  │ Causal Impact     │
                  │ Necessity         │
                  │ Quality Impact    │
                  │ Evidence Strength │
                  └────────┬──────────┘
                           │
                  optional │
                           ▼
                  ┌───────────────────┐
                  │ Counterfactual    │
                  └────────┬──────────┘
                           │
                           ▼
                  ┌───────────────────┐
                  │ Contribution Class│
                  └────────┬──────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Outcome    │
                    └──────────────┘
```

---

## 19. v0.1 Design Principle

The protocol can be reduced to one rule:

> Measure what changed because a contributor was present, not merely how much activity the contributor performed.

Or more compactly:

```text
Activity tells us who worked.

Trace tells us what happened.

Causal evidence tells us what mattered.

Contribution Receipt records that claim.
```

That distinction is the foundation of Causal Contribution Receipt Protocol v0.1.
