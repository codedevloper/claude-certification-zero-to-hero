# Acme Logistics invoicing service

Fictional sample project for Lab 10. It calculates freight invoice totals.

## Commands

- Run all tests: `python -m unittest discover -s tests -v`
- Run one test file: `python -m unittest tests.test_totals -v`
- There is no build step. Python 3.10+ standard library only; do not add dependencies without asking.

## Project layout

- `src/invoicing/totals.py`: invoice maths (subtotal, VAT, discounts). Pure functions only.
- `tests/`: unit tests, one file per module.
- Architecture notes: @docs/architecture.md

## Code style

- Use `decimal.Decimal` for money, never `float`. Round with `ROUND_HALF_UP` to 2 places at the end.
- Type hints on every public function. Docstrings say what the function returns and what it raises.
- Raise `ValueError` with a clear message for invalid input; never return a sentinel such as -1.

## Workflow

- Write or update a failing test before changing behaviour, then make it pass.
- Run the full test suite before you say a task is done, and show the result.
- Keep changes small. One logical change per commit, with a message in the imperative mood.

## Security rules

- Never read, print or edit `.env` files or anything under `secrets/`. Ask the developer instead.
- Never push to a remote, and never use `--force` with git.
- Invoice data in tests must be synthetic. Never paste real customer names or account numbers.
