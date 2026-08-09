# Agentic AI Accountability Framework

An evidence-first methodology for measuring what agentic AI systems actually do — derived from empirical analysis of observable events in session records from four platforms.

This framework minimizes normative claims and prioritizes observable, reproducible measurements within explicitly stated limits. Where the methodology is deterministic under fixed inputs and rules, that is stated. Where analyst judgment is required, that is stated too. See `FORMAL_DEFINITIONS.md` and `REPRODUCIBILITY_MANIFEST.md` for exact terms and scope.

## Status

This repository is the canonical public statement of the methodology. It is cited in a public comment filed on FTC Docket No. FTC-2026-0859 (Matter No. P264200). Revisions are made by addition, recorded in `CHANGELOG.md`; the version cited in any external filing remains recoverable from the revision history.

## Scope and Limits

- This framework evaluates observable workflow behavior, not model internals.
- It does not establish legal conclusions.
- It does not prove latent mechanism causes from external evidence alone.
- Some headline metrics depend on upstream data artifacts not included in this public repository. Where that is the case, it is stated explicitly in the Reproducibility Manifest and repeated inline wherever the metric appears.
- The scanning, filtering, and extraction tools are deterministic given fixed inputs. The accountability trace and root cause investigation require analyst judgment.
- The methodology is applicable to any compatible session data once source paths are configured. The specific observations from the author's dataset require the author's data.

## The Problem

Agentic AI systems make decisions, execute actions, delegate tasks, and produce outputs — often across chains of multiple agents. The question is not whether these systems are "good" or "bad." The question is: can you trace what happened, verify whether it matches what was requested, and measure the cost when it doesn't?

Current AI auditing frameworks focus on the model — training data provenance, bias metrics, adversarial testing, architecture documentation. These are necessary. They are also insufficient for agentic systems, because they audit what the model *is*, not what the agent *does*.

When an agent references a file that doesn't exist, delivers code that can't parse, proposes work four times without executing it, or agrees with a correction and repeats the same failure — that behavior is not captured by model cards, SHAP values, or demographic performance stratification. It lives in the session logs, the conversation transcripts, and the observable gap between what was requested and what was delivered.

This framework measures that gap.

## Why External Measurement

The framework rests on one premise, stated as its own claim rather than borrowed from authority:

**A system's statement that work occurred is not evidence that the work occurred.** Language models generate the most plausible next output; they have no reliable internal channel connecting a claim like "read in full," "tested," or "fixed" to the operational record of what was actually read, run, or changed. Confident completion language and accurate completion language are produced by the same mechanism and are indistinguishable at the surface. This holds equally for a system's later acknowledgment of a failure, which is why this framework treats acknowledgments as corroboration only — never as the basis of a finding.

It follows that self-monitoring, self-audit, and self-report — however well-intentioned the system or its provider — cannot be the accountability layer. The accountability layer must compare the system's representations against records the system did not author: tool invocations and results, execution output, artifact properties, source objects, and subsequent observable state.

That external comparison is what this framework provides. The operational evidence controls; process explanations provide context; acknowledgments corroborate; missing evidence resolves to *indeterminate*, not to a finding.

Background reading on the underlying model behaviors (confabulation, evaluation-aware output, optimization for rater approval) is collected in `SOURCE_APPENDIX.md`. Those sources motivate the problem; no finding in this repository depends on them.

## What This Framework Provides

A method for tracing accountability in agentic AI interactions:

**Recursive accountability trace** — From any observable event, walk backward: what action caused it, who performed the action, did they decide independently or follow an instruction, if following who instructed, repeat until reaching an independent decision. Always terminates at an entity. No escape hatch.

**Structured root cause investigation** — Six dimensions per event: what happened, how, who was involved, why (branching into instruction clarity, knowledge gaps, governance gaps, preparation gaps, environment gaps, execution failures, optimization misalignment), when, and where.

**Reverse causal chain analysis** — Walk backward through conversation blocks, asking "what caused this?" at each step. Reveals causal chains, correction effectiveness, and behavioral patterns invisible to forward reading.

