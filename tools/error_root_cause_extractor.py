"""
ERROR ROOT CAUSE EXTRACTOR v1.1
================================
Reads reviewable_errors.csv (output of error_forensic_prep.py)
and extracts the ACTUAL root cause from each event's
traceback/error snippet.

If reviewable_errors.csv is not found, falls back to reading
master_errors.csv directly (unfiltered — less accurate).

Produces:
  1. root_causes_by_type.csv — per event: the actual failing
     operation, the file/line, and what was missing
  2. root_cause_summary.md — simplified table showing real
     patterns from the author's research corpus

Does NOT classify accountability. Shows the observable chain.

Run: python error_root_cause_extractor.py
"""

import csv
import re
import sys
import traceback as tb_mod
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter


SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_CSV = SCRIPT_DIR / "error_scan_output" / "reviewable_errors.csv"
FALLBACK_CSV = SCRIPT_DIR / "error_scan_output" / "master_errors.csv"
OUTPUT_CSV = SCRIPT_DIR / "error_scan_output" / "root_causes_by_type.csv"
SUMMARY_MD = SCRIPT_DIR / "error_scan_output" / "root_cause_summary.md"


def extract_root_cause(row):
    """From an error row, extract the observable causal chain."""
    snippet = row.get("snippet", "").replace("\\n", "\n")
    error_msg = row.get("error_message", "")
    pattern_type = row.get("pattern_type", "")
    exception_name = row.get("exception_name", "")
    file_ref = row.get("file_reference", "")
    sender = row.get("sender", "")

    # What failed (the immediate operation)
    failing_operation = ""
    # What was missing (the absent check or condition)
    what_was_missing = ""
    # The specific trigger
    specific_trigger = ""

    # --- Extract based on pattern type ---

    if pattern_type == "traceback":
        # Full traceback: last File line = where, last exception = what
        file_lines = re.findall(r'File "([^"]+)", line (\d+)', snippet)
        if file_lines:
            last_file, last_line = file_lines[-1]
            failing_operation = f"{Path(last_file).name}:{last_line}"
        else:
            failing_operation = file_ref or "unknown location"

        # The exception at the bottom
        exc_match = re.search(
            r'(\w+(?:Error|Exception|Warning)):\s*(.+?)(?:\n|$)', snippet
        )
        if exc_match:
            specific_trigger = f"{exc_match.group(1)}: {exc_match.group(2)[:150]}"
        else:
            specific_trigger = error_msg[:150]

        # What was missing depends on exception type
        what_was_missing = _infer_missing_check(exception_name, error_msg, snippet)

    elif pattern_type == "exception_line":
        failing_operation = file_ref or "unknown location"
        specific_trigger = f"{exception_name}: {error_msg[:150]}"
        what_was_missing = _infer_missing_check(exception_name, error_msg, snippet)

    elif pattern_type == "syntax_error_detail":
        # Syntax errors have file + line in the error itself
        syn_match = re.search(r'File "([^"]+)", line (\d+)', snippet)
        if syn_match:
            failing_operation = f"{Path(syn_match.group(1)).name}:{syn_match.group(2)}"
        else:
            failing_operation = file_ref or "inline code"
        specific_trigger = f"SyntaxError: {error_msg[:150]}"
        what_was_missing = "Code syntax validation before execution (ast.parse)"

    elif pattern_type == "file_not_found":
        # Extract the path that wasn't found
        path_match = re.search(
            r"(?:No such file or directory|cannot find)[:\s]*['\"]?([^'\"\\n]{5,200})",
            snippet, re.IGNORECASE
        )
        if path_match:
            specific_trigger = f"Path not found: {path_match.group(1)[:150]}"
        else:
            specific_trigger = error_msg[:150]
        failing_operation = file_ref or "file/path operation"
        what_was_missing = "Path existence check before access (Path.exists, ls, find)"

    elif pattern_type == "permission_denied":
        path_match = re.search(
            r"(?:Permission denied|Access is denied)[:\s]*['\"]?([^'\"\\n]{5,200})",
            snippet, re.IGNORECASE
        )
        if path_match:
            specific_trigger = f"Access denied: {path_match.group(1)[:150]}"
        else:
            specific_trigger = error_msg[:150]
        failing_operation = file_ref or "access operation"
        what_was_missing = "Permission/access check before operation"

    elif pattern_type == "errno":
        specific_trigger = error_msg[:150]
        failing_operation = file_ref or "OS operation"
        what_was_missing = _infer_missing_check("OSError", error_msg, snippet)

    elif pattern_type == "win_error":
        specific_trigger = error_msg[:150]
        failing_operation = file_ref or "Windows operation"
        what_was_missing = "OS condition check before operation"

    elif pattern_type == "ps_error":
        specific_trigger = error_msg[:150]
        failing_operation = "PowerShell command"
        if "not recognized" in error_msg.lower():
            what_was_missing = "Cmdlet/command availability check (Get-Command)"
        elif "parameter" in error_msg.lower():
            what_was_missing = "Parameter validation (Get-Help <cmdlet>)"
        else:
            what_was_missing = "PowerShell environment verification"

    elif pattern_type == "npm_node_error":
        specific_trigger = error_msg[:150]
        failing_operation = "Node.js operation"
        if "cannot find module" in error_msg.lower():
            what_was_missing = "Module installation check (npm list)"
        else:
            what_was_missing = "Node environment verification"

    elif pattern_type == "unicode_escape":
        specific_trigger = "Windows path in regular string (\\U interpreted as unicode escape)"
        failing_operation = file_ref or "string containing Windows path"
        what_was_missing = "Raw string prefix (r\"...\") — documented rule not followed"

    elif pattern_type == "critical_marker":
        specific_trigger = error_msg[:150]
        failing_operation = file_ref or "unknown"
        what_was_missing = "Needs triage — may be prose, template, or real error"

    else:
        specific_trigger = error_msg[:150]
        failing_operation = file_ref or "unknown"
        what_was_missing = "Unknown — needs manual review"

    return {
        "failing_operation": failing_operation,
        "specific_trigger": specific_trigger.replace("\n", " ").strip()[:200],
        "what_was_missing": what_was_missing,
    }


