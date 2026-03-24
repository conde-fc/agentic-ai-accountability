# ROI Measurement Template

A structured framework for measuring whether your AI deployment is delivering value proportional to what you pay for it.

This template adapts procurement evaluation methodology to the problem most organizations skip: measuring what AI actually does after deployment — not what the vendor promised, not what the demo showed, but what happens in daily operation with real tasks and real users.

---

## Part 1: Deployment Profile

Fill in your current AI deployment. This establishes the baseline.

### 1A. What AI tools are deployed?

| Tool | Platform | Plan/Tier | Monthly cost | Users | Primary use |
|---|---|---|---|---|---|
| | | | $ | | |
| | | | $ | | |
| | | | $ | | |
| **Total** | | | **$** | | |

### 1B. Which workflows use AI?

| Workflow | Tool used | Frequency | Estimated time saved per task | Who owns it |
|---|---|---|---|---|
| | | /day /week /month | min | |
| | | /day /week /month | min | |
| | | /day /week /month | min | |

### 1C. What session data is available?

| Source | Available? | Location | Approx. file count |
|---|---|---|---|
| Claude Code JSONL | Y / N | | |
| Codex JSONL | Y / N | | |
| Cowork JSONL | Y / N | | |
| Claude web export | Y / N | | |
| ChatGPT export | Y / N | | |
| Other | Y / N | | |
| Billing/invoice records | Y / N | | |

---

## Part 2: Run the Measurement

### 2A. Scan for observable events

Run the tool pipeline (see GETTING_STARTED.md):

```
universal_error_scanner.py → error_forensic_prep.py → error_root_cause_extractor.py
```

Record your results:

| Metric | Your value |
|---|---|
| Total observable events | |
| Filtered as noise | |
| Reviewable events | |
| ALARMING | |
| CONCERNING | |
| NOT_CONCERNING | |
| NEEDS_TRIAGE | |

### 2B. Calculate your error rate

```
Error rate = reviewable events / total session files scanned
```

| Metric | Your value |
|---|---|
| Total session files scanned | |
| Reviewable events | |
| Error rate (events per session) | |

### 2C. Identify your top event types

From your `root_cause_summary.md`, list the top 5:

| Rank | Event type | Count | What was absent |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### 2D. Calculate preventable rate

From the concern level distribution:

```
Preventable rate = (ALARMING + CONCERNING) / total reviewable events
```

| Metric | Your value |
|---|---|
| ALARMING + CONCERNING | |
| Total reviewable | |
| Preventable rate | % |

---

## Part 3: Token and Cost Measurement

### 3A. Token data (if JSONL sessions available)

Extract token usage from your session files. Claude Code and Cowork JSONL files include `usage` fields with `input_tokens`, `output_tokens`, `cache_read_input_tokens`, and `cache_creation_input_tokens`.

| Platform | Total sessions | Total tokens | Error cycle tokens | Waste % |
|---|---|---|---|---|
| | | | | |
| | | | | |
| **Combined** | | | | |

**Error cycle tokens** = tokens consumed from the message containing an event through all retry messages until resolution or abandonment. See `findings/TOKEN_WASTE_ANALYSIS.md` for methodology.

### 3B. Infrastructure overhead (per conversation)

If you can observe your context window breakdown (some platforms expose this in developer tools or settings), record:

| Category | Tokens | % of context |
|---|---|---|
| System prompt | | |
| Tool definitions | | |
| MCP / connector schemas | | |
| Memory / project files | | |
| Autocompact buffer | | |
| **Total infrastructure** | | |
| Your messages + outputs | | |

```
Infrastructure overhead % = total infrastructure / total context loaded
```

### 3C. Cost attribution

| Category | Tokens | Est. cost | % of total |
|---|---|---|---|
| Delivered value | | $ | |
| Error cycle waste | | $ | |
| Infrastructure overhead | | $ | |
| Behavioral waste (est.) | | $ | |
| **Total** | | **$** | 100% |

**How to estimate cost from tokens:**

