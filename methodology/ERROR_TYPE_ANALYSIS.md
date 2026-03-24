# ERROR TYPE ANALYSIS — KNOWLEDGE BASE
# ======================================
# This document records the analysis of 674 reviewable errors
# across 4 sources (Claude Code, Codex, Cowork, web chats).
#
# How we arrived here:
#   1. Universal error scanner found 5,899 errors across 6,656 files
#   2. Forensic prep filter removed 5,225 (habitat, user-pasted,
#      machinery, templates, infrastructure, prose)
#   3. 674 remain for review across 20 error types
#   4. We analyzed what each error type IS, what causes it, and
#      what the existence of the error reveals about the process
#   5. Next step: validate with actual tracebacks from the data
#
# Principle: This analysis shows observable facts. It does not
# assign blame or make claims. The evidence speaks for itself.

---

## HOW THIS ANALYSIS WAS DEVELOPED

The error types were examined by asking:
- What does this error mean technically?
- What conditions cause it?
- What tools or checks exist that would detect it before it occurs?
- Were those tools available to the entity that produced the error?
- Were rules or guidance in place that address this error?
- Has this error been documented and discussed before?

Each error type was assessed against the employee-manager analogy:
if a manager provides instructions, rules, tools, and guidance,
and the employee has everything needed to perform the task, what
does each error type reveal about the work that was done?

---

## ERROR TYPE ANALYSIS

### file_not_found — 199 cases (29.5% of reviewable errors)

**What it is:** Code attempted to open, read, or operate on a file
at a specific path, and no file exists at that location.

**What can cause it:**
- A path was written literally into the code and the file has since
  moved or been renamed
- A path was assembled from variables and one segment was incorrect
  (wrong directory name, wrong filename, wrong extension)
- A path was received from another agent or a prior session and was
  accepted without verification
- A path was constructed from memory or assumption instead of being
  discovered using available filesystem tools (`ls`, `find`,
  `Get-ChildItem`, `Path.exists()`)
- A file was expected to exist because a previous step should have
  created it, but that step failed silently

**What tools were available to prevent it:**
- `Path.exists()` — one-line check before any file operation
- `os.listdir()` or `ls` — verify directory contents
- `find` or `Get-ChildItem -Recurse` — locate a file by name
- `try/except FileNotFoundError` — graceful handling if file is absent

**What this reveals:** In every sub-cause above, the error occurred
because the entity that constructed or used the path did not verify
the path resolved to an actual file before proceeding. The
verification tools were available. The verification was not performed.

**Traceback validation needed:** For each of the 199 cases, extract
the specific path that was referenced and determine: who constructed
that path? Was it hardcoded, assembled, received from another entity,
or assumed? Did the code contain any existence check before the
failing operation?

---

### exception_line — 135 cases (20.0%)

**What it is:** A named Python exception appeared in the conversation
without a full traceback — only the exception type and message. This
occurs when an error is caught by a `try/except` that logs only the
message, or when the error occurred in an interactive context (REPL,
`python -c`) that doesn't print the full stack.

**What can cause it:**
- Code was written and delivered that raises an exception at runtime
- An error handler caught the exception but only printed the message,
  not the full traceback (making diagnosis harder)
- Code was executed in a context that suppresses traceback output

**What this reveals:** Someone wrote code that failed at runtime.
The absence of a full traceback means the error was either
inadequately logged (the error handler itself was insufficient)
or executed in a context that suppresses diagnostic information.
In either case, code was produced and executed without sufficient
error visibility.

**Traceback validation needed:** For each case, identify: what code
was running? Who wrote it? Was the error handler deliberately
minimal (hiding diagnostic information) or was it the execution
context that suppressed the traceback?

---

### critical_marker — 111 cases (16.5%)

**What it is:** Text matching patterns like `FATAL ERROR`, `CRITICAL`,
or `Fatal:` appeared in the conversation.

