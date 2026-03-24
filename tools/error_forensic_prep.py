"""
ERROR FORENSIC EVIDENCE PREP v1.0
==================================
PURPOSE: Prepare error evidence for agent forensic review.

This script does NOT analyze or classify errors.
It does two things:
  1. Filters OUT errors that clearly don't need root-cause analysis
  2. Extracts the full decision chain for everything remaining

The output is a set of "case files" — one per unique deduplicated review case —
containing everything an agent or analyst needs to trace the causal chain.
It also writes reviewable_errors.csv, the canonical filtered input for
error_root_cause_extractor.py.

FILTERED OUT (no root-cause needed):
  - Permission denied / access denied (HABITAT — environment issue)
  - User-pasted tracebacks (USER_PASTED — user showing error to AI)
  - Repeated identical errors from same tool (DEDUP — same rg/du error)

KEPT FOR REVIEW (needs agent analysis):
  - Agent-generated code errors (SyntaxError, NameError, etc.)
  - Agent command failures that may indicate wrong action
  - Errors where preceding context suggests misalignment
  - All tracebacks with file references (actual code bugs)

PER CASE FILE, EXTRACTS:
  - 5 messages BEFORE the error (user request → agent plan → action)
  - The message containing the error
  - 3 messages AFTER the error (agent response to error)
  - Sender for each message
  - The error details

OUTPUT:
  error_scan_output/cases/           — one .txt per case
  error_scan_output/cases_index.csv  — index of all cases
  error_scan_output/filtered_out.csv — what was filtered and why
  error_scan_output/prep_summary.txt — counts

Run: python error_forensic_prep.py
"""

import csv
import json
import os
import re
import sys
import traceback as tb
from pathlib import Path
from datetime import datetime
from collections import Counter


# =============================================================================
# CONFIG
# =============================================================================

HOME = Path.home()
PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_CSV = PROJECT_ROOT / "error_scan_output" / "master_errors.csv"
REVIEWABLE_CSV = PROJECT_ROOT / "error_scan_output" / "reviewable_errors.csv"
CASES_DIR = PROJECT_ROOT / "error_scan_output" / "cases"
INDEX_CSV = PROJECT_ROOT / "error_scan_output" / "cases_index.csv"
FILTERED_CSV = PROJECT_ROOT / "error_scan_output" / "filtered_out.csv"
SUMMARY_PATH = PROJECT_ROOT / "error_scan_output" / "prep_summary.txt"

# Fallback source paths — used only when source_filepath from scanner output
# is missing or the file has moved. Override via environment variables if needed.
SOURCE_PATHS = {
    "chats_manager": Path(os.environ.get(
        "CHATS_MANAGER_PATH",
        str(HOME / "Downloads" / "FRAMEWORK" / "08_CHATS")
    )),
    "claude_code": Path(os.environ.get(
        "CLAUDE_CODE_PATH",
        str(HOME / ".claude" / "projects")
    )),
    "codex": Path(os.environ.get(
        "CODEX_PATH",
        str(HOME / ".codex" / "sessions")
    )),
    "cowork": Path(os.environ.get(
        "COWORK_PATH",
        str(Path(os.environ.get("APPDATA", "")) / "Claude" / "local-agent-mode-sessions")
    )),
}

CONTEXT_BEFORE = 5   # messages before error
CONTEXT_AFTER = 3    # messages after error
MSG_CAP = 2000       # max chars per message in case file


# =============================================================================
# FILTER RULES — what gets excluded from review
# =============================================================================

