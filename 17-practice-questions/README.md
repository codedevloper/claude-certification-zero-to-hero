# 17 · Practice Questions

> **Unofficial.** Every question here was written independently for this repository. None was taken from, adapted
> from or reconstructed from an Anthropic exam, an exam dump or any other question bank, and none should be assumed
> to resemble live exam content. Anthropic's exam policy treats all real exam content as confidential.

## What's here

| Track | Folder | Files |
|---|---|---|
| CCAO-F — Claude Certified Associate – Foundations | [`ccao-f/`](ccao-f/) | `d1.json` … `d7.json`, one per exam domain |
| CCAR-P — Claude Certified Architect – Professional | [`ccar-p/`](ccar-p/) | `d1.json` … `d7.json`, one per exam domain |

Question counts per domain roughly follow the official blueprint weights in
[`registry.yaml`](../16-certification-tracks/registry.yaml), and every official objective has several questions.
The generated [CCAO-F](../16-certification-tracks/ccao-f/coverage-matrix.md) and
[CCAR-P](../16-certification-tracks/ccar-p/coverage-matrix.md) coverage matrices show which questions test each objective.

## How to practise

- **Interactively:** use the [mock-exam engine](../18-mock-examinations/README.md), in timed or learning mode, by domain,
  or by retrying questions you missed.
- **By reading:** the JSON is human-readable. Cover the `answer` field and work through a domain file.

## Question format

Each domain file validates against [`schema/question-bank.schema.json`](schema/question-bank.schema.json):

```json
{
  "schema_version": 1,
  "track": "CCAR-P",
  "domain": 3,
  "unofficial": true,
  "notice": "Independently authored practice questions. Not official Anthropic exam content.",
  "questions": [
    {
      "id": "CCAR-P-D3-001",
      "objective": "CCAR-P-3.1",
      "type": "single",
      "difficulty": "intermediate",
      "category": "security",
      "scenario": "A fictional organisation and situation…",
      "question": "What should the architect do first?",
      "options": {"A": "…", "B": "…", "C": "…", "D": "…"},
      "answer": ["C"],
      "explanation": "Why C is right, and the principle behind it.",
      "why_incorrect": {"A": "…", "B": "…", "D": "…"},
      "module": "07-tool-use-and-function-calling/06-tool-security.md",
      "references": ["https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview"]
    }
  ]
}
```

| Field | Rule |
|---|---|
| `id` | `TRACK-D<domain>-<nnn>`, unique across the repository |
| `objective` | An objective ID from the registry, belonging to the file's domain |
| `type` / `select` | `single` has exactly one key; `multiple` has 2+ keys and `select` equal to the number of keys |
| `difficulty` | `foundation`, `intermediate` or `advanced` |
| `category` | `concept`, `scenario`, `architecture`, `troubleshooting`, `security` or `cost-performance` |
| `why_incorrect` | One rationale for every distractor, and only for distractors |
| `module` | A learning page that teaches the concept (must exist) |
| `references` | Official documentation URLs |

## Quality rules

1. Test reasoning and judgment in a realistic scenario, not recall of trivia.
2. Use fictional organisations and synthetic data.
3. Make every distractor plausible, and explain why it is wrong.
4. Make every question distinct. The validator rejects stems that are more than 85% similar.
5. Base answers only on facts verified against official documentation, as of the date in the registry.
6. **No test-taking cues.** Write distractors as competent but inferior choices of similar length to the key. The
   validator fails a bank when the key is the longest option in more than 40% of items, or when one answer position
   is used far more or less often than chance.

After adding or editing questions, run `python tools/shuffle_options.py` once. It gives every question a fair,
reproducible answer order (seeded by the question ID) and remaps the key and rationales, so never refer to options by
letter in question text.

## Validation

```bash
python tools/validate_questions.py
```

The validator checks the schema, unique IDs, objective/domain consistency, that answer keys are valid options,
`select` counts, distractor rationales, explanations that claim a different letter is correct, module paths and
near-duplicates. CI runs it on every pull request.

## Contributing questions

Read [CONTRIBUTING.md](../CONTRIBUTING.md) and [docs/STYLE.md](../docs/STYLE.md). Add a question to the right domain
file with the next free ID, run the validator, then regenerate the coverage matrix with `python tools/build_coverage.py`.
