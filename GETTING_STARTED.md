# Getting Started

From zero to your first AI behavioral measurement in 10 minutes.

---

## What You Need

**Session data from at least one of these sources:**

| Platform | Where to find it | File type |
|---|---|---|
| Claude Code | `~/.claude/projects/` | `.jsonl` |
| Codex | `~/.codex/sessions/` | `.jsonl` |
| Cowork | `%APPDATA%/Claude/local-agent-mode-sessions/` | `.jsonl` |
| Claude web (exported) | Your export download | `_chat.json` |
| ChatGPT (exported) | Your export download | `_chat.json` — ChatGPT exports must be split into individual `_chat.json` files per conversation and placed in the chats directory. The scanner discovers `**/_chat.json` files and handles the ChatGPT `mapping` format automatically. |

**Python 3.8+** installed.

**No external dependencies.** All tools use only the Python standard library.

---

## Quick Start (10 minutes)

### Step 1: Clone the repo

```bash
git clone https://github.com/conde-fc/agentic-ai-accountability.git
cd agentic-ai-accountability/tools
```

### Step 2: Configure your paths

Open `universal_error_scanner.py` and find the CONFIGURATION section (around line 68). Set `CHATS_MANAGER_PATH` to wherever your web chat exports are:

```python
CHATS_MANAGER_PATH = os.environ.get(
    "CHATS_MANAGER_PATH",
    str(HOME / "Downloads" / "my_chat_exports")  # ← edit this
)
```

Or set the environment variable instead:

```bash
# Linux/Mac
export CHATS_MANAGER_PATH="/path/to/your/chat/exports"

# Windows PowerShell
$env:CHATS_MANAGER_PATH = "C:\path\to\your\chat\exports"
```

Claude Code, Codex, and Cowork paths are auto-detected from standard locations but can also be overridden:

```bash
export CLAUDE_CODE_PATH="/path/to/.claude/projects"
export CODEX_PATH="/path/to/.codex/sessions"
export COWORK_PATH="/path/to/cowork/sessions"
```

### Step 3: Scan

```bash
python universal_error_scanner.py
```

This scans all configured sources and produces:
- `error_scan_output/master_errors.csv` — every detected event
- `error_scan_output/error_summary.txt` — counts by type, platform, sender
- `error_scan_output/error_tracebacks.jsonl` — full traceback blocks

**Expected time:** 1-5 minutes depending on how many session files you have.

### Step 4: Filter

```bash
python error_forensic_prep.py
```

This removes noise (permission denied from search tools, user-pasted errors, template code, internal machinery) and produces:

- `error_scan_output/reviewable_errors.csv` — the canonical set of events that passed filtering (this is what Step 5 reads)
- `error_scan_output/cases/` — one text file per unique deduplicated review case, with conversation context
- `error_scan_output/cases_index.csv` — index with empty review columns
- `error_scan_output/filtered_out.csv` — what was removed and why
- `error_scan_output/prep_summary.txt` — filter breakdown

### Step 5: Extract root causes

```bash
python error_root_cause_extractor.py
```

This reads `reviewable_errors.csv` (output of Step 4) and maps each event to its trigger, what check was absent, and a concern level. The filtering is done once in Step 4 — Step 5 consumes that output directly.

Output:
- `error_scan_output/root_causes_by_type.csv` — every event with extracted cause
- `error_scan_output/root_cause_summary.md` — summary tables

### Step 6: Read your results

Open `error_scan_output/root_cause_summary.md`. You now have:

- How many events were found
- How many are ALARMING vs CONCERNING vs NOT_CONCERNING vs NEEDS_TRIAGE
- Top triggers from your actual data
- What checks were absent
- Breakdown by error type, source, and platform

---

## What To Do With Your Results

### If you want a quick health check:

Look at the concern level distribution. In the author's dataset, 9.3% were ALARMING and 67.2% were CONCERNING. How does yours compare?

### If you want to reduce errors:

Open `evidence/DATA_DRIVEN_PREFLIGHT_CHECKLIST.md`. For each error type in your results, the checklist shows the exact prevention check — usually 1-2 lines of code.

### If you want to trace accountability for a specific event:

Open a case file from `error_scan_output/cases/`. It shows the conversation context: what the user requested, what the agent planned, what action was taken, and what failed. Use `methodology/ERROR_CAUSAL_CHAIN_DESIGN.md` to trace the decision chain.

### If you want to analyze conversation-level patterns:

Pick one conversation transcript. Apply the technique in `methodology/REVERSE_CAUSAL_CHAIN_ANALYSIS.md`: walk backward block by block, asking "what caused this?" at each step.

### If you want to measure token waste:

If your session files contain token usage data (Claude Code and Cowork JSONL files include `usage` fields with `input_tokens` and `output_tokens`), you can calculate the tokens consumed in error cycles. See `findings/TOKEN_WASTE_ANALYSIS.md` for the methodology.

### If you want to build prevention into your workflow:

Add relevant sections from `evidence/DATA_DRIVEN_PREFLIGHT_CHECKLIST.md` to your project's CLAUDE.md, AGENTS.md, or equivalent agent configuration file.

---

## Scanning Only One Source

```bash
python universal_error_scanner.py --source claude_code
python universal_error_scanner.py --source codex
python universal_error_scanner.py --source cowork
python universal_error_scanner.py --source chats_manager
```

---

## Troubleshooting

**"No files found" for a source:**
The path doesn't exist or is empty. Check that the platform stores data where the scanner expects it. For web chat exports, verify `CHATS_MANAGER_PATH` points to the right directory.

**Very high event count dominated by one type:**
Likely `permission_denied` from search tools scanning system directories. The filter step (Step 4) removes these automatically.

**Case files say "Could not load conversation — file not found":**
The scanner records each event's source file path. If the file has moved since scanning, the forensic prep tool can't load the conversation context. Re-run the scanner to update paths.

**Script exits immediately on double-click (Windows):**
The tools detect non-interactive execution and skip the "Press Enter" prompt. Run from a terminal/PowerShell window instead.

---

## Next Steps

Once you have your first results, see:

- `methodology/ERROR_CAUSAL_CHAIN_DESIGN.md` — How to trace accountability
- `methodology/VERBATIM_FAILURE_CATALOGUE.md` — 8 known structural patterns to search for
- `findings/TOKEN_WASTE_ANALYSIS.md` — How to quantify resource waste
- `ROI_MEASUREMENT_TEMPLATE.md` — How to build a full cost/benefit picture
