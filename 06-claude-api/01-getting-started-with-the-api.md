# Getting Started with the API

> **Level:** Beginner · **Time:** ~40 min · **Exam relevance:** CCAO-F D3 · CCAR-P D3

## In plain English

The Claude apps (web, desktop, mobile) are finished products. The **Claude API** is the building material: an HTTPS
endpoint your own software calls to send Claude a request and get a response back. Everything you build, such as a
document summariser, a support assistant or an agent, sits on top of it.

To use it you need three things:

1. An account in the **Claude Console** (the developer platform at `platform.claude.com`), where you manage keys,
   workspaces, billing and usage.
2. An **API key** (or another supported credential) that identifies your organisation and workspace.
3. A way to call the API: the official **SDK** for your language (Python here) or raw HTTP.

## Why it matters

- The API is how Claude becomes part of a business process rather than a separate tab.
- Getting credential handling right on day one prevents the most common and most expensive beginner mistake: a leaked
  key.
- Choosing the integration mechanism (direct API, a cloud platform, MCP, a CLI) is an exam objective for architects
  (CCAR-P-3.7), and authentication design is another (CCAR-P-3.2).

## How it works

### The Console, organisations and workspaces

In the Console you belong to an **organisation**, which owns billing. Inside it, **workspaces** group API keys,
usage limits and resources (for example uploaded files and Skills). Common patterns:

| Workspace | Purpose |
|---|---|
| `dev` | Individual experimentation, low spend limits |
| `staging` | Integration testing with production-like settings |
| `prod-<app>` | One per production application, so usage, limits and keys are separated |

Workspaces also matter technically: prompt caches and uploaded files are scoped to a workspace on the Claude API, so
splitting one application's traffic across workspaces reduces cache reuse (see
[prompt caching](../04-context-engineering/03-prompt-caching.md)).

### Credentials

| Credential | Use it for | Notes |
|---|---|---|
| API key (in `ANTHROPIC_API_KEY`) | Most applications and scripts | Create in the Console; shown once; scope to a workspace |
| `ant auth login` profile | Local development with the Anthropic CLI | The SDKs read the active profile automatically when no key is set |
| Workload identity federation | Production workloads in clouds or CI | Exchanges your platform's identity token for short-lived credentials; no long-lived key to leak |
| Cloud-platform credentials | Claude via AWS, Google Cloud or Azure | AWS IAM / SigV4, Google Application Default Credentials, Microsoft Entra ID or keys; see [cloud platforms](07-cloud-platforms.md) |
| Admin API key | Organisation administration (members, workspaces, keys) | Separate, more powerful; never used for inference code |

The SDK resolves credentials in a documented order (as of 2026-10-24): `ANTHROPIC_API_KEY`, then
`ANTHROPIC_AUTH_TOKEN`, then a CLI profile, then workload identity federation variables. An unset
`ANTHROPIC_API_KEY` therefore does not necessarily mean "no credentials".

### Keep keys out of code

The rule in this repository, and in any serious engineering team: **never hardcode credentials**.

```bash
# macOS / Linux: set for the current shell session
export ANTHROPIC_API_KEY="paste-your-key-here"

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "paste-your-key-here"
```

For local projects, a `.env` file that is listed in `.gitignore` is common; commit only a `.env.example` with
placeholder values. In production, use a secrets manager or workload identity federation. See
[secrets management](../12-ai-security/10-secrets-management.md).

### Install the SDK

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install anthropic              # the 1.x SDK requires Python 3.10+
```

Extras exist for cloud platforms, for example `pip install "anthropic[vertex]"` or `"anthropic[aws]"` (see
[cloud platforms](07-cloud-platforms.md)).

### Your first request

```python
import anthropic

client = anthropic.Anthropic()  # finds ANTHROPIC_API_KEY (or another supported credential)

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": "In two sentences, what is a context window?"}],
)

if response.stop_reason == "end_turn":
    for block in response.content:
        if block.type == "text":
            print(block.text)
else:
    print("Stopped early:", response.stop_reason)

print("request id:", response._request_id)   # quote this when reporting problems
print("usage:", response.usage.input_tokens, "in /", response.usage.output_tokens, "out")
```

The same request over raw HTTP:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-5-5",
    "max_tokens": 1000,
    "messages": [{"role": "user", "content": "In two sentences, what is a context window?"}]
  }'
```

Three headers matter: `x-api-key` (authentication), `anthropic-version` (the API version your code was written
against) and `content-type`. Beta features add an `anthropic-beta` header; the SDK sets it when you pass `betas=[...]`.

### Discovering models

Model IDs and capabilities change. The Models API returns the models your organisation can use, with their context
window (`max_input_tokens`), maximum output (`max_tokens`) and capabilities:

```python
for model in client.models.list():
    print(model.id, model.max_input_tokens, model.max_tokens)
```

