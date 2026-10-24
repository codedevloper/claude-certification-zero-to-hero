# Building an MCP Server

> **Level:** Intermediate · **Time:** ~60 min · **Exam relevance:** CCAR-P 3.7, 3.1

## In plain English

An MCP server is a small program that says "here are the things I can do" and then does them when asked. With the official Python SDK you write ordinary Python functions, add a decorator to each one, and the SDK handles the protocol: building JSON Schemas from your type hints, validating arguments, answering discovery requests and speaking stdio or HTTP.

In this page you build a read-only server for a fictional IT team, *Contoso IT Assets*, with:

- two **tools** (search assets, get one asset),
- one **resource** (the list of office sites), and
- one **prompt** (a site audit template users can pick).

You then test it without a model, inspect it with the MCP Inspector, and connect it to Claude Code and Claude Desktop.

> **Version note:** The code on this page targets the **MCP Python SDK v2** (`mcp` package; 2.3.0 is the latest release on PyPI as of 2026-10-24), verified against the [python-sdk README and docs](https://github.com/modelcontextprotocol/python-sdk) and the [official server tutorial](https://modelcontextprotocol.io/docs/develop/build-server); the server and test script below were run against `mcp` 2.3.0 on 2026-10-24. v2 uses `from mcp.server import MCPServer`. Examples you find online using `FastMCP` from `mcp.server.fastmcp` are from the 1.x era. The SDK requires **Python 3.11 or later**.

## Why it matters

- **Packaging an integration once** for every MCP host is the main reason to choose MCP (CCAR-P-3.7).
- **Server design is tool design.** Names, descriptions, schemas and errors decide how well Claude uses your server; everything in [Tool design best practices](../07-tool-use-and-function-calling/05-tool-design-best-practices.md) applies.
- **Server authors own the first line of defence**: least privilege, input validation and safe error messages live here.

## How it works

### How the SDK maps Python to MCP

| You write | The SDK produces |
|---|---|
| `@mcp.tool()` on a function | A tool. Name from the function name, description from the docstring, `inputSchema` from type hints (`Annotated[..., Field(...)]` adds per-field descriptions and constraints; `Literal` adds enums; defaults make arguments optional) |
| Return value of a tool | Tool result content; typed returns also produce structured content |
| `raise ToolError("...")` | A tool result with `isError: true` that the **model** sees and can recover from |
| Any other exception | A failed call with a generic message; details go to your log |
| `@mcp.resource("scheme://path")` | A resource (or a URI template such as `greeting://{name}`) |
| `@mcp.prompt()` | A prompt; parameters become string arguments the user fills in |
| `mcp.run()` | Serves over stdio (default) |
| `mcp.run(transport="streamable-http", port=8000)` | Serves Streamable HTTP at `http://127.0.0.1:8000/mcp` |

The SDK serves both the current protocol revision (2026-07-28) and older `initialize`-era clients from the same server without configuration.

### Project setup

> **Cost:** building and testing the server is free. Using it from Claude consumes your Claude plan usage or API credits.

```bash
# Create a project (uv is the SDK's recommended tool; pip works too)
uv init contoso-assets
cd contoso-assets
uv add "mcp[cli]"        # or: pip install "mcp[cli]"; the cli extra adds `mcp dev` and `mcp run`
```

## Example

### The server: `server.py`

```python
"""Contoso IT Assets MCP server (read-only, synthetic data).

Targets the MCP Python SDK v2 (`mcp` 2.x). Run with:  uv run server.py
"""
from __future__ import annotations

import logging
import os
from typing import Annotated, Literal

from pydantic import Field

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

# stdio servers must never print to stdout; logging writes to stderr by default.
logging.basicConfig(level=os.environ.get("ASSETS_LOG_LEVEL", "INFO"))
log = logging.getLogger("contoso-assets")

mcp = MCPServer("contoso-assets")

SITES = {"LDN": "London HQ", "MAN": "Manchester", "EDI": "Edinburgh"}
ASSETS = [
    {"tag": "LT-0001", "type": "laptop", "model": "Surface Laptop 7", "site": "LDN", "status": "in_use"},
    {"tag": "LT-0002", "type": "laptop", "model": "ThinkPad X1", "site": "MAN", "status": "repair"},
    {"tag": "MN-0101", "type": "monitor", "model": "Dell U2724D", "site": "LDN", "status": "spare"},
    {"tag": "PH-0450", "type": "phone", "model": "Pixel 9", "site": "EDI", "status": "in_use"},
]

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)


@mcp.tool(title="Search IT assets", annotations=READ_ONLY)
def assets_search(
    query: Annotated[str, Field(description="Words to match against asset type or model, e.g. 'laptop'.")],
    site: Annotated[Literal["LDN", "MAN", "EDI"] | None, Field(description="Limit to one site code.")] = None,
    status: Literal["in_use", "spare", "repair"] | None = None,
    limit: Annotated[int, Field(ge=1, le=25, description="Maximum results to return.")] = 10,
) -> list[dict]:
    """Search Contoso's IT asset register by type or model, optionally filtered by site and status.

    Use this when someone asks what equipment exists, where it is, or how many spares a site has.
    Returns asset tag, type, model, site and status. Does not return who an asset is assigned to.
    """
    words = query.lower().split()
    if not words:
        raise ToolError("query is empty; pass a type or model, for example 'laptop' or 'ThinkPad'.")
    hits = [a for a in ASSETS
            if all(w in f"{a['type']} {a['model']}".lower() for w in words)
            and (site is None or a["site"] == site)
            and (status is None or a["status"] == status)]
    log.info("assets_search query=%r site=%s status=%s hits=%d", query, site, status, len(hits))
    return hits[:limit]


@mcp.tool(title="Get one IT asset", annotations=READ_ONLY)
def assets_get(
    asset_tag: Annotated[str, Field(description="Asset tag such as LT-0001.")],
) -> dict:
    """Get the full register entry for one asset by its tag. Use after assets_search to confirm details."""
    for asset in ASSETS:
        if asset["tag"] == asset_tag.upper():
            return asset
    raise ToolError(f"No asset with tag {asset_tag!r}. Tags look like LT-0001; try assets_search first.")


@mcp.resource("assets://sites")
def list_sites() -> str:
    """Office sites and their codes, one per line."""
    return "\n".join(f"{code}: {name}" for code, name in SITES.items())


@mcp.prompt()
def site_audit(site_code: str) -> str:
    """Prepare a quarterly IT asset audit summary for one site."""
    return (
        f"Prepare a quarterly IT asset audit for site {site_code}. "
        "Use assets_search to list every asset at the site, group them by status, "
        "flag anything in 'repair' and suggest which spares could replace it. "
        "Finish with a three-line summary for the facilities manager."
    )


if __name__ == "__main__":
    # stdio is the default transport; pass transport="streamable-http" to serve over HTTP.
    mcp.run(transport=os.environ.get("ASSETS_TRANSPORT", "stdio"))
```

Design notes:

- Every tool is read-only, namespaced (`assets_`) and annotated. Annotations are hints for hosts, not security.
- `Literal` site codes and `Field(ge=1, le=25)` constrain inputs; the SDK rejects bad arguments with an error the model can read.
- `ToolError` messages tell Claude how to fix its call.
- The assignee field is deliberately absent, a data-minimisation choice.
- Configuration comes from environment variables, never hard-coded secrets.

### Test without a model: `test_server.py`

The v2 SDK's `Client` can connect to the server object in-process, which makes fast, free tests.

```python
"""In-process tests for the Contoso IT Assets server. Run: uv run python test_server.py"""
import asyncio

from mcp import Client

from server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("tools:", [t.name for t in tools.tools])

        result = await client.call_tool("assets_search", {"query": "laptop", "site": "MAN"})
        print("search:", result.is_error, result.structured_content)

        missing = await client.call_tool("assets_get", {"asset_tag": "XX-9999"})
        print("missing:", missing.is_error, missing.content[0].text)

        sites = await client.read_resource("assets://sites")
        print("sites:", sites.contents[0].text.splitlines())

        prompt = await client.get_prompt("site_audit", {"site_code": "LDN"})
        print("prompt:", prompt.messages[0].content.text[:60], "...")


asyncio.run(main())
```

### Inspect interactively

```bash
uv run mcp dev server.py
```

This opens the **MCP Inspector**, which launches your server over stdio like a real host. Use its Tools, Resources and Prompts tabs to call each primitive and check the generated schemas and descriptions.

### Connect it to Claude Code

```bash
# Local scope (only you, this project). Everything after -- is the command that starts the server.
claude mcp add --transport stdio contoso-assets -- uv --directory /ABSOLUTE/PATH/contoso-assets run server.py

claude mcp list            # should show contoso-assets as connected
```

Then, in a Claude Code session: `How many spare monitors does London have?`, or pick the prompt from the slash-command menu (MCP prompts appear as commands; see [MCP in Claude Code](../09-claude-code/07-mcp-in-claude-code.md)).

### Connect it to Claude Desktop

Add the server to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`; Windows: `%APPDATA%\Claude\`) and restart Claude Desktop:

```json
{
  "mcpServers": {
    "contoso-assets": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE/PATH/contoso-assets", "run", "server.py"]
    }
  }
}
```

You may need the full path to `uv` (`which uv` on macOS or Linux).

### Serve over HTTP (for shared or remote use)

```bash
ASSETS_TRANSPORT=streamable-http uv run server.py      # serves http://127.0.0.1:8000/mcp
# or, without changing code:
uv run mcp run server.py --transport streamable-http
```

Before exposing an HTTP server beyond your machine you need TLS, authentication (OAuth 2.1 as described in [Architecture](02-architecture.md#authorisation-for-http-servers); the SDK's [authorization docs](https://py.sdk.modelcontextprotocol.io/) cover server-side support), request size limits and DNS-rebinding protection. Only a reachable HTTPS endpoint can be used by claude.ai connectors or the Claude API MCP connector.

## Enterprise use case

*Contoso* (fictional) started with exactly this read-only server on engineers' laptops (stdio, each engineer's own API token from an environment variable). After a month of usage logs showed which questions people actually asked, the IT team added one write tool, `assets_request_transfer`, which creates a transfer *request* in the ticketing system rather than moving the asset. It carries `destructive_hint=False` and `read_only_hint=False`, and the request still needs a facilities manager's approval in the ticketing system.

They then deployed the server centrally over Streamable HTTP behind the corporate identity provider so that the operations team could use it as a custom connector in Claude Enterprise. The central deployment validates token audience, maps the user's group membership to which sites they can see, and logs every call with the user's ID. The stdio build remains for offline development and is pinned to a reviewed release in the internal package index.

## Common mistakes

- **Copying 1.x examples** (`from mcp.server.fastmcp import FastMCP`) into a v2 project, or the reverse. Check the installed version with `uv pip show mcp` or `pip show mcp`.
- **Using `print()` in a stdio server.** Use `logging` (stderr).
- **Returning an error string** instead of raising `ToolError`. A returned string has `isError: false`, so it looks like success.
- **Relative paths in host configuration.** Hosts launch the server from their own working directory; use absolute paths.
- **One tool per REST endpoint.** Design around tasks.
- **Exposing an HTTP server on `0.0.0.0` without authentication** "just for testing".
- **Putting secrets in `claude_desktop_config.json` or `.mcp.json` committed to git.** Use environment variables or a secret store.

## Security considerations

- **Least privilege** at the server: use credentials scoped to what the tools need, read-only where possible, per user for remote servers.
- **Validate everything**, even with schema constraints: authorisation checks per call, no string-built SQL or shell.
- **Minimise returned data**, and keep error messages free of internals.
- **Supply chain**: pin your SDK version, review dependencies, sign or checksum your releases. Users of your server should be able to verify its provenance.
- See [MCP security](05-mcp-security.md) and [secrets management](../12-ai-security/10-secrets-management.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ImportError: cannot import name 'MCPServer'` | SDK 1.x installed | Upgrade to `mcp` 2.x, or follow the 1.x docs consistently |
| Host shows "failed to connect" for a stdio server | Wrong path, `uv` not found, or Python below 3.11 | Use absolute paths and the full path to `uv`; check `python --version` |
| Server runs but host sees garbage or disconnects | Output on stdout | Remove `print()`; log to stderr |
| Claude never calls a tool | Weak docstring | Describe when to use it and what it returns |
| Tool call fails with a validation error | Argument outside `Field` constraints or `Literal` set | Expected; the message goes to the model, which can retry |