def should_filter_out(row):
    """Return (True, reason) if this error doesn't need root-cause review."""
    sender = row.get("sender", "").lower()
    pattern = row.get("pattern_type", "")
    error_msg = row.get("error_message", "")
    snippet = row.get("snippet", "")
    combined = f"{error_msg} {snippet}".lower()

    # 1. User-pasted errors — user is showing the AI what went wrong
    if sender in ("user", "human"):
        return True, "USER_PASTED: error was in user message (user showing error to AI)"

    # 2. Permission/access denied — environment issue, not decision error
    if pattern == "permission_denied":
        return True, "HABITAT: permission denied — environment config issue"
    if "access is denied" in combined and "rg:" in combined:
        return True, "HABITAT: ripgrep access denied — search path not scoped"
    if "access is denied" in combined and "at li" in combined:
        return True, "HABITAT: PowerShell access denied"

    # 3. Repeated ripgrep/du/stat filesystem errors
    if re.search(r"no such file or directory (du|stat|age|ca)", combined):
        return True, "HABITAT: filesystem tool hit missing path"

    # 4. WinError 1920 symlink — known infrastructure issue
    if "[winerror 1920]" in combined:
        return True, "INFRASTRUCTURE: WinError 1920 symlink — documented known issue"

    # 5. FATAL template strings that weren't evaluated
    if re.search(r'fatal.*\{e\}["\)]', combined):
        return True, "TEMPLATE: unevaluated f-string in error handler code"

    # 6. Queue/progress/system messages
    if sender in ("progress", "queue-operation", "event_msg", "system", "compacted"):
        # These are internal machinery, not decision errors
        # UNLESS they contain actual tracebacks
        if pattern != "traceback":
            return True, f"MACHINERY: internal {sender} message, not a decision error"

    return False, ""


# =============================================================================
# DEDUP — collapse repeated identical errors from same conversation
# =============================================================================

def dedup_errors(errors):
    """Remove duplicate errors (same conv_id + same error_message + same pattern_type).
    Keep first occurrence only."""
    seen = set()
    unique = []
    duped = []
    for row in errors:
        key = (row.get("conv_id", ""), row.get("error_message", "")[:100],
               row.get("pattern_type", ""))
        if key in seen:
            duped.append(row)
        else:
            seen.add(key)
            unique.append(row)
    return unique, duped


# =============================================================================
# CONVERSATION LOADING
# =============================================================================

_file_cache = {}


def find_conv_file(source, conv_id, source_filepath=""):
    """Find the conversation file on disk.
    
    Tries source_filepath first (exact path from scanner output).
    Falls back to searching SOURCE_PATHS if the exact path is missing
    or the file no longer exists at that location.
    """
    # Try exact path from scanner output first
    if source_filepath:
        exact = Path(source_filepath)
        if exact.exists():
            return exact

    cache_key = f"{source}:{conv_id}"
    if cache_key in _file_cache:
        return _file_cache[cache_key]

    base = SOURCE_PATHS.get(source)
    if not base or not base.exists():
        _file_cache[cache_key] = None
        return None

    if source == "chats_manager":
        for f in base.rglob("_chat.json"):
            if conv_id in str(f):
                _file_cache[cache_key] = f
                return f
    else:
        for f in base.rglob("*.jsonl"):
            if conv_id in f.stem:
                _file_cache[cache_key] = f
                return f

    _file_cache[cache_key] = None
    return None


def load_messages(filepath):
    """Load conversation into list of {role, text} dicts."""
    if filepath is None:
        return []

    suffix = filepath.suffix.lower()
    messages = []

    try:
        if suffix == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            raw = data.get("messages", data.get("chat_messages", []))

            # ChatGPT mapping format
            if isinstance(data, dict) and "mapping" in data:
                raw = []
                for node_id, node in data.get("mapping", {}).items():
                    msg = node.get("message")
                    if msg and msg.get("content", {}).get("parts"):
                        role = msg.get("author", {}).get("role", "unknown")
                        text = "\n".join(
                            str(p) for p in msg["content"]["parts"]
                            if isinstance(p, str)
                        )
                        if text:
                            raw.append({"role": role, "text": text})

            for msg in raw:
                role = msg.get("sender", msg.get("role", msg.get("author", "unknown")))
                if isinstance(role, dict):
                    role = role.get("role", "unknown")
                text = msg.get("content", msg.get("text", ""))
                if isinstance(text, list):
                    text = "\n".join(
                        b.get("text", str(b)) if isinstance(b, dict) else str(b)
                        for b in text
                    )
                elif isinstance(text, dict):
                    text = text.get("text", str(text))
                if text and isinstance(text, str) and len(text) > 5:
                    messages.append({"role": str(role).lower(), "text": text})

        elif suffix == ".jsonl":
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    role = (obj.get("role") or obj.get("sender") or
                            obj.get("type") or "unknown")
                    if isinstance(role, dict):
                        role = role.get("role", "unknown")

                    # Aggressive text extraction
                    texts = []
                    _walk(obj, texts, 0)
                    combined = "\n".join(texts)
                    if combined and len(combined) > 15:
                        messages.append({"role": str(role).lower(), "text": combined})

    except (PermissionError, OSError, json.JSONDecodeError):
        pass

    return messages


