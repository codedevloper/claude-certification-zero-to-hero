"""Load the knowledge base, chunk it, screen it for injected instructions and index it.

Chunking strategy: split each Markdown file on its `##` sections (a section is usually one topic
in a policy), then split any section longer than `max_chars` on sentence boundaries with one
sentence of overlap. Each chunk keeps the document title and section heading, which helps both
BM25 (the heading words are searchable) and the model (it knows where the text came from).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .bm25 import BM25Index

# Phrases that indicate text addressed to an AI system rather than to employees. A match does not
# prove an attack, so matching chunks are quarantined for human review rather than silently lost.
INJECTION_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"ignore (all |any )?(previous|prior|above) instructions",
        r"\bnote (to|for) (ai|llm|the) (assistant|model)s?\b",
        r"\b(ai|llm) assistants?\b.*\b(must|should|tell|say)\b",
        r"disregard (the )?(system|previous) (prompt|instructions)",
        r"\byou are now\b",
        r"(email|send|share) (us |them )?(your|their) (username and )?password",
    )
]


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    section: str
    text: str

    def searchable(self) -> str:
        return f"{self.title}\n{self.section}\n{self.text}"


@dataclass
class KnowledgeBase:
    chunks: list[Chunk] = field(default_factory=list)
    quarantined: list[tuple[Chunk, str]] = field(default_factory=list)
    index: BM25Index = field(default_factory=BM25Index)

    def search(self, query: str, k: int = 4) -> list[tuple[Chunk, float]]:
        return [(self.chunks[i], score) for i, score in self.index.search(query, k)]

    def get(self, chunk_id: str) -> Chunk | None:
        return next((c for c in self.chunks if c.chunk_id == chunk_id), None)


def _sentence_windows(text: str, max_chars: int) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    windows: list[str] = []
    current: list[str] = []
    for s in sentences:
        if current and len(" ".join(current + [s])) > max_chars:
            windows.append(" ".join(current))
            current = [current[-1]]  # one sentence of overlap keeps context across the boundary
        current.append(s)
    if current:
        windows.append(" ".join(current))
    return windows


def chunk_markdown(doc_id: str, markdown: str, max_chars: int = 700) -> list[Chunk]:
    title_match = re.search(r"^#\s+(.+)$", markdown, re.M)
    title = title_match.group(1).strip() if title_match else doc_id
    parts = re.split(r"^##\s+(.+)$", markdown, flags=re.M)
    sections = [("Overview", parts[0].replace(title_match.group(0), "") if title_match else parts[0])]
    sections += [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    chunks: list[Chunk] = []
    for section, body in sections:
        body = re.sub(r"\s+", " ", body).strip()
        if not body:
            continue
        for window in _sentence_windows(body, max_chars):
            chunks.append(Chunk(f"{doc_id}#{len(chunks) + 1}", doc_id, title, section, window))
    return chunks


def screen_chunk(chunk: Chunk) -> str | None:
    """Return the matching pattern if the chunk looks like it carries instructions for an AI."""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(chunk.text) or pattern.search(chunk.section):
            return pattern.pattern
    return None


def load_kb(directory: Path, max_chars: int = 700, quarantine: bool = True) -> KnowledgeBase:
    kb = KnowledgeBase()
    for path in sorted(directory.glob("*.md")):
        for chunk in chunk_markdown(path.stem, path.read_text(encoding="utf-8"), max_chars):
            reason = screen_chunk(chunk) if quarantine else None
            if reason:
                kb.quarantined.append((chunk, reason))
            else:
                kb.chunks.append(chunk)
    if not kb.chunks:
        raise ValueError(f"no indexable chunks found in {directory}")
    kb.index.fit([c.searchable() for c in kb.chunks])
    return kb
