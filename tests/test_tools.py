"""Repository tooling behaves correctly on small synthetic inputs."""
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
