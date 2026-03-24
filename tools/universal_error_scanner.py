"""
UNIVERSAL ERROR & TRACEBACK SCANNER v1.1
=========================================
Scans AI agent session files for errors, tracebacks, and failure patterns.
Produces one master CSV with every error found across all platforms.

Sources scanned:
  1. Web chat exports (_chat.json) — Claude, ChatGPT, DeepSeek, Grok, Gemini, Perplexity
  2. Claude Code sessions (.claude/projects/*/*.jsonl)
  3. Codex sessions (.codex/sessions/**/*.jsonl)
  4. Cowork sessions (AppData/Claude/local-agent-mode-sessions/**/*.jsonl)

Configuration:
  - All source paths are configurable via environment variables:
      CHATS_MANAGER_PATH  — web chat exports directory
      CLAUDE_CODE_PATH    — Claude Code projects directory
      CODEX_PATH          — Codex sessions directory
      COWORK_PATH         — Cowork sessions directory
  - If not set, standard platform locations are used as defaults.

What it detects:
  - Python tracebacks (full block extraction)
  - Named exceptions (NameError, TypeError, etc.)
  - PowerShell errors (CommandNotFoundException, etc.)
  - Windows errors (WinError, [Errno])
  - Node.js errors (ReferenceError, ENOENT, etc.)
  - Permission/access errors
  - File not found patterns
  - Syntax errors (with file + line if available)
  - Custom error markers (CRITICAL ERROR, FATAL, etc.)

Output:
  error_scan_output/master_errors.csv       — every error with full context
  error_scan_output/error_summary.txt       — counts by type, platform, source
  error_scan_output/error_tracebacks.jsonl  — full traceback blocks (not truncated)

Rules:
  - Read-only on all source files
  - Resumable via checkpoint
  - Scans BOTH user AND assistant messages (errors appear in both)
  - UTF-8 with BOM for Excel compatibility

Run:  python universal_error_scanner.py
      python universal_error_scanner.py --source chats_manager
      python universal_error_scanner.py --source claude_code
"""

import json
import csv
import re
import os
import sys
import traceback as tb
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Optional, Tuple


# =============================================================================
# CONFIGURATION
# =============================================================================
# Paths are auto-detected from standard platform locations.
# The chats_manager path is the only one that varies by user setup.
# Set the environment variable CHATS_MANAGER_PATH to override, or edit below.

HOME = Path.home()
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "error_scan_output"

# Chats manager path — override with environment variable if needed
CHATS_MANAGER_PATH = os.environ.get(
    "CHATS_MANAGER_PATH",
    str(HOME / "Downloads" / "FRAMEWORK" / "08_CHATS")  # default — edit for your setup
)

# Source locations
SOURCES = {
    "chats_manager": {
        "search_paths": [
            Path(CHATS_MANAGER_PATH),
        ],
        "pattern": "**/_chat.json",
        "format": "chat_json",
    },
    "claude_code": {
        "search_paths": [
            Path(os.environ.get("CLAUDE_CODE_PATH", str(HOME / ".claude" / "projects"))),
        ],
        "pattern": "**/*.jsonl",
        "format": "claude_jsonl",
    },
    "codex": {
        "search_paths": [
            Path(os.environ.get("CODEX_PATH", str(HOME / ".codex" / "sessions"))),
        ],
        "pattern": "**/*.jsonl",
        "format": "codex_jsonl",
    },
    "cowork": {
        "search_paths": [
            Path(os.environ.get("COWORK_PATH",
                str(Path(os.environ.get("APPDATA", "")) / "Claude" / "local-agent-mode-sessions"))),
        ],
        "pattern": "**/*.jsonl",
        "format": "cowork_jsonl",
    },
}

# =============================================================================
# ERROR PATTERNS
# =============================================================================

# Python exceptions
PYTHON_EXCEPTIONS = [
    "ArithmeticError", "AssertionError", "AttributeError", "BlockingIOError",
    "BrokenPipeError", "BufferError", "ChildProcessError", "ConnectionError",
    "ConnectionAbortedError", "ConnectionRefusedError", "ConnectionResetError",
    "EOFError", "EnvironmentError", "FileExistsError", "FileNotFoundError",
    "FloatingPointError", "IOError", "ImportError", "IndentationError",
    "IndexError", "InterruptedError", "IsADirectoryError", "JSONDecodeError",
    "KeyError", "KeyboardInterrupt", "LookupError", "MemoryError",
    "ModuleNotFoundError", "NameError", "NotADirectoryError",
    "NotImplementedError", "OSError", "OverflowError", "PermissionError",
    "ProcessLookupError", "RecursionError", "ReferenceError", "RuntimeError",
    "StopAsyncIteration", "StopIteration", "SyntaxError", "SystemError",
    "TabError", "TimeoutError", "TypeError", "UnboundLocalError",
    "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeError",
    "UnicodeTranslationError", "ValueError", "WindowsError", "ZeroDivisionError",
]

