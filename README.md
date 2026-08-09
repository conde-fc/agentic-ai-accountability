# Agentic AI Accountability Framework

An evidence-first methodology for analyzing observable AI-agent workflow records, developed from a research corpus spanning four platforms.

This framework minimizes normative claims and prioritizes observable, reproducible measurements within explicitly stated limits. Where the methodology is deterministic under fixed inputs and rules, that is stated. Where analyst judgment is required, that is stated too. See `FORMAL_DEFINITIONS.md` and `REPRODUCIBILITY_MANIFEST.md` for exact terms and scope.

## Status

This repository is the public statement of the methodology. It is cited in a public comment filed on FTC Docket No. FTC-2026-0859 (Matter No. P264200). Git history preserves earlier README versions; externally cited versions should be identified by commit SHA or release tag.

## Development Status

The repository currently contains observable-record processing tools, methodology documents, and project-reported corpus analyses. Some analyses require human judgment and access to source records that are not public.

Additional evaluation components and independent validation remain proposed. They are not represented here as implemented or validated.

## Scope and Limits
- This framework evaluates observable workflow behavior, not model internals.
- It does not establish legal conclusions.
- It does not prove latent mechanism causes from external evidence alone.
- Some headline metrics depend on upstream data artifacts not included in this public repository. Where that is the case, it is stated explicitly in the Reproducibility Manifest and repeated inline wherever the metric appears.
- The scanning, filtering, and extraction tools are deterministic given fixed inputs. The accountability trace and root cause investigation require analyst judgment.
- The methodology is designed for supported session-data formats once source paths are configured. The specific observations from the author's dataset require access to that dataset.

## Record Boundary

Findings are limited to evidence present in the available source records. Missing or unavailable evidence is reported as a limitation and is not treated by itself as proof that an action did or did not occur.

## The Problem

Agentic AI systems make decisions, execute actions, delegate tasks, and produce outputs — often across chains of multiple agents. The question is not whether these systems are "good" or "bad." The question is: can you trace what happened, verify whether it matches what was requested, and measure the cost when it doesn't?

Model-level audit frameworks address areas such as training-data governance, performance evaluation, bias assessment, adversarial testing, and architecture documentation. This repository addresses a different unit of analysis: observable AI-agent workflow behavior in completed records.

When an agent references a file that doesn't exist, delivers code that can't parse, proposes work four times without executing it, or agrees with a correction and repeats the same failure — that behavior is not captured by model cards, SHAP values, or demographic performance stratification. It lives in the session logs, the conversation transcripts, and the observable gap between what was requested and what was delivered.

This framework analyzes that observable gap within available records.

## Why External Measurement

System-generated descriptions of actions are evaluated against evidence available in completed records. System self-report may provide context, but it is not treated as proof by itself. When the record does not contain sufficient evidence, the framework records that limitation rather than inferring what occurred outside the observable record.

The method evaluates observable records rather than model internals. It does not claim that user-accessible records capture every system action or side effect.

## What This Framework Provides

A method for tracing accountability in agentic AI interactions:

**Recursive accountability trace** — From an observable event, trace backward through actions, instructions, and attributable decisions as far as the available record supports. When attribution cannot be resolved, record the boundary rather than infer an actor or cause.

**Structured root cause investigation** — Six dimensions per event: what happened, how, who was involved, why (branching into instruction clarity, knowledge gaps, governance gaps, preparation gaps, environment gaps, execution failures, optimization misalignment), when, and where.

**Reverse causal chain analysis** — Walk backward through conversation blocks to examine candidate causal sequences, correction responses, and recurring patterns supported by the available record.

**Data-driven prevention checklist** — Maps listed prevention rules to project-observed patterns and documented occurrence counts. The mapping is limited to the research corpus and the stated classification rules.

**Token and resource measurement** — Reports measurements or estimates only where source records contain the necessary usage fields, with the basis and limitations stated beside each reported figure.

## What This Framework Does NOT Do

- Does not audit models, training data, or architecture
- Does not assess bias across demographic groups
- Does not perform adversarial model testing
- Does not certify compliance with any regulation
- Does not make legal claims or conclusions
- Does not replace human judgment

It analyzes observable records and presents the supporting references available within those records. Interpretation belongs to the reviewer.

## Corpus Observations

All figures below are project-reported results from the author's research corpus: **5,899 observable events identified across 6,656 session files from four platforms.** Eligibility rules, detector versions, deduplication rules, and exclusions are specified in `REPRODUCIBILITY_MANIFEST.md`. These results have not been independently reproduced from public source data unless explicitly stated. Each figure carries a status label:

