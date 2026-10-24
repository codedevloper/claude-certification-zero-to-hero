"""Minimal unified-diff parser.

It records, per file, every line that exists in the *new* version with its new line
number and whether the change added it. Only added lines are in scope for findings:
a reviewer that reports on unchanged code creates noise the author cannot act on.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
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
    in_hunk = False
    for raw in text.splitlines():
        if raw.startswith("diff --git "):
            current, in_hunk = None, False
            continue
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            if target == "/dev/null":  # deleted file: nothing added to review
                current = None
            else:
                path = target[2:] if target.startswith("b/") else target
                current = FileDiff(path=path)
                files.append(current)
            in_hunk = False
            continue
        if raw.startswith("--- ") and not in_hunk:
            continue
        m = HUNK.match(raw)
        if m:
            new_line = int(m.group(1))
            in_hunk = True
            continue
        if not in_hunk or current is None:
            continue
        if raw.startswith("+"):
            current.lines.append((new_line, raw[1:], True))
            new_line += 1
        elif raw.startswith("-"):
            continue  # removed lines do not exist in the new file
        elif raw.startswith("\\"):
            continue  # "\ No newline at end of file"
        else:
            current.lines.append((new_line, raw[1:] if raw.startswith(" ") else raw, False))
            new_line += 1
    return files
