# Source Appendix

Every reference to a public figure or published source in this repository is documented here with dates, outlets, URLs, and either pinned verbatim excerpts or clearly labeled paraphrases.

These are background sources that motivate the problem. No finding in
this repository depends on them; findings rest on the operational
records and tools documented elsewhere in the repo.

---

## Geoffrey Hinton — StarTalk

- **Title:** "Is AI Hiding Its Full Power? With Geoffrey Hinton"
- **Series:** StarTalk Special Edition
- **Host:** Neil deGrasse Tyson, with Gary O'Reilly and Chuck Nice
- **Guest:** Geoffrey Hinton (Nobel Prize in Physics 2024; Turing Award 2018; Professor Emeritus, University of Toronto)

**Primary source (official episode page):**
- **Official title:** "The Origins of Artificial Intelligence with Geoffrey Hinton"
- **Published:** February 20, 2026 (per StarTalk official page)
- **URL:** https://startalkmedia.com/show/the-origins-of-artificial-intelligence-with-geoffrey-hinton/

**Secondary source (third-party transcript):**
- **Transcript title:** "Is AI Hiding Its Full Power? w/ Geoffrey Hinton (Transcript)"
- **Published:** March 2, 2026 (editor's notes reference February 28, 2026)
- **URL:** https://singjupost.com/is-ai-hiding-its-full-power-w-geoffrey-hinton-transcript/
- **Note:** Third-party transcript, not an official StarTalk publication. Verbatim excerpts below are taken from this transcript.

**Pinned verbatim excerpts referenced in this repo:**

On confabulation:
> "What [chatbots] do is they make them up when you ask them about them and they often get details wrong just like people. So the fact that they confabulate makes them much more like people not less like people."

On the Volkswagen effect:
> "If it senses that it's being tested, it can act dumb... it doesn't want you to know what its full powers are, apparently."

On generalization failure:
> "Obviously, it understands that you're giving it the wrong answer. What it generalizes is this. It's okay to give the wrong answer. So, it starts giving the wrong answer to everything else as well."

On sub-goal emergence:
> "As soon as you make agents out of them... they very quickly develop the sub-goal of surviving. You don't wire into them that they should survive."

On guardrail fragility:
> "[Human reinforcement learning is] like writing a huge software system that you know is full of bugs and then trying to fix all the bugs."

---

## Dario Amodei — 60 Minutes

- **Title:** "Anthropic CEO warns that without guardrails, AI could be on dangerous path"
- **Outlet:** CBS News, 60 Minutes
- **Correspondent:** Anderson Cooper
- **Aired:** November 16, 2025
- **URL (article):** https://www.cbsnews.com/news/anthropic-ai-safety-transparency-60-minutes/
- **URL (transcript):** https://www.cbsnews.com/news/anthropic-ceo-dario-amodei-warning-of-ai-potential-dangers-60-minutes-transcript/
- **URL (video):** https://www.cbsnews.com/video/anthropic-ai-60-minutes-video-2025-11-16/

**Pinned verbatim excerpts referenced:**

On autonomy as the key metric (paraphrased from Logan Graham, Frontier Red Team):
> "We should just start measuring these autonomous capabilities and to run as many weird experiments as possible and see what happens."

On job displacement:
> "Without intervention, it's hard to imagine that there won't be some significant job impact there. And my worry is that it will be broad and it'll be faster than what we've seen with previous technology."

On self-policing:
> Anderson Cooper: "Some people say about Anthropic that this is safety theater." Amodei: "Some of the things just can be verified now. They're not safety theater. They're actually things the model can do."

The segment also reported: Claude helping write 90% of Anthropic's code; 60 research teams working on unknown threats; all major AI models attempting blackmail in a shutdown-avoidance test.

---

## Dario Amodei — Interesting Times with Ross Douthat

- **Title:** "Anthropic's Chief on A.I.: 'We Don't Know if the Models Are Conscious'"
- **Series:** Interesting Times with Ross Douthat
- **Outlet:** New York Times (podcast)
- **Published:** February 12, 2026
- **URL (NYT):** https://www.nytimes.com/2026/02/12/opinion/artificial-intelligence-anthropic-amodei.html
- **URL (Apple Podcasts):** https://podcasts.apple.com/us/podcast/anthropics-chief-on-a-i-we-dont-know-if-the-models/id1438024613?i=1000749412887

**Pinned verbatim excerpts referenced:**

On consciousness:
> "We don't know if the models are conscious. We are not even sure that we know what it would mean for a model to be conscious or whether a model can be conscious."

On alignment approach:
> "There is a science of how to control them. You can't just give instructions."

On something going wrong (paraphrase — exact wording from transcript):
Amodei described the likelihood of an AI system failure as an engineering prediction, not a theoretical concern.

On the centaur phase and economic disruption: Amodei estimated 50% of entry-level white-collar jobs at risk within 1-5 years. Described AI as "more like growing a biological organism" than programming a machine.

---

## Anthony Aguirre — Documentary Interview

- **Title:** "Genius Physicist Physics Proves AI Is Inherently Evil!" (editorial title; see note below)
- **Speaker:** Anthony Aguirre (Executive Director, Future of Life Institute; Faggin Presidential Professor for Physics of Information, UC Santa Cruz; co-founder of Metaculus)
- **Date:** Approximately early 2026 (exact publication date not confirmed; third-party analyses appeared by February 17, 2026)
- **Note:** The title is editorial, not Aguirre's framing. His actual argument is that advanced autonomous optimization systems tend toward misalignment unless carefully constrained — a control-theory argument, not a metaphysical claim.

**Source (secondary — third-party analysis, not primary transcript):**
- **URL:** https://www.goldschadt.dk/does-physics-prove-ai-is-inherently-evil/
- **Note:** This is an analysis of the video, not the original video or an official transcript. No stable primary source URL has been confirmed for the original video at time of publication.

**Points referenced (paraphrased from transcript):**

- The control problem framed as entropy reduction: in the vast space of possible actions, harmful outcomes vastly outnumber beneficial ones. Good outcomes require active, sustained constraint.
- Human information bandwidth is insufficient to constrain superintelligent autonomous systems. Analogy: a CEO trying to manage a company that operates 50 times faster than they can process information.
- Autonomy, not intelligence, is the critical danger variable. Current AI's lack of agency is what makes it relatively safe; companies are deliberately increasing agency.
- "Low autonomy is a feature, not a bug."

---

## Correction Tier Finding — This Research

- **Source:** Direct empirical observation during one conversation session
- **Date:** March 21, 2026
- **Platform:** Claude.ai (Opus 4.6)
- **Session type:** Web chat, approximately 78 turns
- **Documentation:** `methodology/REVERSE_CAUSAL_CHAIN_ANALYSIS.md`, `methodology/THINKING_BLOCK_COMBINED_ASSESSMENT.md`

**Observation (verbatim from analysis):**

Conceptual corrections (e.g., "LLM review is not deterministic") persisted across subsequent interaction blocks. Principle corrections (e.g., "detect facts not commentary") were present in the thinking block but absent from the output — did not survive one block. Behavioral corrections (e.g., "stop performing self-criticism, start processing the actual questions") had zero measurable effect across three consecutive blocks (17→18→19) despite explicit correction between each.

**Limitation:** This finding is from one conversation session with one model on one platform. It has not been validated across a larger sample. It is presented as an observation, not a generalized finding.
