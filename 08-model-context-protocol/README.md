# Module 08: Model Context Protocol (MCP)

> **Level:** Intermediate · **Time:** ~4 to 5 hours including the lab · **Exam relevance:** CCAR-P 3.1, 3.2, 3.7, 3.8, 5.1; CCAO-F 5.2

[Module 07](../07-tool-use-and-function-calling/README.md) showed how to give Claude tools inside one application. The Model Context Protocol (MCP) answers the next question: how do you build an integration **once** and use it from many AI applications, such as Claude Code, the Claude apps, Claude Desktop, your own agents built on the Claude API, and third-party tools? This module explains the protocol, has you build a small server with the official Python SDK, connects it to Claude in three different ways, and then spends real time on what can go wrong and when MCP is the wrong choice.

## Learning objectives

By the end of this module you can:

1. Explain what MCP standardises, who governs it, and where it fits next to tool use, APIs and agent-to-agent protocols.
2. Describe the architecture: hosts, clients and servers; the stdio and Streamable HTTP transports; the tools, resources and prompts primitives; capability discovery; and OAuth 2.1-based authorisation for HTTP servers.
3. Build and test a minimal MCP server in Python with the official `mcp` SDK (v2).
4. Connect MCP servers to Claude through Claude apps connectors, Claude Code (`claude mcp add`) and the Claude API MCP connector.
5. Identify MCP-specific risks (tool poisoning, rug pulls, confused deputy, token passthrough, malicious local servers) and apply controls such as provenance checks, allow-lists and pinning.
6. Choose between MCP, a direct API or CLI integration, and an agent-to-agent protocol, and justify the choice (CCAR-P-3.7).

## Pages in this module

| # | Page | What you learn |
|---|---|---|
| 1 | [What is MCP?](01-what-is-mcp.md) | The problem MCP solves, history, governance, vocabulary |
| 2 | [Architecture](02-architecture.md) | Hosts, clients, servers, transports, primitives, discovery, authorisation |
| 3 | [Building an MCP server](03-building-an-mcp-server.md) | A working Python server with tools, a resource and a prompt |
| 4 | [Using MCP with Claude](04-using-mcp-with-claude.md) | Claude apps connectors, Claude Code, the API MCP connector |
| 5 | [MCP security](05-mcp-security.md) | Threats, the spec's security best practices, enterprise controls |
| 6 | [MCP versus alternatives](06-mcp-vs-alternatives.md) | MCP, direct API/CLI and agent-to-agent protocols, with a decision guide |

## Hands-on lab

- [Lab 09: MCP fundamentals](../19-hands-on-labs/lab-09-mcp-fundamentals/README.md) walks through MCP concepts and a server in mock mode by default (`CLAUDE_LAB_MODE=mock`), with an optional live step (`CLAUDE_LAB_MODE=live`).

> **Cost:** requires API credits (live mode).

## Prerequisites

- [Module 07: Tool use and function calling](../07-tool-use-and-function-calling/README.md), all pages. MCP tools become ordinary Claude tools once connected.
- Basic understanding of HTTP and JSON. Familiarity with OAuth helps for pages 2 and 5.
- Python 3.11 or later for the server in page 3 (the MCP Python SDK v2 requires it; the rest of this repository targets 3.10+).

## Exam relevance

Objective IDs come from [`registry.yaml`](../16-certification-tracks/registry.yaml).

| Objective | Where this module helps |
|---|---|
| CCAR-P-3.7 Choose integration mechanism (MCP, API/CLI, agent-to-agent) | Page 6 decision guide; pages 1 and 4 |
| CCAR-P-3.2 Analyse authentication and authorisation to find security gaps | Pages 2 and 5: OAuth 2.1, audience validation, token passthrough |
| CCAR-P-3.1 Evaluate tool and agent configuration for capability bloat | Pages 4 and 5: tool allow-lists, server allow-lists |
| CCAR-P-3.8 Evaluate progressive discovery versus monolithic context | Page 4: deferred loading and tool search for MCP tools |
| CCAR-P-5.1 Implement guardrails and safety controls | Page 5 |
| CCAO-F-5.2 Manage uploaded knowledge and connectors | Page 4: Claude apps connectors |

## Key facts to remember (as of 2026-10-24)

- The current MCP specification revision is **2026-07-28**. It makes requests stateless and replaces the old `initialize` handshake with per-request metadata and an optional `server/discover` request. Many clients and servers still speak **2025-11-25**, which used `initialize`.
- MCP was introduced by Anthropic in November 2024 and donated to the **Agentic AI Foundation**, a directed fund of the Linux Foundation, on 2025-12-09.
- The Python SDK's current major line is **v2** (`mcp` 2.3.0 on PyPI as of 2026-10-24), with `from mcp.server import MCPServer`.
- The Claude API MCP connector needs **both** `mcp_servers` and an `mcp_toolset` entry in `tools`, plus the `mcp-client-2025-11-20` beta header. It supports tool calls only, over remote HTTP servers.

## Next module

Continue to [Module 09: Claude Code](../09-claude-code/README.md), where MCP is one of several ways to extend an agentic coding tool for a whole team.