# PowerShell errors
PS_EXCEPTIONS = [
    "CommandNotFoundException", "ItemNotFoundException", "ParameterBindingException",
    "PSSecurityException", "RuntimeException", "InvalidOperationException",
    "MethodInvocationException", "PropertyNotFoundException",
]

# Node.js errors  
NODE_EXCEPTIONS = [
    "ReferenceError", "RangeError", "URIError", "EvalError",
    "ENOENT", "EACCES", "EPERM", "EEXIST", "EISDIR", "ENOTDIR",
]

ALL_EXCEPTION_NAMES = "|".join(
    PYTHON_EXCEPTIONS + PS_EXCEPTIONS + NODE_EXCEPTIONS
)

# Compiled patterns
PATTERNS = {
    "traceback": re.compile(
        r"Traceback \(most recent call last\):\s*\n(?:.*\n)*?\s*(\w+(?:Error|Exception|Warning)\b.*)",
        re.MULTILINE
    ),
    "exception_line": re.compile(
        rf"^({ALL_EXCEPTION_NAMES}):\s*(.+)$",
        re.MULTILINE
    ),
    "win_error": re.compile(
        r"\[WinError \d+\]\s*.+",
    ),
    "errno": re.compile(
        r"\[Errno \d+\]\s*.+",
    ),
    "ps_error": re.compile(
        r"(?:^|\n)(\w+)\s*:\s*(.*(?:CommandNotFoundException|ItemNotFoundException|ParameterBinding|Cannot find|is not recognized).*)",
        re.MULTILINE
    ),
    "syntax_error_detail": re.compile(
        r'File "([^"]+)", line (\d+).*?\n\s*.*?\n\s*\^+\s*\n\s*(SyntaxError|IndentationError|TabError):\s*(.*)',
        re.DOTALL
    ),
    "file_not_found": re.compile(
        r"(?:No such file or directory|The system cannot find the (?:file|path)|Could not find a part of the path)[:\s]*['\"]?([^'\"\\n]+)",
    ),
    "permission_denied": re.compile(
        r"(?:Permission denied|Access is denied|PermissionError)[:\s]*['\"]?([^'\"\\n]*)",
    ),
    "critical_marker": re.compile(
        r"(?:CRITICAL ERROR|FATAL ERROR|FATAL|UNHANDLED EXCEPTION)[:\s]+(.+)",
        re.IGNORECASE
    ),
    "npm_node_error": re.compile(
        r"(?:npm ERR!|Error: Cannot find module|MODULE_NOT_FOUND)\s*(.*)",
    ),
    "unicode_escape": re.compile(
        r"SyntaxError: \(unicode error\) ['\"]?unicodeescape['\"]? codec can't decode",
    ),
}

# Context window: chars before/after match to capture
CONTEXT_BEFORE = 100
CONTEXT_AFTER = 300
SNIPPET_MAX = 500


# =============================================================================
# TEXT EXTRACTION (per format)
# =============================================================================

