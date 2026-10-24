---
name: release-notes
description: Draft customer-facing release notes for the invoicing service from git history since a given tag. Use when the developer asks for release notes or a changelog entry.
argument-hint: "[since-tag]"
disable-model-invocation: true
allowed-tools: Bash(git log *) Bash(git diff *) Read
---

Draft release notes for the changes since git tag $ARGUMENTS.

1. Run `git log --oneline $ARGUMENTS..HEAD` and read the commit messages.
2. For any commit whose message is unclear, run `git diff` on that commit and read the change.
3. Group the changes under three headings: "New", "Fixed" and "Changed". Leave out refactors and test-only
   changes unless they change behaviour.
4. Write one plain-English line per change for finance staff who use the invoices, not for developers.
5. Never include customer names, account numbers or amounts from real invoices.
6. Show the draft and stop. Do not commit, tag or push anything.