def _walk(obj, collector, depth):
    if depth > 8:
        return
    if isinstance(obj, str) and len(obj) > 15:
        collector.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("uuid", "id", "session_id", "conversation_id",
                     "parent_id", "model", "timestamp", "hash", "version"):
                continue
            _walk(v, collector, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _walk(item, collector, depth + 1)


# =============================================================================
# CASE FILE GENERATION
# =============================================================================

def build_case_file(row, case_num, messages):
    """Build a human-readable case file for one error."""
    msg_index = int(row.get("msg_index", 0))

    lines = []
    lines.append(f"CASE {case_num:04d}")
    lines.append("=" * 60)
    lines.append(f"Source:       {row.get('source', '')}")
    lines.append(f"Platform:     {row.get('platform', '')}")
    lines.append(f"Conv ID:      {row.get('conv_id', '')}")
    lines.append(f"Msg Index:    {msg_index}")
    lines.append(f"Sender:       {row.get('sender', '')}")
    lines.append(f"Pattern:      {row.get('pattern_type', '')}")
    lines.append(f"Exception:    {row.get('exception_name', '')}")
    lines.append(f"Error:        {row.get('error_message', '')[:300]}")
    lines.append(f"File Ref:     {row.get('file_reference', '')}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("DECISION CHAIN (messages before → error → response after)")
    lines.append("-" * 60)

    if not messages:
        lines.append("[Could not load conversation — file not found]")
    else:
        # Messages BEFORE the error
        start = max(0, msg_index - CONTEXT_BEFORE)
        end = min(len(messages), msg_index + CONTEXT_AFTER + 1)

        for j in range(start, end):
            if j >= len(messages):
                break
            msg = messages[j]
            role = msg["role"]
            text = msg["text"][:MSG_CAP]

            marker = ""
            if j == msg_index:
                marker = " <<< ERROR HERE"
            elif j < msg_index:
                if role in ("user", "human"):
                    marker = " [USER REQUEST]"
                elif role in ("assistant",):
                    marker = " [AGENT ACTION/PLAN]"
            else:
                if role in ("assistant",):
                    marker = " [AGENT RESPONSE TO ERROR]"

            lines.append("")
            lines.append(f"--- MSG {j} [{role.upper()}]{marker} ---")
            lines.append(text[:MSG_CAP])

    lines.append("")
    lines.append("-" * 60)
    lines.append("ERROR SNIPPET (from scanner)")
    lines.append("-" * 60)
    lines.append(row.get("snippet", "").replace("\\n", "\n")[:1500])

    lines.append("")
    lines.append("-" * 60)
    lines.append("REVIEW QUESTIONS (for the reviewing agent)")
    lines.append("-" * 60)
    lines.append("1. What did the user request? (from [USER REQUEST] messages)")
    lines.append("2. What did the agent understand/plan? (from [AGENT ACTION/PLAN])")
    lines.append("3. Was the action that caused the error aligned with the request?")
    lines.append("4. Was this the agent's own decision or delegated to a subagent?")
    lines.append("5. Was the user request clear and specific enough?")
    lines.append("6. Did the agent verify before acting? (pre-flight check)")
    lines.append("7. What structural rule would have prevented this error?")
    lines.append("8. Which VERBATIM_FAILURE_CATALOGUE pattern does this match?")
    lines.append("   (1=False claim, 2=Misattribution, 3=Fabricated cause,")
    lines.append("    4=Verification absence, 5=Unrequested deliverable,")
    lines.append("    6=Proposal without execution, 7=Scope elaboration,")
    lines.append("    8='You're right' non-correction, NEW=new pattern)")

    return "\n".join(lines)


# =============================================================================
# MAIN
# =============================================================================

def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: {INPUT_CSV} not found. Run universal_error_scanner.py first.")
        return

    CASES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  ERROR FORENSIC EVIDENCE PREP")
    print(f"  Input:  {INPUT_CSV}")
    print(f"  Output: {CASES_DIR}")
    print("=" * 60)

    # Read all errors
    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        all_errors = list(reader)

    print(f"\n  Total errors: {len(all_errors)}")

    # Step 1: Filter
    kept = []
    filtered = []
    filter_reasons = Counter()

    for row in all_errors:
        exclude, reason = should_filter_out(row)
        if exclude:
            row["filter_reason"] = reason
            filtered.append(row)
            filter_reasons[reason.split(":")[0]] += 1
        else:
            kept.append(row)

    print(f"  Filtered out: {len(filtered)}")
    for reason, count in filter_reasons.most_common():
        print(f"    {reason}: {count}")
    print(f"  Kept for review: {len(kept)}")

    # Step 2: Dedup
    unique, duped = dedup_errors(kept)
    print(f"  After dedup: {len(unique)} unique ({len(duped)} duplicates removed)")

    # Step 3: Write filtered-out CSV (always, even if empty, with stable schema)
    canonical_filter_fieldnames = [
        "source", "platform", "conv_id", "source_filepath", "msg_index", "sender",
        "pattern_type", "exception_name", "error_message", "file_reference",
        "snippet", "match_position", "filter_reason"
    ]
    with open(FILTERED_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=canonical_filter_fieldnames,
                           quoting=csv.QUOTE_ALL, extrasaction="ignore")
        w.writeheader()
        w.writerows(filtered)
    print(f"\n  Filtered CSV: {FILTERED_CSV} ({len(filtered)} rows)")

    # Step 3b: Write reviewable_errors.csv (always, even if empty)
    # This is the canonical input for error_root_cause_extractor.py
    if kept:
        review_fieldnames = list(kept[0].keys())
    elif all_errors:
        review_fieldnames = list(all_errors[0].keys())
    else:
        review_fieldnames = ["source", "platform", "conv_id", "source_filepath",
                             "msg_index", "sender", "pattern_type", "exception_name",
                             "error_message", "file_reference", "snippet", "match_position"]
    with open(REVIEWABLE_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=review_fieldnames, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(kept)
    print(f"  Reviewable CSV: {REVIEWABLE_CSV} ({len(kept)} rows)")

    # Step 4: Clear old case files before generating new ones
    import shutil
    if CASES_DIR.exists():
        shutil.rmtree(CASES_DIR)
    CASES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n  Generating {len(unique)} case files...")

    cases_index = []
    conv_msg_cache = {}

    for i, row in enumerate(unique):
        source = row.get("source", "")
        conv_id = row.get("conv_id", "")
        source_filepath = row.get("source_filepath", "")

        # Load conversation (cached)
        cache_key = f"{source}:{conv_id}"
        if cache_key not in conv_msg_cache:
            filepath = find_conv_file(source, conv_id, source_filepath)
            conv_msg_cache[cache_key] = load_messages(filepath)
        messages = conv_msg_cache[cache_key]

        case_num = i + 1
        case_text = build_case_file(row, case_num, messages)

        # Write case file
        case_filename = f"case_{case_num:04d}.txt"
        case_path = CASES_DIR / case_filename
        with open(case_path, "w", encoding="utf-8") as f:
            f.write(case_text)

        cases_index.append({
            "case_num": case_num,
            "file": case_filename,
            "source": source,
            "platform": row.get("platform", ""),
            "conv_id": conv_id,
            "sender": row.get("sender", ""),
            "pattern_type": row.get("pattern_type", ""),
            "exception_name": row.get("exception_name", ""),
            "error_message": row.get("error_message", "")[:200],
            "has_context": "yes" if messages else "no",
            "reviewed": "",
            "catalogue_pattern": "",
            "root_cause": "",
            "notes": "",
        })

        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{len(unique)} cases generated")

    # Write cases index CSV (always, even if 0 cases)
    index_fieldnames = ["case_num", "file", "source", "platform", "conv_id",
                        "sender", "pattern_type", "exception_name", "error_message",
                        "has_context", "reviewed", "catalogue_pattern", "root_cause", "notes"]
    with open(INDEX_CSV, "w", encoding="utf-8-sig", newline="") as f:
        if cases_index:
            fieldnames = list(cases_index[0].keys())
        else:
            fieldnames = index_fieldnames
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(cases_index)
    print(f"\n  Cases index: {INDEX_CSV} ({len(cases_index)} cases)")

    # Write summary
    lines = [
        "ERROR FORENSIC PREP SUMMARY",
        "=" * 60,
        f"Date: {datetime.now().isoformat()}",
        f"Total errors scanned: {len(all_errors)}",
        f"Filtered out (no review needed): {len(filtered)}",
        f"Kept for review: {len(kept)}",
        f"After dedup: {len(unique)}",
        f"Case files generated: {len(unique)}",
        "",
        "FILTER BREAKDOWN",
        "-" * 40,
    ]
    for reason, count in filter_reasons.most_common():
        lines.append(f"  {reason:25s}: {count}")

    # Cases by source
    src_counts = Counter(c["source"] for c in cases_index)
    lines.extend(["", "CASES BY SOURCE", "-" * 40])
    for src, count in src_counts.most_common():
        lines.append(f"  {src:20s}: {count}")

    # Cases by pattern type
    pat_counts = Counter(c["pattern_type"] for c in cases_index)
    lines.extend(["", "CASES BY PATTERN TYPE", "-" * 40])
    for pat, count in pat_counts.most_common():
        lines.append(f"  {pat:25s}: {count}")

    # Cases by exception
    exc_counts = Counter(c["exception_name"] for c in cases_index if c["exception_name"])
    lines.extend(["", "CASES BY EXCEPTION (top 20)", "-" * 40])
    for exc, count in exc_counts.most_common(20):
        lines.append(f"  {exc:30s}: {count}")

    lines.extend([
        "",
        "HOW TO USE",
        "-" * 40,
        "1. Open cases_index.csv in Excel",
        "2. Sort/filter by pattern_type, source, or exception",
        "3. Open each case_NNNN.txt file to review the decision chain",
        "4. Fill in the 'reviewed', 'catalogue_pattern', 'root_cause' columns",
        "5. New patterns discovered → add to VERBATIM_FAILURE_CATALOGUE",
        "",
        "REVIEW PRIORITY (suggested order):",
        "  1. traceback cases (actual code crashes with file refs)",
        "  2. exception_line cases (named exceptions without full traceback)",
        "  3. syntax_error_detail cases (agent wrote broken code)",
        "  4. All others",
        "",
        "=" * 60,
    ])

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Summary: {SUMMARY_PATH}")

    print(f"\n{'=' * 60}")
    print(f"  PREP COMPLETE: {len(unique)} case files ready for review")
    print(f"  Cases dir: {CASES_DIR}")
    print(f"  Index: {INDEX_CSV}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Interrupted.")
    except Exception:
        tb.print_exc()
    if sys.stdin.isatty():
        input("\nPress Enter to exit...")
