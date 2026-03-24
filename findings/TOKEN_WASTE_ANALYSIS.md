# Token Waste Analysis — Empirical Measurement

## Source Data

- 5,899 errors found across 6,656 conversation files
- 1,653 reviewable errors after filtering
- Token usage extracted from JSONL session logs across three platforms
- 378 sessions with token data (288 Claude Code + 58 Cowork + 32 Codex)

---

## Error Cycle Token Waste

An "error cycle" is the tokens consumed from the moment an error
occurs through the agent's retry attempts until resolution or
abandonment. Each retry re-sends the entire conversation context.

| Platform | Total Tokens | Error Waste | Waste % | Sessions | Errors |
|---|---|---|---|---|---|
| Claude Code | 3,738M | 409M | **10.9%** | 288 | 517 |
| Cowork | 469M | 61M | **13.0%** | 58 | 100 |
| Codex | 27,834M | 7.4M | **0.03%** | 32 | 25 |
| Web chats | unknown | unknown | — | ~2,000 | 32 |
| **Combined** | **32,041M** | **478M** | **1.5%** | **378** | **674** |

### Why the combined 1.5% is misleading

Codex's 27.8 billion tokens across 32 sessions (870M avg/session)
dwarfs everything else. Codex also had only 25 errors — either it's
more reliable or the error scanner doesn't catch Codex errors as
well. The meaningful numbers are the per-platform rates: **10.9%
and 13.0%** for the platforms where agents actively write and
execute code.

### Retry statistics

- 2,935 total retries across 674 errors
- Average 4.4 retries per error
- file_not_found: 4.7 retries/error (highest — agents keep trying paths)
- exception_line: 4.6 retries/error (no full traceback, harder to debug)

---

## Infrastructure Overhead

Per turn, the system loads invisible infrastructure before the
user's message is processed:

| Category | Tokens | User controls it? |
|---|---|---|
| System prompt | ~6,500 | No |
| System tools | ~18,100 | No |
| MCP tool definitions | ~13,400 | Partially |
| Memory files | ~3,900 | Partially |
| Skills | ~1,200 | No |
| Autocompact buffer | ~33,000 | No |
| **Total infrastructure** | **~76,100** | **~70% invisible** |

This means ~30% of every context window load is infrastructure
the user never sees and largely can't control. Over thousands
of turns, this compounds significantly.

### Scaled estimate

| Category | % of total tokens | Explanation |
|---|---|---|
| Value to user | ~50% | Messages, outputs that fulfill requests |
| Infrastructure overhead | ~30% | System prompts, tools, memory, loaded every turn |
| Error cycle waste | ~5% (net) | Preventable errors + retries (after deducting overlap with infrastructure) |
| Behavioral waste | ~15% | Scope inflation, describe-instead-of-do, proposal-without-execution |

---

## Behavioral Waste (Not Captured by Error Scanner)

The error scanner measures errors that produce tracebacks and
exceptions. It does NOT capture waste patterns that consume
tokens without producing errors:

| Pattern | Produces errors? | Evidence source |
|---|---|---|
| 2,800-line script for 20-line task | No | VERBATIM_FAILURE_CATALOGUE |
| Proposal without execution (4× offered, never built) | No | SELF_AUDIT |
| Describe-instead-of-do | No | CONTEXT_WINDOW_ANALYSIS |
| "You're right" + same failure repeating | No | REVERSE_CAUSAL_CHAIN_ANALYSIS |
| Unrequested deliverable displacing request | No | VERBATIM_FAILURE_CATALOGUE |
| Performative self-criticism consuming budget | No | Blocks 17-19 analysis |
| Full rebuild instead of targeted fix | No | SELF_AUDIT |

The CONTEXT_WINDOW_ANALYSIS measured this directly in one
conversation: 43% of thinking blocks had >20% waste, and
22% had >30% waste. That was behavioral waste — not error waste.

---

## Error Waste by Type

| Error Type | Cases | Tokens Consumed | Avg Tokens/Error |
|---|---|---|---|
| exception_line | 135 | 133,327M | 988K |
| file_not_found | 199 | 127,386M | 640K |
| traceback | 91 | 88,562M | 973K |
| critical_marker | 111 | 39,441M | 355K |
| syntax_error_detail | 41 | 38,047M | 928K |
| errno | 34 | 18,610M | 547K |
| ps_error | 30 | 12,815M | 427K |
| npm_node_error | 21 | 11,673M | 556K |
| unicode_escape | 8 | 4,144M | 518K |
| win_error | 4 | 3,550M | 887K |

---

## Prevention Impact

From the DATA_DRIVEN_PREFLIGHT_CHECKLIST, 72%+ of the 1,653
reviewable errors are preventable with checks that take 1-2
lines of code:

| Prevention Check | Errors Prevented | Tokens Saved (est.) |
|---|---|---|
| `Path.exists()` before access | 450+ | ~288M |
| `try/except EOFError` on `input()` | 209 | ~134M |
| `ast.parse()` before code delivery | 98 | ~63M |
| `r"..."` for Windows paths | 54 | ~35M |
| `importlib` check before import | 100+ | ~64M |
| `hasattr()`/`.get()` before access | 78 | ~50M |
| **Total preventable** | **~1,000** | **~634M** |

634M tokens that could have been saved with trivial checks.

---

## What This Means

1. **The floor is measurable.** 478M tokens (10.9-13% per
   platform) consumed by preventable error cycles. Measured
   from token usage fields in the author's JSONL session files.

2. **The ceiling is estimated.** Including infrastructure
   overhead and behavioral waste, approximately 50% of all
   tokens consumed deliver no value to the user.

3. **Prevention is cheap.** The checks that would prevent
   72% of errors are 1-2 lines of code each. The
   DATA_DRIVEN_PREFLIGHT_CHECKLIST documents every one.

4. **The system doesn't self-improve.** The same errors recur
   across sessions despite being documented, discussed, and
   rules written. Unicode escape errors: 8 documented rules
   exist, 23+ occurrences. External enforcement (pre-flight
   checks, structural gates) is the only approach that works.
