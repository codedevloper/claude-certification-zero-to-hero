# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-10-24

### Changed (full repository review, 2026-10-24)

- Practice questions no longer reward test-taking tricks: CCAR-P distractors rewritten (longest-option key rate 96% to
  14%), answer positions balanced, and the validator now fails banks with these cues
- Security examples hardened: diff smuggling (project 04), case-insensitive asset checks (project 03), exact IP and
  cited-evidence matching (project 05), look-alike domains and mixed recipients (lab 14), bare links (project 02)
- Facts corrected: forced `tool_choice` and sampling-parameter scope, API version `2026-10-21`, model lifecycle
  example, data-processor split, BAA and Console, `claude mcp add` commands, MCP deprecations, hook matchers
- GitHub Actions pinned to commit SHAs with least-privilege permissions
- Licence split into `LICENSE` (MIT) and `LICENSE-CONTENT.md` (CC BY 4.0)
- Consistent page navigation on all module pages; clearer eligibility, study-plan and starting-point guidance
- Mock-exam CLI rejects answers given after time runs out and invalid options; secret scanner judges the matched value

### Added

- Five practice questions on gaps (Managed Agents, platform availability, A/B test power, Microsoft 365 connector)
- CCAR-F stop-gap study map; `tools/build_page_nav.py`; `tools/shuffle_options.py`

- "About the maintainer" section in the README, with Credly verification links for the maintainer's CCAO-F, CCAR-F
  and CCAR-P certifications
- Manual trigger (`workflow_dispatch`) for the CI workflow

- Initial repository structure: 26 numbered sections, governance files, issue and PR templates
- Certification registry (`16-certification-tracks/registry.yaml`) verified against the official v1.0 exam guides on
  2026-10-24: CCAO-F and CCAR-P fully supported, CCAR-F and CCDV-F recorded as planned
- Learning modules 00–15, preparation tracks for CCAO-F and CCAR-P, and the AI security track
- Unofficial practice question banks with JSON Schema, plus validation tooling
- Mock-exam engine (terminal and browser): timed and learning modes, domain breakdowns, local progress, fixed forms
- 20 hands-on labs with an offline mock mode, and 5 real-world projects with tests
- Learning roadmaps, flashcards, cheat sheets, interview preparation, troubleshooting, glossary and FAQ
- GitHub Pages website (MkDocs + Material) with grouped navigation, search, dark mode and the browser practice exam, deployed by `.github/workflows/pages.yml`
- CI: content validation, coverage and form checks, internal and external link checks, markdown lint, tests, lab
  smoke tests and secret scanning
