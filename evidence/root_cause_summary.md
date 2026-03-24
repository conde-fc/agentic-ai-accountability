# ERROR ROOT CAUSE SUMMARY
Generated: 2026-03-24T00:39:16
Total reviewable errors: 1653

## CONCERN LEVEL DISTRIBUTION

- **ALARMING**: 153 (9.3%)
- **CONCERNING**: 1110 (67.2%)
- **NOT_CONCERNING**: 26 (1.6%)
- **NEEDS_TRIAGE**: 364 (22.0%)

## ROOT CAUSES BY ERROR TYPE (from actual data)

Each row shows: error type, count, top actual triggers found
in the traceback/snippet data, and what check was absent.

### exception_line — 366 cases

Concern: CONCERNING: 274, ALARMING: 85, NOT_CONCERNING: 7

Top triggers from data:
- [100x] EOFError: EOF when reading a line
- [17x] SyntaxError: unexpected character after line continuation character
- [10x] IndexError: list index out of range
- [10x] SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UX
- [10x] TypeError: can't subtract offset-naive and offset-aware datetimes

What was absent:
- [100x] Input source availability check (execution context verification)
- [85x] Syntax validation (ast.parse) before execution
- [38x] Object structure inspection (type, dir, hasattr)

Source: claude_code: 336, cowork: 22, codex: 6, chats_manager: 2

---

### critical_marker — 364 cases

Concern: NEEDS_TRIAGE: 364

Top triggers from data:
- [39x] Fatal: {str(e)[:50]}")
- [16x] FATAL: EVERGREEN_HOME not set"); input("Press Enter..."); sys.exit(1)
- [16x] FATAL: {DB} not found"); input("Press Enter..."); sys.exit(1)
- [14x] FATAL: {input_path} not found. Run ev_data.py first.")
- [13x] FATAL: {DB} not found")

What was absent:
- [364x] Needs triage — may be prose, template, or real error

Source: claude_code: 192, chats_manager: 158, codex: 8, cowork: 6

---

### file_not_found — 357 cases

Concern: CONCERNING: 357

Top triggers from data:
- [62x] Path not found: du: ca
- [48x] No such file or directory: 'C:
- [23x] Path not found: ls: ca
- [20x] Path not found: /sessio
- [20x] Path not found: grep: VERSIO

What was absent:
- [357x] Path existence check before access (Path.exists, ls, find)

Source: claude_code: 274, cowork: 82, codex: 1

---

### traceback — 298 cases

Concern: CONCERNING: 286, NOT_CONCERNING: 11, ALARMING: 1

Top triggers from data:
- [109x] EOFError: EOF when reading a line
- [12x] TypeError: can't subtract offset-naive and offset-aware datetimes
- [8x] IndexError: list index out of range
- [8x] AttributeError: 'list' object has no attribute 'get'
- [7x] AttributeError: 'NoneType' object has no attribute 'get'

What was absent:
- [106x] Input source availability check (execution context verification)
- [40x] Object structure inspection (type, dir, hasattr)
- [40x] Path existence check (Path.exists)

Source: claude_code: 281, cowork: 14, codex: 3

---

### errno — 75 cases

Concern: CONCERNING: 75

Top triggers from data:
- [14x] [Errno 2] No such file or directory
- [8x] [Errno 13] Permission denied: '~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 
- [4x] [Errno 2] No such file or directory: 'C:\\\\Users\\\\[user]\\\\Downloads\\\\FRAMEWORK\\\\_ARCHIVE\\\\
- [4x] [Errno 2] No such file or directory: '~/Downloads/anthropic_system_prompts_all_versions
- [4x] [Errno 2] No such file or directory: '~/Downloads/FRAMEWORK/08_CHATS/CHATGPT/02_EXTRACT

What was absent:
- [75x] OS condition verification before operation

Source: claude_code: 65, cowork: 10

---

### ps_error — 63 cases

Concern: CONCERNING: 63

Top triggers from data:
- [18x] Error: Cannot find module 'docx'
- [14x] Where : The term 'extglob.FileSystemLabel' is not recognized as the name of a cmdlet, function, scri
- [8x] Error: Cannot find module 'pptxgenjs'
- [5x] sqlite3: The term 'sqlite3' is not recognized as a name of a cmdlet, function, script file, or execu
- [4x] pandoc : The term 'pandoc' is not recognized as the name of a cmdlet, function, script file, or oper