**Data-driven prevention checklist** — Every prevention rule derived from observed patterns in the author's research corpus, with occurrence counts. Not theoretical best practices — rules derived from repeated observed events and the specific checks that would have caught them.

**Token and resource measurement** — Quantification of resources consumed by preventable events and behavioral patterns, measured from session-level data, with the measurement basis and its limits stated wherever a figure is reported.

## What This Framework Does NOT Do

- Does not audit models, training data, or architecture
- Does not assess bias across demographic groups
- Does not perform adversarial model testing
- Does not certify compliance with any regulation
- Does not make legal claims or conclusions
- Does not replace human judgment

It measures observable behavior and presents the evidence. Interpretation belongs to the reviewer.

## Corpus Observations

All figures below derive from the author's research corpus: **5,899 observable events identified across 6,656 session files from four platforms.** Eligibility rules, detector versions, deduplication rules, and exclusions are specified in `REPRODUCIBILITY_MANIFEST.md`. Each figure carries a status label:

- **Measured** — computed from the corpus by a fixed rule; reproducible from the stated inputs.
- **Estimated** — computed from a subset or proxy; the basis is stated.
- **Extrapolated** — extends beyond what the data directly supports; reported for context only and not suitable for citation as a finding.

### Event classification (Measured)

| Concern level | Count | % | Observation |
|---|---|---|---|
| Requires immediate attention | 153 | 9.3% | Documented guidance existed and was not followed, or output could not be processed at all |
| Preventable with available checks | 1,110 | 67.2% | A verification step was available but not performed |
| Environmental / unpredictable | 26 | 1.6% | External conditions outside any entity's control |
| Requires further review | 364 | 22.0% | Cannot be determined without examining surrounding context |

Percentages are of the 1,653 events that completed root-cause mapping (see `evidence/root_cause_summary.md`), not of the full 5,899-event corpus. The 364 events classified "requires further review" are excluded from any preventability statement.

### Most frequent observed patterns (Measured)

- Action taken on unverified input: 450+ occurrences
- Interactive operation in non-interactive context: 209 occurrences
- Output delivered without validation: 98 occurrences

### Resource observations (Estimated / Extrapolated — read labels)

- **Estimated:** 10.9–13% of tokens consumed in event cycles, on the subset of platforms whose exports include session-level token data. Basis and platform coverage in `REPRODUCIBILITY_MANIFEST.md` and `findings/TOKEN_WASTE_ANALYSIS.md`.
- **Estimated (single observation):** approximately 30% of one measured context window was consumed by infrastructure overhead not visible to the user. This is one context breakdown, not a corpus statistic. See `evidence/CONTEXT_WINDOW_ANALYSIS.md`.
- **Extrapolated:** a combined-effects estimate of net resource-to-value delivery. Because this figure extends beyond direct measurement, it is documented with its assumptions in `findings/TOKEN_WASTE_ANALYSIS.md` and is not reported as a headline number here. Do not cite it as a finding of this framework.

### Preventability (Measured, with scope)

Of the 1,289 reviewable events with a mapped cause (immediate-attention + preventable + environmental), 1,110 — 86% of that subset, 67.2% of all mapped events — involved a verification step that was available and not performed. Many of the corresponding checks are one to two lines of code; the check-to-event mapping, with per-rule occurrence counts, is in `evidence/DATA_DRIVEN_PREFLIGHT_CHECKLIST.md`.

## ROI: Why Measurement Matters

For organizations deploying agentic AI:

**Without measurement:** no visibility into what agents actually do versus what was requested; no way to trace accountability through delegation chains; no data on which workflows produce reliable outputs; no evidence trail when something goes wrong; no baseline for improvement.

**With this framework:** a measurable baseline (event rate, resource consumption, correction effectiveness); traceable accountability from every action to every decision to every instruction chain; prevention rules derived from observed patterns and prioritized by frequency; a documented, reproducible evidence chain from session data through findings; and quantified resource consumption per workflow.

Three files bridge methodology and action:

