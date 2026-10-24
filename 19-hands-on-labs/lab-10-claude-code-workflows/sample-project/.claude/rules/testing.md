---
paths:
  - "tests/**/*.py"
---

# Testing rules

- Use the standard library `unittest`; do not introduce pytest or other test dependencies.
- Every money assertion compares `Decimal` values, never floats.
- Test data must be synthetic. Use fictional company names and round numbers that are easy to check by hand.
- Name tests after the behaviour they check, for example `test_rejects_negative_price`.
