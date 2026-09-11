# Causal Contribution Receipt Protocol — Core Invariants

Version: v0.1

## 1. Purpose

The Causal Contribution Receipt Protocol records evidence-backed claims about how a contributor participated in the formation of an outcome.

The protocol distinguishes contribution from activity, ownership, entitlement, and payment.

The central principle is:

> Work performed is not equivalent to contribution created.

A contributor MAY consume substantial resources while having little causal effect on an outcome.

A contributor MAY also perform a small amount of work while having a decisive effect on quality, safety, correctness, or usefulness.

The protocol therefore records multiple dimensions of contribution independently.

---

## 2. Terminology

### Contributor

An entity whose participation is being evaluated.

Examples include:

* human
* agent
* dataset
* source
* tool
* service

### Outcome

The result to which the contribution claim refers.

Examples include:

* generated answer
* system design
* research summary
* decision
* software artifact
* audited result

### Evidence

Traceable references supporting a contribution claim.

Evidence MAY include:

* source inputs
* generated outputs
* decisions
* downstream usage
* audit records
* execution traces

### Assessment

A structured observation of contribution-related dimensions.

In v0.1, the assessment dimensions are:

* `work`
* `causal_impact`
* `necessity`
* `quality_impact`
* `evidence_strength`

### Counterfactual Assessment

An optional evaluation of what changes when the contributor is removed from the evaluated process.

v0.1 supports the `leave_one_out` method.

A counterfactual result is evidence supporting a contribution claim.

It is not absolute causal truth.

---

## 3. Core Invariants

### CCR-INV-001 — Every Contribution Receipt MUST reference an outcome

A contribution has meaning only relative to an identifiable result.

A receipt without an outcome is invalid.

```text
Contributor
    ↓
Contribution
    ↓
Outcome
```

The protocol MUST NOT record contribution as an isolated property of an entity.

---

### CCR-INV-002 — Every Contribution Receipt MUST identify exactly one contributor

Each receipt evaluates one contributor relative to one outcome.

A contributor MAY be a human, agent, dataset, source, tool, or service.

If multiple contributors are evaluated, separate receipts SHOULD be issued.

```text
Outcome
 ├─ Receipt A → Contributor A
 ├─ Receipt B → Contributor B
 └─ Receipt C → Contributor C
```

This rule keeps individual claims independently auditable.

---

### CCR-INV-003 — Work MUST NOT be treated as equivalent to contribution

Resource consumption alone MUST NOT determine causal contribution.

The following measurements MAY be recorded as work:

* inference time
* token usage
* GPU usage
* API calls
* execution duration
* storage usage
* network usage

However:

```text
High Work
≠
High Contribution
```

and:

```text
Low Work
≠
Low Contribution
```

Example:

```text
Agent A
1,000,000 tokens
No material effect on final result

Agent B
300 tokens
Detects critical false evidence
Prevents incorrect final output
```

Agent B MAY have substantially higher causal contribution despite performing less work.

---

### CCR-INV-004 — Contribution claims MUST include evidence references

A receipt MUST contain traceable evidence supporting the contribution claim.

A self-declared statement such as:

```text
"I made an important contribution."
```

is insufficient.

At least one evidence reference MUST be present.

Evidence SHOULD allow an auditor to reconstruct at least part of the following relationship:

```text
Input
  ↓
Contributor Action
  ↓
Recorded Output or Decision
  ↓
Downstream Use
  ↓
Outcome
```

---

### CCR-INV-005 — Counterfactual measurements MUST NOT be treated as absolute causal truth

A counterfactual experiment estimates what might have occurred without a contributor.

For example:

```text
Baseline:
A + B + C + D → quality 0.92

Without B:
A + C + D → quality 0.67

Observed delta:
0.25
```

The value `0.25` is evidence of possible causal significance.

It MUST NOT automatically be interpreted as:

```text
B contributed exactly 25%
```

Interaction effects, substitution effects, model randomness, measurement error, and evaluator uncertainty MAY affect the result.