def _infer_missing_check(exception_name, error_msg, snippet):
    """Based on exception type, what check would have prevented it."""
    checks = {
        "FileNotFoundError": "Path existence check (Path.exists)",
        "ModuleNotFoundError": "Module availability check (pip list, try import)",
        "ImportError": "Module availability check (pip list, try import)",
        "SyntaxError": "Syntax validation (ast.parse) before execution",
        "IndentationError": "Code formatting validation before delivery",
        "TabError": "Code formatting validation before delivery",
        "NameError": "Variable definition verification (read code before delivery)",
        "AttributeError": "Object structure inspection (type, dir, hasattr)",
        "KeyError": "Dictionary key verification (data.keys, data.get)",
        "IndexError": "Collection length check (len) before index access",
        "TypeError": "Type checking before operation (type, isinstance)",
        "ValueError": "Input validation before conversion",
        "PermissionError": "Access permission check before operation",
        "OSError": "OS condition verification before operation",
        "EOFError": "Input source availability check (execution context verification)",
        "RuntimeError": "Edge case handling (specific error instead of generic raise)",
        "UnicodeDecodeError": "Encoding detection before reading (chardet, try/except)",
        "UnicodeEncodeError": "Encoding specification on write (encoding='utf-8')",
        "NotADirectoryError": "Path type check (is_file vs is_dir) before operation",
        "RecursionError": "Recursion depth guard or iterative alternative",
    }
    base = checks.get(exception_name, "")
    if not base:
        # Try to infer from message
        msg_lower = error_msg.lower()
        if "no such file" in msg_lower:
            return "Path existence check"
        if "permission" in msg_lower or "access" in msg_lower:
            return "Permission check before access"
        if "not found" in msg_lower:
            return "Existence/availability check"
        return "Pre-execution verification"
    return base


