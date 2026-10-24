# Progress Tracker

Status of the repository build. "Complete" means written, checked by the automated validators, and with no
placeholders. It does not mean every sentence has had expert human review; see [Known gaps](#known-gaps).

**Last updated:** 2026-10-24 · **Release:** v1.0 (unreleased; local only)

## Summary

| Area | Status | Size | Verified by |
|---|---|---|---|
| Certification registry | Complete | 2 supported tracks, 2 planned | Official v1.0 exam guides (2026-10-24) |
| Learning modules 00–15 | Complete | 16 modules, 139 pages, ~262k words | Link check, exam-claims check, snippet compile/run by authors |
| AI security track (module 12) | Complete | 16 pages, OWASP LLM Top 10 2025 and agentic mapping | Sources checked 2026-10-24 |
| CCAO-F track | Complete | Overview, 7 domain guides, exercises, scenarios, revision, readiness | Coverage matrix: 30/30 objectives |
| CCAR-P track | Complete | Overview, 7 domain guides, exercises, scenarios, revision, readiness | Coverage matrix: 38/38 objectives |
| Practice questions | Complete | 132 CCAO-F + 141 CCAR-P = **273** | Schema, keys, distractors, near-duplicates, answer-cueing limits |
| Mock exams | Complete | Terminal + browser engines, 6 fixed forms | Unit tests, scripted CLI run, in-browser test |
| Hands-on labs | Complete | **20** labs | All 20 pass in mock mode (`tools/run_lab_smoke.py`) |
| Real-world projects | Complete | **5** projects | 173 offline tests passing |
| Learning roadmaps | Complete | 7, 15, 30, 60 and 90-day plans | Link check |
| Flashcards | Complete | 106 CCAO-F + 147 CCAR-P + 94 fundamentals = **347** | `tools/flashcards.py` |
| Interview prep, cheat sheets, troubleshooting | Complete | 22 files | Link check |
| Glossary and FAQ | Complete | 167 glossary terms | Link check |
| Governance files, templates, CI | Complete | 3 workflows, 4 issue templates, PR template | Local equivalents of every CI job pass |
| GitHub Pages website | Complete, not yet deployed | MkDocs + Material, 236 pages, search, interactive practice exam | Strict build with 0 warnings; 3,411 internal links crawled; browser-tested locally |

## Quality gates (local run, 2026-10-24)

| Check | Result |
|---|---|
| `tools/validate_all.py --labs`: questions, flashcards, internal links, exam claims, secrets, coverage, forms, web bundle, labs | Pass |
| `pytest` (repository tests) | Pass |
| Project test suites (5) | Pass (173 tests) |
| markdownlint-cli2 | 0 errors |
| External links (`tools/check_external_links.py`, 264 URLs) | All reachable; a few sites block bots (403) and need manual checks |
| Bandit SAST (Python) | No medium/high issues after review; low-severity findings are lab `assert` self-checks, non-crypto `random`, and fixed-argument `subprocess` |
| Originality scan (2026-10-24) | Compared every 10-word sequence against 256 cited sources (250 web pages, the 4 official exam guides, the exam policy and NIST AI 600-1). 18 passages that echoed source wording were rewritten, along with one workflow adapted from the docs. The remaining matches are citations, required code/API syntax, official names and figures, and the official exam blueprint tables. |
| Snyk Code scan | **Not run:** the Snyk MCP needs the maintainer to authenticate (`snyk_auth`) |

## Independent review (2026-10-24)

Five independent reviews (API accuracy, product facts, question quality, learner experience, code and security) were
run on the whole repository. Every critical, high, medium and low finding was fixed or explicitly decided, in four
verified commits. Decided, not changed: code repeated across the five projects stays, so each project can be copied out
and run on its own.

## Known gaps

These are honest limitations of v1.0. None is hidden as "complete".

1. **Live-mode code was not run against the paid API.** Every lab and project runs offline in mock mode.
   Live paths follow the current API rules, and labs 03 and 07 were checked against the real `anthropic` 2.3.0 SDK
   using a local stub server, but no request was sent to Anthropic. Expect small fixes on the first live run.
2. **Snyk scan pending** until the maintainer authenticates Snyk (see above).
3. **Exam guides change on 2026-11-17.** The registry reflects v1.0. Re-verify and update after that date
   (see the [ROADMAP](ROADMAP.md)).
4. **Facts labelled `Unverified`.** Search the repository for `Unverified:` to list them. Most concern plan-specific
   features, regional or compliance attestations (FedRAMP, HIPAA eligibility per offering), and a few beta details.
   Each needs confirming against an official page or with Anthropic.
5. **Planned tracks:** CCAR-F and CCDV-F have verified facts in the registry but no track content. The maintainer's
   third certification is not yet identified.
6. **Expert review:** content was written to strict standards and machine-checked, but a human subject-matter review of
   each module (especially practice-question answer keys) is still recommended before public release.
7. **External links:** some pages (claude.ai, hhs.gov, iso.org) block automated checks and were not machine-verified.

## Next steps

- [ ] Maintainer review of README, disclaimers and licence choice
- [ ] Authenticate Snyk and run a code scan
- [ ] Spot-review a sample of practice questions per domain
- [ ] Optional: run a few labs in live mode to confirm live paths
- [ ] Set up a personal git identity, commit, then push to the personal GitHub repository
- [ ] Turn on GitHub Pages: Settings > Pages > Source: **GitHub Actions** (the site deploys on the next push to `main`)
- [ ] After 2026-11-17: refresh the registry from the updated exam guides
