# Website (GitHub Pages)

This folder holds the configuration for the published website. The content itself is the repository's Markdown;
nothing here duplicates it.

| File | Purpose |
|---|---|
| `mkdocs.yml` | Base MkDocs + Material configuration: theme, colours, Markdown extensions, link validation |
| `hooks.py` | Adapts GitHub-flavoured Markdown for the site (see below) |
| `assets/` | Site CSS and favicon |

## How the build works

`python tools/build_site.py` does the following:

1. Stages the reading material into `.site/docs/`: Markdown pages, images, and the browser mock-exam app from
   `18-mock-examinations/web/`. Program inputs such as lab `data/`, project `src/` and `tests/`, and the Claude Code
   `sample-project/` are not published as pages.
2. Generates the navigation from the numbered folders, grouped into the tabs Start here, Learn, Certify, Build and About.
3. Writes `.site/mkdocs.yml`, which inherits this folder's `mkdocs.yml`, then runs MkDocs into `site/`.

`hooks.py` then makes three adjustments at build time, without changing source files:

- It renders Markdown inside `<details>` blocks and centred `<div>` blocks.
- It rewrites links to files that are not pages (`.py`, `.yaml`, `.json`, `LICENSE`, folders without a README) to the
  GitHub repository, so they never 404 on the site.
- It adds an **Open the practice exam app** button to the mock-examinations page.

Both `.site/` and `site/` are git-ignored.

## Commands

```bash
pip install -r requirements-docs.txt
python tools/build_site.py             # build into site/
python tools/build_site.py --serve     # live preview at http://127.0.0.1:8000
python tools/build_site.py --strict    # fail on any warning (what CI runs)
```

`REPO_URL` and `SITE_URL` are read from the environment; the Pages workflow sets both. Locally, `REPO_URL` defaults
to your `origin` git remote.

## Versions

MkDocs 1.6.1, Material for MkDocs 9.7.7 and their Markdown extensions are pinned in `requirements-docs.txt`. The
Material team has announced that MkDocs 2.0 will break plugins and themes, so the site deliberately stays on MkDocs 1.x.
Re-evaluate before upgrading.
