"""Repository tooling behaves correctly on small synthetic inputs."""
import json

import check_links
import scan_secrets
import validate_questions
from mockexam.scoring import parse_answer


def test_slugify_matches_github_style():
    assert check_links.slugify("2. Why it matters!") == "2-why-it-matters"
    assert check_links.slugify("Check your `understanding`") == "check-your-understanding"


def test_strip_code_ignores_links_in_fences():
    text = "```\n[x](missing.md)\n```\n[y](real.md)"
    stripped = check_links.strip_code(text)
    assert "missing.md" not in stripped and "real.md" in stripped


def test_secret_patterns_detect_and_allow():
    key = "sk-ant-api03-" + "A" * 40
    assert scan_secrets.PATTERNS["Anthropic API key"].search(key)
    assert scan_secrets.ALLOW.search("ANTHROPIC_API_KEY=your-api-key-here")


def test_correct_claim_regex():
    found = validate_questions.CORRECT_CLAIM.findall("Option C is correct because... and (B) is the best fit")
    assert [f.upper() for f in found] == ["C", "B"]


def test_parse_answer_ignores_noise():
    assert parse_answer(" b ; d ") == ("B", "D")


def test_repository_checks_pass():
    """The live repository must pass the core content checks."""
    for report in (validate_questions.validate(), check_links.check(), scan_secrets.scan()):
        assert report.ok, report.errors[:10]


def _q(qid, opts, answer):
    return {"id": qid, "scenario": "A synthetic scenario for testing.", "question": "Pick?", "options": opts,
            "answer": answer, "explanation": "Because.", "why_incorrect": {k: f"not {k}" for k in opts if k not in answer}}


def test_longest_option_detection():
    assert validate_questions.longest_is_key(_q("X", {"A": "short", "B": "a much longer answer"}, ["B"]))
    assert not validate_questions.longest_is_key(_q("X", {"A": "short", "B": "a much longer answer"}, ["A"]))


def test_cueing_stats_counts_positions():
    qs = [_q(f"X-{i}", {"A": "aa", "B": "bbbb", "C": "c", "D": "dd"}, ["B"]) for i in range(8)]
    stats = validate_questions.cueing_stats(qs)
    assert stats["longest_rate"] == 1.0
    assert stats["positions"]["B"] == (8, 2.0)


def test_shuffle_keeps_the_correct_text_and_rationales():
    import shuffle_options
    q = _q("CCAR-P-D1-001", {"A": "alpha", "B": "bravo", "C": "charlie", "D": "delta"}, ["C"])
    q["why_incorrect"] = {"A": "why alpha", "B": "why bravo", "D": "why delta"}
    out = shuffle_options.shuffle(json.loads(json.dumps(q)))
    assert [out["options"][a] for a in out["answer"]] == ["charlie"]
    for letter, why in out["why_incorrect"].items():
        assert why == "why " + out["options"][letter]
    again = shuffle_options.shuffle(json.loads(json.dumps(q)))
    assert again == out  # deterministic


def test_letter_references_are_detected():
    import shuffle_options
    q = _q("X", {"A": "a", "B": "b", "C": "c", "D": "d"}, ["A"])
    q["explanation"] = "Option B is tempting but wrong."
    assert shuffle_options.refers_to_letters(q)


def test_secret_allowlist_applies_to_the_matched_value_only():
    real_looking = "sk-ant-api03-" + "Q" * 40
    line = f"api_key = '{real_looking}'  # see example in docs"
    matches = [m.group(0) for m in scan_secrets.PATTERNS["Anthropic API key"].finditer(line)]
    assert matches and not scan_secrets.ALLOW.search(matches[0])