As of 2026-10-24 the current models include `claude-opus-5-5` (default in this repository), `claude-sonnet-5-5`,
`claude-haiku-5-5` and `claude-fable-5-1`. Use IDs exactly as published, with no date suffix, and check the
[models overview](https://platform.claude.com/docs/en/about-claude/models/overview) for the current list. Model choice
is covered in [Module 05](../05-claude-products-and-models/03-model-selection.md).

### Client configuration worth knowing

| Setting | Default (Python SDK, as of 2026-10-24) | When to change |
|---|---|---|
| `timeout` | 10 minutes | Lower for interactive endpoints; use streaming for long outputs |
| `max_retries` | 2 (connection errors, 408, 409, 429, 5xx) | Raise for batch-like jobs; 0 when your own retry layer handles it |
| `base_url` / `ANTHROPIC_BASE_URL` | Anthropic's API | Corporate gateways or proxies |
| `ANTHROPIC_LOG` | off | `info` or `debug` for troubleshooting |

## Example

*Northwind Lending* (fictional) gives each developer a personal `dev` workspace key with a low spend limit, and
production services get credentials through workload identity federation. A small start-up check, run when each
service boots, fails fast with a helpful message rather than at the first user request:

```python
import os
import sys

import anthropic


def check_claude_access(model: str = "claude-opus-5-5") -> None:
    if not any(os.environ.get(v) for v in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
                                            "ANTHROPIC_FEDERATION_RULE_ID")):
        print("No Claude credential in the environment. See the team runbook.", file=sys.stderr)
    client = anthropic.Anthropic()
    try:
        info = client.models.retrieve(model)
        print(f"OK: {info.id} available, context window {info.max_input_tokens} tokens")
    except anthropic.AuthenticationError:
        sys.exit("Credential rejected (401). Check the key or federation settings.")
    except anthropic.NotFoundError:
        sys.exit(f"Model {model} not available to this organisation (404).")
    except anthropic.APIConnectionError:
        sys.exit("Cannot reach the API. Check network, proxy or base_url.")


if __name__ == "__main__":
    check_claude_access()
```

> **Cost:** listing and retrieving models does not generate tokens; the first-request example does and requires API
> credits (live mode).

## Enterprise use case

*Contoso Health* (fictional) set up its Claude API estate before the first pilot:

- One organisation; workspaces per environment and per application; spend limits on each.
- Developer keys only in `dev`, rotated every 90 days and revoked automatically when someone leaves.
- Production services authenticate through workload identity federation from their cloud runtime, so there are no
  long-lived production keys at all.
- An internal gateway in front of the API adds request logging, data-loss-prevention checks and per-team cost
  attribution.
- A pre-commit hook and the CI secret scanner block commits containing key patterns.

Because the healthcare data involved has residency and retention requirements, the architecture review also compared
direct API access with the cloud platforms (see [cloud platforms](07-cloud-platforms.md) and
[data governance and compliance](../13-enterprise-ai-architecture/05-data-governance-and-compliance.md)).

## Common mistakes

- **Hardcoding a key** in a notebook or script that later gets shared or committed.
- **Calling the API from a browser or mobile app** with an embedded key. Anyone can extract it. Call from your backend.
- **Inventing model IDs** or adding date suffixes. Copy IDs from the models page or the Models API.
- **One key for everything.** You lose cost attribution and must rotate everything when one leaks.
- **Setting both `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN`.** The SDK may send both and the request is rejected.
- **Ignoring `stop_reason`.** Even a "hello world" should check it.

## Security considerations

- Store keys in a secrets manager; inject them as environment variables at run time.
- Prefer short-lived credentials (workload identity federation, cloud IAM) for production.
- Apply least privilege: separate workspaces, spend limits and keys per application and environment.
- Rotate keys, revoke on departure, and monitor usage for anomalies.
- If a key leaks: revoke it in the Console immediately, issue a new one, review usage logs, and run your incident
  process (see [incident response](../15-production-operations/07-incident-response.md)).
- Log the `request-id` of each call (not the key) so you can trace issues with Anthropic support.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `AuthenticationError` (401) | Missing, wrong or revoked key; OAuth token sent as an API key | Check the environment variable in the running process; regenerate the key |
| `PermissionDeniedError` (403) | Workspace or organisation not permitted for this action | Check workspace settings and access in the Console |
| `NotFoundError` (404) on a model | Typo, retired ID or model not available to you | List models with `client.models.list()` |
| `ModuleNotFoundError: anthropic` | SDK not installed in the active environment | Activate the virtual environment; `pip install anthropic` |
| Requests hang then time out | Network, proxy or firewall | Set proxy configuration or `base_url`; test with cURL |

More in [troubleshooting API errors](../24-troubleshooting/api-errors.md).

## Check your understanding

1. Why should production services prefer workload identity federation or cloud IAM over long-lived API keys?
2. Name two reasons to use separate workspaces for separate applications.
3. What three HTTP headers does a basic Messages API request need?
4. A teammate wants to call the API directly from a single-page web app. What do you advise?

<details>
<summary>Answers</summary>

1. They issue short-lived credentials tied to the workload's identity, so there is no long-lived secret to leak,
   rotate or store.
2. Any two of: separate spend limits and cost attribution; independent key rotation and revocation; isolation of
   resources such as files and caches; different access controls per environment.
3. `x-api-key` (or `Authorization: Bearer` for OAuth tokens), `anthropic-version` and `content-type: application/json`.
4. Do not embed a key in client-side code. Route requests through a backend service that holds the credential,
   authenticates the user and enforces limits.

</details>

## Further reading

- [Get started with Claude](https://platform.claude.com/docs/en/get-started) (Anthropic docs)
- [API overview](https://platform.claude.com/docs/en/api/overview) (Anthropic docs)
- [Client SDKs](https://platform.claude.com/docs/en/api/client-sdks) (Anthropic docs)
- [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) (Anthropic docs)
- [Lab 01 — First Claude interaction](../19-hands-on-labs/lab-01-first-claude-interaction/README.md)
- Next page: [The Messages API](02-messages-api.md)
