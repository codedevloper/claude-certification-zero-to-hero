# 16 · Certification Tracks

Each supported Anthropic certification has its own preparation track. Every track maps **each official exam
objective** to learning modules, hands-on labs and practice questions. Facts come from
[`registry.yaml`](registry.yaml), which was verified against the official exam guides; the human-readable summary is
[exam-facts.md](../25-official-resources/exam-facts.md).

| Track | Who it's for | Items / time | Track |
|---|---|---|---|
| **CCAO-F** — Claude Certified Associate – Foundations | Business and knowledge workers using the Claude apps | 60 / 120 min | [Start the CCAO-F track](ccao-f/README.md) |
| **CCAR-P** — Claude Certified Architect – Professional | Architects and senior engineers delivering production systems | 63 / 120 min | [Start the CCAR-P track](ccar-p/README.md) |
| CCAR-F — Claude Certified Architect – Foundations | Developers building agentic systems | 60 / 120 min | Planned: facts recorded in the registry |
| CCDV-F — Claude Certified Developer – Foundations | Developers building on the API | 53 / 120 min | Planned: facts recorded in the registry |

## Preparing for CCAR-F before its track exists

CCAR-F (Claude Certified Architect – Foundations) has no dedicated track yet; it is the first one planned (see the
[roadmap](../ROADMAP.md)). Until then, the existing modules cover its five domains well:

| CCAR-F domain (weight) | Study these modules | Practise with |
|---|---|---|
| Agentic Architecture & Orchestration (27%) | [10 Agentic AI](../10-agentic-ai/README.md), [13 Architecture patterns](../13-enterprise-ai-architecture/02-architecture-patterns.md) | Labs [12](../19-hands-on-labs/lab-12-agentic-task-execution/README.md), [13](../19-hands-on-labs/lab-13-human-in-the-loop/README.md); [project 05](../20-real-world-projects/05-agentic-investigation-assistant/README.md) |
| Tool Design & MCP Integration (18%) | [07 Tool use](../07-tool-use-and-function-calling/README.md), [08 MCP](../08-model-context-protocol/README.md) | Labs [08](../19-hands-on-labs/lab-08-tool-invocation/README.md), [09](../19-hands-on-labs/lab-09-mcp-fundamentals/README.md) |
| Claude Code Configuration & Workflows (20%) | [09 Claude Code](../09-claude-code/README.md) | Lab [10](../19-hands-on-labs/lab-10-claude-code-workflows/README.md) |
| Prompt Engineering & Structured Output (20%) | [03 Prompt engineering](../03-prompt-engineering/README.md) | Labs [02](../19-hands-on-labs/lab-02-prompt-improvement/README.md), [03](../19-hands-on-labs/lab-03-structured-outputs/README.md) |
| Context Management & Reliability (15%) | [04 Context engineering](../04-context-engineering/README.md), [15 Reliability](../15-production-operations/05-reliability-engineering.md) | Labs [05](../19-hands-on-labs/lab-05-context-management/README.md), [18](../19-hands-on-labs/lab-18-reliability-engineering/README.md) |

The CCAR-P practice questions in domains 1–3 are the closest available practice. Weights are from the official CCAR-F
exam guide v1.0 recorded in [`registry.yaml`](registry.yaml).

## What every track contains

| File | Purpose |
|---|---|
| `README.md` | Exam overview, logistics, domain table and study sequence |
| `objective-map.yaml` | Each official objective mapped to modules and labs (the input to the coverage matrix) |
| `coverage-matrix.md` | **Generated:** objective → module → lab → practice questions |
| `study-guide/domain-N.md` | Detailed domain-by-domain notes |
| `practical-exercises.md` | Hands-on exercises with success criteria |
| `decision-scenarios.md` | Worked decision-making case studies |
| `revision-notes.md` | Condensed notes for the final week |
| `common-misconceptions.md` | Frequent misunderstandings, corrected |
| `exam-day.md` | Logistics, conduct rules and pacing |
| `readiness-assessment.md` | Self-assessment against every objective |

Practice questions live in [17-practice-questions](../17-practice-questions/README.md), timed and untimed mock exams
in [18-mock-examinations](../18-mock-examinations/README.md), and flashcards in [23-flashcards](../23-flashcards/README.md).

## Adding a new certification

The repository is designed so a new exam slots in without reorganisation:

1. Add (or flip from `planned` to `supported`) an entry in [`registry.yaml`](registry.yaml), with domains, weights and
   paraphrased objective IDs taken from the official exam guide. Record the source and date in the
   [verification log](../25-official-resources/verification-log.md).
2. Create `16-certification-tracks/<slug>/` with the files listed above, including `objective-map.yaml`.
3. Add question banks in `17-practice-questions/<slug>/d1.json …` and a flashcard deck in `23-flashcards/decks/<slug>.yaml`.
4. Run `python tools/build_coverage.py`, `python tools/build_mock_forms.py` and `python tools/validate_all.py`.

The mock-exam engine, validators and coverage tooling pick up the new track automatically from the registry.
