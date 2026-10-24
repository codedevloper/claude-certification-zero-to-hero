# Contributing

Thank you for helping learners. This repository aims to be accurate, original and safe to publish, so
contributions follow a few firm rules.

## Ground rules

1. **Original work only.** Write explanations, examples, diagrams and questions in your own words. Do not paste or
   lightly reword tutorials, courses, blog posts, other repositories or question banks.
2. **No exam content, ever.** Do not submit real exam questions, reconstructions of them, "recalled" items, dumps or
   answer keys, and do not reuse the sample questions printed in the official exam guides. Anthropic's exam policy
   makes exam content confidential, and PRs containing it will be closed.
3. **Source your facts.** Check facts against official documentation, date anything time-sensitive, and label anything
   you cannot verify. Exam facts belong in [`registry.yaml`](16-certification-tracks/registry.yaml) and nowhere else.
4. **Synthetic data only.** Use fictional organisations and invented data. Never include real personal data, customer
   data or employer-confidential material.
5. **No secrets.** Never commit API keys, tokens or `.env` files. Use environment variables and `.env.example`.

The full standards are in [docs/STYLE.md](docs/STYLE.md). The list of planned files is in [docs/CONTENT-MAP.md](docs/CONTENT-MAP.md).

## Ways to contribute

| Contribution | Where | Notes |
|---|---|---|
| Fix an error or outdated fact | Any page | Cite the official source in the PR; add a row to the [verification log](25-official-resources/verification-log.md) |
| Add practice questions | `17-practice-questions/<track>/dN.json` | See the [question rules](17-practice-questions/README.md) |
| Add flashcards | `23-flashcards/decks/*.yaml` | Use unique IDs and an existing `module` path |
| Improve a lab | `19-hands-on-labs/lab-*` | Must still pass in mock mode |
| Add a certification track | `16-certification-tracks/` | See [Adding a new certification](16-certification-tracks/README.md#adding-a-new-certification) |
| Report a problem | GitHub Issues | Use the issue templates |

## Development setup

```bash
git clone <your fork>
cd claude-certification-zero-to-hero
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Before you open a pull request

```bash
python tools/validate_all.py --labs   # questions, flashcards, links, exam claims, secrets, coverage, forms, labs
python -m pytest tests -q             # engine and tooling tests
```

If you changed questions:

```bash
python tools/build_coverage.py        # regenerate coverage matrices
python tools/build_web_bundle.py      # refresh the browser mock-exam bundle
```

To preview how your change looks on the website:

```bash
pip install -r requirements-docs.txt
python tools/build_site.py --serve    # live preview at http://127.0.0.1:8000
```

Write links as you would for GitHub. The site build converts them, and sends links to code and data files to the
GitHub repository. CI builds the site in strict mode, so a broken link or anchor fails the build.

Regenerate the fixed mock forms (`python tools/build_mock_forms.py`) only when the question bank has grown
substantially. That changes the forms learners may already be using, so mention it in the PR.

## Pull request process

1. Keep each PR focused on one topic.
2. Fill in the PR template checklist.
3. CI must pass: markdown lint, internal links, schema validation, tests, lab smoke tests and secret scanning.
4. A maintainer reviews for accuracy, originality and tone. Expect questions about sources.

## Commit messages

Use the imperative mood and a short summary line, for example `Add CCAR-P domain 3 questions on retrieval strategy`.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
