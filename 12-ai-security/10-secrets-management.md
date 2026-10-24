# Secrets Management for AI Systems

> **Level:** Intermediate · **Time:** ~35 min · **Exam relevance:** CCAR-P D3 (3.2), CCAR-P D5 (5.1), CCAR-P D7 (7.1)

## In plain English

Secrets are the values that prove identity to other systems: API keys, OAuth tokens, database passwords, signing
keys, private certificates. AI systems add two new places where secrets leak. First, the model's context window:
anything in it can appear in output, logs or a tool call steered by an attacker. Second, agents that write and run
code or read repositories can find secrets lying around and use them.

The rule for this page fits on one line: **the model should never see a secret, and the agent should only reach the
secrets its tools need, at the moment they need them.**

## Why it matters

- A leaked Anthropic API key lets someone spend your budget and, depending on workspace configuration, access
  stored resources such as files. A leaked downstream key can be far worse.
- Coding agents (including Claude Code) operate in repositories and shells where `.env` files, cloud credentials and
  SSH keys often sit within reach.
- Secrets in prompts, logs and traces turn every observability tool into a secrets store.

## How it works

### Where secrets leak in LLM systems

| Leak path | Example | Control |
|---|---|---|
| System prompt | "Use API key sk-... to call the CRM" | Never. Tools obtain credentials outside the model |
| Tool results | A config file or environment dump returned to the model | Redact secrets in tool results; do not build tools that read secret stores |
| Model output | Model echoes a key it saw in a file | Output scanning for secret patterns; block before display |
| Logs and traces | Request bodies logged with headers or tool arguments | Structured logging with allow-listed fields; redaction; metadata-only tracing |
| Agent filesystem | `.env`, `~/.aws/credentials`, `~/.ssh` readable by a coding agent | Sandboxing, permission deny rules, credential-free dev containers |
| Agent memory | Agent stores a token in long-term memory "for next time" | Memory write filters; never allow credentials in memory |
| Source control | Example scripts with real keys committed | Secret scanning in CI and pre-commit; `.env.example` with placeholders |
| Client-side apps | API key shipped in a browser or mobile app | Always call Claude through your backend; never expose keys client-side |

### Principles

1. **Read from the environment or a secret manager at runtime.** Never hardcode. The Anthropic SDKs read
   `ANTHROPIC_API_KEY` (or other configured credential sources such as an `ant auth login` profile or workload
   identity federation) automatically.
2. **Prefer short-lived credentials** issued by your identity platform over static keys (see
   [agent identity and permissions](09-agent-identity-and-permissions.md)).
3. **Broker, do not hand over.** Tools receive credentials from a broker or have them injected at the network
   layer; the model gets results, not keys.
4. **Separate per environment and per workload.** Distinct keys per environment and per application, each in its own
   workspace with limits, so a leak is contained and attributable.
5. **Rotate and revoke.** Have a tested procedure; practise it before you need it.
6. **Detect.** Scan repositories, logs and model outputs for secret patterns.

### Coding agents

