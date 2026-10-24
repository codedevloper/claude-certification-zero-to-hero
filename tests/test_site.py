"""GitHub Pages build helpers: navigation ordering, staging filters and link rewriting."""
from pathlib import Path

import build_site
import hooks


class FakeFiles:
    def __init__(self, paths):
        self.paths = set(paths)

    def get_file_from_path(self, path):
        return path if path in self.paths else None


def test_natural_sort_orders_numbers():
    names = ["15-day.md", "7-day.md", "lab-10", "lab-2"]
    assert sorted((Path(n) for n in names), key=build_site.natural) == [
        Path("7-day.md"), Path("15-day.md"), Path("lab-2"), Path("lab-10")]


def test_staging_skips_program_inputs():
    assert build_site.wanted(Path("03-prompt-engineering/01-clear-direct-instructions.md"))
    assert not build_site.wanted(Path("20-real-world-projects/02-x/data/kb/page.md"))
    assert not build_site.wanted(Path("19-hands-on-labs/lab-10/sample-project/CLAUDE.md"))
    assert not build_site.wanted(Path("tools/README.md"))


def test_link_rewriting(monkeypatch):
    monkeypatch.setattr(hooks, "_repo_root", build_site.ROOT)
    monkeypatch.setattr(hooks, "_repo_url", "https://github.com/u/r")
    files = FakeFiles({"06-claude-api/README.md", "16-certification-tracks/README.md"})
    page = "16-certification-tracks/README.md"
    # Existing site page: untouched.
    assert hooks._rewrite("../06-claude-api/README.md#x", page, files) == "../06-claude-api/README.md#x"
    # Data file: sent to GitHub.
    assert hooks._rewrite("registry.yaml", page, files) == "https://github.com/u/r/blob/main/16-certification-tracks/registry.yaml"
    # External and in-page links: untouched.
    assert hooks._rewrite("https://example.com", page, files) == "https://example.com"
    assert hooks._rewrite("#top", page, files) == "#top"


def test_markdown_adaptation(monkeypatch):
    class Page:
        class file:
            src_uri = "FAQ.md"

    monkeypatch.setattr(hooks, "_repo_root", build_site.ROOT)
    monkeypatch.setattr(hooks, "_repo_url", "")
    md = "<details>\n<summary>A</summary>\n\n**x**\n</details>\n```\n<details>\n```"
    out = hooks.on_page_markdown(md, Page, {}, FakeFiles(set()))
    assert out.splitlines()[0] == "<details markdown>"
    assert out.splitlines()[-2] == "<details>"  # code blocks are left alone
