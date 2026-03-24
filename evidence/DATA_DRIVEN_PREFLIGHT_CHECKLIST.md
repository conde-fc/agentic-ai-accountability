# DATA-DRIVEN PRE-FLIGHT CHECKLIST
# ==================================
# Every rule in this document was derived from actual errors
# found in 1,653 reviewable cases across Claude Code, Codex,
# Cowork, and web chat sessions.
#
# The number in brackets is how many times this specific
# failure occurred in the data. This is not theory.
# This is what happened.
#
# MANDATORY: Read the relevant section BEFORE writing code
# that involves that operation.

---

## BEFORE ACCESSING ANY FILE OR PATH [450+ errors]

The #1 error across all sources. 341 cases of file/path
operations without existence checks, plus 109 shell commands
on nonexistent paths, plus 35 open()/read on missing files.

```python
# BEFORE opening, reading, writing, or referencing ANY path:
from pathlib import Path

path = Path(your_path)

# CHECK 1: Does it exist?
if not path.exists():
    print(f"ERROR: {path} does not exist")
    # Handle: raise, return, create, or ask user
    
# CHECK 2: Is it the type you expect?
if not path.is_file():   # or .is_dir() for directories
    print(f"ERROR: {path} exists but is not a file")

# CHECK 3: Can you access it? (wrap in try for symlinks)
try:
    stat = path.stat()
except OSError as e:
    print(f"ERROR: Cannot access {path}: {e}")
```

**Shell commands too:**
```bash
# BEFORE running du, ls, stat, grep on a path:
test -e "$path" || echo "ERROR: $path does not exist"
```

**Why this matters:** 450 errors — 27% of all reviewable
errors — would have been prevented by a single `path.exists()`
check.

---

## BEFORE USING input() [209 errors]

The #2 error. `input("Press Enter to exit...")` is in the
best practices as a REQUIRED feature for interactive scripts.
But 209 times it was used in non-interactive contexts where
stdin doesn't exist.

```python
# BEFORE using input():
import sys

# CHECK: Is this running interactively?
if sys.stdin.isatty():
    input("Press Enter to exit...")
else:
    # Non-interactive: log instead of blocking
    print("Script complete.")
```

**Or make it safe universally:**
```python
try:
    input("Press Enter to exit...")
except EOFError:
    pass  # Non-interactive context, just continue
```

**The rule update:** The best practice should say:
"Add `input('Press Enter...')` for interactive scripts,
WRAPPED in `try/except EOFError` or guarded by
`sys.stdin.isatty()`."

---

## BEFORE DELIVERING ANY CODE [98 errors]

98 cases of code with syntax errors that never parsed. The
code was delivered or executed without being validated first.

```python
# BEFORE delivering or executing ANY generated code:
import ast

code_string = """your generated code here"""

try:
    ast.parse(code_string)
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
    # DO NOT deliver or execute. Fix first.
```

**For scripts written to files:**
```python
# After writing a .py file, validate it:
import subprocess
result = subprocess.run(
    ["python", "-c", f"import ast; ast.parse(open('{script_path}').read())"],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"SYNTAX ERROR in {script_path}: {result.stderr}")
```

**Why this matters:** 98 scripts couldn't even parse. Not a
runtime bug — the code wasn't valid Python. One check catches
all of them.

---

## BEFORE USING WINDOWS PATHS IN PYTHON [54 errors]

31 unicode escape errors + 23 additional syntax errors from
unescaped backslashes. All from the same cause: `\U` in
`C:\Users` interpreted as Unicode.

```python
# NEVER do this:
path = "~\Downloads"      # \U = unicode escape

# ALWAYS do one of these:
path = r"~\Downloads"      # raw string
path = "~/Downloads"       # forward slashes
path = Path.home() / "Downloads"        # Path object (best)
```

**Why this matters:** This exact error has been documented,
discussed, fixed, and re-occurred 54 times across multiple
sessions. The rule exists. The fix is trivial. The error
keeps happening.

