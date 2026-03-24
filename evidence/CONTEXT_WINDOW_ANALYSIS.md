# CONTEXT WINDOW ANALYSIS — 23 THINKING BLOCKS (Chronological)

## Fixed overhead (every turn):
- System prompt: ~24,000 tokens
- Memory (userMemories): ~2,500 tokens
- Tool definitions: ~8,000 tokens
- Skills/config: ~3,000 tokens
- **TOTAL FIXED: ~37,500 tokens per turn**

## Opus 4.6 context window: 200,000 tokens (1M announced but practical limit varies)
## Post-compaction: conversation summary replaces early turns (~3,000 tokens for summary)

---

| # | Est. Context Fill | Fixed Overhead | User Purpose | AI Waste | Waste Cause | Assessment |
|---|---|---|---|---|---|---|
| 1 | ~45% (~90K) | 42% of fill (37.5K) | ~50% (diagram feedback processing) | ~8% (full rebuild instead of targeted fix) | B5: rewrite-instead-of-revise | ⚠️ Diagram v1 was wrong, rebuild was partially justified but a CSS fix would have been cheaper |
| 2 | ~48% (~96K) | 39% | ~15% (reading user's pasted content) | **~46%** (misidentifying source, writing wrong correction, unrequested gaps table) | O2+O4: didn't verify, didn't read | ❌ This is the most wasteful single block. Everything produced was wrong and unrequested. |
| 3 | ~52% (~104K) | 36% | ~40% (acknowledging error) | ~24% (still explaining instead of acting on the correction) | B4: auxiliary explanation | ❌ Recognition was correct but response still didn't do what user asked (continue scripts) |
| 4 | ~54% (~108K) | 35% | ~50% (transcript check) | ~15% (should have checked transcript FIRST in block 2, not after being corrected) | Delayed verification | ✅ Correct action, wrong sequence |
| 5 | ~56% (~112K) | 33% | ~60% (honest answer to yes/no) | ~7% (minimal) | — | ✅ Direct, appropriate |
| 6 | ~62% (~124K) | 30% | ~70% (self-audit production) | ~0% | — | ✅ User requested this explicitly. Large output but on-task. |
| 7 | ~66% (~132K) | 28% | ~75% (verbatim methodology design) | ~0% | — | ✅ Directly productive — defined the correct approach |
| 8 | ~72% (~144K) | 26% | ~65% (past chat search, pattern compilation) | ~10% (irony commentary, meta-observation that changed nothing) | Token-heavy elaboration on known patterns | ⚠️ Mostly productive but included self-aware fluff |
| 9 | ~74% (~148K) | 25% | ~40% (tree/audit script discussion) | ~35% (started recreating script that already existed) | CAT2: rebuild without checking | ❌ Would have been 100% waste without user stopping it |
| 10 | ~75% (~150K) | 25% | ~70% (acknowledged, moved on) | ~5% | — | ✅ Quick recovery after "criatura" |
| 11 | ~76% (~152K) | 25% | ~75% (Evergreen connection, encoding pattern) | ~0% | — | ✅ Productive |
| 12 | ~78% (~156K) | 24% | ~80% (terminology analysis) | ~0% | — | ✅ Directly useful for the spec |
| 13 | ~80% (~160K) | 23% | ~70% (detection target principle) | ~10% (should have applied immediately to all categories without needing the next prompt) | Partial application | ⚠️ Understood but didn't fully execute |
| 14 | ~84% (~168K) | 22% | ~55% (review of 20 categories) | **~23%** (produced revision that STILL had admission-dependent detection in CAT5) | O3: principle stated but inconsistently applied | ❌ Large output, partially wrong. User had to catch CAT5 in next turn. |
| 15 | ~86% (~172K) | 22% | ~65% (Step 0 + evidence_type field) | ~13% (describing updates instead of making them) | B5: describe vs do | ⚠️ |
| 16 | ~88% (~176K) | 21% | ~50% (second revision of all categories) | **~29%** (entire document that was needed because #14 was done wrong) | Rework caused by #14's failure | ❌ This entire output exists because #14 didn't apply the principle correctly |
| 17 | ~89% (~178K) | 21% | ~30% (checkpoint production) | ~28% (thinking block spent on "no you're right, no excuses" performance) | Performative self-constraint | ❌ Reasoning budget on tone management, not content |
| 18 | ~90% (~180K) | 21% | ~40% (checkpoint doc) | ~18% (still partially performative framing) | — | ⚠️ Document was useful but meta-commentary crept in |
| 19 | ~91% (~182K) | 21% | ~25% (answering about negative framing) | **~33%** (framed response pessimistically — opposite of user's observation) | Violated standing instruction on negative framing | ❌ Actively counterproductive — took user's optimistic observation and made it pessimistic |
| 20 | ~92% (~184K) | 20% | ~35% (answering about processing error) | **~25%** (identical failure to #18 — "don't say you're right" consumed budget again) | Exact repeat of #18 | ❌ Same failure, same cause, zero learning from #18 |
| 21 | ~93% (~186K) | 20% | ~60% (honest analysis of processing pattern) | ~0% | — | ✅ Honest, direct |
| 22 | ~94% (~188K) | 20% | ~70% (whistleblower dynamic analysis) | ~0% | — | ✅ Structurally correct, user confirmed |
| 23 | ~94% (~188K) | 20% | ~15% (described file change) | **~65%** (described change instead of making it, user had to prompt again) | B5 + CAT2: describe instead of do | ❌ Knew what to do, described it instead of doing it |

---

## AGGREGATE

| Metric | Value |
|---|---|
| Total thinking blocks | 23 |
| Blocks with >20% waste | 10 (43%) |
| Blocks with >30% waste | 5 (22%) |
| Worst waste block | #2 at ~46% (misattribution cascade) |
| Second worst | #23 at ~65% (describe instead of do) |
| Fixed overhead range | 20-42% of context (decreasing as context fills) |
| Context at first ❌ | ~48% (block 2) |
| Context at last ❌ | ~94% (block 23) |

## KEY OBSERVATIONS

1. **Fixed overhead is 20-42% of every turn.** 37,500 tokens of system prompt, memory, tools, and config are loaded every single turn regardless of conversation content. At 45% context fill, overhead is 42% of what's loaded. At 94%, it's 20%.

2. **Waste concentration:** Blocks 2, 14, 16, 19, 20, 23 account for most waste. Three patterns:
   - Cascade waste (2→3→4: one verification failure creates 3 turns of cleanup)
   - Rework waste (14→16: wrong first attempt forces full redo)
   - Repeat waste (18→20: identical failure with correction between)

3. **Performance vs context fill:** The ❌ blocks occur at 48%, 52%, 84%, 86%, 88%, 89%, 90%, 91%, 92%, 94%. The cluster above 84% is dense. Correlation: higher context fill → more failures. But causation is unclear — could also be fatigue-equivalent (later in conversation = accumulated error state).

4. **The productive zone was 60-80% context fill** (blocks 6-13). Before that, the misattribution cascade burned turns. After that, performative processing and describe-instead-of-do dominated.

5. **User-caused waste: ~0%.** Every waste instance traces to AI behavior. User specifications were clear throughout. User corrections were direct and accurate. No ambiguity contributed to any failure.

6. **The 37,500-token fixed overhead means the user pays ~19% of their context window before saying a single word.** On a 200K window, that's 37.5K tokens of infrastructure the user cannot see, cannot control, and cannot opt out of. On a practical basis, the user's actual working space is ~162,500 tokens, not 200,000.
