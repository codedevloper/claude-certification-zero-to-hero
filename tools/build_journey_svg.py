#!/usr/bin/env python3
"""Draw the README's animated "learning journey" diagram as light and dark SVGs.

The seven stages light up in order, then the labs and projects branches, and the loop
restarts. The animation is plain CSS inside the SVG, so it plays on GitHub and on the
website, and it stops (showing the finished diagram) for readers who prefer reduced motion.

  python tools/build_journey_svg.py           # write images/learning-journey-{light,dark}.svg
  python tools/build_journey_svg.py --check   # fail if the files are missing or stale (CI)
"""
from __future__ import annotations

import sys
from html import escape

from common import ROOT, Report

OUT_DIR = ROOT / "images"

STAGES = [
    (("Foundations",), "00–02"),
    (("Prompting &", "context"), "03–05"),
    (("Building",), "06–09"),
    (("Systems",), "10–11"),
    (("Secure &", "govern"), "12–13"),
    (("Operate",), "14–15"),
    (("Certify",), "16–18"),
]
# (title, subtitle, index of the stage it branches from)
BRANCHES = [("Labs 01–20", "hands-on, free in mock mode", 2), ("Projects 01–05", "real-world builds", 4)]

THEMES = {
    "light": {"card": "#ffffff", "line": "#d0d7de", "text": "#1f2328", "muted": "#59636e",
              "accent": "#c15f3c", "glow": "#f4e2d8", "badge_text": "#ffffff"},
    "dark": {"card": "#161b22", "line": "#3d444d", "text": "#e6edf3", "muted": "#9198a1",
             "accent": "#e07a55", "glow": "#3a2219", "badge_text": "#0d1117"},
}

W, H = 1000, 280
NODE_W, NODE_H, GAP, X0, Y0 = 118, 100, 24, 15, 34
BRANCH_W, BRANCH_H, BRANCH_Y = 176, 54, 206
CYCLE = 12.0                     # seconds per loop
STEP, FIRST_ON = 1.0, 0.6        # stage i lights at FIRST_ON + i * STEP
HOLD_UNTIL, FADE = 10.0, 0.8     # everything stays lit until HOLD_UNTIL, then fades
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def node_x(i: int) -> float:
    return X0 + i * (NODE_W + GAP)


def keyframes(name: str, on_at: float) -> str:
    """Off, fade in at `on_at`, stay on, fade out together with everything else."""
    pct = lambda t: f"{100 * t / CYCLE:.2f}%"  # noqa: E731
    return (f"@keyframes {name} {{ 0%, {pct(on_at)} {{ opacity: 0 }} {pct(on_at + 0.4)}, {pct(HOLD_UNTIL)} "
            f"{{ opacity: 1 }} {pct(HOLD_UNTIL + FADE)}, 100% {{ opacity: 0 }} }}")


