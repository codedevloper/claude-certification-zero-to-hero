"""Blueprint-weighted, randomised question selection."""
from __future__ import annotations

import random
from collections import defaultdict

from .bank import Question, Track


def allocate(weights: dict[int, float], count: int) -> dict[int, int]:
    """Split `count` items across domains in proportion to blueprint weights
    (largest-remainder method, so the total is always exact)."""
    total = sum(weights.values())
    raw = {d: count * w / total for d, w in weights.items()}
    alloc = {d: int(v) for d, v in raw.items()}
    leftover = count - sum(alloc.values())
    for d in sorted(raw, key=lambda d: raw[d] - alloc[d], reverse=True)[:leftover]:
        alloc[d] += 1
    return alloc


def select_questions(
    track: Track,
    count: int,
    rng: random.Random,
    domain: int | None = None,
    weak_ids: set[str] | None = None,
) -> list[Question]:
    pool = [q for q in track.questions if domain is None or q.domain == domain]
    if not pool:
        return []
    count = min(count, len(pool))
    by_domain: dict[int, list[Question]] = defaultdict(list)
    for q in pool:
        by_domain[q.domain].append(q)

    def ordered(qs: list[Question]) -> list[Question]:
        qs = qs[:]
        rng.shuffle(qs)
        if weak_ids:  # previously-missed questions first
            qs.sort(key=lambda q: q.id not in weak_ids)
        return qs

    if domain is not None:
        return ordered(by_domain[domain])[:count]

    alloc = allocate({d: track.domains[d]["weight"] for d in by_domain}, count)
    chosen: list[Question] = []
    spare: list[Question] = []
    for d, qs in by_domain.items():
        qs = ordered(qs)
        chosen += qs[: alloc[d]]
        spare += qs[alloc[d]:]
    # If a domain had fewer questions than its allocation, top up from the rest.
    rng.shuffle(spare)
    chosen += spare[: count - len(chosen)]
    rng.shuffle(chosen)
    return chosen
