# Troubleshooting: Labs and This Repository

Problems running the hands-on labs, the projects, the mock-exam engine or the repository's checks. Setup guide:
[00 · Environment setup](../00-getting-started/environment-setup.md). Labs: [19 · Hands-on labs](../19-hands-on-labs/README.md).

## How the labs run

Every lab imports the shared helper [`19-hands-on-labs/common/claude_lab.py`](../19-hands-on-labs/common/claude_lab.py):

| Variable | Default | Effect |
|---|---|---|
| `CLAUDE_LAB_MODE` | `mock` | `mock` runs offline with canned responses (free); `live` calls the real API |
| `CLAUDE_LAB_MODEL` | `claude-opus-5-5` | Model used by most labs in live mode |
| `CLAUDE_LAB_FAST_MODEL` | `claude-haiku-5-5` | Cheaper model for cost-sensitive steps |
| `ANTHROPIC_API_KEY` | unset | Needed only in live mode (or an `ant auth login` profile) |

Each lab prints a banner showing the mode: `MOCK — offline, no credits used` or `LIVE — uses API credits`.

> **Cost:** requires API credits (live mode).

## Mock mode versus live mode

### The lab output looks fake

**Symptom:** answers such as `[mock response] You asked: ...`.

**Cause:** you are in mock mode (the default). That is expected: mock mode exercises the code path, not the model.

**Fix:** to see real answers, set live mode in the same shell that runs the lab:

```bash
export ANTHROPIC_API_KEY="..."        # from your secrets manager; never commit it
export CLAUDE_LAB_MODE=live
python 19-hands-on-labs/lab-01-first-claude-interaction/lab.py
```

### Works in mock mode, fails in live mode

| Symptom | Likely cause | Fix |
|---|---|---|
| `Live mode needs the SDK` | `anthropic` not installed | `pip install -r 19-hands-on-labs/requirements.txt` in the active environment |
| 401 authentication error | Key unset in this shell, or wrong key | Export the key in the shell that runs Python; check with a presence/length print, never print the key |
| 404 model not found | `CLAUDE_LAB_MODEL` mistyped or not available to your organisation | Unset it to use the default, or use an exact ID |
| 429 rate limit | Low tier, loops in a lab | Wait for `retry-after`; run one lab at a time |
| Different output shape | Real responses include thinking blocks, usage and varied wording | Use `text_of(response)`; do not assert on exact text |

### Works in live mode, fails in mock mode

**Symptom:** `ValueError` raised before any network call, for example:

- `assistant prefill is not supported on current Claude models`
- `'temperature' is not supported on current Claude models`
- `forced tool_choice is not supported on current models`
- `the first message must have role 'user'`

**Cause:** the mock client validates requests against current API rules. If you are on an older model in live mode,
the real API may accept what the mock rejects, but current models reject it too.

**Fix:** correct the request (see [API errors](api-errors.md#400-invalid_request_error)). The mock is catching a bug
early.

### A lab's mock responder returns the wrong thing

**Cause:** responders registered with `@register_mock` are tried newest first; a responder returning `None` passes to
the next. A generic responder registered last can shadow a specific one.

**Fix:** make each responder check the request (for example the last user message or the tools present) and return
`None` when it does not apply.

## Virtual environment problems

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: yaml` / `jsonschema` / `pytest` | Tools run with the system Python | Use `.venv/bin/python tools/...` or activate the venv first |
| `ModuleNotFoundError: claude_lab` | Running a lab from an unexpected working directory or a copied file | Run the lab file from the repository root, unmodified paths |
| `python: command not found` / wrong version | Python 3.10+ not installed or not first on `PATH` | Install 3.10+; `python3 -m venv .venv` |
| Packages installed but still missing | Installed into a different environment | `which python` and `python -m pip --version` should both point into `.venv` |
| Broken venv after a Python upgrade | The venv links to a removed interpreter | Delete `.venv` and recreate it |

Create a clean environment:

```bash
python3 -m venv .venv
. .venv/bin/activate                          # Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pip install -r 19-hands-on-labs/requirements.txt   # only needed for live mode
```

## Repository checks

| Command | What it checks |
|---|---|
| `python tools/check_links.py` | Every relative Markdown link and heading anchor resolves |
| `python tools/check_exam_claims.py` | Pages stating exam facts link to the registry and match it |
| `python tools/validate_questions.py` | Practice-question banks match the schema and objectives |
| `python tools/flashcards.py` | Flashcard decks: required fields, unique IDs, valid objectives and module paths |
| `python tools/scan_secrets.py` | No credentials committed |

### Link checker failures

| Message | Cause | Fix |
|---|---|---|
| `broken link -> ../path/file.md` | Target missing or path wrong relative to **this** file | Fix the relative path; use only paths in [CONTENT-MAP](../docs/CONTENT-MAP.md) |
| `missing anchor #...` | Heading text changed, or anchor slug computed differently | Use GitHub-style slugs: lowercase, punctuation removed, spaces to hyphens |
| `link escapes repository` | Too many `../` | Count directory levels from the linking file |

Links inside code spans and fenced code blocks are ignored by the checker. External `http(s)` links are checked
separately in CI.

### Exam-claims failures

**Message:** `states exam facts but does not link registry.yaml / exam-facts.md / official source`.

**Cause:** the page mentions a pass mark, fee or cut score without a source link.

**Fix:** add a link to [`registry.yaml`](../16-certification-tracks/registry.yaml) or
[exam-facts.md](../25-official-resources/exam-facts.md), and make sure the numbers match the registry.

### Flashcard validation failures

| Message | Fix |
|---|---|
| `duplicate card id` | IDs must be unique across all decks (`FUN-FC-001`, `CCAO-F-FC-...`) |
| `unknown objective` | Use an objective ID from the registry, or omit `objective` |
| `module path does not exist` | `module` must be a CONTENT-MAP path that exists in the repository |
| `empty 'front'` / `'back'` | Fill both sides; quote YAML strings containing `:` or `#` |

## Mock exam engine

**Symptom:** `run_mock_exam.py` reports no questions or an unknown track.

**Fix:** run the question validator first; check the track slug (`ccao-f`, `ccar-p`); run from the repository root.
See [18 · Mock examinations](../18-mock-examinations/README.md).

## Still stuck

Open an issue with: the command you ran, the full error output (with any secrets removed), your OS, Python version
and `CLAUDE_LAB_MODE`. See [CONTRIBUTING](../CONTRIBUTING.md).
