"""Render a validated summary as Markdown for each audience.

Model text is escaped before rendering so a summary cannot inject Markdown links, HTML or
headings into the page that displays it.
"""
from __future__ import annotations

import html
import re
from typing import Any

_MD_SPECIAL = re.compile(r"([\\`*_\[\]<>#|])")


def escape_md(text: str) -> str:
    return _MD_SPECIAL.sub(r"\\\1", html.unescape(text)).replace("\n", " ")


def render_markdown(summary: dict[str, Any]) -> str:
    audience = summary["audience"]
    lines = [f"## {escape_md(summary['headline'])}", "", f"*Audience: {audience}*", "", escape_md(summary["summary"]), ""]
    if audience == "executive":
        order = ("decision", "risk", "metric", "finding", "action")
        lines.append("### What matters")
    elif audience == "engineering":
        order = ("finding", "metric", "action", "risk", "decision")
        lines.append("### Technical points")
    else:
        order = ("risk", "finding", "action", "decision", "metric")
        lines.append("### Risk and control points")
    for category in order:
        for kp in summary["key_points"]:
            if kp["category"] == category:
                lines.append(f"- **{category}**: {escape_md(kp['point'])}")
                if audience != "executive":
                    lines.append(f"  - Source: \"{escape_md(kp['evidence_quote'])}\"")
    if summary["action_items"]:
        lines += ["", "### Actions", "", "| Action | Owner |", "|---|---|"]
        for item in summary["action_items"]:
            lines.append(f"| {escape_md(item['action'])} | {escape_md(item['owner'])} |")
    if summary["open_questions"]:
        lines += ["", "### Open questions"]
        lines += [f"- {escape_md(q)}" for q in summary["open_questions"]]
    return "\n".join(lines) + "\n"