For Claude Code, the [security documentation](https://code.claude.com/docs/en/security) describes protections you can
build on: permission rules (including `permissions.deny`), sandboxed bash with filesystem and network isolation,
running the whole tool in a sandbox runtime or dev container, and secure credential storage for Claude Code's own
credentials (macOS Keychain where available). Use deny rules to keep the agent away from secret files, for example:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(~/.aws/**)",
      "Read(~/.ssh/**)",
      "Bash(printenv*)",
      "Bash(env)"
    ]
  }
}
```

Check the exact rule syntax for your version in
[Claude Code permissions](https://code.claude.com/docs/en/permissions) and in this repository's
[permissions and settings page](../09-claude-code/04-permissions-and-settings.md). Deny rules match commands as
written, so pair them with sandboxing for enforcement that does not depend on command text.

## Example

A redaction layer used in two places: on tool results before they are returned to Claude, and on log records before
they are written. It uses the standard library and a small set of patterns; extend the list for the credential types
your organisation uses.

```python
"""redact.py - remove secret-shaped values from tool results and log records."""
import json
import re

PATTERNS = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("aws_access_key", re.compile(r"\b(AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----")),
    ("password_assignment", re.compile(r"(?i)\b(password|passwd|secret|api_key)\s*[:=]\s*\S+")),
]
SENSITIVE_KEYS = {"authorization", "x-api-key", "password", "token", "secret", "api_key", "cookie"}


def redact_text(text: str) -> tuple[str, list[str]]:
    hits = []
    for name, pattern in PATTERNS:
        if pattern.search(text):
            hits.append(name)
            text = pattern.sub(f"[REDACTED:{name}]", text)
    return text, hits


def redact_obj(obj):
    """Recursively redact dict/list structures (e.g. JSON tool results or log records)."""
    if isinstance(obj, dict):
        return {k: ("[REDACTED]" if k.lower() in SENSITIVE_KEYS else redact_obj(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_obj(v) for v in obj]
    if isinstance(obj, str):
        return redact_text(obj)[0]
    return obj


if __name__ == "__main__":
    tool_output = {"file": "deploy.cfg",
                   "content": "region=eu-west-1\napi_key = sk-ant-api03-EXAMPLEEXAMPLEEXAMPLEEXAMPLE\n",
                   "headers": {"Authorization": "Bearer abc.def.ghi"}}
    print(json.dumps(redact_obj(tool_output), indent=2))
```

And the right way to construct a client, with no key in code:

```python
import anthropic

# Reads ANTHROPIC_API_KEY, an `ant auth login` profile, or workload identity federation settings.
client = anthropic.Anthropic()
```

Treat redaction as a safety net. The primary control is not giving the agent tools that can read secrets at all.

## Enterprise use case

*Acme Logistics* rolls out Claude Code to 80 developers. A review of the pilot finds that developers keep production
database URLs with embedded passwords in `.env` files, and that two internal MCP servers were configured with literal
API keys in `.mcp.json` committed to Git.

Remediation:

1. Pre-commit and CI secret scanning across all repositories, with the two committed keys rotated immediately.
2. MCP configurations changed to reference environment variables populated by the developer's secret manager login,
   and later to OAuth-based remote servers.
3. Managed settings push deny rules for `.env*`, cloud credential directories and SSH keys, and enable sandboxed bash.
4. Development databases use short-lived credentials issued per developer session; production credentials are not
   available on laptops.
5. Separate Claude API workspaces and keys for development, CI and production, each with spend limits.

## Common mistakes

- Putting keys in the system prompt so the model can call an API itself.
- Calling the Claude API directly from a browser with an embedded key.
- Logging the full HTTP request, including the `x-api-key` header, while debugging and leaving it on.
- One key shared across environments and teams, so rotation breaks everything.
- Relying on "please do not read .env" in `CLAUDE.md` instead of permission rules and sandboxing.

## Security considerations

- If a secret ever reaches the model's context, treat it as exposed: rotate it, even if you see no misuse.
- Some Claude features persist data (for example files uploaded through the Files API, or stateful agent sessions).
  Do not upload files containing secrets.
- Secret scanning tools have false negatives. Combine pattern-based scanning with structural controls.
- Build a revocation runbook: where each key lives, who owns it, how to rotate it in minutes. This feeds
  [incident response](../15-production-operations/07-incident-response.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| SDK raises an authentication error in CI | Key not provided to the job, or both `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` set | Provide one credential source via the CI secret store |
| Redaction mangles legitimate output | Over-broad patterns | Narrow patterns; whitelist known safe formats |
| Agent still reads secrets through Bash | Deny rules only cover file tools | Enable sandboxing; deny environment-dumping commands |

## Check your understanding

1. State the one-line rule for secrets in AI systems.
2. Why is a key in the system prompt a problem even if the model is told never to reveal it?
3. Name two places, other than source code, where AI systems commonly leak secrets.
4. What should you do if a secret is found in a model's context?

<details>
<summary>Answers</summary>

1. The model should never see a secret, and the agent should only reach the secrets its tools need, when they need
   them.
2. System prompts can be extracted and the model can be manipulated; also, prompts are logged and cached. Instructions
   are not access control.
3. Any two of: logs and traces, tool results, model output, agent memory, agent-readable filesystems, client-side
   apps.
4. Treat it as exposed and rotate it, then fix the path that let it in.

</details>

## Further reading

- Anthropic: [Claude Code security](https://code.claude.com/docs/en/security) and
  [permissions](https://code.claude.com/docs/en/permissions)
- Anthropic: [API overview](https://platform.claude.com/docs/en/api/overview) (authentication)
- OWASP: [Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- In this repository: [environment setup](../00-getting-started/environment-setup.md),
  [Lab 15: sensitive data protection](../19-hands-on-labs/lab-15-sensitive-data-protection/README.md)

<!-- page-nav:start -->
---

[← Previous: Agent Identity and Permissions](09-agent-identity-and-permissions.md) · [Module overview](README.md) · [Next: Logging and Auditability →](11-logging-and-auditability.md)
<!-- page-nav:end -->
