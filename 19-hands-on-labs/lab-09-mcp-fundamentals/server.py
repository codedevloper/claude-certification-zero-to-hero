"""A minimal MCP server built with the official MCP Python SDK (v2).

Optional extra for Lab 09. `lab.py` does not need it: lab.py speaks the protocol with the
standard library so the lab runs offline. This file shows the same four tools written with
the SDK, which generates schemas from type hints and handles the protocol for you.

Verified against `mcp` 2.3.0 (MCP Python SDK v2, which speaks protocol revision 2026-07-28)
on 2026-10-24. Requires Python 3.11+.

Install (in a virtual environment):
    pip install "mcp>=2.0,<3"

Check it without any MCP host (in-process client, no network, no API credits):
    python server.py --self-test

Run it over stdio for a host such as Claude Code:
    claude mcp add --transport stdio northwind-it -- python /absolute/path/to/server.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

DATA = Path(__file__).resolve().parent / "data"
RUNBOOKS = json.loads((DATA / "runbooks.json").read_text(encoding="utf-8"))
SERVICES = json.loads((DATA / "services.json").read_text(encoding="utf-8"))
ServiceName = Literal["vpn", "email", "loan-portal"]

mcp = MCPServer(
    "northwind-it",
    instructions="Read-only IT runbooks and service status for Northwind Lending's service desk (fictional).",
)
_tickets: list[dict] = []  # in memory only; nothing is persisted


@mcp.tool(
    title="Search IT runbooks",
    annotations=ToolAnnotations(read_only_hint=True, idempotent_hint=True, open_world_hint=False),
)
def search_runbooks(
    query: Annotated[str, Field(min_length=2, max_length=100, description="Words to look for in runbook titles and steps")],
    max_results: Annotated[int, Field(ge=1, le=5)] = 3,
) -> list[dict]:
    """Search the service desk runbooks. Returns matching runbooks with their steps."""
    words = query.lower().split()
    hits = [rb for rb in RUNBOOKS
            if any(w in (rb["title"] + " " + rb["service"] + " " + " ".join(rb["steps"])).lower() for w in words)]
    return hits[:max_results]


@mcp.tool(
    title="Get service status",
    annotations=ToolAnnotations(read_only_hint=True, idempotent_hint=True, open_world_hint=False),
)
def get_service_status(service: ServiceName) -> dict:
    """Return the current status of an internal service."""
    return {"service": service, **SERVICES[service]}


@mcp.tool(
    title="Create incident ticket",
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False),
)
def create_incident_ticket(
    service: ServiceName,
    summary: Annotated[str, Field(min_length=10, max_length=200)],
    priority: Literal["P2", "P3", "P4"],
) -> dict:
    """Open a new incident ticket. Each call creates another ticket, so check for an open one first."""
    ticket = {"ticket_id": f"INC-{1000 + len(_tickets) + 1}", "service": service, "summary": summary, "priority": priority}
    _tickets.append(ticket)
    return ticket


@mcp.tool(
    title="Restart service",
    annotations=ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=False, open_world_hint=False),
)
def restart_service(service: ServiceName) -> str:
    """Restart an internal service. Interrupts every user of that service."""
    # Present so clients can see a destructive tool in tools/list. It never does anything real.
    raise ToolError(f"Restarting {service} must go through the change-management process; nothing was restarted.")


async def self_test() -> None:
    from mcp.client import Client

    async with Client(mcp) as client:  # in-process connection, intended for tests
        listed = await client.list_tools()
        for tool in listed.tools:
            a = tool.annotations
            print(f"tool {tool.name:<24} read_only={a.read_only_hint} destructive={a.destructive_hint}")
        ok = await client.call_tool("search_runbooks", {"query": "vpn", "max_results": 1})
        print("call search_runbooks -> isError =", ok.is_error, "|", ok.content[0].text[:80])
        bad = await client.call_tool("search_runbooks", {"query": "vpn", "max_results": 50})
        print("call with max_results=50 -> isError =", bad.is_error)
        blocked = await client.call_tool("restart_service", {"service": "vpn"})
        print("call restart_service -> isError =", blocked.is_error, "|", blocked.content[0].text[:80])


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        asyncio.run(self_test())
    else:
        mcp.run()  # stdio by default
