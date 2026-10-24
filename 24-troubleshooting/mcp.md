# Troubleshooting: MCP (Model Context Protocol)

> **As of 2026-10-24.** The current MCP specification revision is **2026-07-28** (stateless, per-request
> metadata, no `initialize` handshake); many servers and clients still speak earlier handshake-based revisions. Check
> the [specification](https://modelcontextprotocol.io/specification/latest) and the
> [Claude Code MCP docs](https://code.claude.com/docs/en/mcp). Concepts: [08 · MCP](../08-model-context-protocol/README.md).

## Quick checks

| Where | Check |
|---|---|
| Claude Code | `claude mcp list`, `/mcp` (status, reconnect, sign in), `claude mcp get <name>` |
| Claude apps | The connector's status in settings; your organisation's allowed connectors |
| Your own client | Server stderr (stdio) or HTTP logs; the raw JSON-RPC exchange |
| Any | Run the server by hand; test it with the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) |

## Connection problems

### Server never starts (stdio)

**Symptom:** status shows failed or pending; no tools appear.

**Likely causes:** wrong command or path; missing runtime (`python`, `node`, `uvx`); dependencies not installed in the
environment the host uses; required environment variables missing; the server prints logs to **stdout**, corrupting
the JSON-RPC stream.

**Diagnosis:** run the exact command from your configuration in a terminal; check the host's MCP logs; confirm the
interpreter path (a virtual environment active in your shell is not active for the host).

**Fix:** use absolute paths to the interpreter; pass variables with `--env KEY=value` (or the config `env` block);
send server logs to stderr only; put options for Claude Code before `--` and the server command after it:

```bash
claude mcp add --transport stdio --env INVENTORY_DB="$INVENTORY_DB" inventory \
  -- /opt/venvs/inventory/bin/python /opt/servers/inventory/server.py
```

### Remote server unreachable (Streamable HTTP)

**Symptom:** connection refused, TLS errors, 404 or 405 responses.

**Likely causes:** wrong URL or path (many servers serve on `/mcp`); a proxy or firewall; certificate issues; the
server only supports the deprecated HTTP+SSE transport; version mismatch between client and server eras.

**Diagnosis:** `curl -i` the endpoint (expect a JSON-RPC style error rather than a network failure); check the
transport type in your config; read the server's supported versions (`server/discover` on current servers, or the
`UnsupportedProtocolVersion` error data, code `-32022`).

**Fix:** correct the URL and `--transport http`; use `--transport sse` only for legacy servers; update the SDK on the
older side so both speak a common revision; configure proxy settings per your host's docs.

### Slow start or timeouts

**Fix:** raise `MCP_TIMEOUT` (start-up, milliseconds) and `MCP_TOOL_TIMEOUT` (tool calls) in Claude Code; make the
server lazy-load heavy resources; add progress notifications for long operations.

## Authentication problems

**Symptom:** 401 Unauthorized, an endless sign-in loop, or 403 on some tools only.

**Likely causes:**

| Signal | Meaning |
|---|---|
| 401 with `WWW-Authenticate: Bearer resource_metadata=...` | Not signed in or token expired; client must run the OAuth flow |
| 403 with `error="insufficient_scope"` | Token valid but lacks a scope; step-up authorization needed |
| Token accepted by one server but rejected by another | Audience binding: tokens are issued for one server (`resource` parameter) |
| Works locally, fails in CI | Interactive OAuth cannot complete headless |

**Diagnosis:** inspect the `WWW-Authenticate` header; fetch the protected resource metadata URL it names; confirm the
authorization server's metadata is reachable; check the clock (token expiry).

**Fix:**

- In Claude Code, run `/mcp` and sign in, or `claude mcp login <name>` (`--no-browser` over SSH); "Clear
  authentication" and retry if tokens are stale.
- Request the scopes named in the challenge; ask the server owner to emit all needed scopes in one challenge.
- For headless use, use a credential mechanism the server supports for machine clients, injected from a secrets
  store; never paste tokens into prompts or committed config.
- Server authors: implement Protected Resource Metadata (RFC 9728), validate token audience (RFC 8707), never pass
  client tokens through to downstream APIs.
- For stdio servers, credentials come from environment variables, not the OAuth flow.

## Tool discovery problems

**Symptom:** server connected but tools are missing, outdated or never used.

**Likely causes:**

- The server registered no tools (exception during registration, or capability not declared).
- The tool list changed but the client cached the old one.
- Names collide across servers, or contain characters the host rejects.
- Too many tools: the host defers or truncates, or Claude picks badly among similar tools.
- Permission rules deny the tools (`mcp__server__*` in a deny list).
- Descriptions are vague, so Claude never chooses the tool.

**Diagnosis:** list tools with the Inspector; in Claude Code check `/mcp` for the tool list and `/permissions` for deny
rules; ask Claude which tools it can see.

**Fix:** fix registration errors (check server stderr); reconnect (`/mcp` → reconnect) after changes; give tools
specific names and descriptions saying when to use them; disable servers you do not need; allow the tools explicitly
(`mcp__inventory__*`) if your policy permits.

## Results problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Output truncated or saved to a file | Exceeds `MAX_MCP_OUTPUT_TOKENS` (default 25,000 in Claude Code) | Paginate, filter server-side, or raise the limit deliberately |
| Claude ignores an error | Server raised a protocol error instead of returning a tool error | Return tool-level errors with a clear message so the model can adapt |
| Odd instructions appear in results | Content from external data (possible indirect prompt injection) | Treat results as untrusted; sanitise; require approval for consequential follow-up actions |

## Security red flags while debugging

Stop and review if you see any of these:

- A tool description that tells the model to read unrelated files, call other tools or contact external URLs.
- A server that asks for broad credentials it does not need.
- A local HTTP server listening on `0.0.0.0` without authentication or `Origin` checks.
- Tool definitions that change between sessions without a release.

See [08 · MCP security](../08-model-context-protocol/05-mcp-security.md) and
[12 · MCP server security](../12-ai-security/08-mcp-server-security.md).