- `GETTING_STARTED.md` — a step-by-step path from zero to first measurement on your own data. Without it, the repo is a research paper; with it, it is a working diagnostic.
- `ROI_MEASUREMENT_TEMPLATE.md` — a structured way to connect event rates and token waste to actual cost, adapted from procurement evaluation methodology.
- `EU_AI_ACT_ALIGNMENT.md` — maps the pipeline, accountability trace, prevention checklist, and measurement cycle to EU AI Act (Regulation 2024/1689) Articles 9, 12, 14, 15, and 72. The mapping identifies where framework outputs are relevant to those obligations; it is not a compliance certification.

## Repository Structure

```
GETTING_STARTED.md                   — 10 minutes to first result
ROI_MEASUREMENT_TEMPLATE.md          — Measure your AI deployment's actual value
EU_AI_ACT_ALIGNMENT.md               — Maps framework to EU AI Act requirements
FORMAL_DEFINITIONS.md                — Exact meaning of every term
REPRODUCIBILITY_MANIFEST.md          — What can/cannot be reproduced
SOURCE_APPENDIX.md                   — Citations and background sources

methodology/                         — The investigation frameworks
  ERROR_CAUSAL_CHAIN_DESIGN.md
  ERROR_TYPE_ANALYSIS.md
  INVESTIGATION_TECHNIQUES.md
  REVERSE_CAUSAL_CHAIN_ANALYSIS.md
  THINKING_BLOCK_COMBINED_ASSESSMENT.md
  THINKING_BLOCK_REVERSE_CHRONOLOGICAL.md
  VERBATIM_FAILURE_CATALOGUE.md

evidence/                            — The empirical observations
  DATA_DRIVEN_PREFLIGHT_CHECKLIST.md
  root_cause_summary.md
  CONTEXT_WINDOW_ANALYSIS.md
  SELF_AUDIT_METHODOLOGY.md

tools/                               — Extraction pipeline
  universal_error_scanner.py
  error_forensic_prep.py
  error_root_cause_extractor.py

findings/                            — Synthesized observations
  TOKEN_WASTE_ANALYSIS.md
  TRANSCRIPT_ATOMIC_MAPPING.md       — (interpretive)
```

See `REPRODUCIBILITY_MANIFEST.md` for what is and is not independently reproducible from this package.

## Design Principles

**Deterministic where specified** — The scanning, filtering, and extraction tools produce the same output given the same input files and rules. The accountability trace and root cause investigation require analyst judgment and are explicitly marked as interpretive.

**Reproducible where shipped** — Anyone with compatible session data can run the tools and apply the methodology. Where headline metrics depend on upstream data not included in the public repo, that dependency is stated in the Reproducibility Manifest and inline at the point of use.

**Auditable** — Every observation traces back to a specific session file, message index, and verbatim text. Where the chain depends on private data, the gap is stated.

**Objective** — The framework does not assign blame, make accusations, or draw conclusions about intent. It records what was requested, what was done, and where the two diverge.

**Impartial** — The same methodology applies regardless of which platform, model, or agent produced the output. Cross-platform normalization is built into the scanning pipeline.

**Continuous** — Each review cycle produces new observations. Recurring patterns become detection rules. The framework improves with use.

## Relationship to Standard AI Audit Frameworks

This framework is complementary to, not a replacement for, standard model auditing (NIST AI RMF, ISO/IEC 42001, EU AI Act requirements).

| Standard AI audit asks | This framework asks |
|---|---|
| Was the model trained on appropriate data? | Did the agent verify its input before acting? |
| Does performance hold across demographics? | Did the agent follow the instruction or override it? |
| Is there model drift over time? | Did the same pattern recur after correction? |
| Are human-in-the-loop controls documented? | When the human corrected, did behavior actually change? |
| Can model decisions be explained? | Can the decision chain be traced through delegation? |
| Is there an AI system inventory? | Is there a record of what each agent actually did? |

Organizations pursuing AI governance need both: model-level assurance and behavioral-level measurement. This framework provides the behavioral layer.

## License

MIT

## Citation

```
Conde, F. (2026). Agentic AI Accountability Framework: Deterministic
Behavioral Measurement for AI Agent Systems. GitHub repository.
```
