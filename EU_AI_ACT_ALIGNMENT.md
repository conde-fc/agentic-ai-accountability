# EU AI Act Alignment

How this framework maps to requirements of the EU Artificial Intelligence Act (Regulation (EU) 2024/1689).

---

## Purpose of This Document

Organizations deploying AI systems in the European Union face specific obligations under the AI Act. This document maps the capabilities already present in this repository to the Act's requirements — showing where the framework provides direct support, partial support, or relevant evidence.

This is not legal advice. It is a technical mapping between an operational measurement framework and a regulatory text. Organizations should consult qualified legal counsel for compliance determinations.

**Regulation reference:** Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024, laying down harmonised rules on artificial intelligence.

**Official source:** https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai

**Key dates:**
- Entered into force: 1 August 2024
- Prohibited practices and AI literacy obligations: 2 February 2025
- GPAI model rules: 2 August 2025
- Full application (most provisions including high-risk rules): 2 August 2026
- Extended transition for high-risk AI embedded in regulated products: 2 August 2027

---

## Article 9 — Risk Management System

**What the Act requires:**

Providers of high-risk AI systems must establish and maintain a risk management system throughout the AI system's lifecycle. This includes identifying and analyzing known and reasonably foreseeable risks, estimating and evaluating risks that may emerge when the system is used in accordance with its intended purpose, and adopting appropriate risk management measures.

**What this framework provides:**

| Requirement | Framework capability | Where |
|---|---|---|
| Identify known and foreseeable risks | The scanning pipeline extracts observable failure events from actual operational data — not theoretical risk categories but documented instances | `tools/universal_error_scanner.py` |
| Estimate risks from actual use | Error rate calculation, concern level distribution, and preventable-rate measurement provide quantitative risk baselines | `ROI_MEASUREMENT_TEMPLATE.md` Part 2 |
| Adopt risk management measures | The DATA_DRIVEN_PREFLIGHT_CHECKLIST provides specific prevention rules derived from observed events, each with occurrence counts | `evidence/DATA_DRIVEN_PREFLIGHT_CHECKLIST.md` |
| Iterative risk management process | The measurement cycle (baseline → prevention → re-measurement → comparison) operationalizes continuous risk management | `ROI_MEASUREMENT_TEMPLATE.md` Part 6 |
| Testing procedures for risk identification | The 3-stage scanning pipeline (scan → filter → extract) provides deterministic, repeatable risk identification from session data | `GETTING_STARTED.md` |

**Coverage level:** Partial. The framework addresses post-deployment operational risk measurement. It does not cover pre-market risk assessment, training data governance, or design-phase risk management.

---

## Article 12 — Record-Keeping

**What the Act requires:**

High-risk AI systems must technically allow for the automatic recording of events (logs) over the system's lifetime. These logs should facilitate risk identification, support post-market monitoring, and enable tracing of system operation.

**What this framework provides:**

| Requirement | Framework capability | Where |
|---|---|---|
| Automatic recording of events | The scanner extracts and catalogs all detectable events from existing session logs (JSONL, JSON) across four platform types | `tools/universal_error_scanner.py` |
| Facilitate risk identification | Events are classified by type, concern level, and preventability — each traceable to source file, message index, and verbatim text | `tools/error_root_cause_extractor.py` |
| Support post-market monitoring | The pipeline is designed for repeated execution: scan → filter → extract → measure → compare to baseline | `REPRODUCIBILITY_MANIFEST.md` |
| Tracing of system operation | The `source_filepath` field links every extracted event back to the exact session file and message that produced it | `tools/universal_error_scanner.py` (source_filepath column) |
| Identification of persons involved in verification | The accountability trace methodology identifies who made each decision in the chain | `methodology/ERROR_CAUSAL_CHAIN_DESIGN.md` |

**Coverage level:** Strong support for deployer-side record-keeping and evidence preparation. The framework processes the logs that AI platforms already produce and structures them for auditability. It does not generate the logs themselves — that is the provider's responsibility under Article 12. Deployers have separate duties under Article 26(5)-(6) to monitor operation and keep logs under their control; this framework supports those deployer obligations.

---

## Article 14 — Human Oversight

**What the Act requires:**

High-risk AI systems must be designed to allow effective human oversight during use. Humans must be able to understand the system's capabilities and limitations, detect anomalies and dysfunctions, remain aware of automation bias, correctly interpret outputs, and decide to override or stop the system.

**What this framework provides:**

| Requirement | Framework capability | Where |
|---|---|---|
| Understand capabilities and limitations | The VERBATIM_FAILURE_CATALOGUE documents 8 structural failure signatures that indicate specific capability limits | `methodology/VERBATIM_FAILURE_CATALOGUE.md` |
| Detect anomalies and dysfunctions | The scanning pipeline detects tracebacks, exceptions, permission errors, file-not-found patterns, and custom error markers automatically | `tools/universal_error_scanner.py` |
| Awareness of automation bias | The REVERSE_CAUSAL_CHAIN_ANALYSIS documents observed correction tiers: conceptual corrections persist, principle corrections don't survive one block, behavioral corrections have zero effect — an observed single-session instance of automation-bias dynamics (see SOURCE_APPENDIX.md, Correction Tier Finding) | `methodology/REVERSE_CAUSAL_CHAIN_ANALYSIS.md` |
| Interpret outputs correctly | The accountability trace provides a structured method for tracing any AI output back through the decision chain to determine what was requested vs what was delivered | `methodology/ERROR_CAUSAL_CHAIN_DESIGN.md` |
| Override or stop decisions | The prevention checklist provides specific checks that, if implemented, give operators decision points before AI actions execute | `evidence/DATA_DRIVEN_PREFLIGHT_CHECKLIST.md` |