## Check your understanding

1. Where does the SDK get a tool's description and input schema?
2. What is the difference between raising `ToolError` and raising `ValueError` inside a tool?
3. Why must a stdio server avoid `print()`?
4. What do you need to add before letting claude.ai custom connectors use this server?

<details>
<summary>Answers</summary>

1. The description from the function's docstring and the input schema from its type hints (with `Annotated`/`Field` for per-field descriptions and constraints, and `Literal` for enums).
2. `ToolError` produces a tool result with `isError: true` and your message, which the model reads and can act on. Any other exception is treated as a crash: the model learns only that the call failed, and details go to the server log.
3. In stdio, stdout carries the JSON-RPC protocol stream; extra output corrupts it.
4. Serve it over Streamable HTTP at a public HTTPS endpoint reachable from Anthropic's infrastructure, with proper authentication (OAuth 2.1 with audience validation), plus hardening such as rate and size limits.

</details>

## Further reading

- [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server) (modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) and [SDK documentation](https://py.sdk.modelcontextprotocol.io/) (GitHub, modelcontextprotocol)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) (GitHub, modelcontextprotocol)
- [Lab 09: MCP fundamentals](../19-hands-on-labs/lab-09-mcp-fundamentals/README.md)
- Previous: [Architecture](02-architecture.md) · Next: [Using MCP with Claude](04-using-mcp-with-claude.md)