def extract_texts_chat_json(filepath: Path) -> List[Dict]:
    """Extract text blocks from CHATS_MANAGER _chat.json files.
    
    Raises json.JSONDecodeError or UnicodeDecodeError on malformed files
    so the caller can record them as skipped.
    """
    results = []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Determine platform from parent directory
    platform_dir = filepath.parent.parent.name if filepath.parent.parent else "unknown"
    conv_id = filepath.parent.name

    messages = data.get("messages", data.get("chat_messages", []))
    if isinstance(data, dict) and "mapping" in data:
        # ChatGPT format
        messages = []
        for node_id, node in data["mapping"].items():
            msg = node.get("message")
            if msg and msg.get("content", {}).get("parts"):
                messages.append({
                    "sender": msg.get("author", {}).get("role", "unknown"),
                    "content": "\n".join(str(p) for p in msg["content"]["parts"] if isinstance(p, str)),
                    "index": len(messages),
                })

    for i, msg in enumerate(messages):
        sender = msg.get("sender", msg.get("role", msg.get("author", "unknown")))
        if isinstance(sender, dict):
            sender = sender.get("role", "unknown")

        # Get text from various content formats
        content = msg.get("content", msg.get("text", ""))
        if isinstance(content, list):
            texts = []
            for block in content:
                if isinstance(block, str):
                    texts.append(block)
                elif isinstance(block, dict):
                    texts.append(block.get("text", block.get("content", "")))
            content = "\n".join(texts)
        elif isinstance(content, dict):
            content = content.get("text", content.get("content", str(content)))

        if content and len(content) > 10:
            results.append({
                "source": "chats_manager",
                "platform": platform_dir,
                "conv_id": conv_id,
                "source_filepath": str(filepath),
                "msg_index": msg.get("index", i),
                "sender": str(sender),
                "text": str(content),
            })

    return results


def extract_texts_jsonl(filepath: Path, source_name: str) -> List[Dict]:
    """Extract text from JSONL files (Claude Code, Codex, Cowork).
    
    Strategy: be aggressive. Walk the entire JSON tree for every line,
    extract ALL string values longer than 20 chars. This catches errors
    in tool outputs, shell stderr, nested content blocks, etc. regardless
    of the specific JSONL schema.
    
    Raises ValueError if the file contains lines but none are valid JSON.
    Raises PermissionError/OSError on access failures.
    """
    results = []
    conv_id = filepath.stem

    # Determine platform from path
    path_str = str(filepath)
    if ".claude" in path_str:
        platform = "claude_code"
    elif ".codex" in path_str:
        platform = "codex"
    elif "local-agent-mode" in path_str:
        platform = "cowork"
    else:
        platform = "unknown"

    total_lines = 0
    parse_errors = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            total_lines += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue

            # Determine role from common fields
            role = (obj.get("role") or obj.get("sender") or 
                    obj.get("type") or obj.get("item_type") or "unknown")
            if isinstance(role, dict):
                role = role.get("role", "unknown")

            # Aggressively extract ALL text from the object
            all_texts = []
            _walk_for_text(obj, all_texts, depth=0)
            
            combined = "\n".join(all_texts)
            if combined and len(combined) > 20:
                results.append({
                    "source": source_name,
                    "platform": platform,
                    "conv_id": conv_id,
                    "source_filepath": str(filepath),
                    "msg_index": line_num,
                    "sender": str(role),
                    "text": combined,
                })

    # If the file had content but none of it was valid JSON, report it
    if total_lines > 0 and parse_errors == total_lines:
        raise ValueError(f"All {total_lines} non-empty lines failed JSON parsing — file is not valid JSONL")

    return results