**Coverage level:** Partial. The framework provides the measurement and investigation tools that human overseers need to detect problems and understand failures. It does not implement the oversight mechanisms themselves (stop buttons, approval workflows, etc.) — those are system design decisions.

---

## Article 15 — Accuracy, Robustness, and Cybersecurity

**What the Act requires:**

High-risk AI systems must achieve an appropriate level of accuracy, robustness, and cybersecurity. They must be resilient to errors, faults, and inconsistencies, and must maintain performance under adversarial conditions.

**What this framework provides:**

| Requirement | Framework capability | Where |
|---|---|---|
| Appropriate level of accuracy | The error rate calculation (events per session) provides a direct operational accuracy baseline | `ROI_MEASUREMENT_TEMPLATE.md` Part 2B |
| Resilience to errors and faults | The preventable-rate measurement (67.2% of mapped events in the author's dataset) quantifies how many operational failures were avoidable with basic checks | `evidence/root_cause_summary.md` |
| Performance monitoring | Token waste measurement quantifies resource consumption in error cycles, providing a cost-denominated performance metric | `findings/TOKEN_WASTE_ANALYSIS.md` |
| Ongoing accuracy assessment | The measurement cycle enables longitudinal accuracy tracking across tool versions and configuration changes | `ROI_MEASUREMENT_TEMPLATE.md` Part 6 |

**Coverage level:** Partial. The framework measures operational accuracy and identifies robustness gaps from deployed system behavior. It does not perform adversarial testing, cybersecurity assessment, or pre-deployment accuracy benchmarking.

---

## Article 72 — Post-Market Monitoring

**What the Act requires:**

Providers of high-risk AI systems must establish a post-market monitoring system to collect and review relevant performance information, enabling identification of any need for corrective or preventive action. The post-market monitoring plan must be part of the technical documentation.

**What this framework provides:**

| Requirement | Framework capability | Where |
|---|---|---|
| Collect performance information | The 3-tool pipeline extracts, filters, and classifies performance-relevant events from operational session data | `tools/` (all 3 scripts) |
| Review collected information | Case files provide per-event evidence packages with conversation context for human review | `tools/error_forensic_prep.py` |
| Identify need for corrective action | Concern-level classification (ALARMING, CONCERNING, NOT_CONCERNING, NEEDS_TRIAGE) prioritizes review effort | `tools/error_root_cause_extractor.py` |
| Identify need for preventive action | Each observed event type maps to a specific prevention rule in the checklist | `evidence/DATA_DRIVEN_PREFLIGHT_CHECKLIST.md` |
| Post-market monitoring plan | The ROI template Part 6 provides a structured ongoing measurement cycle with defined metrics and comparison periods | `ROI_MEASUREMENT_TEMPLATE.md` Part 6 |
| Continuous improvement | The detection library grows with each review cycle — new patterns are documented using the VERBATIM_FAILURE_CATALOGUE format | `methodology/VERBATIM_FAILURE_CATALOGUE.md` |

**Coverage level:** Strong support for deployer-side monitoring and evidence preparation relevant to Article 72. The scanning pipeline provides systematic collection, structured review, and evidence-based corrective/preventive action — the operational layer that deployers need. It does not itself constitute the provider's post-market monitoring system, which is a provider-side design and documentation obligation.

---

## Article 4 — AI Literacy

**What the Act requires:**

Providers and deployers must ensure that staff dealing with AI systems have a sufficient level of AI literacy, taking into account their technical knowledge, experience, and the context in which the systems are used.

**What this framework provides:**

The framework itself serves as a literacy tool. Running the pipeline on an organization's own session data produces concrete, organization-specific evidence of what AI systems actually do — not abstract concepts but observed behaviors, error rates, and resource consumption patterns from the organization's own workflows.

The GETTING_STARTED.md provides a structured onboarding path, and the FORMAL_DEFINITIONS.md provides exact terminology. The ROI_MEASUREMENT_TEMPLATE.md translates technical findings into business language accessible to non-technical staff.

**Coverage level:** Indirect but valuable. The framework supports AI literacy by making AI behavior observable and measurable.

---

## Summary Alignment Table

| AI Act Article | Requirement | Framework coverage | Primary assets |
|---|---|---|---|
| Art. 9 | Risk management system | Partial — post-deployment operational risk | Scanner + checklist + ROI template |
| Art. 12 | Record-keeping and logging | Strong support — deployer-side log processing and evidence preparation | Scanner + source_filepath tracing |
| Art. 14 | Human oversight | Partial — detection and investigation tools | Failure catalogue + accountability trace |
| Art. 15 | Accuracy and robustness | Partial — operational accuracy measurement | Error rate + token waste + prevention rate |
| Art. 72 | Post-market monitoring | Strong support — deployer-side monitoring and evidence preparation | Full 3-tool pipeline + ROI measurement cycle |
| Art. 4 | AI literacy | Indirect — makes AI behavior observable | GETTING_STARTED + FORMAL_DEFINITIONS |

---

## What This Framework Does Not Cover

For full AI Act compliance, organizations also need (not provided by this framework):

- Pre-market conformity assessment (Articles 16-17, 43)
- Training and validation data governance (Article 10)
- Technical documentation for providers (Article 11)
- Transparency and instructions for use (Article 13)
- CE marking and registration (Articles 16, 49)
- Fundamental rights impact assessment (Article 27)
- Serious incident reporting procedures (Article 73)
- Adversarial testing and cybersecurity assessment (Article 15, partial)

This framework addresses the operational measurement layer — what happens after deployment, during actual use, with real data. It complements but does not replace the provider-side obligations above.
