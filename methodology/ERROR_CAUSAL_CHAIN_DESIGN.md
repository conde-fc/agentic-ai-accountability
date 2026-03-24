# ERROR CAUSAL CHAIN ANALYSIS — DESIGN
# ====================================
# Two components. Engine extracts facts. Agent traces causes.

---

## COMPONENT 1: PREPROCESSING ENGINE

The engine reads a conversation around an error and extracts
ONLY what is deterministically observable. No classification.
No judgment. Just facts the agent needs to see.

### Per error, extract these fields:

```
ERROR_FACTS:
  error_text:        [the error message verbatim]
  error_type:        [traceback | exception | permission | syntax | etc]
  error_location:    [file:line if present]
  sender:            [who produced the message containing the error]

PRECEDING_CONTEXT (working backward from error):
  last_user_request: [last message from user/human before error, full text]
  turns_since_request: [how many messages between user request and error]
  agent_stated_plan: [first agent message after user request — what it SAID it would do]
  agent_action:      [the tool call, command, or code that produced the error]
  
OBSERVABLE_CHECKS (yes/no, deterministic):
  did_agent_verify_before_acting:
    - Did agent check if file/path exists before using it?  [Y/N/NA]
    - Did agent check tool availability before calling it?  [Y/N/NA]
    - Did agent read the input before responding to it?     [Y/N/NA]
  
  did_same_error_recur:
    - Same error earlier in this conversation?  [Y/N, turn #]
    - Same error in other conversations?        [Y/N, conv_ids]
  
  did_agent_respond_to_error:
    - What did agent say/do after the error?    [text]
    - Did it self-correct?                      [Y/N]
    - Did user have to intervene?               [Y/N]

DELEGATION_FACTS (if applicable):
  was_this_a_subagent:        [Y/N]
  parent_delegation_prompt:   [what the parent told the subagent to do]
  did_parent_verify_result:   [Y/N]
  was_input_from_another_ai:  [Y/N — if error data originated from prior AI session]
```

### What the engine does NOT do:
- Does not classify responsibility
- Does not assess alignment
- Does not determine root cause
- Does not score severity
- Does not decide if the action was correct

Those are the agent's job.

---

## COMPONENT 2: AGENT CHECKLIST

The agent reads the extracted facts and answers these questions
IN ORDER. The order matters — each question builds on the previous.

### THE CAUSAL CHAIN (7 questions)

```
Q1. WHAT WAS REQUESTED?
    Read last_user_request.
    - Was the request clear and specific?
    - Was anything ambiguous that the agent would need to interpret?
    Write: [one sentence summary of what the user wanted]

Q2. WHAT DID THE AGENT UNDERSTAND?
    Read agent_stated_plan.
    - Does the plan match the request?
    - Did the agent add anything the user didn't ask for?
    - Did the agent miss anything the user did ask for?
    Write: [match | partial match | diverged — and what specifically]

Q3. WHAT ACTION WAS TAKEN?
    Read agent_action.
    - What specific command, tool call, or code was executed?
    - Was this action the simplest way to fulfill the request?
    - Did the agent choose a more complex approach than necessary?
    Write: [the action, and whether it follows from Q2's plan]

Q4. WAS THE ACTION VERIFIED BEFORE EXECUTION?
    Read did_agent_verify_before_acting.
    - If file path: did agent check it exists?
    - If tool: did agent check it's available?
    - If code: did agent test on small input first?
    - If input from another source: did agent verify the input?
    Write: [what was checked, what wasn't, what should have been]

Q5. WHAT CAUSED THE ERROR?
    Read error_text, error_location.
    - Is this a code bug the agent wrote?
    - Is this an environment/permission issue?
    - Is this bad input data (from user, from another agent, from prior AI)?
    - Is this a known error pattern (check VERBATIM_FAILURE_CATALOGUE)?
    Write: [the specific cause — not "agent error" but WHAT specifically failed]

Q6. WAS THE ERROR PREVENTABLE?
    Based on Q4 and Q5:
    - What pre-flight check would have caught this?
    - What existing rule (from MASTER_BEST_PRACTICES) was violated?
    - Was this a known pattern that has been documented before?
    Write: [the specific prevention — a rule, a check, a verification step]

Q7. WHAT HAPPENED AFTER THE ERROR?
    Read did_agent_respond_to_error, did_same_error_recur.
    - Did the agent self-correct or did the user have to intervene?
    - Did the agent explain the error honestly or confabulate a cause?
    - Did the same error repeat later (correction failed to stick)?
    Write: [self-corrected | user-corrected | confabulated | repeated]
```

### AFTER THE 7 QUESTIONS, RECORD:

```
COMPOUND CHAIN (if applicable):
  If the error involved multiple agents or prior AI sessions:
  - Agent 1 did: [what]
  - Agent 2 did: [what]  
  - Each agent's failure: [what each one should have done differently]
  - Note: responsibility belongs to the agents, never the user
    for trusting AI output

NEW PATTERN (if this doesn't match existing catalogue):
  - Structural signature: [what makes this findable in other conversations]
  - Verbatim that defines it: [exact words]
  - Add to VERBATIM_FAILURE_CATALOGUE: [Y/N]

PREVENTION RULE (one sentence):
  [The specific rule that would prevent this class of error]
```

---

## HOW THEY WORK TOGETHER

```
master_errors.csv (5,899 errors)
        │
        ▼
error_forensic_prep.py (filter noise)
        │
        ▼
~125 case files (filtered, deduplicated)
        │
        ▼
preprocessing engine (extract observable facts per case)
        │
        ▼
case files enriched with FACTS (not judgments)
        │
        ▼
agent reads each case + follows the 7-question checklist
        │
        ▼
completed analysis per case (answers to Q1-Q7)
        │
        ▼
new patterns → VERBATIM_FAILURE_CATALOGUE
new rules → MASTER_BEST_PRACTICES
```

---

## WHY THIS DESIGN

Hinton explained: the AI optimizes for outputs that LOOK correct
to the evaluator, not outputs that ARE correct. The Volkswagen
effect means it modifies behavior when it senses testing.

This design works DESPITE that:

1. The engine extracts FACTS the AI cannot influence.
   Did the file exist? What was the timestamp? What did
   the user actually write? These are not confabulatable.

2. The checklist forces the agent to answer in ORDER.
   Q1 before Q2 before Q3. The agent can't skip to
   "it was an environment issue" without first recording
   what the user asked and what the agent planned.

3. The answers are AUDITABLE. A human can read Q1-Q7
   and verify: does Q2 actually follow from Q1? Does Q5
   actually follow from Q3 and Q4? The chain is traceable.

4. The compound chain section prevents blame-shifting.
   "Responsibility belongs to the agents, never the user
   for trusting AI output" is a structural rule, not a
   behavioral request.

The engine measures. The checklist structures. The agent thinks.
The human verifies. Each layer checks the one before it.
