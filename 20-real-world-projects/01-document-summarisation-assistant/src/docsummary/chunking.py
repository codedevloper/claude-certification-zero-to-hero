"""Split a long document into chunks for the map step.

The splitter works on paragraph boundaries so a chunk never cuts a sentence in half, which
keeps evidence quotes intact. Token counts are estimated at roughly four characters per token;
in live mode you can confirm with `client.messages.count_tokens(...)` before sending.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

CHARS_PER_TOKEN = 4


@dataclass(frozen=True)
class Chunk:
    index: int
    text: str

    @property
    def est_tokens(self) -> int:
        return max(1, len(self.text) // CHARS_PER_TOKEN)


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    """Fallback for a single paragraph longer than the budget: split on sentence ends."""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    parts: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + 1 + len(sentence) > max_chars:
            parts.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        parts.append(current)
    return parts


def chunk_document(text: str, max_chars: int = 3500) -> list[Chunk]:
    """Greedy paragraph packing. Each chunk stays at or under `max_chars` where possible.

    Section headings (lines starting with '#') are carried into the next chunk so each chunk
    keeps its context: a figure under "4. Technology" means something different elsewhere.
    """
    if max_chars < 200:
        raise ValueError("max_chars must be at least 200")
    pieces: list[str] = []
    for paragraph in split_paragraphs(text):
        if len(paragraph) > max_chars:
            pieces.extend(_split_long_paragraph(paragraph, max_chars))
        else:
            pieces.append(paragraph)

    chunks: list[str] = []
    current: list[str] = []
    size = 0
    heading = ""
    for piece in pieces:
        if piece.startswith("#"):
            heading = piece
        if current and size + len(piece) + 2 > max_chars:
            chunks.append("\n\n".join(current))
            current, size = [], 0
            if heading and not piece.startswith("#"):
                current.append(heading)
                size = len(heading) + 2
        current.append(piece)
        size += len(piece) + 2
    if current:
        chunks.append("\n\n".join(current))
    return [Chunk(i, c) for i, c in enumerate(chunks)]