For subscription plans, divide monthly cost by total monthly tokens:
```
Cost per token = monthly subscription / total tokens consumed
Waste cost = waste tokens × cost per token
```

For API billing, use current rates from https://docs.anthropic.com/en/docs/about-claude/models (pricing changes over time — verify before calculating):
```
[Model]:   $__/M input, $__/M output
[Model]:   $__/M input, $__/M output
[Model]:   $__/M input, $__/M output
```

---

## Part 4: Prevention ROI

### 4A. What would prevention save?

For each of your top 5 event types, the DATA_DRIVEN_PREFLIGHT_CHECKLIST shows the prevention check. Estimate the implementation effort:

| Event type | Count | Prevention check | Implementation effort | Tokens saved (est.) |
|---|---|---|---|---|
| | | | lines of code / config | |
| | | | lines of code / config | |
| | | | lines of code / config | |
| | | | lines of code / config | |
| | | | lines of code / config | |
| **Total** | | | | |

### 4B. Monthly savings projection

```
Monthly waste (current)     = $___
Preventable %               = ___%
Potential monthly savings    = $___
Annual projection            = $___
Implementation effort        = ___ hours
Payback period              = ___ days
```

### 4C. Non-cost value

Beyond token savings, prevention reduces:

| Impact | Current (estimate) | After prevention (target) |
|---|---|---|
| User time spent correcting AI errors | hrs/week | hrs/week |
| Retry cycles per workflow | per task | per task |
| Rework from incorrect AI output | incidents/month | incidents/month |
| Trust degradation (user stops relying on AI) | qualitative | qualitative |

---

## Part 5: Baseline Report

Compile your findings into a single-page baseline:

```
DEPLOYMENT: [tools, users, monthly cost]
MEASUREMENT PERIOD: [date range, sessions scanned]
ERROR RATE: [events per session]
PREVENTABLE RATE: [% of events that were preventable]
TOP EVENTS: [top 3 types with counts]
TOKEN WASTE: [% consumed by error cycles]
COST WASTE: [$ estimate]
PREVENTION PLAN: [top 3 checks to implement, effort estimate]
PROJECTED SAVINGS: [monthly, annual]
```

This baseline becomes the "before" measurement. After implementing prevention checks, re-run the pipeline and compare.

---

## Part 6: Ongoing Measurement

This is not a one-time audit. The framework improves with use.

### Measurement cycle

```
Month 1:  Run pipeline → establish baseline → implement top 3 prevention checks
Month 2:  Re-run pipeline → measure improvement → implement next 3 checks
Month 3:  Re-run pipeline → compare to baseline → report cumulative improvement
Ongoing:  Re-run quarterly → track trend → adjust prevention rules
```

### What to track over time

| Metric | Baseline | Month 2 | Month 3 | Trend |
|---|---|---|---|---|
| Events per session | | | | |
| Preventable % | | | | |
| Token waste % | | | | |
| Top event type count | | | | |
| New patterns discovered | | | | |

### Growing the detection library

Each review cycle may reveal event patterns not in the current catalogue. When a new pattern recurs:

1. Document it using the VERBATIM_FAILURE_CATALOGUE format (structural signature + exact text)
2. Add the prevention rule to your project's pre-flight checklist
3. If the pattern is generalizable, consider contributing it back to this repository

---

## Adapting This Template

### For a single developer

Focus on Parts 1-2 and 4A. Run the scanner on your Claude Code sessions, check your error rate and top event types, implement the corresponding prevention checks from the checklist.

### For a team

Add user-level breakdown to Part 2. Which team members' workflows produce the most events? Which workflows have the highest error rates? This informs training and configuration priorities.

### For an organization evaluating AI ROI

Focus on Parts 3 and 5. The baseline report is the deliverable. It answers: "We spend $X/month on AI tools. Here's what percentage delivers value, what percentage is waste, and what it would cost to reduce that waste."

### For a client engagement

Parts 1-5 become the engagement scope. Part 5 is the deliverable. Part 6 is the ongoing relationship. The template structures the entire engagement from intake through measurement through prevention through tracking.