- **Project-measured** — computed from the corpus by a stated fixed rule; independent reproduction requires the source inputs identified in the reproducibility documentation.
- **Estimated** — computed from a subset or proxy; the basis is stated.
- **Extrapolated** — extends beyond what the data directly supports; reported for context only and not suitable for citation as a finding.

### Event classification (Project-measured)

| Concern level | Count | % | Observation |
|---|---|---|---|
| Requires immediate attention | 153 | 9.3% | Documented guidance existed and was not followed, or output could not be processed at all |
| Preventable with available checks | 1,110 | 67.2% | A verification step was available but not performed |
| Environmental / unpredictable | 26 | 1.6% | External conditions outside any entity's control |
| Requires further review | 364 | 22.0% | Cannot be determined without examining surrounding context |

Percentages are of the 1,653 events that completed root-cause mapping (see `evidence/root_cause_summary.md`), not of the full 5,899-event corpus. The 364 events classified "requires further review" are excluded from any preventability statement.

### Most frequent observed patterns (Project-measured)

- Action taken on unverified input: 450+ occurrences
- Interactive operation in non-interactive context: 209 occurrences
- Output delivered without validation: 98 occurrences

### Resource observations (Estimated / Extrapolated — read labels)

- **Estimated:** 10.9–13% of tokens consumed in event cycles, on the subset of platforms whose exports include session-level token data. Basis and platform coverage in `REPRODUCIBILITY_MANIFEST.md` and `findings/TOKEN_WASTE_ANALYSIS.md`.
- **Estimated (single observation):** approximately 30% of one measured context window was consumed by infrastructure overhead not visible to the user. This is one context breakdown, not a corpus statistic. See `evidence/CONTEXT_WINDOW_ANALYSIS.md`.
- **Extrapolated:** a combined-effects estimate of net resource-to-value delivery. Because this figure extends beyond direct measurement, it is documented with its assumptions in `findings/TOKEN_WASTE_ANALYSIS.md` and is not reported as a headline number here. Do not cite it as a finding of this framework.

### Preventability (Project-measured, with scope)

Under the project's stated classification rules, 1,110 of 1,289 reviewable events with a mapped cause — 86% of that subset and 67.2% of all mapped events — were classified as involving an available verification step that was not performed. The check-to-event mapping and per-rule occurrence counts are reported in `evidence/DATA_DRIVEN_PREFLIGHT_CHECKLIST.md`.

## ROI: Why Measurement Matters

For organizations deploying agentic AI:

**Without structured measurement:** available records are less systematically organized for comparing requests with observed actions, tracing documented delegation, identifying recurring workflow patterns, and establishing a baseline for later comparison.

**With this framework:** available records can be organized into project-defined event rates, resource observations, correction responses, documented attribution paths, and prevention-rule mappings, subject to the source-data and reproducibility limits stated in this repository.

Three files bridge methodology and action:

- `GETTING_STARTED.md` — a step-by-step path from zero to first measurement on your own data. Without it, the repo is a research paper; with it, it is a working diagnostic.
- `ROI_MEASUREMENT_TEMPLATE.md` — a structured way to connect event rates and token waste to actual cost, adapted from procurement evaluation methodology.
- `EU_AI_ACT_ALIGNMENT.md` — maps the pipeline, accountability trace, prevention checklist, and measurement cycle to EU AI Act (Regulation 2024/1689) Articles 9, 12, 14, 15, and 72. The mapping identifies where framework outputs are relevant to those obligations; it is not a compliance certification.

## Repository Structure

```
GETTING_STARTED.md                   — Setup and initial-use instructions
ROI_MEASUREMENT_TEMPLATE.md          — Connect project observations to user-supplied cost assumptions
EU_AI_ACT_ALIGNMENT.md               — Describes potential relevance to selected EU AI Act provisions; not a compliance determination
FORMAL_DEFINITIONS.md                — Definitions used by this repository
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

**Reproducibility scope** — The included tools are intended for compatible session data. Independent portability is established only where a documented external reproduction has been completed; unavailable source inputs and other dependencies are identified in the Reproducibility Manifest.

**Auditability target** — Released observations should identify the supporting session reference, message location, and source text where disclosure is permitted. Dependencies on private source data are stated as reproducibility limits.

**Neutral attribution** — The framework does not assign intent from external records. It records the request, the observable record of subsequent actions or outputs, and identified differences within that evidentiary scope.

**Platform-neutral design** — The methodology is designed for supported record formats without assigning different standards by provider. Cross-platform normalization is included in the scanning pipeline.

**Versioned development** — New observations and detection-rule changes should be documented in version history.

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

Model-level assurance and observable-record measurement address different questions. This repository is limited to the observable-record layer described above.

## License

MIT

## Citation

```
Conde, F. (2026). Agentic AI Accountability Framework: Observable-Record
Measurement for AI Agent Systems. GitHub repository.
```
