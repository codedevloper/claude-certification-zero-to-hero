# Frequently Asked Questions

> **Disclaimer:** `claude-certification-zero-to-hero` is an **unofficial**, community educational repository. It is
> **not affiliated with, endorsed by or sponsored by Anthropic**, Pearson VUE or any certification body. "Claude" and
> "Anthropic" are trademarks of Anthropic. Nothing here is official exam content, and none of it reproduces or
> reconstructs real exam questions. Always treat the official exam guides and documentation as the source of truth.

Contents: [About the repository](#about-the-repository) · [The certifications](#the-certifications) ·
[Studying](#studying) · [Labs and costs](#labs-and-costs) · [Contributing](#contributing)

## About the repository

### What is this repository?

A structured, original curriculum that takes you from no Claude knowledge to certification readiness and
production-grade skills: 16 learning modules, certification tracks, practice questions, mock exams, hands-on labs,
real-world projects, interview preparation, cheat sheets, flashcards and troubleshooting guides. Start with the
[README](README.md) and [how to use this repo](00-getting-started/how-to-use-this-repo.md).

### Who is it for?

Beginners, business users of the Claude apps, developers, security engineers, DevSecOps practitioners, cloud,
solution and enterprise architects, and technical leaders. [Choose your path](00-getting-started/choose-your-path.md)
suggests routes for each.

### Is it official?

No. See the disclaimer above. Anthropic's own learning resources are listed in
[25 · Official resources](25-official-resources/README.md).

### How current is the content?

Every page with time-sensitive facts (model names, prices, features, exam details) states the date it was checked;
the baseline for this release is **2026-10-24**. Exam facts are held in one machine-readable file,
[`registry.yaml`](16-certification-tracks/registry.yaml), with a human-readable summary in
[exam-facts.md](25-official-resources/exam-facts.md) and a history in the
[verification log](25-official-resources/verification-log.md). Anything we could not verify is labelled
**Unverified** where it appears.

### What licence does it use?

Code is under the [MIT License](LICENSE) and educational content under CC BY 4.0; the certificate images are excluded. See [LICENSE-CONTENT.md](LICENSE-CONTENT.md) for details and attribution wording.

## The certifications

All exam facts below come from [`registry.yaml`](16-certification-tracks/registry.yaml) (verified 2026-10-24 against
the official v1.0 exam guides on the
[Anthropic Partner Academy certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications)
and the [Pearson VUE Claude Certification Program page](https://www.pearsonvue.com/us/en/anthropic.html)).

### Which certifications does this repository prepare me for?

Three full tracks:

| Exam | Code | Audience | Track |
|---|---|---|---|
| Claude Certified Associate – Foundations | CCAO-F | Business and knowledge workers using Claude as a productivity tool | [CCAO-F track](16-certification-tracks/ccao-f/README.md) |
| Claude Certified Architect – Foundations | CCAR-F | Architects and developers building agentic systems with the Agent SDK, Claude Code and MCP | [CCAR-F track](16-certification-tracks/ccar-f/README.md) |
| Claude Certified Architect – Professional | CCAR-P | Mid- to senior-level architects and engineers delivering production Claude solutions | [CCAR-P track](16-certification-tracks/ccar-p/README.md) |

Facts for one further exam, Claude Certified Developer – Foundations (CCDV-F), are recorded in the registry, but there
is no track for it. The modules already cover much of its material.

### Who can take the exams?

As of 2026-10-24, the certification exams are open to organisations in the **Claude Partner Network**: registration
runs through the Anthropic Partner Academy (Skilljar) and scheduling through Pearson VUE. If your organisation is not a
partner, you can still use this repository and Anthropic's free [Claude Academy](https://academy.claude.com/)
courses, which award certificates of completion rather than certifications. Check the official pages for any change to
eligibility.

### Can I register with a personal email address?

No. Registration needs a partner email address on a recognised company domain; personal addresses are rejected. If your
company's domain is not recognised yet, adding it takes 7 to 10 days, so ask your partner contact well before you plan
to book. You must also be at least 18. See [exam facts](25-official-resources/exam-facts.md).

### Is there a discount?

It depends on your organisation's partner tier. Registered-tier partners pay the list price; Select, Preferred and
Global Premier partners get 50% off at checkout, and Global Premier partners get 100% off through 2026-12-31. A retake
costs the full fee, less your tier discount. Prices and tiers are set by Anthropic and can change: confirm at checkout.

### Can I take the exam online from any country?

Mostly. Candidates with an ID from Belarus, Cuba, North Korea, Russia, Syria or restricted regions of Ukraine must use a
Pearson VUE test centre instead of online proctoring, and Pearson has suspended delivery to residents of Iran (from
2026-09-08). Check the [Pearson VUE page](https://www.pearsonvue.com/us/en/anthropic.html) before you book.

### What are the format, fee and pass mark?

| | CCAO-F | CCAR-F | CCAR-P |
|---|---|---|---|
| Items | 60 (multiple-choice and multiple-response) | 60, in 4 scenarios drawn from a published bank of 6 | 63 (multiple-choice and multiple-response) |
| Time | 120 minutes | 120 minutes | 120 minutes |
| Passing | Scaled score 720 on a 100–1,000 scale | Scaled score 720 on a 100–1,000 scale | Scaled score 720 on a 100–1,000 scale |
| Fee (list price) | USD 99 | USD 125 | USD 175 |
| Validity | 12 months | 12 months | 12 months |
| Delivery | Pearson VUE, online proctored or test centre | Pearson VUE, online proctored or test centre | Pearson VUE, online proctored or test centre |

Domain weights are in the registry, on [exam-facts.md](25-official-resources/exam-facts.md) and on the one-pagers for
[CCAO-F](22-cheat-sheets/ccao-f-one-pager.md), [CCAR-F](22-cheat-sheets/ccar-f-one-pager.md) and
[CCAR-P](22-cheat-sheets/ccar-p-one-pager.md).

### What if I fail?

Per the registry, the retake policy requires waiting 14 days after a first failed attempt, 30 days after a second and
90 days after a third, with at most four attempts per exam in a rolling 12 months. Your score report shows
percent-correct by domain; use it with the track's [readiness assessment](16-certification-tracks/ccao-f/readiness-assessment.md)
to focus your study.

### How do I renew?

Credentials are valid for 12 months. According to [exam-facts.md](25-official-resources/exam-facts.md), on-time
renewal is a free, non-proctored assessment, and a lapsed credential means retaking the exam. Confirm the current
process on the official certifications page.

### Are the exams changing?

Yes. Pearson VUE states that updated exam guides will be published on **2026-11-17** and that CCAO-F, CCDV-F and
CCAR-P will include updated content from **2026-12-07**. If you sit an exam on or after that date, study against the
updated guide. This repository will be re-verified; check the [verification log](25-official-resources/verification-log.md).

### Are the practice questions real exam questions?

No. Every practice question, mock exam item and flashcard is original, written to the published objectives. Exam
content is confidential under the candidate agreement, and this repository does not collect, reproduce or reconstruct
it. Please do not submit remembered exam questions.

### Which certification should I take first?

If you use Claude in the apps for business work and do not write code, CCAO-F. If you design and deliver production
systems and meet the recommended experience (3+ years in systems architecture or platform engineering and 6+ months
with LLM systems in production, per the registry), CCAR-P. Many architects study the CCAO-F material quickly first,
because it covers product features the architect exam assumes.

## Studying

### How long will it take?

It depends on your starting point. The [roadmaps](00-getting-started/roadmaps/README.md) offer 7-, 15-, 30-, 60- and
90-day plans. A typical working professional new to Claude might choose the 30-day plan for CCAO-F and the 60-day plan
for CCAR-P.

### What is the best way to study?

Read the modules mapped to each objective (the track's coverage matrix lists them), do the related labs, drill
[flashcards](23-flashcards/README.md), then take [practice questions](17-practice-questions/README.md) and
[mock exams](18-mock-examinations/README.md) under timed conditions. Review every wrong answer's explanation and the
linked module. Hands-on practice matters, especially for CCAR-P.

### Do I need to code?

Not for CCAO-F, which is aimed at business users of the Claude apps rather than API developers; the labs are useful but optional for that track. For CCAR-P you
should be comfortable reading Python and JSON and running the labs.

### Do mock exam scores predict the real exam?

Not precisely. Our scoring is a rough guide; the real exam uses scaled scoring set by the exam provider. Use mock
results to find weak domains, not to predict a pass.

### Where can I get help with a concept?

The [Glossary](GLOSSARY.md), the module's Further reading section, the [cheat sheets](22-cheat-sheets/README.md) and
the [troubleshooting guides](24-troubleshooting/README.md). For errors in this repository, open an issue.

## Labs and costs

### Do the labs cost money?

Not by default. Every lab runs in **mock mode** (`CLAUDE_LAB_MODE=mock`), which is offline and free, using a fake
client that returns canned responses so the code runs end to end. Live mode (`CLAUDE_LAB_MODE=live`) calls the real
Claude API and uses your API credits; each lab marks paid steps with a cost note. See
[19 · Hands-on labs](19-hands-on-labs/README.md).

### How much does live mode cost?

It depends on the model, the number of tokens and how often you run a lab. Most labs use small prompts, and the shared helper
provides a cheaper model setting (`CLAUDE_LAB_FAST_MODEL`) for cost-sensitive steps. Check current prices on the official
[pricing page](https://platform.claude.com/docs/en/about-claude/pricing) and the
[model selection cheat sheet](22-cheat-sheets/model-selection.md), set a spending limit in the Claude Console, and watch
the `usage` printed by the labs.

### What do I need installed?

Python 3.10 or later, a virtual environment and the packages in `requirements-dev.txt` (plus
`19-hands-on-labs/requirements.txt` for live mode). Follow [environment setup](00-getting-started/environment-setup.md).
Problems are covered in [labs and repository troubleshooting](24-troubleshooting/labs-and-repository.md).

### How do I keep my API key safe?

Store it in an environment variable or a git-ignored `.env` file (copy `19-hands-on-labs/.env.example`), never in
code, notebooks, screenshots or commits. Rotate it if it leaks. See [SECURITY](SECURITY.md).

### Can I use Amazon Bedrock, Google Vertex AI or Microsoft Foundry instead?

The labs target the Claude API by default. Concepts transfer, but authentication, model IDs and feature availability
differ by platform; see [06 · Cloud platforms](06-claude-api/07-cloud-platforms.md).

## Contributing

### Can I contribute?

Yes. Read [CONTRIBUTING](CONTRIBUTING.md), the [style guide](docs/STYLE.md) and the
[code of conduct](CODE_OF_CONDUCT.md). Corrections to dated facts, new practice questions, labs and translations are
especially welcome.

### What are the rules for contributed content?

Original work only: no copied tutorials, courses or question banks, and never real or reconstructed exam questions.
Check facts against official sources, date anything time-sensitive, label anything unverified, use fictional
organisations and synthetic data, and never commit credentials.

### Which checks should I run before a pull request?

```bash
python tools/check_links.py
python tools/check_exam_claims.py
python tools/validate_questions.py
python tools/flashcards.py
python tools/scan_secrets.py
```

### I found an outdated fact. What should I do?

Open an issue or pull request with the official source link and the date you checked it. Exam facts are changed in
[`registry.yaml`](16-certification-tracks/registry.yaml) first and recorded in the
[verification log](25-official-resources/verification-log.md).

### I found a security problem in the code

Do not open a public issue. Follow [SECURITY](SECURITY.md).

---

*Unofficial and unaffiliated with Anthropic. Exam facts: [`registry.yaml`](16-certification-tracks/registry.yaml),
verified 2026-10-24. Official sources: [Anthropic Partner Academy](https://anthropic-partners.skilljar.com/page/partner-certifications),
[Pearson VUE](https://www.pearsonvue.com/us/en/anthropic.html).*
