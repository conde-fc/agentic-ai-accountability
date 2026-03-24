# Investigation Techniques — Mapped to AI Agent Error Forensics

This document maps formal root cause analysis techniques to the
methodology used in this project. Each technique was identified
because we were already using it — we named them after the fact.

---

## Techniques and How They Apply

### 5 Whys

**What it is:** Ask "why?" recursively until you reach the root cause.

**How we use it:** The accountability trace (Component 1 of the
Causal Chain Design). Error → action → who decided → independent
or following instruction → if following, who instructed → repeat.

**Where it works:** Single-cause linear chains. An agent wrote
code that crashed → why? → the agent didn't test it → why? →
no validation step exists → why? → no governance rule requires it.

**Where it breaks:** Compound failures with branching causes.
When Agent 0 fabricated URLs AND Codex didn't verify them,
the 5 Whys produces two parallel chains, not one.

---

### 5W1H (What, Who, When, Where, Why, How)

**What it is:** Fact-gathering framework. Establishes the
complete picture before analysis begins.

**How we use it:** The investigation template (Component 2).
Every error gets: what happened, how, who was involved, why
(branching into cause categories), when in the session, where
in the codebase.

**Where it works:** Every error. This is the universal first step.

**Where it breaks:** It doesn't break — it's the foundation.
But it gathers facts without tracing causality. That's why
it needs the 5 Whys on top of it.

---

### Ishikawa / Fishbone Diagram

**What it is:** Categorizes potential causes into branches.
Traditional branches: People, Process, Equipment, Materials,
Environment, Management.

**How we use it:** Our 8 cause categories ARE Ishikawa branches:

| Traditional | Our Category |
|---|---|
| People | Execution failure |
| Process | Governance gap |
| Equipment | Environment gap |
| Materials | Knowledge gap / knowledge not applied |
| Environment | Preparation gap |
| Management | Instruction ambiguity |
| — | Misaligned optimization (AI-specific) |

**Where it works:** Ensuring we consider all possible cause
types, not just the obvious one. When an agent hits
FileNotFoundError, the obvious cause is "path wrong." The
Ishikawa forces us to also ask: was the instruction clear?
Did the agent have the knowledge? Was there a governance rule?

---

### Fault Tree Analysis (FTA)

**What it is:** Boolean logic from failure backward. AND gates
(both conditions needed) and OR gates (either sufficient).

**How we use it:** Compound multi-agent failures.

Example — fabricated git clone URLs:
```
git clone FAILED
  ├── AND: URLs were fabricated
  │         └── Agent 0 confabulated them
  └── AND: URLs were not verified
            └── Codex skipped verification
```
Both failures were necessary. Either agent doing its job
correctly would have prevented the error.

**Where it works:** Any error involving multiple agents,
delegation chains, or multiple defense failures.

---

### Swiss Cheese Model (Reason's Model)

**What it is:** Multiple defense layers, each with holes. An
incident happens when holes align across all layers.

**How we use it:** The audit engine proposal-without-execution
pattern is pure Swiss Cheese:

- Layer 1 (User): didn't lock scope with a contract → hole
- Layer 2 (Agent): didn't self-prioritize critical path → hole
- Layer 3 (Governance): no rule forcing critical-path-first → hole

All three holes aligned → audit engine never built across 20+ turns.

**Where it works:** Understanding how systems of defenses fail.
Every "governance gap" finding is a hole in a Swiss Cheese layer.

---

### Causal Factor Charting

**What it is:** Timeline-based. Plot events chronologically,
identify which were causal vs contextual.

**How we use it:** The Reverse Causal Chain Analysis (formerly
"House of Horrors Walk") IS a causal factor chart. It goes
block by block through the conversation, marking each as causal
(Block 2's misidentification → Block 3's waste) or context
(Block 8's productive search → no causal link to later failures).

**Where it works:** Any conversation-length analysis where you
need to trace how early events influenced later outcomes.

---

### Barrier Analysis

**What it is:** Identifies what barriers should have prevented
the incident and why each barrier failed.

**How we use it:** Every "governance gap" finding is barrier
analysis. "Was there a CLAUDE.md rule requiring path verification?
No. That barrier didn't exist." Every "preparation gap" finding
is also barrier analysis: "Was there an existence check in the
code? No. That barrier was absent."

The DATA_DRIVEN_PREFLIGHT_CHECKLIST is the output of barrier
analysis: here are the barriers that should exist, derived from
the errors that occurred when they didn't.

---

### Change Analysis

**What it is:** Compare what happened vs what normally works.
What changed? The change is the likely cause.

**How we use it:** The CONTEXT_WINDOW_ANALYSIS showed performance
degrading after 80% context fill. What changed? Context pressure
increased. The productive zone was 60-80%. After that, failures
clustered. The variable that changed (context fill) correlates
with the failure rate.

Also applies to EOFError: the code works in interactive context.
What changed? Execution context (non-interactive). The change
is the cause.

---

### FMEA (Failure Mode and Effects Analysis)

**What it is:** Forward-looking. List every possible failure
mode, rate severity × probability × detectability.

**How we use it:** Retrospectively. The VERBATIM_FAILURE_CATALOGUE
is a retrospective FMEA — each entry is a known failure mode
with a structural signature for detection. The error scanner +
forensic prep pipeline IS the detection mechanism.

What we haven't done yet: forward-looking FMEA to predict
failure modes we haven't seen. The data-driven preflight
checklist is a step toward this — it predicts that any code
accessing a path without `Path.exists()` will eventually fail.

---

### Kepner-Tregoe (IS / IS NOT)

**What it is:** Structured elimination. "The problem IS in X,
IS NOT in Y. What's different about X?"

**How we use it:** The error distribution data supports this:
"Permission denied IS concentrated in Claude Code (3,345 cases),
IS NOT in web chats (0 cases). Why? Claude Code uses ripgrep
across broad paths; web chats don't execute shell commands."

"SyntaxError IS 84 cases in agent-written code, IS NOT in
user-uploaded code. What's different? Agent-written code was
never validated before execution."

---

## The Composite

No single technique covers everything. This project uses a
composite where each technique handles one part:

| Layer | Technique | Purpose |
|---|---|---|
| Fact gathering | 5W1H | Establish what happened |
| Accountability | 5 Whys | Trace to independent decision |
| Cause categories | Ishikawa | Consider all cause types |
| Compound analysis | Fault Tree | AND/OR logic for multi-agent |
| Defense analysis | Barrier Analysis | Identify missing safeguards |
| Timeline analysis | Causal Factor Chart | Block-by-block conversation trace |
| System-level | Swiss Cheese | How defense gaps aligned |
| Pattern library | FMEA (retrospective) | Known failure modes + detection |
| Isolation | Kepner-Tregoe | Narrow variables by elimination |

The tools in this repository (scanner → filter → extractor)
prepare the evidence. The methodology documents describe how
to apply these techniques. The agent reviews each case using
the structured checklist. The findings feed back into the
pattern library, improving future detection.
