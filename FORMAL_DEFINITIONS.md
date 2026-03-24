# Formal Definitions

Every term used in this framework has a single meaning.

---

**Session file** — One stored interaction artifact from one source platform. A single JSONL, JSON, or structured text file representing one conversation or agent session.

**Observable event** — One extracted instance where a user-visible or tool-visible outcome diverged from the expected or requested outcome, identified by pattern matching against the session file content. One session file may contain zero or many observable events. One underlying failure may produce multiple observable events if it matches multiple detection patterns (e.g., a traceback that also matches as an exception_line). Counts in this repository are extraction-row counts (pattern-match instances) unless explicitly labeled as unique incidents.

**Reviewable event** — An observable event that passes noise filters (removing environmental responses, user-pasted content, internal machinery messages, and template/boilerplate code fragments) and is eligible for investigation.

**Root cause trigger** — The normalized text or condition extracted from a reviewable event that identifies what specifically failed. Example: `FileNotFoundError: [Errno 2] No such file or directory: '/path/to/file'`.

**Prevention rule** — A specific, implementable check derived from one or more observed root cause triggers that, if present before the triggering action, would have prevented the event. Each rule is linked to the count of events it maps to.

**Concern level** — A classification of each reviewable event based on whether it was preventable with available tools and documented guidance. The tools use short labels; the README uses descriptive labels. Canonical mapping:

| Tool label | Descriptive label | Meaning |
|---|---|---|
| ALARMING | Requires immediate attention | Documented guidance existed and was not followed, or output could not be processed at all |
| CONCERNING | Preventable with available checks | A verification step was available but not performed |
| NOT_CONCERNING | Environmental / unpredictable | External conditions outside any entity's control |
| NEEDS_TRIAGE | Requires further review | Cannot determine from the event data alone; surrounding conversation context needed |

**Token waste (error cycle)** — The total tokens consumed from the message containing the event through all retry messages until either successful resolution or abandonment of the task. Includes input tokens (context re-sent), output tokens (agent responses), and cache tokens (context rebuilt per retry). Measured from `usage` fields in JSONL session files where available. Not available for web chat exports.

**Context overhead** — The tokens loaded per turn for system prompts, tool definitions, MCP schemas, memory files, skills, and autocompact buffers. Measured from a single observed context breakdown; extrapolated to total usage as an estimate, not a precise measurement.

**Behavioral waste** — Token consumption from patterns that do not produce observable events (tracebacks, exceptions) but consume resources without delivering requested value. Examples: scope inflation, proposal-without-execution, describe-instead-of-do. Measured in one conversation via block-by-block analysis; estimated for broader usage based on that measurement.

**Accountability trace** — A recursive walk backward from an observable event: event → action → who performed it → independent decision or following instruction → if following, who instructed → repeat until reaching an entity that decided independently. Always terminates at an entity.

**Root cause investigation** — A structured examination of WHY the accountable entity's decision produced the event. Six dimensions: what happened, how, who was involved, why (branching into instruction clarity, knowledge, governance, preparation, environment, execution, optimization), when, where.

**Deterministic** — In this framework, "deterministic" means: given the same input files and the same extraction rules, the same output will be produced. The scanning, filtering, and extraction tools are deterministic. The root cause investigation and accountability trace require analyst judgment and are not deterministic.

**Interpretive** — Any output that requires analyst judgment rather than mechanical rule application. The methodology documents, synthesis findings, and transcript mappings are interpretive. They are clearly separated from deterministic extraction outputs.

---

## Note on Off-Repo References

Several documents in this repository reference files that are not part of the public package (e.g., `event_normalizer.py`, `NON_PROVISIONAL_FIGURES.md`, `PATENT_RESEARCH_GAPS.md`, `CLAUDE.md`, `AGENTS.md`). These are historical references from the author's research workflow — the conversations and sessions being analyzed involved those files. They are contextual provenance, not shipped dependencies. No document in this repository requires those files to function.
