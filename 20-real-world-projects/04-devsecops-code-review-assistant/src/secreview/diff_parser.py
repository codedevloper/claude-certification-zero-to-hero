"""Minimal unified-diff parser.

It records, per file, every line that exists in the *new* version with its new line
number and whether the change added it. Only added lines are in scope for findings:
a reviewer that reports on unchanged code creates noise the author cannot act on.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

HUNK = re.compile(r"^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
MAX_DIFF_BYTES = 400_000  # refuse very large diffs instead of silently truncating them


class DiffTooLarge(ValueError):
    pass


@dataclass
class FileDiff:
    path: str
    lines: list[tuple[int, str, bool]] = field(default_factory=list)  # (new_lineno, text, added)

    @property
    def added(self) -> dict[int, str]:
        return {n: t for n, t, is_added in self.lines if is_added}


def parse_unified_diff(text: str) -> list[FileDiff]:
    if len(text.encode("utf-8")) > MAX_DIFF_BYTES:
        raise DiffTooLarge(f"diff is larger than {MAX_DIFF_BYTES} bytes; split the change or review per file")
    files: list[FileDiff] = []
    current: FileDiff | None = None
    new_line = 0
    old_left = new_left = 0  # lines still owed by the open hunk, from its @@ header
    for raw in text.splitlines():
        if old_left > 0 or new_left > 0:
            # Inside a hunk every line is content, even one that looks like a header
            # (an added line "++ /dev/null" shows up as "+++ /dev/null"). The header's
            # counts, not the line's prefix, decide where the hunk ends.
            if raw.startswith("\\"):
                continue  # "\ No newline at end of file"
            tag, body = (raw[:1], raw[1:]) if raw else (" ", "")
            if tag == "+":
                new_left -= 1
                if current is not None:
                    current.lines.append((new_line, body, True))
                new_line += 1
            elif tag == "-":
                old_left -= 1  # removed lines do not exist in the new file
            else:
                old_left -= 1
                new_left -= 1
                if current is not None:
                    current.lines.append((new_line, body if tag == " " else raw, False))
                new_line += 1
            continue
        if raw.startswith("diff --git "):
            current = None
            continue
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            if target == "/dev/null":  # deleted file: nothing added to review
                current = None
            else:
                path = target[2:] if target.startswith("b/") else target
                current = FileDiff(path=path)
                files.append(current)
            continue
        m = HUNK.match(raw)
        if m:
            old_left = int(m.group(1)) if m.group(1) is not None else 1
            new_line = int(m.group(2))
            new_left = int(m.group(3)) if m.group(3) is not None else 1
            continue
        # Anything else outside a hunk ("--- a/x", "index ...", mode lines) is metadata.
    return files
