# 23 · Flashcards

Short question-and-answer cards for spaced repetition. Use them to lock in terms, rules and facts after you have
studied the modules; they are a memory aid, not a way to learn a topic for the first time. All cards are original and
unofficial. None reproduce exam questions.

## Decks

| Deck file | Cards cover | Card IDs |
|---|---|---|
| [`decks/fundamentals.yaml`](decks/fundamentals.yaml) | LLM fundamentals, Claude and Anthropic, prompting, thinking and effort, context engineering, the API, tools and agents, MCP, RAG, security, evaluation | `FUN-FC-001` … |
| [`decks/ccao-f.yaml`](decks/ccao-f.yaml) | CCAO-F objectives, domain by domain | `CCAO-F-FC-001` … |
| [`decks/ccar-p.yaml`](decks/ccar-p.yaml) | CCAR-P objectives, domain by domain | `CCAR-P-FC-001` … |

Start with **fundamentals** whichever certification you target, then move to your track deck. Exam facts referenced by
the track decks come from [`registry.yaml`](../16-certification-tracks/registry.yaml); product and API facts are dated
2026-10-24 in each deck's header comment.

## How to study with the decks

1. **Learn first, then drill.** Read the module linked from a card's `module` field before drilling that card.
2. **Recall actively.** Read the front, say or write your answer, then check the back. Recognising an answer is not
   the same as recalling it.
3. **Space your reviews.** Review new cards the next day, then after 3 days, a week, two weeks and a month. Cards you
   miss go back to the start. Anki or any spaced-repetition app does this scheduling for you (see export below).
4. **Little and often.** Fifteen to twenty minutes a day beats a long weekly session.
5. **Focus by objective.** Track cards carry an `objective` ID; if a mock exam shows a weak domain, filter to its
   objectives (Anki tags make this easy).
6. **Rewrite cards you keep missing.** Often the card is too broad; split it into two smaller cards in your own copy.
7. **Do not rely on cards alone.** Pair them with [practice questions](../17-practice-questions/README.md),
   [mock exams](../18-mock-examinations/README.md) and the [hands-on labs](../19-hands-on-labs/README.md).

Suggested use by study plan:

| Plan | Fundamentals deck | Track deck |
|---|---|---|
| [7-day accelerated](../00-getting-started/roadmaps/7-day-accelerated.md) | Days 1–3, 20 cards a day | Days 4–7, all cards, misses daily |
| [30-day structured](../00-getting-started/roadmaps/30-day-structured.md) | Weeks 1–2, alongside the modules | Weeks 2–4, by domain |
| [60-day comprehensive](../00-getting-started/roadmaps/60-day-comprehensive.md) | Weeks 1–4 | Weeks 4–8, with weekly full reviews |

## Deck format

Each deck is a YAML file with three top-level keys and a list of cards:

```yaml
deck: fundamentals                  # short deck name, used as an Anki tag
title: Fundamentals — Claude, LLMs, prompting, API, tools, MCP, RAG and security
cards:
  - id: FUN-FC-001                  # unique across ALL decks
    front: "What does a large language model fundamentally do?"
    back: "Predicts the next token given all previous tokens; ..."
    module: 01-ai-and-llm-fundamentals/03-large-language-models.md   # where to learn it
  - id: CCAO-F-FC-001
    objective: CCAO-F-1.1           # optional; must be an objective ID from registry.yaml
    front: "..."
    back: "..."
    module: 03-prompt-engineering/01-clear-direct-instructions.md
```

| Field | Required | Rules |
|---|---|---|
| `id` | Yes | Unique across every deck; deck prefix plus `-FC-` plus a three-digit number |
| `front` | Yes | One question or prompt; short enough to read in a few seconds |
| `back` | Yes | The answer in one or two sentences; dated where the fact can change |
| `objective` | No | An objective ID that exists in [`registry.yaml`](../16-certification-tracks/registry.yaml); omit for general fundamentals |
| `module` | Recommended | A repository path listed in [CONTENT-MAP](../docs/CONTENT-MAP.md), optionally with a `#heading` anchor |

Quote strings that contain a colon or `#` so YAML parses them as text.

## Validate and export to Anki

Validate every deck (unique IDs, non-empty sides, known objectives, existing module paths):

```bash
python tools/flashcards.py
```

Export each deck as an Anki-importable CSV (one file per deck, written to the directory you name):

```bash
python tools/flashcards.py --export flashcards-out/
```

Each CSV row has three columns: **front**, **back**, and **tags** (the deck name plus the objective ID, if any). The
export runs only when validation passes.

To import into Anki:

1. In Anki, choose **File → Import** and select one CSV (for example `fundamentals.csv`).
2. Set the note type to **Basic**, the field separator to **Comma**, and map column 1 to *Front*, column 2 to *Back*
   and column 3 to *Tags*.
3. Choose or create a target deck, then import. Repeat for the other CSV files.
4. Re-importing an updated CSV can create duplicates; Anki's duplicate handling setting controls this, or delete the
   old deck first.

## Contributing cards

Write cards in your own words, check facts against official sources, date anything time-sensitive, and run
`python tools/flashcards.py` before opening a pull request. Never add real or reconstructed exam questions. See
[CONTRIBUTING](../CONTRIBUTING.md) and [STYLE](../docs/STYLE.md).