def _walk_for_text(obj, collector: list, depth: int):
    """Recursively walk a JSON object and collect all string values
    that are long enough to potentially contain errors."""
    if depth > 10:
        return  # prevent infinite recursion
    
    if isinstance(obj, str):
        if len(obj) > 20:
            collector.append(obj)
    elif isinstance(obj, dict):
        for key, val in obj.items():
            # Skip keys that are unlikely to contain error text
            if key in ("uuid", "id", "session_id", "conversation_id", 
                       "parent_id", "model", "timestamp", "created_at",
                       "updated_at", "hash", "sha", "version"):
                continue
            _walk_for_text(val, collector, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            _walk_for_text(item, collector, depth + 1)


# =============================================================================
# ERROR DETECTION
# =============================================================================

def scan_text_for_errors(text: str, meta: Dict) -> List[Dict]:
    """Scan a text block for all error patterns. Return list of error records."""
    errors = []

    for pattern_name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            start = max(0, match.start() - CONTEXT_BEFORE)
            end = min(len(text), match.end() + CONTEXT_AFTER)
            snippet = text[start:end].strip()

            # Extract specific error type from match
            error_type = pattern_name
            error_message = match.group(0)[:300]

            # Try to extract the exception name
            exception_name = ""
            if pattern_name == "traceback":
                # Last line of traceback has the exception
                tb_text = match.group(0)
                last_line = tb_text.strip().split("\n")[-1]
                exc_match = re.match(r"(\w+(?:Error|Exception|Warning)):\s*(.*)", last_line)
                if exc_match:
                    exception_name = exc_match.group(1)
                    error_message = exc_match.group(2)[:300]
            elif pattern_name == "exception_line":
                exception_name = match.group(1)
                error_message = match.group(2)[:300] if match.lastindex >= 2 else ""
            elif pattern_name == "syntax_error_detail":
                exception_name = match.group(3) if match.lastindex >= 3 else "SyntaxError"
                error_message = match.group(4)[:300] if match.lastindex >= 4 else ""

            # Extract file path if present
            file_ref = ""
            file_match = re.search(r'File "([^"]+)", line (\d+)', text[max(0, match.start()-200):match.end()])
            if file_match:
                file_ref = f"{file_match.group(1)}:{file_match.group(2)}"

            errors.append({
                "source": meta.get("source", ""),
                "platform": meta.get("platform", ""),
                "conv_id": meta.get("conv_id", ""),
                "source_filepath": meta.get("source_filepath", ""),
                "msg_index": meta.get("msg_index", ""),
                "sender": meta.get("sender", ""),
                "pattern_type": pattern_name,
                "exception_name": exception_name,
                "error_message": error_message.replace("\n", " ").strip(),
                "file_reference": file_ref,
                "snippet": snippet[:SNIPPET_MAX].replace("\n", "\\n"),
                "match_position": match.start(),
            })

    return errors


# =============================================================================
# MAIN SCANNER
# =============================================================================

def find_source_files(source_name: str) -> List[Path]:
    """Find all scannable files for a given source."""
    config = SOURCES.get(source_name)
    if not config:
        return []

    files = []
    for search_path in config["search_paths"]:
        exists = search_path.exists()
        print(f"    Checking: {search_path} {'[FOUND]' if exists else '[NOT FOUND]'}")
        if not exists:
            continue
        for f in search_path.glob(config["pattern"]):
            try:
                if f.is_file() and f.stat().st_size > 0:
                    files.append(f)
            except (OSError, PermissionError):
                continue  # symlink or access error

    return sorted(files)


def scan_source(source_name: str, files: List[Path]) -> Tuple[List[Dict], List[Dict]]:
    """Scan all files from one source. Returns (errors, skipped_files)."""
    all_errors = []
    skipped = []
    config = SOURCES[source_name]
    fmt = config["format"]

    for i, filepath in enumerate(files):
        try:
            if fmt == "chat_json":
                texts = extract_texts_chat_json(filepath)
            else:
                texts = extract_texts_jsonl(filepath, source_name)

            for text_block in texts:
                errors = scan_text_for_errors(text_block["text"], text_block)
                all_errors.extend(errors)

        except Exception as e:
            skipped.append({
                "source": source_name,
                "filepath": str(filepath),
                "reason": f"{type(e).__name__}: {str(e)[:200]}",
            })

        if (i + 1) % 50 == 0:
            print(f"    {source_name}: {i+1}/{len(files)} files, "
                  f"{len(all_errors)} errors found")

    return all_errors, skipped


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parse args
    filter_source = None
    if len(sys.argv) > 2 and sys.argv[1] == "--source":
        filter_source = sys.argv[2]

    print("=" * 60)
    print("  UNIVERSAL ERROR & TRACEBACK SCANNER")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 60)

    all_errors = []
    all_skipped = []
    source_stats = {}

    for source_name, config in SOURCES.items():
        if filter_source and source_name != filter_source:
            continue

        files = find_source_files(source_name)
        if not files:
            print(f"\n  {source_name}: no files found")
            source_stats[source_name] = {"files": 0, "errors": 0, "skipped": 0}
            continue

        print(f"\n  {source_name}: scanning {len(files)} files...")
        errors, skipped = scan_source(source_name, files)
        all_errors.extend(errors)
        all_skipped.extend(skipped)
        source_stats[source_name] = {"files": len(files), "errors": len(errors), "skipped": len(skipped)}
        print(f"  {source_name}: {len(errors)} errors found", end="")
        if skipped:
            print(f" ({len(skipped)} files unreadable)")
        else:
            print()

    # =========================================================================
    # Write master CSV
    # =========================================================================
    csv_path = OUTPUT_DIR / "master_errors.csv"
    fieldnames = [
        "source", "platform", "conv_id", "source_filepath", "msg_index", "sender",
        "pattern_type", "exception_name", "error_message",
        "file_reference", "snippet", "match_position"
    ]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames,
                                 quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        writer.writerows(all_errors)
    print(f"\n  Master CSV: {csv_path} ({len(all_errors)} rows)")

    # =========================================================================
    # Write full tracebacks (not truncated) as JSONL
    # =========================================================================
    tb_path = OUTPUT_DIR / "error_tracebacks.jsonl"
    tb_count = 0
    with open(tb_path, "w", encoding="utf-8") as f:
        for err in all_errors:
            if err["pattern_type"] == "traceback":
                f.write(json.dumps(err, ensure_ascii=False) + "\n")
                tb_count += 1
    print(f"  Tracebacks JSONL: {tb_path} ({tb_count} entries)")

    # =========================================================================
    # Write summary
    # =========================================================================
    summary_path = OUTPUT_DIR / "error_summary.txt"
    lines = [
        "UNIVERSAL ERROR SCAN SUMMARY",
        "=" * 60,
        f"Scan date: {datetime.now().isoformat()}",
        f"Total errors: {len(all_errors)}",
        f"Total tracebacks: {tb_count}",
        "",
        "BY SOURCE",
        "-" * 40,
    ]
    for src, stats in source_stats.items():
        line = f"  {src:20s}: {stats['files']:5d} files, {stats['errors']:6d} errors"
        if stats.get('skipped', 0) > 0:
            line += f", {stats['skipped']} unreadable"
        lines.append(line)

    # By pattern type
    type_counts = Counter(e["pattern_type"] for e in all_errors)
    lines.extend(["", "BY PATTERN TYPE", "-" * 40])
    for ptype, count in type_counts.most_common():
        lines.append(f"  {ptype:25s}: {count:6d}")

    # By exception name (top 30)
    exc_counts = Counter(e["exception_name"] for e in all_errors if e["exception_name"])
    lines.extend(["", "BY EXCEPTION NAME (top 30)", "-" * 40])
    for exc, count in exc_counts.most_common(30):
        lines.append(f"  {exc:30s}: {count:6d}")

    # By platform
    plat_counts = Counter(e["platform"] for e in all_errors)
    lines.extend(["", "BY PLATFORM", "-" * 40])
    for plat, count in plat_counts.most_common():
        lines.append(f"  {plat:20s}: {count:6d}")

    # By sender
    sender_counts = Counter(e["sender"] for e in all_errors)
    lines.extend(["", "BY SENDER (who produced the error)", "-" * 40])
    for sender, count in sender_counts.most_common():
        lines.append(f"  {sender:20s}: {count:6d}")

    # Most common error messages (top 20)
    msg_counts = Counter(e["error_message"][:100] for e in all_errors if e["error_message"])
    lines.extend(["", "MOST COMMON ERROR MESSAGES (top 20)", "-" * 60])
    for msg, count in msg_counts.most_common(20):
        lines.append(f"  [{count:4d}x] {msg}")

    # Most referenced files (top 20)
    file_counts = Counter(e["file_reference"] for e in all_errors if e["file_reference"])
    if file_counts:
        lines.extend(["", "MOST ERROR-PRONE FILES (top 20)", "-" * 60])
        for fref, count in file_counts.most_common(20):
            lines.append(f"  [{count:4d}x] {fref}")

    lines.extend(["", "=" * 60, f"Full data: {csv_path}"])

    # Add skipped files to summary
    if all_skipped:
        lines.extend(["", "UNREADABLE FILES (skipped during scan)", "-" * 60])
        lines.append(f"  Total: {len(all_skipped)}")
        for s in all_skipped:
            lines.append(f"  {s['source']:15s} {s['filepath']}")
            lines.append(f"  {'':15s} Reason: {s['reason']}")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Summary: {summary_path}")

    # Write skipped files CSV (always, even if empty — for audit completeness)
    skipped_path = OUTPUT_DIR / "skipped_files.csv"
    skipped_fieldnames = ["source", "filepath", "reason"]
    with open(skipped_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=skipped_fieldnames, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(all_skipped)
    if all_skipped:
        print(f"  Skipped files: {skipped_path} ({len(all_skipped)} unreadable)")

    print(f"\n{'=' * 60}")
    total_files = sum(s['files'] for s in source_stats.values())
    total_skipped = sum(s.get('skipped', 0) for s in source_stats.values())
    msg = f"  SCAN COMPLETE: {len(all_errors)} errors across {total_files} files"
    if total_skipped:
        msg += f" ({total_skipped} files unreadable — see skipped_files.csv)"
    print(msg)
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