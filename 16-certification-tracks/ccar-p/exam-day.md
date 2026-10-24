# CCAR-P Exam Day

> Logistics, rules and pacing. Exam facts come from [`registry.yaml`](../registry.yaml) (verified
> 2026-10-24). Delivery rules come from the
> [Pearson VUE Claude Certification page](https://www.pearsonvue.com/us/en/anthropic.html) and the
> [Partner Academy certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications);
> the official exam guide and your confirmation email take precedence over this page.

## The exam in one table

| Fact | Value |
|---|---|
| Items | 63 (multiple-choice and multiple-response) |
| Time | 120 minutes |
| Passing standard | Scaled score 720 on a 100–1,000 scale |
| Result | Pass/fail, scaled score, percent-correct by domain |
| Delivery | Pearson VUE: online proctored (OnVUE) or test centre |

## Before the day

- **Name and ID.** Your Pearson profile name must exactly match your government-issued photo ID, in Latin
  characters. Pearson VUE states that a mismatch at check-in means denied entry and a forfeited fee, and that
  name corrections must be requested from Anthropic certification support at least 24 hours before the exam
  (as of 2026-10-24).
- **Rescheduling.** Cancel or reschedule at least 48 hours ahead; later changes and no-shows forfeit the fee.
- **Online proctoring.** Run the OnVUE system test on the exact machine and network you will use. Corporate
  networks and VPNs often block required domains; Pearson VUE advises involving your network administrator if
  the test flags them. Prefer a personal machine on a home network if your corporate device is locked down.
- **Room.** Quiet, private, clear desk and walls, no second monitor, phone out of reach (you may be asked to
  show it during check-in and then place it away).
- **Guide version.** If you test on or after 2026-12-07, use the updated exam guide published 2026-11-17.

## Rules during the exam

> **Source:** the CCAR-P exam guide v1.0 (sections 12–13) and the Anthropic Certification Exam Policy (last updated
> 2026-06-25), both on the [Partner Academy certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications)
> and checked on 2026-10-24. They require you to stay in webcam view when testing online, keep a clear workspace,
> not communicate with anyone, not copy exam content, accept an NDA, and not use AI products during the exam.
> Pearson VUE sets the detailed check-in procedure, so read the agreement presented when you register and at check-in.

- **No AI tools.** You may not use Claude, any other AI assistant, browser, notes or reference material
  during the exam. The exam measures your judgement, not your tooling.
- **No unauthorised materials or people.** No notes, books, phones, smart watches, headphones or other people
  in the room. Do not read questions aloud; the proctor may treat it as a violation.
- **Stay in view.** Leaving the camera frame, looking away for long periods or covering your mouth can trigger
  a proctor warning or termination.
- **Confidentiality (NDA).** Exam content is confidential. Do not share, post, discuss or reconstruct items
  afterwards, including in study groups or this repository. This is also why our practice materials are
  original and never reproduce real items.

## Pacing for 63 items in 120 minutes

- **Average:** about 1 minute 54 seconds per item.
- **Plan:** a first pass at roughly 1 minute 30 seconds per item, flagging anything that needs more thought,
  finishes in about 95 minutes and leaves about 25 minutes for flagged items and a final check.

| Checkpoint | Target |
|---|---|
| 30 minutes | Item 20 or later |
| 60 minutes | Item 40 or later |
| 90 minutes | First pass complete |
| 110 minutes | Flagged items reviewed |
| 120 minutes | Every item answered (assume no penalty for guessing unless the guide says otherwise) |

Scenario items are long. Read the **question stem first** (what is being asked: best, first, most likely,
least), then the scenario, underlining constraints (latency, cost, regulated data, reversibility, ownership).

## Multiple-response strategy

- The item tells you how many to select ("choose two"). Select exactly that number.
- Evaluate **each option independently** as true or false against the scenario before comparing them.
- Watch for options that are true statements but do not answer the question asked.
- Partial credit should not be assumed; treat each multiple-response item as all-or-nothing unless the
  official guide states otherwise.

## Reading architect-level items

| Clue in the stem | What it usually rewards |
|---|---|
| "Most appropriate first step" | Discovery, measurement or diagnosis before building or switching |
| "Best balances cost and quality" | Evidence-based tuning (caching, effort, routing) over blanket upgrades |
| "Minimise risk" | Least privilege, deterministic enforcement, human approval for irreversible actions |
| "Regulated data" | Data minimisation, residency, covered services, retention and audit |
| "Scale to many teams or hosts" | Reusable, governed mechanisms (managed settings, MCP, Skills) |
| "Simplest solution that meets requirements" | The lowest pattern tier that satisfies every stated constraint |

Eliminate answers that rely solely on prompt wording for security, promise certainty from a probabilistic
system, or add complexity the scenario does not need.

## After the exam

You receive pass/fail, a scaled score and percent-correct by domain. If you need a retake, the registry's
policy is 14 days after the first failed attempt, 30 days after the second and 90 after the third, with at
most four attempts per exam in a rolling 12 months. Use the domain breakdown with the
[readiness assessment](readiness-assessment.md) to plan remediation. Digital badges are issued through Credly
according to Pearson VUE (as of 2026-10-24).
