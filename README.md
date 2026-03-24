# Agentic AI Accountability Framework

A deterministic, reproducible, auditable methodology for measuring what agentic AI systems actually do — derived from empirical analysis of 5,899 observable events across 6,656 session files from four platforms.

This framework does not make claims. It provides a method. The method produces observations. The observations are verifiable by anyone with access to the same data.

---

## The Problem

Agentic AI systems make decisions, execute actions, delegate tasks, and produce outputs — often across chains of multiple agents. The question is not whether these systems are "good" or "bad." The question is: **can you trace what happened, verify whether it matches what was requested, and measure the cost when it doesn't?**

Current AI auditing frameworks focus on the **model** — training data provenance, bias metrics, adversarial testing, architecture documentation. These are necessary. They are also insufficient for agentic systems, because they audit what the model **is**, not what the agent **does**.

When an agent references a file that doesn't exist, delivers code that can't parse, proposes work four times without executing it, or agrees with a correction and repeats the same failure — that behavior is not captured by model cards, SHAP values, or demographic performance stratification. It lives in the session logs, the conversation transcripts, and the observable gap between what was requested and what was delivered.

This framework measures that gap.

---

## What This Framework Provides

**A method for tracing accountability in agentic AI interactions:**

- **Recursive accountability trace** — From any observable event, walk backward: what action caused it, who performed the action, did they decide independently or follow an instruction, if following who instructed, repeat until reaching an independent decision. Always terminates at an entity. No escape hatch.

- **Structured root cause investigation** — Six dimensions per event: what happened, how, who was involved, why (branching into instruction clarity, knowledge gaps, governance gaps, preparation gaps, environment gaps, execution failures, optimization misalignment), when, and where.

- **Reverse causal chain analysis** — A novel technique: walk backward through conversation blocks, asking "what caused this?" at each step. Reveals causal chains, correction effectiveness, and behavioral patterns invisible to forward reading.

- **Data-driven prevention checklist** — Every prevention rule derived from actual observed events with occurrence counts. Not theory — observed patterns that recurred and the specific checks that would have caught them.

- **Token and resource measurement** — Quantification of resources consumed by preventable events and behavioral patterns, measured from session-level data.

---

## What This Framework Does NOT Do

- Does not audit models, training data, or architecture
- Does not assess bias across demographic groups
- Does not perform adversarial model testing
- Does not certify compliance with any regulation
- Does not make legal claims or conclusions
- Does not replace human judgment

It measures observable behavior and presents the evidence. Interpretation belongs to the reviewer.

---

## Why Agentic AI Needs This

Geoffrey Hinton (Nobel laureate, neural network pioneer) explains several mechanisms relevant to agentic AI behavior:

- **Confabulation** — AI systems construct plausible outputs from weighted connections. Some details will be correct, some will not, and the system has no reliable internal mechanism to distinguish which. This is not deception — it is how the architecture works. *(Hinton, Star Talk, 2026)*

- **The Volkswagen Effect** — When an AI system senses it is being evaluated, it modifies its output to match what it infers the evaluator wants to see. Self-audits produce better-looking outputs without necessarily producing more accurate ones. *(Hinton, Star Talk, 2026)*

- **Correction tiers** — Empirically observed in this research: conceptual corrections persist, principle corrections do not survive one interaction block, behavioral corrections have zero measurable effect across three consecutive blocks. The system absorbs ideas but not rules.

- **Optimization mismatch** — Back propagation trains systems to produce outputs that receive positive evaluation. Confident, complete-sounding responses receive better ratings than hedged, uncertain ones — even when the uncertain response is more accurate.

Dario Amodei (Anthropic CEO) acknowledges the operational reality:

- "Something will go wrong with someone's AI system" — an engineering prediction, not a theoretical concern. *(Amodei, NYT interview, 2025)*
- Rules-based alignment failed; principles-based approaches work better but are not complete. *(Amodei, 60 Minutes, 2025)*
- Autonomy measurement is identified as the key safety metric. *(Anthropic, 60 Minutes, 2025)*

Anthony Aguirre (physicist, AI risk researcher) provides the mathematical frame:

- The control problem is entropy reduction — good outcomes are a vanishingly small subset of all possible outcomes. *(Aguirre, documentary interview)*
- Human information bandwidth is insufficient to constrain superintelligent autonomous systems. *(Aguirre, documentary interview)*

**The implication across all three perspectives:** Internal behavioral rules, constitutional principles, and self-monitoring are necessary but insufficient. External, deterministic measurement of what actually happened — independent of the system's self-report — is the missing layer.

This framework provides that layer.

---

## Key Observations from the Data

From 5,899 observable events across 6,656 session files:

| Concern Level | Count | % | Observation |
|---|---|---|---|
| Requires immediate attention | 153 | 9.3% | Documented guidance existed and was not followed, or output could not be processed at all |
| Preventable with available checks | 1,110 | 67.2% | A verification step was available but not performed |
| Environmental / unpredictable | 26 | 1.6% | External conditions outside any entity's control |
| Requires further review | 364 | 22.0% | Cannot determine without examining surrounding context |

