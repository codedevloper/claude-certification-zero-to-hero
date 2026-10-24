# Verification Log

A dated record of when facts in this repository were checked against official sources. Add a row whenever you
re-verify something. Never update a fact without also adding a row here.

| Date | What was verified | Source | Result | By |
|---|---|---|---|---|
| 2026-10-24 | CCAO-F exam guide v1.0: format, fee, validity, 7 domains, weights, objectives | Official exam guide PDF via [Partner Academy certifications page](https://anthropic-partners.skilljar.com/page/partner-certifications) | Recorded in `registry.yaml` | Maintainer |
| 2026-10-24 | CCAR-P exam guide v1.0: format, fee, validity, 7 domains, weights, objectives | Same | Recorded in `registry.yaml` | Maintainer |
| 2026-10-24 | CCAR-F and CCDV-F exam guides v1.0: format, fee, domains, weights | Same | Recorded as `planned` tracks | Maintainer |
| 2026-10-24 | Certification Exam Policy (last updated 2026-06-25): confidentiality, no AI assistance, renewals | Exam policy PDF on the same page | Reflected in exam-day guides and in the IP rules in `docs/STYLE.md` | Maintainer |
| 2026-10-24 | Eligibility (Claude Partner Network), retake rules, guide update on 2026-11-17, content change on 2026-12-07 | [Pearson VUE program page](https://www.pearsonvue.com/us/en/anthropic.html) | Recorded in `registry.yaml` | Maintainer |
| 2026-10-24 | Reschedule/cancel deadline | Exam guides v1.0 (24 h) vs [Partner Academy FAQ](https://anthropic-partners.skilljar.com/page/faq-certifications) and Pearson VUE (48 h) | Conflict recorded; learners told to plan on 48 h | Maintainer |
| 2026-10-24 | Current model IDs, context windows, list prices and API behaviour rules | Anthropic API reference (models overview, pricing) | Dated in module 05, module 06 and the cheat sheets | Maintainer |
| 2026-10-24 | Originality: repo text compared with all cited sources and the exam guides for verbatim overlaps of 12+ words | 256 source texts | 18 passages reworded; no copied prose remains; no exam-guide sample questions reused | Maintainer |

## Next scheduled review

- **2026-11-17**: re-read all updated exam guides, update `registry.yaml` and rerun `python tools/build_coverage.py`.
- **Every model release**: re-check model tables, prices and API rules in `docs/STYLE.md` section 1.5.