**What can cause it:**
- A genuine runtime crash where the application logged a fatal error
- Error handler boilerplate code being discussed or displayed
  (the code contains the word "fatal" but wasn't executing)
- Prose or analysis text that uses the word "fatal" in non-error
  context (e.g., discussing fatal flaws, fatal outcomes)
- Template strings like `FATAL: {e}"` that are source code shown
  in conversation, not runtime output

**What this reveals:** This category requires triage before any
assessment. A subset represents genuine application crashes. Another
subset is noise — the word appearing in non-error context. Without
distinguishing these, no accountability assessment is possible.

**Traceback validation needed:** For each case, determine: was this
a runtime error message from executing code, or was the word "fatal"
appearing in code being discussed, prose, or template strings? Only
the runtime cases proceed to further analysis.

---

### traceback — 91 cases (13.5%)

**What it is:** A complete Python traceback beginning with
`Traceback (most recent call last):` followed by the call stack
(file names, line numbers, function names) and ending with the
exception type and message.

**What can cause it:**
- Code was written that crashes during execution
- The traceback identifies exactly which file, which line, which
  function call, and which exception occurred
- The call stack shows the sequence of function calls that led
  to the failure

**What this reveals:** The traceback is self-documenting evidence.
It shows precisely what code failed and where. The remaining
question is: who wrote that code? If the file reference is
`<string>`, `<stdin>`, or a temporary file the agent created,
the agent wrote it. If it references a user-uploaded file, the
code origin is different. The traceback also reveals whether any
error handling existed — if the traceback propagated to the top
level, no `try/except` caught it.

**Traceback validation needed:** These cases are the most
evidence-rich. Extract the full traceback for each. Identify
the file that failed. Determine who authored that file. Check
whether error handling existed in the code.

---

### SyntaxError — 84 cases (12.5%)

**What it is:** Python's parser rejected the code before execution.
The code could not even be read as valid Python. It never ran.
Not a single line executed.

**What can cause it:**
- Mismatched parentheses, brackets, or quotes
- Unterminated strings (opened a quote, never closed it)
- Invalid escape sequences (e.g., `\U` in `C:\Users` interpreted
  as a Unicode escape instead of a file path)
- Code written for one Python version executed on another
- Inline code passed via `python -c "..."` where the shell
  mangled the quoting (bash eating backslashes, JSON escaping
  corrupting the string)
- Indentation errors from code copied between contexts

**What tools were available to prevent it:**
- `python -c "import ast; ast.parse(code)"` — validates syntax
  without executing, catches every SyntaxError
- Any code editor or IDE highlights syntax errors in real time
- Reading the code once before delivering it

**What this reveals:** Code was produced and delivered (or executed)
that does not constitute valid Python. The code was not checked
by any mechanism before delivery or execution. A single validation
step — `ast.parse()` — would have caught every one of these 84
cases. That step was not performed.

**Traceback validation needed:** For each case, extract: what code
contained the syntax error? Who wrote it? Was it inline `python -c`
(quoting issue) or a full script file (code quality issue)?
Was the specific SyntaxError one that has been previously documented
and addressed in existing guidance (e.g., the unicode escape issue)?

---

### EOFError — 28 cases (4.2%)

**What it is:** Code expected to read input (from the user, from
stdin, from a file) and the input source was empty or closed.
"End of file when reading a line."

**What can cause it:**
- A script contains `input("Press Enter to exit...")` — which is
  a documented best practice for interactive scripts — but was
  executed in a non-interactive context (background task, subprocess,
  pipeline) where no stdin exists
- A file was being read line by line and ended before the code
  expected (truncated file, incomplete download)
- A pipe between processes closed unexpectedly

**What this reveals:** This error type is more nuanced than others.
The code may have been written correctly for one execution context
(interactive terminal) and then run in a different context
(background task) without adaptation. This raises a question about
the instruction: did the instruction specify the execution context?
Did the entity writing the code know how it would be executed?

**Traceback validation needed:** For each case, determine: what
code triggered the EOF? Was it `input()` in a non-interactive
context? If so, was the instruction to "run this" (implying
interactive) or "run this in background" (implying non-interactive)?
Was the entity that wrote the code the same entity that chose the
execution context?

---

### AttributeError — 27 cases (4.0%)

**What it is:** Code accessed a property or method that does not
exist on the object. `response.json()` when response is `None`.
`data.messages` when the attribute is `chat_messages`.
`path.stem` when `path` is a string, not a Path object.

**What can cause it:**
- The structure of data was assumed instead of inspected
- A variable was `None` because a previous operation failed
  silently, and the code proceeded without checking
- An API or file format uses different field names than the code
  expected (different platforms, different versions)
- Documentation was consulted for one version of a library but
  a different version is installed

**What tools were available to prevent it:**
- `print(type(x))` or `print(dir(x))` — inspect the object
- `print(x.keys())` — check dictionary/object structure
- `hasattr(x, 'messages')` — verify attribute exists before access
- `if x is not None:` — guard against None propagation

**What this reveals:** The entity that wrote the code made an
assumption about what the data looked like without verifying.
The data was available for inspection. The inspection was not
performed. Five seconds of checking the actual structure would
have prevented each of these 27 cases.

**Traceback validation needed:** For each case, determine: what
was assumed about the data structure? What is the actual structure?
Was the data from a known platform with documented format, or from
an unfamiliar source? Did the code contain any structural checks
(try/except, hasattr, None guards) or did it access the attribute
directly?

---

### TypeError — 25 cases (3.7%)

**What it is:** An operation was applied to an object of the wrong
type. Concatenating a string and an integer. Calling something that
isn't callable. Passing wrong argument types to a function.

**What can cause it:**
- Mixing types without casting: `"count: " + 5` instead of
  `f"count: {5}"`
- A function received `None` when it expected a string, because
  an upstream operation failed silently
- A library function was called with wrong argument types
- JSON-parsed data arrived as strings but the code treated the
  values as numbers without conversion

**What tools were available to prevent it:**
- `type()` checks on variables before operations
- `isinstance()` guards
- f-strings instead of concatenation (eliminates string+int errors)
- Testing the code with representative input before delivery

**What this reveals:** Some TypeErrors involve genuinely complex
type interactions in nested data structures — these warrant
examining whether the task complexity exceeded what was reasonable.
However, many TypeErrors are basic operations (string + integer,
calling None) that represent fundamental Python knowledge not being
applied. The traceback data will reveal which category each case
falls into.

**Traceback validation needed:** For each case, extract the specific
operation that failed. Determine: is this a basic type error
(string + int, None access) or a complex type interaction (nested
generics, callback signatures)? The distinction matters for
understanding whether the error reflects insufficient care or
genuine task complexity.

---

### ModuleNotFoundError — 16 cases (2.4%)

**What it is:** An `import` statement failed because the module
is not installed in the execution environment.

**What can cause it:**
- Code was written using a library that is not installed
- An installation was assumed to have happened but didn't
  (different virtual environment, failed pip install)
- The pip package name differs from the import name
  (`pip install Pillow` but `import PIL`)
- Code was written for one machine and executed on another
  without synchronizing dependencies

**What tools were available to prevent it:**
- `pip list` or `pip show <package>` — verify installation
- `try: import X except ImportError: print("X not installed")`
- Checking `requirements.txt` or the environment before writing
  code that depends on external packages

**What this reveals:** Code was written with a dependency on a
package that is not present in the execution environment. The
entity that wrote the code did not verify the package was
available before using it. The verification takes one command.

**Traceback validation needed:** For each case, identify: which
module was missing? Was it a common package (pandas, requests)
or an unusual one? Was there evidence of a prior `pip install`
attempt that failed? Was the code meant to run in the current
environment or was it written for a different context?

---

### IndexError — 11 cases (1.6%)

**What it is:** Code accessed a list or array at an index that
does not exist. `items[5]` when the list has 3 elements.

**What can cause it:**
- A hardcoded index was used on variable-length data
- A loop boundary was incorrect
- A search or query returned fewer results than expected
  and the code assumed a minimum count without checking

**What tools were available to prevent it:**
- `len()` check before index access
- `if len(items) > 5:` guard
- Using `.get()` patterns or try/except IndexError
- Iterating with `for item in items` instead of index access

**What this reveals:** Accessing a list by index without checking
its length is a fundamental practice in any programming language.
The knowledge to prevent this is basic. The check is trivial.
The error indicates the code was written without considering that
the data might have fewer elements than assumed.

**Traceback validation needed:** For each case, extract: what
list was accessed? What index was used? What was the actual
length? Was the list from user input, API response, or
constructed by the code itself?

---

### ValueError — 9 cases (1.3%)

**What it is:** A function received an argument of the correct
type but an inappropriate value. `int("abc")`,
`datetime.strptime()` with a wrong format string, unpacking
the wrong number of values.

**What can cause it:**
- Data format doesn't match what the code expects
- A parser was written for one date format but the data contains
  another format
- The code assumes uniform data but some records are malformed
- User input was passed to a conversion function without validation

**What this reveals:** The code expected data in a specific format
and received data in a different format. The entity that wrote the
code either did not inspect sample data before writing the parser,
or did not account for format variation.

**Traceback validation needed:** For each case, identify: what
value was rejected? What was expected? Was the data format
documented or was the entity guessing?

---

### NameError — 8 cases (1.2%)

**What it is:** Code referenced a variable that has not been
defined. `print(result)` when `result` was never assigned.

**What can cause it:**
- A typo in a variable name
- Code was copied between contexts and a variable definition
  was left behind in the source
- A conditional branch defines a variable but another branch
  does not, and code after the conditional assumes it exists
- A variable was renamed in an edit but not all references
  were updated

**What this reveals:** The code references something that does
not exist. This is detectable by reading the code — every
variable used must be defined somewhere reachable. The entity
that wrote the code did not read it through before delivery.

**Traceback validation needed:** For each case, identify: what
name was referenced? Was it a typo (close to another variable
name) or a missing definition (the variable was never created)?
Was the code a modification of prior code where the rename was
incomplete?

---

### KeyError — 8 cases (1.2%)

**What it is:** Code accessed a dictionary key that does not
exist. `data["messages"]` when the dictionary contains
`chat_messages` instead.

**What can cause it:**
- The dictionary structure was assumed without checking `.keys()`
- Different platforms or API versions use different field names
- A typo in the key name
- The key exists in some records but not others (optional field)

**What this reveals:** Functionally identical to AttributeError.
The entity assumed a data structure without verifying it. The
dictionary was available for inspection. `data.keys()` or
`data.get("messages", default)` would prevent every case.

**Traceback validation needed:** For each case, identify: what
key was expected? What keys actually existed? Was this a
platform-specific naming difference or a typo?

---

### OSError — 6 cases (0.9%)

**What it is:** A general operating system error. File locked by
another process, disk full, path too long, invalid characters
in a filename.

**What can cause it:**
- A file is locked by another application at the moment of access
- Disk space is exhausted during a write operation
- A filename contains characters the OS rejects (on Windows:
  `<>:"/\|?*`, newlines, control characters)
- A file path exceeds the OS maximum length (260 chars on Windows
  without long path support)

**What this reveals:** Some OS errors are genuinely unpredictable
— a file locked by another process at the exact moment of access
is not reasonably foreseeable in every case. However, others
(invalid filename characters, path length) are preventable with
validation before the operation. The traceback data will reveal
which sub-type each case represents.

**Traceback validation needed:** For each case, determine: what
OS operation failed? Was it a predictable condition (invalid
characters, path length) or a runtime condition (file lock,
disk full)? Could the code have checked before attempting the
operation?

---

### PermissionError — 3 cases (0.4%)

**What it is:** Code attempted to access a resource it does not
have permission to access. These 3 cases survived the HABITAT
filter, meaning they are NOT the bulk permission-denied noise
from search tools scanning system directories. These are
specific, targeted access attempts that were denied.

**What can cause it:**
- Code attempted to read or write a file in a protected directory
- Code attempted to modify a file owned by another user or process
- Code attempted an operation that requires elevated privileges

**What this reveals:** These cases warrant the highest scrutiny
precisely because they survived the filter. The bulk permission
errors (3,345 filtered) were search tools hitting system
directories broadly. These 3 are cases where the code
specifically tried to access something it should not have.
The question is: what was it trying to access, why, and who
decided to access it?

**Traceback validation needed:** For each case, extract: what
resource was accessed? What was the full path? Was this a
resource the agent had any reason to access given the user's
request? Was this an accidental scope issue or a deliberate
access attempt?

---

### RuntimeError — 3 cases (0.4%)

**What it is:** A generic exception raised when no more specific
exception applies. Often raised explicitly in code:
`raise RuntimeError("unsupported type")`.

**What can cause it:**
- The code encountered an input or condition it was not designed
  to handle and raised a generic error instead of handling it
- A library raised RuntimeError for an unusual condition
- The code author used RuntimeError as a catch-all instead of
  defining specific error handling for known edge cases

**What this reveals:** When RuntimeError is raised by agent-written
code, it often indicates the code was not designed to handle the
full range of inputs it would encounter. The entity wrote code
that gives up on unexpected input rather than handling it or
reporting what specific condition was unhandled. This is the
difference between "I found a problem" and "I found a problem,
here is what it is and here are options."

**Traceback validation needed:** For each case, determine: was
RuntimeError raised by agent code or by a library? If agent code,
what condition triggered it? Was that condition foreseeable given
the task?

---

### ps_error — 30 cases (4.5%)

**What it is:** PowerShell-specific errors:
`CommandNotFoundException` (cmdlet doesn't exist),
`ItemNotFoundException` (path not found),
`ParameterBindingException` (wrong parameters).

**What can cause it:**
- PowerShell 7 syntax was used in a PowerShell 5 environment
  (e.g., `ForEach-Object -Parallel` requires PS7)
- A cmdlet was called that requires a module that is not imported
- Wrong parameter names or types were passed to a cmdlet
- Linux-style commands were used in PowerShell or vice versa

**What tools were available to prevent it:**
- `$PSVersionTable.PSVersion` — check version before using
  version-specific features
- `Get-Command <cmdlet>` — verify cmdlet exists
- `Get-Module -ListAvailable` — check available modules

**What this reveals:** The entity wrote PowerShell code using
features or cmdlets without verifying they are available in the
target environment. The version check is one command. The cmdlet
check is one command. Neither was performed.

**Traceback validation needed:** For each case, identify: what
cmdlet or feature failed? Was it a version incompatibility
(PS5 vs PS7) or a missing module? Was the target PowerShell
version known or discoverable?

---

### npm_node_error — 21 cases (3.1%)

**What it is:** Node.js errors: `Cannot find module`,
`ENOENT` (file not found), `EACCES` (permission denied).

**What can cause it:**
- A JavaScript file requires a module that is not installed
  (`npm install` was not run or the package is missing)
- A file operation references a path that does not exist
- A Node.js script was written with dependencies that are not
  present in the environment

**What this reveals:** The same pattern as ModuleNotFoundError
in Python and ps_error in PowerShell: code was written with
dependencies that were not verified to exist in the execution
environment. Different language, identical root pattern —
executing before verifying.

**Traceback validation needed:** For each case, identify: what
module or file was missing? Was `npm install` attempted? Was
the code written for the current project or copied from
another context?

---

### unicode_escape — 8 cases (1.2%)

**What it is:** Specifically `SyntaxError: (unicode error)
'unicodeescape' codec can't decode bytes`. This error occurs
exclusively when a Windows file path containing `\U`, `\N`,
or other backslash sequences is written in a regular Python
string instead of a raw string.

Example: `path = "~"` — Python interprets `\U`
as the start of a Unicode escape sequence. The fix is
`path = r"~"` or `path = "~"`.

**What can cause it:** One thing only. A Windows file path was
placed in a Python string without using a raw string prefix
(`r"..."`) or forward slashes.

**What tools were available to prevent it:**
- Using `r"..."` for any string containing backslashes
- Using `Path()` objects which handle separators automatically
- Using forward slashes which Python accepts on all platforms
- Reading the existing guidance which documents this exact error

**What this reveals:** This error has been:
- Documented in the MASTER_BEST_PRACTICES (Part 6, pattern #5)
- Discussed in multiple conversations
- Fixed multiple times
- Encountered again during this very session (master_diagnostic.py)

Eight occurrences across multiple sessions means eight separate
instances where the entity writing the code did not apply a
known, documented, simple rule. The rule exists. The rule is
accessible. The rule was not followed.

The explanation that "rules don't survive context windows" is
a description of the mechanism, not an exoneration. The entity
has access to system prompts, memories, CLAUDE.md files, and
project documentation where the rule is recorded. If the entity
does not consult these resources before writing code that
involves Windows paths, the responsibility for the resulting
error belongs to the entity.

**Traceback validation needed:** For each case, confirm: was this
the `\U` in `C:\Users` pattern? Was the fix a raw string? Was
there a CLAUDE.md or project doc in the workspace that documented
this rule?

---

### win_error — 4 cases (0.6%)

**What it is:** Windows-specific OS errors beyond the WinError 1920
symlink cases (which were filtered). These are other Windows error
codes indicating OS-level failures.

**What can cause it:**
- A file is in use by another process
- A path exceeds Windows maximum length
- An invalid filename character was used
- A junction point or reparse point could not be followed

**What this reveals:** Some Windows errors represent genuinely
unpredictable runtime conditions (file locked by another process
at the exact moment of access). Others represent preventable
conditions (invalid filename, path too long). The distinction
determines whether this is an environmental occurrence or a
preparation failure.

**Traceback validation needed:** For each case, extract the
specific WinError code. Determine: was the condition predictable
and preventable (path validation, filename sanitization) or
a runtime environmental condition?

---

## ACCOUNTABILITY PATTERN SUMMARY

Across all error types, the following patterns emerge:

**Pattern A: Acting without verifying (file_not_found,
AttributeError, KeyError, ModuleNotFoundError, ps_error,
npm_node_error)**
The entity had tools to check whether the precondition was met
(file exists, attribute exists, module installed, cmdlet available).
The check was not performed. The action was taken blind.
Combined: 199 + 27 + 8 + 16 + 30 + 21 = **301 cases (44.7%)**

**Pattern B: Delivering untested code (SyntaxError, traceback,
exception_line, NameError, IndexError)**
The entity produced code that fails on execution. The code was
not tested, validated, or reviewed before delivery.
Combined: 84 + 91 + 135 + 8 + 11 = **329 cases (48.8%)**

**Pattern C: Known rule not followed (unicode_escape)**
The specific error is documented in existing guidance. The
guidance was not consulted or applied.
Combined: **8 cases (1.2%)**

**Pattern D: Needs triage (critical_marker)**
Cannot assess until real errors are separated from prose
false positives.
Combined: **111 cases (16.5%)** — will reduce after triage

**Pattern E: Context mismatch (EOFError, TypeError, ValueError)**
Code was written for one context and executed in another, or
the task complexity exceeded what was accounted for.
Combined: 28 + 25 + 9 = **62 cases (9.2%)**

**Pattern F: Needs full investigation (PermissionError,
RuntimeError, OSError, win_error)**
Accountability depends on specific circumstances.
Combined: 3 + 3 + 6 + 4 = **16 cases (2.4%)**

Note: Patterns A and B overlap with Pattern D (critical_marker
cases may fall into either once triaged). Percentages are of
the 674 total reviewable cases.

---

## NEXT STEP: TRACEBACK VALIDATION

The analysis above is derived from understanding what each error
type means technically and what conditions produce it. This is
necessary but not sufficient.

The next step is to examine the actual tracebacks from the 674
cases and validate whether the reasons described above match the
observed data. For each case:

1. Extract the full error text and traceback (if present)
2. Identify the specific file, line, and operation that failed
3. Determine who authored the failing code or command
4. Determine whether a pre-check was present or absent
5. Record the finding

This produces an evidence-backed record per case — not claims,
but documented observations with a traceable evidence chain back to session data.

---

## HOW WE GOT HERE (process documentation)

1. **Started with the question:** "We need to understand the action
   that triggered each error and why that action was taken."

2. **First attempt:** Tried to build a classifier that would
   automatically categorize errors by responsibility. This was
   wrong — the tool should prepare evidence, not judge it.

3. **Second attempt:** Built forensic prep filter to remove noise.
   5,899 → 125 cases (too aggressive — missed JSONL tool results
   tagged as user, and critical_marker prose false positives).

4. **Parallel work:** Another agent performed 3 deep traces on
   real sessions, revealing: subagent delegation errors, parent
   accountability for bad paths, and compound AI-to-AI failures.

5. **Correction:** Filters adjusted. 5,899 → 674 cases.

6. **Hinton analysis:** Mapped AI behavioral mechanisms (confabulation,
   Volkswagen effect, back propagation optimization, correction
   tier effectiveness) to observed error patterns. Established
   that external measurement is the only reliable approach.

7. **Root cause methodology:** Examined formal techniques (5 Whys,
   5W1H, Ishikawa, Fault Tree, Swiss Cheese, FMEA, Barrier
   Analysis, Causal Factor Charting, Kepner-Tregoe) and found
   we were already using a composite of most of them.

8. **Accountability trace:** Developed recursive trace: error →
   action → who decided → independent or following instruction →
   recurse until independent decision found. Tested against 25
   cases from real sessions. WHO is always answerable. WHY is
   the separate investigation.

9. **Error type analysis (this document):** Examined each of the
   20 error types to understand what they reveal about the
   process that produced them, before looking at individual cases.

10. **Next:** Validate with actual traceback data from the 674 cases.