What was absent:
- [32x] PowerShell environment verification
- [31x] Cmdlet/command availability check (Get-Command)

Source: claude_code: 45, cowork: 16, codex: 2

---

### npm_node_error — 55 cases

Concern: CONCERNING: 55

Top triggers from data:
- [24x] MODULE_NOT_FOUND',
- [18x] Error: Cannot find module 'docx'
- [8x] Error: Cannot find module 'pptxgenjs'
- [2x] Error: Cannot find module 'image-size'
- [2x] MODULE_NOT_FOUND\",t}return r[e]}i.keys=function(){return Object.keys(r)},i.resolve=s,e.exports=i,i.

What was absent:
- [28x] Module installation check (npm list)
- [27x] Node environment verification

Source: cowork: 28, claude_code: 26, codex: 1

---

### syntax_error_detail — 44 cases

Concern: ALARMING: 44

Top triggers from data:
- [5x] SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: truncated \UX
- [2x] SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 188-189: truncated
- [2x] SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 200-201: truncated
- [2x] SyntaxError: unexpected character after line continuation character toolu_018rfKzfBCbrrL4mAQhUQmzc E
- [2x] SyntaxError: no binding for nonlocal 'current_char' found toolu_019rkNGeKJ83MiaHPsTqvo3t Error: Exit

What was absent:
- [44x] Code syntax validation before execution (ast.parse)

Source: claude_code: 37, cowork: 4, codex: 3

---

### unicode_escape — 23 cases

Concern: ALARMING: 23

Top triggers from data:
- [23x] Windows path in regular string (\U interpreted as unicode escape)

What was absent:
- [23x] Raw string prefix (r"...") — documented rule not followed

Source: claude_code: 21, codex: 2

---

### win_error — 8 cases

Concern: NOT_CONCERNING: 8

Top triggers from data:
- [2x] [WinError 32] The process cannot access the file because it is being used by another process: 'C:\\U
- [2x] [WinError 3] The system cannot find the path specified: '~\\Downloads\\FRAMEWORK\\08_
- [2x] [WinError 267] The directory name is invalid: '~\\Downloads\\FRAMEWORK\\08_CHATS\\CLA
- [2x] [WinError 17] The system cannot move the file to a different disk drive: '~\\Download

What was absent:
- [8x] OS condition check before operation

Source: claude_code: 8

---

## SIMPLIFIED EVIDENCE TABLE

| Error Type | Count | Primary Root Cause | What Was Absent | Concern |
|---|---|---|---|---|
| exception_line | 366 | EOFError: EOF when reading a line | Input source availability check (execution context | CONCERNING |
| critical_marker | 364 | Fatal: {str(e)[:50]}") | Needs triage — may be prose, template, or real err | NEEDS_TRIAGE |
| file_not_found | 357 | Path not found: du: ca | Path existence check before access (Path.exists, l | CONCERNING |
| traceback | 298 | EOFError: EOF when reading a line | Input source availability check (execution context | CONCERNING |
| errno | 75 | [Errno 2] No such file or directory | OS condition verification before operation | CONCERNING |
| ps_error | 63 | Error: Cannot find module 'docx' | PowerShell environment verification | CONCERNING |
| npm_node_error | 55 | MODULE_NOT_FOUND', | Module installation check (npm list) | CONCERNING |
| syntax_error_detail | 44 | SyntaxError: (unicode error) 'unicodeescape' codec can't dec | Code syntax validation before execution (ast.parse | ALARMING |
| unicode_escape | 23 | Windows path in regular string (\U interpreted as unicode es | Raw string prefix (r"...") — documented rule not f | ALARMING |
| win_error | 8 | [WinError 32] The process cannot access the file because it  | OS condition check before operation | NOT_CONCERNING |

---

## WHAT THIS TABLE SHOWS

Each row is derived from the actual error data — the
traceback text, the exception message, the file reference.
The 'Primary Root Cause' is the most common trigger found
in the real snippets. The 'What Was Absent' is the check
that, if present, would have prevented the error.

This is not a claim of accountability. It is a record of
what the data shows: what failed, what was missing, and
how concerning the pattern is based on whether it was
preventable with available tools and documented guidance.

ALARMING = documented rule exists and was not followed,
  or code was so broken it could not parse
CONCERNING = preventable with a basic check that was available
  but not performed
NOT_CONCERNING = may be environmental or unpredictable
NEEDS_TRIAGE = cannot assess until real errors separated
  from false positives