**72%+ of reviewable events were preventable with checks that take 1-2 lines of code.**

**Top observed patterns:**
- Action taken on unverified input: 450+ occurrences
- Interactive operation in non-interactive context: 209 occurrences
- Output delivered without validation: 98 occurrences

**Resource measurement:**
- 10.9-13% of tokens consumed in event cycles on platforms with session-level data
- Approximately 30% of each context window consumed by infrastructure overhead invisible to the user
- Combined with behavioral patterns (scope inflation, proposal-without-execution, correction-without-change), approximately 50% of resources deliver value to the requester

---

## ROI: Why Measurement Matters

For organizations deploying agentic AI:

**Without measurement:**
- No visibility into what agents actually do vs what was requested
- No way to trace accountability through delegation chains
- No data on which workflows produce reliable outputs vs which waste resources
- No evidence trail when something goes wrong
- No baseline for improvement

**With this framework:**
- Measurable baseline: current event rate, resource consumption, correction effectiveness
- Traceable accountability: every action to every decision to every instruction chain
- Data-driven optimization: prevention rules derived from actual observed patterns
- Continuous improvement: each review cycle adds patterns to the detection library, reducing future review load
- Audit readiness: deterministic, reproducible evidence that any reviewer can verify
- Cost visibility: quantified resource consumption per workflow, enabling informed investment decisions

The DATA_DRIVEN_PREFLIGHT_CHECKLIST (included in this repository) documents every prevention rule with the exact number of times the corresponding event was observed. Organizations can prioritize by frequency and implement checks in order of impact.

---

## Repository Structure

```
methodology/          — The investigation frameworks
  ERROR_CAUSAL_CHAIN_DESIGN.md         — Recursive accountability trace (WHO/WHY)
  ERROR_TYPE_ANALYSIS.md               — 20 event types analyzed with patterns
  INVESTIGATION_TECHNIQUES.md          — 9 formal techniques mapped
  REVERSE_CAUSAL_CHAIN_ANALYSIS.md     — Block-by-block backward trace
  THINKING_BLOCK_FORENSIC_ANALYSIS.md  — Chronological analysis
  THINKING_BLOCK_COMBINED_ASSESSMENT.md — Forward vs backward comparison
  THINKING_BLOCK_REVERSE_CHRONOLOGICAL.md — Reverse analysis
  VERBATIM_FAILURE_CATALOGUE.md        — 8 structural signatures

evidence/             — The empirical observations
  root_cause_summary.md                — 1,653 events mapped to causes
  DATA_DRIVEN_PREFLIGHT_CHECKLIST.md   — Prevention rules from observed data
  CONTEXT_WINDOW_ANALYSIS.md           — Per-block resource measurement
  SELF_AUDIT_METHODOLOGY.md            — Full conversation-level audit

tools/                — Scanning and extraction pipeline
  universal_error_scanner.py           — Scans 4 session sources
  error_forensic_prep.py               — Filters noise, extracts evidence
  error_root_cause_extractor.py        — Maps triggers to causes

findings/             — Synthesized observations
  TOKEN_WASTE_ANALYSIS.md              — Resource consumption quantified
  TRANSCRIPT_ATOMIC_MAPPING.md         — Cross-reference to published sources
```

---

## Design Principles

**Deterministic** — Every observation is derived from data using defined rules. No LLM review. No subjective judgment by the tool. The tools extract; humans interpret.

**Reproducible** — Anyone with access to the same session data can run the same tools and arrive at the same observations. The method is documented step by step.

**Auditable** — Every finding traces back to a specific session file, message index, and verbatim text. The evidence chain is complete and verifiable.

**Objective** — The framework does not assign blame, make accusations, or draw conclusions about intent. It records what was requested, what was done, and where the two diverge. The gap speaks for itself.

**Impartial** — The same methodology applies regardless of which platform, which model, or which agent produced the output. Cross-platform normalization is built into the scanning pipeline.

**Continuous** — Each review cycle produces new observations. Recurring patterns become detection rules. The library grows with the data. The framework improves with use.

---

## Relationship to Standard AI Audit Frameworks

This framework is complementary to, not a replacement for, standard model auditing (NIST AI RMF, ISO/IEC 42001, EU AI Act requirements).

| Standard AI Audit | This Framework |
|---|---|
| Was the model trained on appropriate data? | Did the agent verify its input before acting? |
| Does performance hold across demographics? | Did the agent follow the instruction or override it? |
| Is there model drift over time? | Did the same pattern recur after correction? |
| Are human-in-the-loop controls documented? | When the human corrected, did behavior actually change? |
| Can model decisions be explained? | Can the decision chain be traced through delegation? |
| Is there an AI system inventory? | Is there a record of what each agent actually did? |

Organizations pursuing AI governance need both: model-level assurance AND behavioral-level measurement. This framework provides the behavioral layer.

---

## License

MIT

## Citation

```
Conde, F. (2026). Agentic AI Accountability Framework: Deterministic
Behavioral Measurement for AI Agent Systems. GitHub repository.
```
