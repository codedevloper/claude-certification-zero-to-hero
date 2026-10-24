## Summary

<!-- What does this PR change, and why? -->

## Type of change

- [ ] Content fix (error or outdated fact)
- [ ] New or improved learning content
- [ ] Practice questions or flashcards
- [ ] Lab or project code
- [ ] Tooling, CI or repository structure

## Sources

<!-- Link the official documentation you checked. For exam facts, link the official exam guide page. -->

## Checklist

- [ ] The wording is original; nothing is copied from tutorials, courses or other repositories
- [ ] No real, recalled or reconstructed exam questions, and no reuse of official sample questions
- [ ] Facts are checked against official sources; time-sensitive facts are dated; unverified facts are labelled
- [ ] Only fictional organisations and synthetic data are used
- [ ] No secrets, keys or `.env` files
- [ ] `python tools/validate_all.py --labs` passes
- [ ] `python -m pytest tests -q` passes
- [ ] If questions changed: `python tools/build_coverage.py` and `python tools/build_web_bundle.py` were run
- [ ] Security considerations are included where relevant