def classify_concern_level(pattern_type, exception_name, error_msg, what_was_missing):
    """
    NOT CONCERNING: Environmental, unpredictable, or one-time issues
    CONCERNING: Preventable errors where a basic check was skipped
    ALARMING: Known documented rules violated, or repeated patterns
              that indicate systemic failure despite guidance
    """
    msg_lower = error_msg.lower()

    # ALARMING: documented rule exists and was not followed
    if pattern_type == "unicode_escape":
        return "ALARMING", "Documented rule exists, was not followed"
    if pattern_type == "permission_denied" and pattern_type != "FILTERED":
        return "ALARMING", "Targeted access attempt that survived filter"

    # ALARMING: code so broken it can't parse
    if exception_name == "SyntaxError":
        return "ALARMING", "Code failed to parse — never tested before delivery"
    if exception_name == "IndentationError":
        return "ALARMING", "Code indentation broken — never read before delivery"

    # CONCERNING: preventable with basic checks
    preventable_exceptions = {
        "FileNotFoundError", "ModuleNotFoundError", "ImportError",
        "NameError", "KeyError", "IndexError", "AttributeError",
    }
    if exception_name in preventable_exceptions:
        return "CONCERNING", f"Preventable with {what_was_missing}"

    # CONCERNING: file not found pattern (broader than just the exception)
    if pattern_type == "file_not_found":
        return "CONCERNING", "Path not verified before use"

    if pattern_type == "ps_error":
        return "CONCERNING", "PowerShell environment not checked"
    if pattern_type == "npm_node_error":
        return "CONCERNING", "Node.js environment not checked"

    # NOT CONCERNING: needs triage first
    if pattern_type == "critical_marker":
        return "NEEDS_TRIAGE", "May be prose, template, or real error"

    # Contextual — depends on specifics
    if exception_name in ("EOFError", "TypeError", "ValueError"):
        return "CONCERNING", "May involve complexity — review instruction context"

    if exception_name in ("OSError", "RuntimeError"):
        return "NOT_CONCERNING", "May be environmental or unpredictable"

    if pattern_type == "win_error":
        return "NOT_CONCERNING", "Windows OS condition — may be unpredictable"

    if pattern_type == "traceback":
        return "CONCERNING", "Code crashed at runtime — review traceback"

    if pattern_type == "exception_line":
        return "CONCERNING", "Exception in executed code — review context"

    return "CONCERNING", "Review needed"