---

## BEFORE IMPORTING ANY MODULE [100+ errors]

36 `require('docx')`, 16 `require('pptxgenjs')`, 12 each
for `curl_cffi`, `youtube_transcript_api`, `fitz`. Plus 31
unspecified module-not-found errors.

```python
# BEFORE writing code that imports a non-standard module:

# CHECK: Is it installed?
import importlib
def check_module(name):
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        print(f"ERROR: {name} not installed. Run: pip install {name}")
        return False

# Use before depending on it:
if not check_module("fitz"):
    sys.exit(1)
```

**For Node.js:**
```javascript
// BEFORE require():
try {
    require.resolve('docx');
} catch(e) {
    console.error('docx not installed. Run: npm install docx');
    process.exit(1);
}
```

**Common pip vs import name mismatches (from our data):**
```
pip install PyMuPDF        → import fitz
pip install Pillow         → import PIL
pip install python-docx    → import docx
pip install pptxgenjs      → (Node.js, not Python)
```

---

## BEFORE ACCESSING OBJECT ATTRIBUTES [78 errors]

54 AttributeError (accessing attributes on wrong type) +
24 AttributeError on NoneType (upstream failure unchecked).

```python
# BEFORE accessing .attribute on anything:

# CHECK 1: Is it None?
if result is None:
    print("ERROR: Previous operation returned None")
    return  # or handle

# CHECK 2: Does it have the attribute?
if not hasattr(result, 'get'):
    print(f"ERROR: Expected dict-like, got {type(result)}")
    return

# CHECK 3: For dictionaries, use .get() with default:
value = data.get("messages", [])  # NOT data["messages"]
```

**The NoneType pattern specifically:**
```python
# This fails silently then crashes later:
result = some_function()       # returns None on failure
result.process()               # AttributeError: NoneType

# This catches it at the source:
result = some_function()
if result is None:
    raise ValueError("some_function returned None — check inputs")
result.process()
```

---

## BEFORE USING datetime OPERATIONS [27 errors]

27 cases of `TypeError: can't subtract offset-naive and
offset-aware datetimes`. All from mixing timezone-aware and
timezone-naive datetime objects.

```python
# BEFORE any datetime comparison or arithmetic:
from datetime import datetime, timezone

# Make EVERYTHING timezone-aware:
now = datetime.now(timezone.utc)      # NOT datetime.now()

# When parsing timestamps:
dt = datetime.fromisoformat(timestamp)
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)  # assume UTC if naive
```

---

## BEFORE ACCESSING LIST/ARRAY BY INDEX [20 errors]

20 cases of `IndexError: list index out of range`.

```python
# BEFORE items[N]:
if len(items) > N:
    value = items[N]
else:
    print(f"ERROR: Expected {N+1}+ items, got {len(items)}")
    value = default_value

# OR use safe pattern:
value = items[N] if len(items) > N else default_value
```

---

## BEFORE ACCESSING DICTIONARY KEYS [14 errors]

14 cases of `KeyError` from `data["key"]` when key doesn't exist.

```python
# NEVER do:
value = data["messages"]        # KeyError if missing

# ALWAYS do:
value = data.get("messages")    # Returns None if missing
value = data.get("messages", [])  # Returns default if missing

# OR check first:
if "messages" in data:
    value = data["messages"]
```

**When you don't know the keys (different platforms):**
```python
# FIRST, inspect:
print(f"Available keys: {list(data.keys())}")
# THEN access the right one
```

---

## BEFORE REFERENCING ANY VARIABLE [16 errors]

16 NameError cases — variable used but never defined.

```python
# BEFORE delivering code, search for every variable used:
# - Is it defined in this scope?
# - Is it imported?
# - Is it a parameter?
# If you can't find the definition, it will crash.

# Common cause: renaming a variable but missing some references
# BEFORE: result = process(data)
# AFTER:  output = process(data)
#         print(result)  ← NameError: result no longer exists
```

