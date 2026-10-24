"""MkDocs hooks for the GitHub Pages site.

The repository's Markdown is written for GitHub. These hooks adapt it for the site without
changing the source files:

* `<details>` and `<div align="center">` blocks get the `markdown` attribute, so the Markdown
  inside them is rendered (GitHub does that implicitly).
* Relative links to files that are not site pages (code, data, LICENSE, folders without a
  README) are rewritten to the GitHub repository, so they never 404 on the site.
* The mock-exam page gets a button that opens the interactive practice app.
"""
from __future__ import annotations

import posixpath
import re
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r"(\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
# The GitHub-only "Previous · Module overview · Next" footer; the site has its own footer.
PAGE_NAV = re.compile(r"\n*<!-- page-nav:start -->.*?<!-- page-nav:end -->\n*", re.DOTALL)
FENCE = re.compile(r"^\s*(```|~~~)")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
BRANCH = "main"

_repo_root: Path | None = None
_repo_url = ""


def on_config(config, **_):
    global _repo_root, _repo_url
    _repo_root = Path(config["config_file_path"]).resolve().parent.parent
    _repo_url = (config.get("repo_url") or "").rstrip("/")
    return config


def _rewrite(target: str, page_src: str, files) -> str:
    if SCHEME.match(target) or target.startswith(("#", "/")):
        return target
    path_part, hash_, frag = target.partition("#")
    if not path_part:
        return target
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(page_src), unquote(path_part)))
    if resolved.startswith(".."):
        return target
    if files.get_file_from_path(resolved) is not None:
        return target  # a page or asset that exists on the site
    disk = _repo_root / resolved if _repo_root else None
    if disk is not None and disk.is_dir():
        readme = posixpath.join(resolved, "README.md")
        if files.get_file_from_path(readme) is not None:
            return path_part.rstrip("/") + "/README.md" + (hash_ + frag if frag else "")
        return f"{_repo_url}/tree/{BRANCH}/{resolved}" if _repo_url else target
    if _repo_url and disk is not None and disk.exists():
        return f"{_repo_url}/blob/{BRANCH}/{resolved}" + (hash_ + frag if frag else "")
    return target


def on_page_markdown(markdown: str, page, config, files, **_):
    src = page.file.src_uri
    markdown = PAGE_NAV.sub("\n", markdown)
    out, in_fence = [], False
    for line in markdown.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence:
            line = line.replace("<details>", "<details markdown>")
            line = line.replace('<div align="center">', '<div align="center" markdown>')
            line = LINK.sub(lambda m: m.group(1) + _rewrite(m.group(2), src, files) + m.group(3), line)
        out.append(line)
    text = "\n".join(out)

    if src == "18-mock-examinations/README.md":
        button = (
            '\n[Open the practice exam app](web/index.html){ .app-launch }\n\n'
            "Runs entirely in your browser. Progress is stored only on this device.\n"
        )
        text = re.sub(r"^(# .+)$", r"\1\n" + button.replace("\\", "\\\\"), text, count=1, flags=re.MULTILINE)
    return text
