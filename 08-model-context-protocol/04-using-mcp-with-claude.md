# Using MCP with Claude

> **Level:** Intermediate · **Time:** ~45 min · **Exam relevance:** CCAR-P 3.1, 3.7, 3.8; CCAO-F 5.2

## In plain English

Once an MCP server exists, there are several ways to plug it into Claude, depending on who is using it and where the code runs:

- **Claude apps** (claude.ai, Claude Desktop, Cowork): add the server as a **connector**. Knowledge workers switch it on in a conversation and use it in plain language.
- **Claude Code**: add the server with `claude mcp add` or a shared `.mcp.json` file. Developers use it alongside Claude Code's built-in tools.
- **Claude API**: your application can either let the API connect to a remote server for you (the **MCP connector**) or run its own MCP client and pass the tools to Claude (the SDK **MCP helpers**).

The server is the same in every case. What changes is who connects to it, where the connection comes from, and who controls which tools are enabled.

## Why it matters

- **Choosing the right surface** for each audience is part of the integration decision (CCAR-P-3.7).
- **Tool allow-lists and deferred loading** are where you control capability bloat and context size (CCAR-P-3.1, 3.8).
- **Connector management** in the Claude apps is a Foundations topic for knowledge workers and admins (CCAO-F-5.2).
- **Network placement** matters: Claude apps connectors and the API connector reach servers from Anthropic's cloud, while Claude Code and Claude Desktop local servers run on the user's machine.

## How it works

### Overview of the options

| Surface | Server location | Transport | Who connects | Primitives used | Configured by |
|---|---|---|---|---|---|
| Claude apps: directory connectors | Vendor-hosted | Remote HTTP | Anthropic's cloud | Tools (and interactive UI for some connectors) | Users; admins on Team and Enterprise |
| Claude apps: custom connectors | Your remote server | Remote HTTP | Anthropic's cloud | Tools | Individual users (Free, Pro, Max); owners or delegated roles (Team, Enterprise) |
| Claude Desktop: local servers | User's machine | stdio | The desktop app | Tools, resources, prompts | User, in `claude_desktop_config.json` |
| Claude Code | Local or remote | stdio, Streamable HTTP, SSE, WebSocket | Claude Code on the user's machine (or cloud session) | Tools, resources, prompts | User, project `.mcp.json`, or managed policy |
| Claude API: MCP connector (beta) | Remote, public | Streamable HTTP or SSE | Anthropic's API | **Tools only** | Your application's request |
| Claude API: SDK MCP helpers (beta) | Anywhere your app can reach | Any, including stdio | Your application | Tools, prompts, resources | Your code |

### 1. Claude apps connectors