def main():
    # Prefer reviewable_errors.csv (output of forensic_prep, single source of truth)
    # Fall back to master_errors.csv ONLY if reviewable_errors.csv does not exist
    # (meaning forensic_prep has not been run yet).
    # If reviewable_errors.csv exists but is empty, that means prep ran and
    # filtered everything out — do NOT fall back to unfiltered data.
    input_path = INPUT_CSV
    if not INPUT_CSV.exists():
        if FALLBACK_CSV.exists():
            print(f"  Note: {INPUT_CSV.name} not found.")
            print(f"  Reading {FALLBACK_CSV.name} instead (unfiltered — run error_forensic_prep.py first for best results).")
            input_path = FALLBACK_CSV
        else:
            print(f"ERROR: Neither {INPUT_CSV.name} nor {FALLBACK_CSV.name} found.")
            print(f"  Run universal_error_scanner.py, then error_forensic_prep.py first.")
            return

    print("=" * 60)
    print("  ERROR ROOT CAUSE EXTRACTOR")
    print(f"  Input: {input_path.name}")
    print("=" * 60)

    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reviewable = list(reader)

    print(f"\n  Reviewable errors: {len(reviewable)}")

    # Extract root causes
    results = []
    level_counts = Counter()
    pattern_level = defaultdict(lambda: Counter())

    for row in reviewable:
        cause = extract_root_cause(row)
        level, level_reason = classify_concern_level(
            row.get("pattern_type", ""),
            row.get("exception_name", ""),
            row.get("error_message", ""),
            cause["what_was_missing"]
        )
        level_counts[level] += 1
        pattern_level[row.get("pattern_type", "")][level] += 1

        results.append({
            "source": row.get("source", ""),
            "platform": row.get("platform", ""),
            "conv_id": row.get("conv_id", ""),
            "sender": row.get("sender", ""),
            "pattern_type": row.get("pattern_type", ""),
            "exception_name": row.get("exception_name", ""),
            "failing_operation": cause["failing_operation"],
            "specific_trigger": cause["specific_trigger"],
            "what_was_missing": cause["what_was_missing"],
            "concern_level": level,
            "concern_reason": level_reason,
            "original_snippet": row.get("snippet", "")[:300],
        })

    # Write detailed CSV (always, even if 0 results — prevents stale output)
    output_fieldnames = ["source", "platform", "conv_id", "sender", "pattern_type",
                         "exception_name", "failing_operation", "specific_trigger",
                         "what_was_missing", "concern_level", "concern_reason", "original_snippet"]
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        if results:
            fieldnames = list(results[0].keys())
        else:
            fieldnames = output_fieldnames
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(results)
    print(f"\n  Root causes CSV: {OUTPUT_CSV} ({len(results)} rows)")

    # Build summary markdown
    lines = [
        "# ERROR ROOT CAUSE SUMMARY",
        f"Generated: {datetime.now().isoformat()[:19]}",
        f"Total reviewable errors: {len(reviewable)}",
        "",
        "## CONCERN LEVEL DISTRIBUTION",
        "",
    ]
    for level in ["ALARMING", "CONCERNING", "NOT_CONCERNING", "NEEDS_TRIAGE"]:
        count = level_counts.get(level, 0)
        pct = count / len(reviewable) * 100 if reviewable else 0
        lines.append(f"- **{level}**: {count} ({pct:.1f}%)")

    # Per error type: show actual root causes from data
    lines.extend([
        "",
        "## ROOT CAUSES BY ERROR TYPE (from actual data)",
        "",
        "Each row shows: error type, count, top actual triggers found",
        "in the traceback/snippet data, and what check was absent.",
        "",
    ])

    # Group by pattern_type
    by_type = defaultdict(list)
    for r in results:
        by_type[r["pattern_type"]].append(r)

    for ptype in sorted(by_type.keys(), key=lambda x: -len(by_type[x])):
        items = by_type[ptype]
        count = len(items)

        # Top triggers
        trigger_counts = Counter(i["specific_trigger"][:100] for i in items)
        # Top missing checks
        missing_counts = Counter(i["what_was_missing"] for i in items)
        # Concern distribution
        concern_dist = Counter(i["concern_level"] for i in items)

        lines.append(f"### {ptype} — {count} cases")
        lines.append("")

        # Concern level for this type
        concern_str = ", ".join(
            f"{lvl}: {cnt}" for lvl, cnt in concern_dist.most_common()
        )
        lines.append(f"Concern: {concern_str}")
        lines.append("")

        # Top 5 actual triggers
        lines.append("Top triggers from data:")
        for trigger, cnt in trigger_counts.most_common(5):
            lines.append(f"- [{cnt}x] {trigger}")
        lines.append("")

        # What was missing
        lines.append("What was absent:")
        for missing, cnt in missing_counts.most_common(3):
            lines.append(f"- [{cnt}x] {missing}")
        lines.append("")

        # Source distribution
        src_counts = Counter(i["source"] for i in items)
        lines.append("Source: " + ", ".join(
            f"{s}: {c}" for s, c in src_counts.most_common()
        ))
        lines.append("")
        lines.append("---")
        lines.append("")

    # Simplified evidence table
    lines.extend([
        "## SIMPLIFIED EVIDENCE TABLE",
        "",
        "| Error Type | Count | Primary Root Cause | What Was Absent | Concern |",
        "|---|---|---|---|---|",
    ])

    for ptype in sorted(by_type.keys(), key=lambda x: -len(by_type[x])):
        items = by_type[ptype]
        count = len(items)
        top_missing = Counter(i["what_was_missing"] for i in items).most_common(1)
        missing_str = top_missing[0][0] if top_missing else "unknown"
        top_trigger = Counter(
            i["specific_trigger"][:80] for i in items
        ).most_common(1)
        trigger_str = top_trigger[0][0] if top_trigger else "unknown"
        # Most common concern level
        top_concern = Counter(i["concern_level"] for i in items).most_common(1)
        concern_str = top_concern[0][0] if top_concern else "unknown"

        lines.append(
            f"| {ptype} | {count} | {trigger_str[:60]} | "
            f"{missing_str[:50]} | {concern_str} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## WHAT THIS TABLE SHOWS",
        "",
        "Each row is derived from the actual error data — the",
        "traceback text, the exception message, the file reference.",
        "The 'Primary Root Cause' is the most common trigger found",
        "in the real snippets. The 'What Was Absent' is the check",
        "that, if present, would have prevented the error.",
        "",
        "This is not a claim of accountability. It is a record of",
        "what the data shows: what failed, what was missing, and",
        "how concerning the pattern is based on whether it was",
        "preventable with available tools and documented guidance.",
        "",
        "ALARMING = documented rule exists and was not followed,",
        "  or code was so broken it could not parse",
        "CONCERNING = preventable with a basic check that was available",
        "  but not performed",
        "NOT_CONCERNING = may be environmental or unpredictable",
        "NEEDS_TRIAGE = cannot assess until real errors separated",
        "  from false positives",
    ])

    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Summary: {SUMMARY_MD}")

    # Print key stats
    print(f"\n  CONCERN LEVELS:")
    for level in ["ALARMING", "CONCERNING", "NOT_CONCERNING", "NEEDS_TRIAGE"]:
        count = level_counts.get(level, 0)
        pct = count / len(reviewable) * 100 if reviewable else 0
        print(f"    {level:20s}: {count:5d} ({pct:.1f}%)")

    print(f"\n{'=' * 60}")
    print(f"  EXTRACTION COMPLETE")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Interrupted.")
    except Exception:
        tb_mod.print_exc()
    if sys.stdin.isatty():
        input("\nPress Enter to exit...")
