# Model Context Protocol (MCP) Cheat Sheet

> **As of 2026-10-24**, checked against the specification at
> [modelcontextprotocol.io](https://modelcontextprotocol.io/specification/latest), whose current revision is
> **2026-07-28**. That revision made the protocol stateless (no `initialize` handshake); servers and clients that
> must talk to older peers still support the earlier, handshake-based revisions (2025-11-25 and before). Full
> lessons: [08 · Model Context Protocol](../08-model-context-protocol/README.md).

## 1. What MCP is, in one line

An open, JSON-RPC 2.0 based protocol that lets an AI application (the **host**) connect to external systems
(**servers**) through a standard interface, so one integration works across many AI applications.

## 2. Roles

| Role | What it is | Example |
|---|---|---|
| Host | The AI application the user interacts with | Claude Desktop, Claude Code, your own agent |
| Client | The connector inside the host that talks to one server | One client per configured server |
| Server | A program that exposes context and capabilities | A ticketing-system server, a file-search server |

## 3. Primitives

| Side | Primitive | Controlled by | Purpose |
|---|---|---|---|
| Server | **Tools** | Model | Functions the model can call (`tools/list`, `tools/call`) |
| Server | **Resources** | Application | Data to read into context (`resources/list`, `resources/read`) |
| Server | **Prompts** | User | Reusable templates and workflows (`prompts/list`, `prompts/get`) |
| Client | **Elicitation** | User | Server asks the user for more information |
| Client | **Sampling** | Host | Server asks the host's model for a completion |
| Client | **Roots** | Host | Host tells the server which directories or URIs are in scope |

Utilities: progress, cancellation, logging, argument completion. Optional **extensions** (negotiated through
capabilities) include Tasks (long-running work), MCP Apps (interactive UI) and Skills over MCP.

## 4. Transports

| Transport | How it works | Use for |
|---|---|---|
| **stdio** | Host launches the server as a subprocess; newline-delimited JSON-RPC over stdin/stdout | Local tools, developer machines |
| **Streamable HTTP** | Each message is an HTTP POST to one endpoint; replies are JSON or a request-scoped SSE stream | Remote and shared servers |
| HTTP+SSE (legacy) | Older two-endpoint transport | Deprecated; only for old servers |

## 5. Message shapes

```json
{"jsonrpc": "2.0", "id": 7, "method": "tools/call",
 "params": {"name": "search_tickets", "arguments": {"query": "printer", "limit": 5},
            "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
                      "io.modelcontextprotocol/clientCapabilities": {}}}}
```

- Every request in the current revision carries its protocol version and client capabilities in `_meta`
  (mirrored to the `MCP-Protocol-Version` header on HTTP).
- `server/discover` lets a client learn a server's supported versions up front.
- An unsupported version returns error `-32022` (`UnsupportedProtocolVersion`) listing supported versions.
- Tool **execution** errors come back in the tool result (so the model can react); **protocol** errors use JSON-RPC
  `error` objects.

## 6. A minimal Python server (official SDK, `MCPServer`, formerly FastMCP)

```python
from mcp.server import MCPServer

mcp = MCPServer("acme-inventory")

@mcp.tool()
def stock_level(sku: str) -> dict:
    """Return the on-hand quantity for one SKU. Use for any stock or availability question."""
    data = {"AC-100": 42, "AC-200": 0}          # synthetic data
    if sku not in data:
        raise ValueError(f"Unknown SKU {sku}")   # surfaces as a tool error the model can see
    return {"sku": sku, "on_hand": data[sku]}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

As of 2026-10-24, the `mcp` package is at version 2 (2.3.0 on PyPI), which renamed `FastMCP` to `MCPServer` and removed
the `mcp.server.fastmcp` module, per the SDK's
[migration guide](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/migration.md). The code above follows
the official [server quickstart](https://modelcontextprotocol.io/docs/develop/build-server). On 1.x, use
`from mcp.server.fastmcp import FastMCP` instead. Confirm that your SDK version implements the protocol revision your
host expects.

## 7. Using MCP with Claude

| Surface | How |
|---|---|
| Claude Code | `claude mcp add --transport http <name> <url>` or `--transport stdio <name> -- <command>`; scopes `local`, `project` (`.mcp.json`), `user`; OAuth via `/mcp` |
| Claude apps | Connectors (remote MCP servers) added by users or admins, subject to plan and organisation settings |
| Claude API | MCP connector: `mcp_servers=[{"type": "url", "url": ..., "name": ...}]` **plus** `tools=[{"type": "mcp_toolset", "mcp_server_name": ...}]` with beta `mcp-client-2025-11-20` |
| Your own agent | Use an MCP client library, convert listed tools to Claude tool definitions, run the tool loop |

## 8. Authorization (HTTP transports)

- Based on **OAuth 2.1**. The MCP server is an OAuth resource server; the client is an OAuth client.
- Servers **must** publish Protected Resource Metadata (RFC 9728); clients use it to find the authorization server.
- Clients **must** send the `resource` parameter (RFC 8707) so tokens are bound to that one server (audience).
- PKCE is required; client registration via Client ID Metadata Documents (preferred), pre-registration or Dynamic
  Client Registration (deprecated, kept for compatibility).
- Servers **must** validate the token audience and **must not** accept or pass through tokens issued for other
  services (no token passthrough).
- stdio servers do not use this flow; they take credentials from the environment.
- 401 = missing or invalid token; 403 with `insufficient_scope` = step-up authorization needed.

## 9. Security checklist

| Risk | Control |
|---|---|
| Malicious or compromised server | Install from trusted sources, pin versions, review code, run in a sandbox |
| Tool poisoning (hidden instructions in tool descriptions) | Review descriptions; treat annotations as untrusted; alert on description changes |
| Indirect prompt injection via tool results | Treat results as data; human approval for consequential actions |
| Over-broad permissions | Least-privilege scopes; separate read and write tools; allowlists per server |
| Confused deputy / token passthrough | Audience-bound tokens; never forward user tokens to other services |
| Local server exposed to the network | Bind to localhost, validate `Origin` headers, require auth |
| Data exfiltration through chained tools | Limit outbound tools; log every call; DLP on outputs |

More: [08 · MCP security](../08-model-context-protocol/05-mcp-security.md),
[12 · MCP server security](../12-ai-security/08-mcp-server-security.md) and the official
[security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices).

## 10. MCP versus alternatives

| Option | Choose when |
|---|---|
| Direct tool use (function calling) | One application, a few tools you own |
| MCP server | The same integration should work across hosts and teams |
| Agent Skills | You need packaged instructions and scripts loaded on demand, not a live connection |
| Plain REST call from your code | No model needs to decide when to call it |

## Further reading

- [MCP introduction](https://modelcontextprotocol.io/docs/getting-started/intro)
- [Specification (latest)](https://modelcontextprotocol.io/specification/latest)
- [Claude Code MCP guide](https://code.claude.com/docs/en/mcp)
- [Claude API MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
