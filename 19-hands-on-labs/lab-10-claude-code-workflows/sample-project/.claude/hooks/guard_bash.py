#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool: block a few dangerous command patterns.

Claude Code sends the pending tool call as JSON on stdin. Exit code 0 lets the normal
permission flow continue (it does NOT approve the call). Exit code 2 blocks the call, and
the text on stderr is shown to Claude as the reason.

This complements the deny rules in settings.json: it inspects the whole command string,
so it also catches patterns hidden inside `bash -c '...'`, `sh -c` or a pipeline.
"""
import json
import re
import sys

BLOCKED = [
    (re.compile(r"(^|[\s;&|'\"(])(cat|less|more|head|tail|source|\.)\s+[^|;&]*\.env\b"), "reading .env files is not allowed; ask the developer for the value"),
    (re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+(/|~|\.\.|\$HOME)(\s|/|$|['\"])"), "recursive delete outside the project is not allowed"),
    (re.compile(r"\bgit\s+push\b.*(--force\b|-f\b|--force-with-lease\b)"), "force-pushing is not allowed"),
    (re.compile(r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z)?sh\b"), "piping a download into a shell is not allowed"),
]


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("guard_bash: could not parse hook input; blocking to be safe", file=sys.stderr)
        return 2  # fail closed
    if event.get("tool_name") != "Bash":
        return 0
    command = str((event.get("tool_input") or {}).get("command", ""))
    for pattern, reason in BLOCKED:
        if pattern.search(command):
            print(f"Blocked by project hook: {reason}.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