Connectors bring MCP servers into claude.ai, Claude Desktop and Cowork. As of 2026-10-24, per [Anthropic's help centre](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp):

- **Directory connectors** are reviewed integrations listed in the [connectors directory](https://claude.ai/directory).
- **Custom connectors** point at any remote MCP server URL. They are available on Free (one custom connector), Pro, Max, Team and Enterprise plans. On Pro and Max, users add their own. On Team, only Owners and Primary Owners can add them for the organisation; on Enterprise, Owners, Primary Owners and custom roles with "Manage access to Libraries" can.
- On Team and Enterprise, after an admin adds a connector, **each member connects individually** (for example by signing in with OAuth). In a conversation, users choose **+ → Connectors** to toggle connectors and can disable individual tools.
- **Claude connects from Anthropic's cloud**, not from the user's device. A server on a private network must allow-list Anthropic's IP addresses, or it will not be reachable.
- Authentication can be **OAuth** (Claude's published client identity, automatic registration, or your own OAuth client) or **fixed request headers** such as an API key. A shared header credential gives every user the same access, so use a narrowly scoped one.
- Anthropic does not verify custom connectors. Review requested OAuth permissions, prefer "Allow always" only for trusted tools, and remember that in Research mode tools can run without further approval, so disable tools that write to external systems.

[Module 05: Connectors and integrations](../05-claude-products-and-models/06-connectors-and-integrations.md) covers the user and admin experience in more detail.

### 2. Claude Code

The essentials (full detail in [MCP in Claude Code](../09-claude-code/07-mcp-in-claude-code.md)):

```bash
# Remote server over Streamable HTTP
claude mcp add --transport http tickets https://mcp.tickets.example.com/mcp

# Local stdio server; everything after -- is the launch command
claude mcp add --transport stdio contoso-assets --env ASSETS_LOG_LEVEL=WARNING -- uv --directory /ABS/PATH run server.py

# Share with the team: writes .mcp.json at the project root
claude mcp add --transport http tickets --scope project https://mcp.tickets.example.com/mcp

claude mcp list        # status of each server
claude mcp get tickets # details, including any connection issue
```

Inside a session, `/mcp` shows server status and handles OAuth sign-in. Claude Code defers MCP tool definitions by default and discovers them with **tool search**, so many servers cost little context. MCP tools are named `mcp__<server>__<tool>` for permission rules, and project `.mcp.json` servers require approval in interactive sessions.

### 3. The Claude API MCP connector (beta)

The API can connect to a remote MCP server on your behalf, so your application needs no MCP client. As of 2026-10-24:

- Use the beta header **`mcp-client-2025-11-20`** (the earlier `mcp-client-2025-04-04` is deprecated).
- Provide **both** halves, or the request fails validation:
  - `mcp_servers`: `[{"type": "url", "url": "...", "name": "...", "authorization_token": "..."}]`
  - in `tools`: `{"type": "mcp_toolset", "mcp_server_name": "<same name>"}`. Every server must be referenced by exactly one toolset.
- Configure tools with `default_config` and per-tool `configs`. Set `"enabled": false` in `default_config` and enable named tools for an **allow-list**, or disable named tools for a **deny-list**. Set `defer_loading` there to combine with [tool search](../07-tool-use-and-function-calling/04-server-tools.md#tool-search-and-deferred-loading).
- Responses contain `mcp_tool_use` and `mcp_tool_result` blocks. The API runs the calls; you do not return results yourself.
- **Limitations**: only MCP **tools** are supported (not resources or prompts); the server must be publicly reachable over HTTP (Streamable HTTP or SSE); local stdio servers cannot be connected.
- **Authentication**: you obtain and refresh the OAuth access token yourself and pass it as `authorization_token`. The API does not run the OAuth flow.
- **Data retention**: the MCP connector is not covered by zero-data-retention arrangements.
- **Availability**: Claude API, Claude Platform on AWS and Microsoft Foundry (beta); not Amazon Bedrock or Google Vertex AI.
- **Pinning** (beta header `mcp-client-2026-09-15`, Claude API): the API records each server's tool list in an `mcp_tool_listing` block, and you can copy that list into the toolset's `tools` field so that a server changing its tools mid-conversation does not change what Claude sees. This is a useful defence against "rug pull" changes; see [MCP security](05-mcp-security.md).

### 4. SDK MCP helpers (your own MCP client)

When you need a local stdio server, MCP prompts or resources, or full control of the connection, run an MCP client in your application and convert its tools for the Anthropic SDK. The Python SDK provides beta helpers in `anthropic.lib.tools.mcp` (install with `pip install "anthropic[mcp]"`): `async_mcp_tool` / `mcp_tool` convert MCP tools for the Tool Runner, `mcp_message` converts prompt messages, and `mcp_resource_to_content` converts resources into content blocks.

## Example

### API MCP connector with an allow-list

> **Cost:** requires API credits (live mode).

```python
import os
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model=os.environ.get("CLAUDE_MODEL", "claude-opus-5-5"),
    max_tokens=16000,
    betas=["mcp-client-2025-11-20"],
    mcp_servers=[{
        "type": "url",
        "url": "https://mcp.tickets.example.com/mcp",
        "name": "tickets",
        "authorization_token": os.environ["TICKETS_MCP_TOKEN"],  # obtained by your OAuth flow
    }],
    tools=[{
        "type": "mcp_toolset",
        "mcp_server_name": "tickets",
        "default_config": {"enabled": False},          # allow-list mode
        "configs": {
            "tickets_search": {"enabled": True},
            "tickets_get": {"enabled": True},
            # tickets_close, tickets_reassign stay disabled
        },
    }],
    messages=[{"role": "user", "content": "Summarise open P1 tickets for the payments team."}],
)

if response.stop_reason == "end_turn":
    for block in response.content:
        if block.type == "mcp_tool_use":
            print("called", block.server_name, block.name, block.input)
        elif block.type == "text":
            print(block.text)
else:
    print("stop_reason:", response.stop_reason)  # handle pause_turn, refusal, max_tokens as in Module 07
```

### Local stdio server through the Tool Runner

This uses the server from [Building an MCP server](03-building-an-mcp-server.md).

> **Cost:** requires API credits (live mode).

```python
import asyncio
import os

from anthropic import AsyncAnthropic
from anthropic.lib.tools.mcp import async_mcp_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = AsyncAnthropic()
server = StdioServerParameters(command="uv", args=["--directory", "/ABS/PATH/contoso-assets", "run", "server.py"])

async def main() -> None:
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            runner = client.beta.messages.tool_runner(       # returns a runner, not a coroutine
                model=os.environ.get("CLAUDE_MODEL", "claude-opus-5-5"),
                max_tokens=16000,
                tools=[async_mcp_tool(t, session) for t in listed.tools],
                messages=[{"role": "user", "content": "How many spare monitors are in London?"}],
            )
            async for message in runner:
                for block in message.content:
                    if block.type == "text":
                        print(block.text)

asyncio.run(main())
```

### A Claude apps custom connector

1. Deploy the server over Streamable HTTPS with OAuth, reachable from Anthropic's IP ranges.
2. In claude.ai (Team or Enterprise owner), open the connector settings, choose to add a custom connector, enter the server URL and, if needed, OAuth client details under advanced settings.
3. Each member connects with their own account, then enables the connector per conversation and switches off tools they do not need.

## Enterprise use case

*Northwind Lending* (fictional) exposed its "policy library" MCP server to three audiences:

- **Underwriters** use it as a **custom connector** in Claude Enterprise. Owners added it once; each underwriter signs in with SSO through OAuth, so the server sees their identity and returns only the policies their role may view. Write tools are not exposed to this connector at all.
- **Engineers** use it in **Claude Code** through a committed `.mcp.json`, plus a managed allow-list so only approved servers can be added on company laptops.
- **The loan-servicing assistant**, a Claude API application, uses the **MCP connector** with an allow-list of two read tools, `defer_loading` on the rest, and the tool-list pinning beta so that a server deployment mid-conversation cannot change the tools Claude is using. The application's backend performs the OAuth client-credentials flow and refreshes the token.

The same server, three entry points, each with the narrowest tool set its audience needs.

## Common mistakes

- **Sending only `mcp_servers`** to the API without an `mcp_toolset` entry, or forgetting the beta header.
- **Expecting resources or prompts through the API connector.** It supports tools only; use the SDK helpers instead.
- **Pointing a claude.ai connector at a server on a private network** without allow-listing Anthropic's IPs.
- **A single shared API key in a team connector** that gives every user admin-level access.
- **Enabling every tool by default** on powerful servers. Use allow-lists.
- **Hard-coding tokens** in code or committed `.mcp.json`. Use environment variables (Claude Code expands `${VAR}` in `.mcp.json`) or a secret store.
- **Forgetting that `pause_turn` and refusals still apply** to API requests that use MCP tools.

## Security considerations

- Prefer **per-user OAuth** over shared credentials so the server can enforce each user's permissions and audit logs show real identities.
- Use **allow-lists**, both of servers (which servers can be added) and of tools (which tools are enabled).
- **Pin** tool lists where the surface supports it, and review changes.
- Remember the **data path**: with connectors and the API connector, tool inputs and results pass through Anthropic's infrastructure; check retention terms for regulated data.
- Full treatment: [MCP security](05-mcp-security.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| API validation error about MCP servers | Missing `mcp_toolset`, name mismatch, or one server referenced twice | One toolset per server, names identical |
| Connector cannot reach the server | Private network or firewall | Expose over HTTPS or allow-list Anthropic's IPs |
| Claude Code shows `Needs authentication` | OAuth not completed | Run `/mcp` and sign in |
| A `.mcp.json` server stays pending | Project servers need approval in interactive sessions | Run `claude` interactively and approve, or check `disabledMcpjsonServers` |
| Tools from a server changed unexpectedly | Server updated its tool list | Pin the list (API beta), review the change, re-approve |

## Check your understanding

1. Which two parameters must appear together to use the Claude API MCP connector, and which beta header is required (as of 2026-10-24)?
2. Your server is only reachable on the corporate VPN. Which of these can use it without changes: claude.ai custom connector, Claude Code on a VPN-connected laptop, the API MCP connector?
3. How do you restrict an API MCP connector to two specific tools?
4. You need an MCP server's prompts in your API application. Which approach do you use?

<details>
<summary>Answers</summary>

1. `mcp_servers` and a `tools` entry of type `mcp_toolset` with a matching `mcp_server_name`; beta header `mcp-client-2025-11-20`.
2. Only Claude Code on the VPN-connected laptop. The claude.ai connector and the API MCP connector connect from Anthropic's cloud and need a publicly reachable endpoint (or allow-listed IPs).
3. Set `default_config: {"enabled": false}` on the `mcp_toolset` and enable the two tools in `configs`.
4. Run your own MCP client and use the SDK MCP helpers (for example `mcp_message` for prompt messages); the API connector supports tools only.

</details>

## Further reading

- [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) (Claude Docs)
- [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) (Claude Help Center)
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) (Claude Code Docs)
- [Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers) (modelcontextprotocol.io)

<!-- page-nav:start -->
---

[← Previous: Building an MCP Server](03-building-an-mcp-server.md) · [Module overview](README.md) · [Next: MCP Security →](05-mcp-security.md)
<!-- page-nav:end -->