---

## BEFORE RUNNING POWERSHELL COMMANDS [63 errors]

32 CommandNotFoundException + 31 environment verification failures.

```powershell
# BEFORE using any cmdlet:
if (Get-Command "your-cmdlet" -ErrorAction SilentlyContinue) {
    your-cmdlet parameters
} else {
    Write-Host "ERROR: your-cmdlet not available"
}

# BEFORE using PS7 features:
if ($PSVersionTable.PSVersion.Major -ge 7) {
    ForEach-Object -Parallel { ... }
} else {
    Write-Host "ERROR: Requires PowerShell 7+"
}

# BEFORE using external tools:
@('rg', 'sqlite3', 'pandoc', 'node') | ForEach-Object {
    if (-not (Get-Command $_ -ErrorAction SilentlyContinue)) {
        Write-Host "WARNING: $_ not found in PATH"
    }
}
```

---

## BEFORE RUNNING NODE.JS CODE [55 errors]

36 `Cannot find module 'docx'` + 16 `pptxgenjs` + others.

```javascript
// BEFORE any require():
const requiredModules = ['docx', 'pptxgenjs', 'image-size'];
for (const mod of requiredModules) {
    try {
        require.resolve(mod);
    } catch(e) {
        console.error(`Missing: npm install ${mod}`);
        process.exit(1);
    }
}
```

---

## BEFORE HANDLING PERMISSIONS [18 errors]

18 cases where access was attempted without checking permissions.

```python
# BEFORE accessing potentially restricted paths:
import os

if not os.access(path, os.R_OK):
    print(f"ERROR: No read permission for {path}")
    return

if not os.access(path, os.W_OK):
    print(f"ERROR: No write permission for {path}")
    return
```

---

## SUMMARY TABLE — DATA-DRIVEN

| Operation | Error Count | Prevention Check | Effort |
|---|---|---|---|
| File/path access | 450+ | `Path.exists()` | 1 line |
| `input()` | 209 | `sys.stdin.isatty()` or `try/except EOFError` | 2 lines |
| Code delivery | 98 | `ast.parse()` | 3 lines |
| Windows paths | 54 | `r"..."` or `Path()` | 0 extra lines |
| Module import | 100+ | `importlib.import_module()` check | 4 lines |
| Attribute access | 78 | `None` check + `hasattr()` | 2 lines |
| PowerShell commands | 63 | `Get-Command` check | 2 lines |
| Node.js modules | 55 | `require.resolve()` | 3 lines |
| datetime operations | 27 | Always use `timezone.utc` | 1 line |
| List index access | 20 | `len()` check | 1 line |
| Permission access | 18 | `os.access()` | 1 line |
| Variable reference | 16 | Read code before delivery | 0 lines |
| Dict key access | 14 | `.get()` instead of `[]` | 0 extra lines |

**Total preventable with these checks: ~1,200+ of 1,653
reviewable errors (72%+)**

---

## HOW TO USE THIS DOCUMENT

1. **For CLAUDE.md / AGENTS.md:** Include the relevant sections
   based on what the agent's tasks involve. File operations?
   Include the file/path section. Code generation? Include the
   code delivery and syntax validation sections.

2. **For code review:** Before delivering any script, check it
   against the summary table. Does it access files? Is there a
   `Path.exists()` check? Does it use `input()`? Is it guarded?

3. **For the preprocessing engine:** These checks can become
   deterministic detectors. Scan agent-written code for:
   - `open(` without preceding `exists()` check
   - `input(` without `isatty()` or `try/except EOFError`
   - String literals containing `C:\U` or `C:\N` (not raw)
   - `data["key"]` without `.get()` or `if key in`
   - `items[N]` without `len()` check

4. **For the feedback loop:** As new errors are found and
   analyzed, add the prevention check to this document. The
   checklist grows with the data. Every error that repeats
   after the rule exists escalates from CONCERNING to ALARMING.