---

### CCR-INV-006 — Contribution classification MUST NOT directly imply payment entitlement

The following classes MAY be used:

```text
critical
high
medium
low
incidental
```

These classes summarize contribution assessment for human and machine interpretation.

However:

```text
critical
≠
payment entitlement
```

and:

```text
critical
≠
fixed royalty percentage
```

Contribution classification MUST NOT directly create a financial claim.

---

### CCR-INV-007 — Contribution, Attribution, Entitlement, and Settlement MUST remain separate

The protocol MUST preserve the following separation:

```text
Contribution
    ≠
Attribution
    ≠
Entitlement
    ≠
Settlement
```

These concepts answer different questions.

#### Contribution

What materially affected the outcome?

#### Attribution

To whom or what should that contribution be associated?

#### Entitlement

Does that contribution create a valid right to receive value?

#### Settlement

What value is actually transferred, to whom, when, and under what rules?

The Causal Contribution Receipt Protocol v0.1 addresses Contribution only.

Downstream protocols MAY consume contribution receipts when performing attribution, entitlement, royalty allocation, or settlement.

---

## 4. Separation of Observation and Judgment

v0.1 intentionally keeps assessment dimensions separate.

For example:

```yaml
assessment:
  work: 0.12
  causal_impact: 0.82
  necessity: 0.74
  quality_impact: 0.91
  evidence_strength: 0.96
```

The protocol does not define:

```text
contribution_score =
  weighted_average(...)
```

in v0.1.

This avoids prematurely embedding subjective weighting rules into the base protocol.

Different domains MAY later use different evaluation policies.

For example:

```text
Safety-critical system
→ quality_impact and necessity weighted strongly

Research provenance
→ evidence_strength weighted strongly

Economic allocation
→ causal_impact and verified downstream use weighted strongly
```

The receipt should preserve observations before economic or governance policies interpret them.

---

## 5. Evidence Before Allocation

The protocol follows this order:

```text
Trace
  ↓
Evidence
  ↓
Contribution Assessment
  ↓
Contribution Receipt
```

Only after a valid Contribution Receipt exists MAY downstream systems perform:

```text
Attribution
  ↓
Entitlement
  ↓
Royalty Allocation
  ↓
Settlement
```

A settlement system SHOULD NOT infer contribution solely from payment destination, identity, resource usage, or execution logs.

---

## 6. Human and Machine Contributions

The protocol MUST NOT assume that the final generator is the primary contributor.

An outcome MAY result from a structure such as:

```text
Human
  ↓
Problem Definition

Dataset
  ↓
Primary Evidence

Agent A
  ↓
Extraction

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
```

Each component MAY have independently meaningful contribution.

A human who defines the problem or constraints MAY be more causally significant than the system that renders the final text.

Likewise, a dataset or evidence source MAY materially contribute without performing active computation.

---

## 7. Minimality Principle

A Contribution Receipt SHOULD contain only information necessary to support and audit the contribution claim.

The protocol SHOULD NOT require disclosure of complete private reasoning, model internals, proprietary prompts, hidden chain-of-thought, or unrelated personal information.

Where possible, implementations SHOULD prefer:

```text
reference
hash
decision record
result delta
evidence identifier
```

over unnecessary full-content replication.

---

## 8. Non-Goals of v0.1

v0.1 does not define:

* Shapley value computation
* coalition contribution
* interaction contribution
* global contribution ranking
* royalty percentages
* ownership
* copyright status
* payment entitlement
* settlement instructions
* currency
* payment rails
* dispute resolution
* contributor identity resolution

These MAY be introduced through later versions or separate protocols.

---

## 9. v0.1 Boundary

The defining question of v0.1 is:

> Can a system record a machine-readable, evidence-backed claim describing how one contributor affected one identifiable outcome?

If yes, the protocol has completed its responsibility.

Everything beyond that boundary belongs to downstream evaluation, attribution, governance, or settlement systems.
