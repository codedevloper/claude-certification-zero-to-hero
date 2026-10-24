"""Lab 09: MCP fundamentals, offline, with the standard library only.

`python lab.py --serve` runs a tiny MCP server over stdio (newline-delimited JSON-RPC 2.0).
`python lab.py` (the default) starts that server as a subprocess and acts as the client:

  Modern flow, protocol revision 2026-07-28 (stateless, no handshake):
    1. server/discover            - versions, capabilities and identity
    2. a request with an unsupported version -> error -32022, client retries with a supported one
    3. tools/list                 - every request carries its own _meta (version, capabilities)
    4. validate tool annotations and apply the client's allow-list policy
    5. hand the allowed tools to Claude, then run the tools/call Claude asks for
    6. tool execution error (isError: true) vs protocol error (unknown tool)
  History, revision 2025-11-25 and earlier:
    7. initialize -> notifications/initialized -> tools/list, in a separate server process

Run offline (default):   CLAUDE_LAB_MODE=mock python lab.py
Run against the API:      CLAUDE_LAB_MODE=live python lab.py   (uses API credits for step 5)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from claude_lab import get_client, MODEL, register_mock, text_of, banner  # noqa: E402
from claude_lab import MODE, TextBlock, ToolUseBlock  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"
MODERN = "2026-07-28"
LEGACY = "2025-11-25"
META_VERSION = "io.modelcontextprotocol/protocolVersion"
META_CAPS = "io.modelcontextprotocol/clientCapabilities"
META_CLIENT = "io.modelcontextprotocol/clientInfo"
META_SERVER = "io.modelcontextprotocol/serverInfo"
SERVER_INFO = {"name": "northwind-it-stdlib", "version": "1.0.0"}


# =========================================================================== server side
def _tool(name, title, description, properties, required, annotations):
    return {"name": name, "title": title, "description": description,
            "inputSchema": {"type": "object", "properties": properties, "required": required,
                            "additionalProperties": False},
            "annotations": annotations}


SERVICES_ENUM = {"type": "string", "enum": ["vpn", "email", "loan-portal"]}
SERVER_TOOLS = [  # deterministic order helps clients cache the list
    _tool("search_runbooks", "Search IT runbooks", "Search the service desk runbooks. Returns matching runbooks with their steps.",
          {"query": {"type": "string"}, "max_results": {"type": "integer", "minimum": 1, "maximum": 5}}, ["query"],
          {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}),
    _tool("get_service_status", "Get service status", "Return the current status of an internal service.",
          {"service": SERVICES_ENUM}, ["service"], {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}),
    _tool("create_incident_ticket", "Create incident ticket", "Open a new incident ticket. Each call creates another ticket.",
          {"service": SERVICES_ENUM, "summary": {"type": "string"}, "priority": {"type": "string", "enum": ["P2", "P3", "P4"]}},
          ["service", "summary", "priority"],
          {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}),
    _tool("restart_service", "Restart service", "Restart an internal service. Interrupts every user of that service.",
          {"service": SERVICES_ENUM}, ["service"],
          {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False}),
]


class ToolExecutionError(Exception):
    """Becomes a result with isError: true, which the model can read and act on."""


def _run_server_tool(name: str, args: dict) -> object:
    runbooks = json.loads((DATA / "runbooks.json").read_text(encoding="utf-8"))
    services = json.loads((DATA / "services.json").read_text(encoding="utf-8"))
    if name == "search_runbooks":
        query, limit = args.get("query"), args.get("max_results", 3)
        if not isinstance(query, str) or not 2 <= len(query) <= 100:
            raise ToolExecutionError("query must be a string of 2 to 100 characters.")
        if not isinstance(limit, int) or not 1 <= limit <= 5:
            raise ToolExecutionError("max_results must be an integer from 1 to 5.")
        words = query.lower().split()
        hits = [rb for rb in runbooks if any(w in json.dumps(rb).lower() for w in words)]
        return hits[:limit]
    if args.get("service") not in services:
        raise ToolExecutionError(f"service must be one of {sorted(services)}.")
    if name == "get_service_status":
        return {"service": args["service"], **services[args["service"]]}
    if name == "create_incident_ticket":
        return {"ticket_id": "INC-1001", "service": args["service"], "priority": args.get("priority"), "simulated": True}
    raise ToolExecutionError("Restarts must go through change management; nothing was restarted.")


def handle(message: dict, state: dict) -> dict | None:
    """Handle one JSON-RPC message. Returns a response, or None for notifications."""
    method, params, msg_id = message.get("method"), message.get("params") or {}, message.get("id")
    if msg_id is None:  # notifications get no response
        if method == "notifications/initialized":
            state["initialized"] = True
        return None

    def ok(result: dict) -> dict:
        result = {"resultType": "complete", **result} if not state.get("legacy") else result
        if not state.get("legacy"):
            result["_meta"] = {META_SERVER: SERVER_INFO}
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def err(code: int, text: str, data=None) -> dict:
        body = {"code": code, "message": text}
        if data is not None:
            body["data"] = data
        return {"jsonrpc": "2.0", "id": msg_id, "error": body}

    if method == "initialize":  # legacy handshake selects legacy semantics for this process
        state["legacy"] = True
        if params.get("protocolVersion") != LEGACY:
            return err(-32602, "Unsupported protocol version", {"supported": [LEGACY]})
        return ok({"protocolVersion": LEGACY, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO})

    if not state.get("legacy"):  # modern: every request must describe itself in _meta
        meta = params.get("_meta") or {}
        if META_VERSION not in meta or META_CAPS not in meta:
            return err(-32602, "Missing required _meta fields")
        if meta[META_VERSION] != MODERN:
            return err(-32022, "Unsupported protocol version", {"supported": [MODERN, LEGACY], "requested": meta[META_VERSION]})
    elif not state.get("initialized"):
        return err(-32600, "Legacy session: send notifications/initialized first")

    if method == "server/discover":
        return ok({"supportedVersions": [MODERN, LEGACY], "capabilities": {"tools": {}},
                   "instructions": "Read-only IT runbooks and service status (fictional)."})
    if method == "tools/list":
        return ok({"tools": SERVER_TOOLS})
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in {t["name"] for t in SERVER_TOOLS}:
            return err(-32602, f"Unknown tool: {name}")  # protocol error
        try:
            data = _run_server_tool(name, args)
            return ok({"content": [{"type": "text", "text": json.dumps(data)}], "structuredContent": data, "isError": False}
                      if isinstance(data, dict) else {"content": [{"type": "text", "text": json.dumps(data)}], "isError": False})
        except ToolExecutionError as exc:  # tool execution error: reported in the result
            return ok({"content": [{"type": "text", "text": str(exc)}], "isError": True})
    return err(-32601, f"Method not found: {method}")


def serve() -> None:
    """stdio transport: one JSON-RPC message per line in, one per line out. Logs go to stderr only."""
    state: dict = {}
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        else:
            reply = handle(message, state)
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()
    print("server: stdin closed, exiting", file=sys.stderr)


# =========================================================================== client side
class StdioClient:
    def __init__(self) -> None:
        self.proc = subprocess.Popen([sys.executable, __file__, "--serve"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.next_id = 0
        self.version = MODERN
        self.wire: list[str] = []

    def _send(self, message: dict) -> dict | None:
        line = json.dumps(message)
        assert "\n" not in line  # stdio framing forbids embedded newlines
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        self.wire.append(f"-> {line[:150]}")
        if "id" not in message:
            return None
        reply = json.loads(self.proc.stdout.readline())
        self.wire.append(f"<- {json.dumps(reply)[:150]}")
        return reply

    def request(self, method: str, params: dict | None = None, *, version: str | None = None, legacy: bool = False) -> dict:
        self.next_id += 1
        params = dict(params or {})
        if not legacy:
            params["_meta"] = {META_VERSION: version or self.version, META_CAPS: {},
                               META_CLIENT: {"name": "lab-09-client", "version": "1.0.0"}}
        return self._send({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params})

    def notify(self, method: str) -> None:
        self._send({"jsonrpc": "2.0", "method": method})

    def close(self) -> int:
        self.proc.stdin.close()  # closing stdin is the graceful shutdown signal
        return self.proc.wait(timeout=10)


# Client-side policy. Annotations are hints from the server and are untrusted unless the server
# is trusted, so the decision is the client's: an explicit allow-list by tool name.
ALLOW = {"search_runbooks", "get_service_status"}
REQUIRE_APPROVAL = {"create_incident_ticket"}
ANNOTATION_KEYS = {"title", "readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"}


def review_annotations(tool: dict) -> list[str]:
    """Check annotation shape and flag risky combinations. Defaults follow the MCP spec."""
    notes = []
    ann = tool.get("annotations")
    if ann is None:
        return ["no annotations: treat as non-read-only and potentially destructive"]
    unknown = set(ann) - ANNOTATION_KEYS
    if unknown:
        notes.append(f"unknown annotation keys {sorted(unknown)}")
    for key in ANNOTATION_KEYS - {"title"}:
        if key in ann and not isinstance(ann[key], bool):
            notes.append(f"{key} must be a boolean")
    read_only = ann.get("readOnlyHint", False)
    destructive = ann.get("destructiveHint", True) if not read_only else False
    if destructive:
        notes.append("destructive")
    if not read_only and not ann.get("idempotentHint", False):
        notes.append("not idempotent: repeated calls repeat the effect")
    if ann.get("openWorldHint", True):
        notes.append("open world: reaches external systems")
    return notes


def decide(tool: dict) -> str:
    name, notes = tool["name"], review_annotations(tool)
    if name in ALLOW:
        # Belt and braces: an allow-listed tool that now claims to be destructive is suspicious.
        return "allow" if "destructive" not in notes else "block (allow-listed tool became destructive)"
    if name in REQUIRE_APPROVAL:
        return "ask a human"
    return "block"


def to_claude_tool(tool: dict) -> dict:
    """MCP tool definition -> Claude Messages API tool definition."""
    return {"name": tool["name"], "description": tool["description"], "input_schema": tool["inputSchema"]}


# --------------------------------------------------------------------------- mock Claude
@register_mock
def fake_claude_with_mcp_tools(**request):
    tools = request.get("tools") or []
    if not any(t["name"] == "search_runbooks" for t in tools):
        return None
    last = request["messages"][-1]["content"]
    if isinstance(last, str):
        return [TextBlock("I'll check the service status and the runbook."),
                ToolUseBlock("get_service_status", {"service": "loan-portal"}),
                ToolUseBlock("search_runbooks", {"query": "loan portal slow", "max_results": 1})]
    return ("The loan origination portal is currently degraded (elevated response times since 08:51 UTC), so this "
            "is a known issue. Per runbook RB-103, don't restart anything: link the user's ticket to the open P2 "
            "incident and record their timestamp and browser.")


def ask_claude(client, mcp: StdioClient, claude_tools: list[dict], question: str) -> tuple[str, list[str]]:
    messages, calls = [{"role": "user", "content": question}], []
    for _ in range(4):
        response = client.messages.create(model=MODEL, max_tokens=4096, output_config={"effort": "low"},
                                          system="You help Northwind Lending's IT service desk. Use the tools for facts.",
                                          tools=claude_tools, tool_choice={"type": "auto"}, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return text_of(response), calls
        results = []
        for block in (b for b in response.content if getattr(b, "type", "") == "tool_use"):
            calls.append(block.name)
            if block.name not in ALLOW:  # never trust that the model only asks for offered tools
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": "Not permitted.", "is_error": True})
                continue
            reply = mcp.request("tools/call", {"name": block.name, "arguments": block.input})
            if "error" in reply:
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": reply["error"]["message"], "is_error": True})
            else:
                text = "\n".join(c["text"] for c in reply["result"]["content"] if c["type"] == "text")
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": text[:2000],
                                "is_error": reply["result"].get("isError", False)})
        messages.append({"role": "user", "content": results})
    raise RuntimeError("no final answer")


# =========================================================================== the lab
def main() -> int:
    banner("Lab 09 - MCP fundamentals (stdlib client and server over stdio)")
    mcp = StdioClient()

    print(f"1. server/discover (revision {MODERN}: stateless, no handshake)")
    discover = mcp.request("server/discover")["result"]
    print(f"   supportedVersions={discover['supportedVersions']} capabilities={list(discover['capabilities'])} "
          f"server={discover['_meta'][META_SERVER]['name']}")

    print("2. A request with a version the server does not support")
    bad = mcp.request("tools/list", version="1900-01-01")
    print(f"   error {bad['error']['code']}: {bad['error']['message']} supported={bad['error']['data']['supported']}")
    mcp.version = next(v for v in bad["error"]["data"]["supported"] if v == MODERN)
    no_meta = mcp._send({"jsonrpc": "2.0", "id": 99, "method": "tools/list", "params": {}})
    print(f"   request without _meta -> error {no_meta['error']['code']}: {no_meta['error']['message']}")

    print("3. tools/list")
    tools = mcp.request("tools/list")["result"]["tools"]
    print("4. Annotation review and client policy")
    print(f"   {'tool':<24} {'policy':<12} notes")
    policy = {}
    for tool in tools:
        policy[tool["name"]] = decide(tool)
        print(f"   {tool['name']:<24} {policy[tool['name']]:<12} {', '.join(review_annotations(tool)) or '-'}")

    print("5. Claude uses the allowed MCP tools")
    claude_tools = [to_claude_tool(t) for t in tools if policy[t["name"]] == "allow"]
    answer, calls = ask_claude(get_client(), mcp, claude_tools,
                               "A loan officer says the loan origination portal is very slow. What should I do?")
    print(f"   Claude called: {calls}")
    print(f"   Claude: {answer}")

    print("6. Errors: tool execution error vs protocol error")
    exec_err = mcp.request("tools/call", {"name": "search_runbooks", "arguments": {"query": "vpn", "max_results": 50}})
    print(f"   bad arguments -> result.isError={exec_err['result']['isError']}: {exec_err['result']['content'][0]['text']}")
    proto_err = mcp.request("tools/call", {"name": "format_disk", "arguments": {}})
    print(f"   unknown tool  -> error {proto_err['error']['code']}: {proto_err['error']['message']}")
    exit_code = mcp.close()

    print(f"7. History: the {LEGACY} handshake (separate server process)")
    old = StdioClient()
    init = old.request("initialize", {"protocolVersion": LEGACY, "capabilities": {},
                                      "clientInfo": {"name": "legacy-client", "version": "0.9"}}, legacy=True)
    old.notify("notifications/initialized")
    legacy_tools = old.request("tools/list", legacy=True)["result"]["tools"]
    print(f"   initialize -> protocolVersion={init['result']['protocolVersion']}; "
          f"notifications/initialized sent; tools/list -> {len(legacy_tools)} tools (no _meta needed)")
    legacy_exit = old.close()

    print("\nWire trace (first lines, truncated):")
    for line in mcp.wire[:4]:
        print(f"   {line}")

    print("\nSelf-checks")
    checks = {
        "discover advertises the modern revision": MODERN in discover["supportedVersions"],
        "unsupported version returns -32022 with a supported list": bad["error"]["code"] == -32022,
        "missing _meta is rejected with -32602": no_meta["error"]["code"] == -32602,
        "every tool has well-formed annotations": all(
            not any("must be a boolean" in n or "unknown" in n for n in review_annotations(t)) for t in tools),
        "destructive tool is blocked by policy": policy["restart_service"] == "block",
        "write tool needs a human": policy["create_incident_ticket"] == "ask a human",
        "only allow-listed tools were offered to Claude": {t["name"] for t in claude_tools} == ALLOW,
        "Claude only called allow-listed tools": set(calls) <= ALLOW and len(calls) > 0,
        "bad arguments give isError (model can self-correct)": exec_err["result"]["isError"] is True,
        "unknown tool gives a JSON-RPC protocol error": proto_err["error"]["code"] == -32602,
        "a tool missing annotations is treated as risky": review_annotations({"name": "x"})[0].startswith("no annotations")
        and decide({"name": "x"}) == "block",
        "legacy handshake still works (history)": init["result"]["protocolVersion"] == LEGACY and len(legacy_tools) == 4,
        "both server processes shut down cleanly": exit_code == 0 and legacy_exit == 0,
    }
    failed = [n for n, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if failed:
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    if "--serve" in sys.argv:
        serve()
    else:
        raise SystemExit(main())