def build(theme: str) -> str:
    c = THEMES[theme]
    css, body = [], []
    css.append(f"text {{ font-family: {FONT}; fill: {c['text']}; }}")
    css.append(f".muted {{ fill: {c['muted']}; }}")
    css.append(".on { opacity: 1; }")
    css.append("@keyframes flow { to { stroke-dashoffset: -16; } }")
    css.append(f".flow {{ stroke-dasharray: 6 10; animation: flow 0.9s linear infinite; }}")

    def lit(name: str, on_at: float) -> str:
        css.append(keyframes(name, on_at))
        css.append(f".{name} {{ animation: {name} {CYCLE}s ease-in-out infinite; }}")
        return name

    cy = Y0 + NODE_H / 2
    for i, (title, modules) in enumerate(STAGES):
        x, on_at = node_x(i), FIRST_ON + i * STEP
        if i:
            x1, x2 = node_x(i - 1) + NODE_W + 3, x - 7
            body.append(f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="{c["line"]}" stroke-width="2"/>')
            body.append(f'<g class="on {lit(f"a{i}", on_at - 0.5)}">'
                        f'<line class="flow" x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="{c["accent"]}" stroke-width="2.5"/>'
                        f'<path d="M{x2 - 1} {cy - 5} L{x2 + 6} {cy} L{x2 - 1} {cy + 5} Z" fill="{c["accent"]}"/></g>')
        body.append(f'<rect x="{x}" y="{Y0}" width="{NODE_W}" height="{NODE_H}" rx="12" fill="{c["card"]}" '
                    f'stroke="{c["line"]}" stroke-width="1.5"/>')
        body.append(f'<rect class="on {lit(f"s{i}", on_at)}" x="{x}" y="{Y0}" width="{NODE_W}" height="{NODE_H}" '
                    f'rx="12" fill="{c["glow"]}" stroke="{c["accent"]}" stroke-width="2"/>')
        body.append(f'<circle cx="{x + 20}" cy="{Y0 + 20}" r="11" fill="{c["accent"]}"/>'
                    f'<text x="{x + 20}" y="{Y0 + 24.5}" text-anchor="middle" font-size="12.5" font-weight="700" '
                    f'style="fill:{c["badge_text"]}">{i + 1}</text>')
        ty = Y0 + 58 - 9 * (len(title) - 1)
        for k, line in enumerate(title):
            body.append(f'<text x="{x + NODE_W / 2}" y="{ty + 18 * k}" text-anchor="middle" font-size="15" '
                        f'font-weight="650">{escape(line)}</text>')
        body.append(f'<text class="muted" x="{x + NODE_W / 2}" y="{Y0 + NODE_H - 12}" text-anchor="middle" '
                    f'font-size="12">Modules {modules}</text>')

    for j, (title, sub, src) in enumerate(BRANCHES):
        sx = node_x(src) + NODE_W / 2
        bx, on_at = sx - BRANCH_W / 2, FIRST_ON + src * STEP + 0.6
        y1, y2 = Y0 + NODE_H + 3, BRANCH_Y - 4
        body.append(f'<line x1="{sx}" y1="{y1}" x2="{sx}" y2="{y2}" stroke="{c["line"]}" stroke-width="2" '
                    f'stroke-dasharray="3 5"/>')
        body.append(f'<g class="on {lit(f"b{j}", on_at)}">'
                    f'<line class="flow" x1="{sx}" y1="{y1}" x2="{sx}" y2="{y2}" stroke="{c["accent"]}" stroke-width="2.5"/>'
                    f'<rect x="{bx}" y="{BRANCH_Y}" width="{BRANCH_W}" height="{BRANCH_H}" rx="10" fill="{c["glow"]}" '
                    f'stroke="{c["accent"]}" stroke-width="2"/></g>')
        body.append(f'<rect x="{bx}" y="{BRANCH_Y}" width="{BRANCH_W}" height="{BRANCH_H}" rx="10" fill="none" '
                    f'stroke="{c["line"]}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        body.append(f'<text x="{sx}" y="{BRANCH_Y + 23}" text-anchor="middle" font-size="14.5" '
                    f'font-weight="650">{escape(title)}</text>')
        body.append(f'<text class="muted" x="{sx}" y="{BRANCH_Y + 42}" text-anchor="middle" '
                    f'font-size="12">{escape(sub)}</text>')

    css.append("@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }")
    summary = ", then ".join(" ".join(t) for t, _ in STAGES)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-labelledby="title">\n'
        f'<!-- Generated by tools/build_journey_svg.py. Do not edit by hand. -->\n'
        f'<title id="title">Learning journey: {escape(summary)}. Labs branch from Building; projects branch '
        f'from Secure and govern.</title>\n'
        f'<style>\n' + "\n".join(css) + '\n</style>\n' + "\n".join(body) + "\n</svg>\n"
    )


def main(check: bool) -> int:
    report = Report("learning journey diagram")
    for theme in THEMES:
        path = OUT_DIR / f"learning-journey-{theme}.svg"
        svg = build(theme)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != svg:
                report.error(f"{path.relative_to(ROOT)} is missing or stale: run python tools/build_journey_svg.py")
        else:
            path.write_text(svg, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    report.print()
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
