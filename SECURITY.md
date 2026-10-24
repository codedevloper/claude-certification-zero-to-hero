# Security Policy

## What this policy covers

This repository contains educational code: labs, projects, the mock-exam engine and repository tooling. Please report:

- a vulnerability in that code (for example, unsafe handling of model output, injection paths or path traversal),
- an accidentally committed secret or credential,
- example code that teaches an insecure pattern without flagging it,
- a dependency with a known vulnerability.

**Out of scope:** vulnerabilities in Anthropic products (Claude, the API, Claude Code). Report those to Anthropic through
its [responsible disclosure policy](https://www.anthropic.com/responsible-disclosure-policy).

## How to report

Please **do not open a public issue** for a security problem. Use GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
from the repository's **Security** tab. Include:

- the affected file(s) and line(s),
- the impact and how to reproduce it,
- a suggested fix, if you have one.

You should receive an acknowledgement within 7 days. Fixes for confirmed issues are prioritised, and reporters are
credited in the [CHANGELOG](CHANGELOG.md) unless they prefer otherwise.

## If you find a leaked credential

Report it privately as above. If it is yours, revoke it immediately in the issuing console (for an Anthropic API key,
the Claude Console), because a key that has reached a public repository must be treated as compromised even after
it is removed from history.

## Security practices in this repository

- No real credentials: configuration uses environment variables and `.env.example` placeholders.
- CI runs [gitleaks](https://github.com/gitleaks/gitleaks) and `tools/scan_secrets.py` on every push and pull request.
- Labs default to offline mock mode, so CI never calls a live API.
- Model output is treated as untrusted input throughout the examples.
- The browser mock exam uses a strict Content Security Policy and renders all content as text.

## Supported versions

Only the `main` branch is maintained.
