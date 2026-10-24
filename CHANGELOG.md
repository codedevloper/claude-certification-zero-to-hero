# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
