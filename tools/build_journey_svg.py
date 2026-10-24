#!/usr/bin/env python3
"""Draw the README's animated "learning journey" diagram as light and dark SVGs.

A glowing marker runs along a progress track; each stage card it reaches pops and fills
with colour, the labs and projects branches light up on the way, and the loop restarts.
The animation is plain CSS inside the SVG, so it plays on GitHub and on the website, and
it stops (showing the finished diagram) for readers who prefer reduced motion.

  python tools/build_journey_svg.py           # write images/learning-journey-{light,dark}.svg
  python tools/build_journey_svg.py --check   # fail if the files are missing or stale (CI)
"""
from __future__ import annotations

import sys
from html import escape

from common import ROOT, Report

OUT_DIR = ROOT / "images"

# 24x24 line icons (stroke only), drawn in the card's icon colour.
ICONS = {
    "book": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5zM4 21.5v-16M8 7.5h8M8 11h6"/>',
    "chat": '<path d="M4 5h16v11H9.5L4 20.5zM8 9h8M8 12.5h5"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "nodes": '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/>'
             '<path d="M12 7.5v3.5M12 11l-5.2 5M12 11l5.2 5"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6zM8.5 12l2.5 2.5 4.5-4.5"/>',
    "pulse": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "trophy": '<path d="M8 4h8v5a4 4 0 0 1-8 0zM8 6H5a3 3 0 0 0 3.5 4M16 6h3a3 3 0 0 1-3.5 4M12 13v4M8 20.5h8M10 17h4v3.5"/>',
    "flask": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5-9V3M7.5 15h9"/>',
    "rocket": '<path d="M12 15l-3-3c1.5-5 5-8 10-9-1 5-4 8.5-9 10zM9 12l-4 1 2-4h4M12 15l-1 4 4-2v-4M6.5 17.5L4 20"/>',
}

STAGES = [
    (("Foundations",), "00–02", "book"),
    (("Prompting &", "context"), "03–05", "chat"),
    (("Building",), "06–09", "code"),
    (("Systems",), "10–11", "nodes"),
    (("Secure &", "govern"), "12–13", "shield"),
    (("Operate",), "14–15", "pulse"),
    (("Certify",), "16–18", "trophy"),
]
# (title, subtitle, icon, index of the stage it branches from)
BRANCHES = [("Labs 01–20", "hands-on, free in mock mode", "flask", 2),
            ("Projects 01–05", "real-world builds", "rocket", 4)]

THEMES = {
    "light": {"card": "#ffffff", "edge": "#e1e4e8", "text": "#1f2328", "muted": "#656d76", "track": "#e6e8eb",
              "shadow": "#1f2328", "shadow_opacity": 0.10},
    "dark": {"card": "#161b22", "edge": "#30363d", "text": "#e6edf3", "muted": "#9198a1", "track": "#262c36",
             "shadow": "#000000", "shadow_opacity": 0.45},
}
GRAD_FROM, GRAD_TO, ACCENT = "#f0915f", "#c4452f", "#d9643f"

W, H = 1020, 300
CARD_W, CARD_H, GAP, X0, Y0 = 124, 118, 22, 10, 14
TRACK_Y = 160
BRANCH_W, BRANCH_H, BRANCH_Y = 232, 52, 222
CYCLE = 6.0                              # seconds per loop
START, STEP = 0.25, 0.5                  # the marker reaches stage i at START + i * STEP
HOLD_UNTIL, FADE = 5.0, 0.5              # everything stays lit until HOLD_UNTIL, then fades
MUTED, WHITE = 'class="muted"', 'class="white"'
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def cx(i: int) -> float:
    return X0 + i * (CARD_W + GAP) + CARD_W / 2


def pct(t: float) -> str:
    return f"{100 * t / CYCLE:.2f}%"


def build(theme: str) -> str:
    c = THEMES[theme]
    css: list[str] = []
    defs, back, front = [], [], []
    end_t = START + (len(STAGES) - 1) * STEP

    css += [
        f"text {{ font-family: {FONT}; fill: {c['text']}; }}",
        f".muted {{ fill: {c['muted']}; }}",
        ".white { fill: #ffffff; }",
        ".pop { transform-box: fill-box; transform-origin: center; }",
        # Pop in with a small overshoot, stay, fade out with everything else.
        "@keyframes flowdash { to { stroke-dashoffset: -14; } }",
        ".dash { stroke-dasharray: 5 9; animation: flowdash 0.6s linear infinite; }",
    ]

    def lit(name: str, on_at: float) -> str:
        css.append(
            f"@keyframes {name} {{ 0%, {pct(on_at)} {{ opacity: 0; transform: scale(0.9) }} "
            f"{pct(on_at + 0.18)} {{ opacity: 1; transform: scale(1.06) }} "
            f"{pct(on_at + 0.32)}, {pct(HOLD_UNTIL)} {{ opacity: 1; transform: scale(1) }} "
            f"{pct(HOLD_UNTIL + FADE)}, 100% {{ opacity: 0; transform: scale(1) }} }}")
        css.append(f".{name} {{ animation: {name} {CYCLE}s ease-out infinite; }}")
        return name

    defs.append(f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GRAD_FROM}"/>'
                f'<stop offset="1" stop-color="{GRAD_TO}"/></linearGradient>')
    defs.append(f'<linearGradient id="gt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GRAD_FROM}"/>'
                f'<stop offset="1" stop-color="{GRAD_TO}"/></linearGradient>')
    defs.append(f'<filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="3" '
                f'stdDeviation="4" flood-color="{c["shadow"]}" flood-opacity="{c["shadow_opacity"]}"/></filter>')
    defs.append('<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="5"/>'
                '</filter>')
    defs.append(f'<filter id="halo" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/>'
                f'</filter>')

    def icon(name: str, x: float, y: float, colour: str, size: float = 26) -> str:
        s = size / 24
        return (f'<g transform="translate({x - size / 2} {y}) scale({s:.3f})" fill="none" stroke="{colour}" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')

    # Progress track and the line that draws itself behind the moving marker.
    x_first, x_last = cx(0), cx(len(STAGES) - 1)
    length = x_last - x_first
    back.append(f'<line x1="{x_first}" y1="{TRACK_Y}" x2="{x_last}" y2="{TRACK_Y}" stroke="{c["track"]}" '
                f'stroke-width="6" stroke-linecap="round"/>')
    css.append(
        f"@keyframes draw {{ 0%, {pct(START)} {{ stroke-dashoffset: {length:.0f}; opacity: 1 }} "
        f"{pct(end_t)}, {pct(HOLD_UNTIL)} {{ stroke-dashoffset: 0; opacity: 1 }} "
        f"{pct(HOLD_UNTIL + FADE)} {{ stroke-dashoffset: 0; opacity: 0 }} 100% {{ stroke-dashoffset: {length:.0f}; opacity: 0 }} }}")
    css.append(f".draw {{ stroke-dasharray: {length:.0f}; animation: draw {CYCLE}s linear infinite; }}")
    back.append(f'<line class="draw" x1="{x_first}" y1="{TRACK_Y}" x2="{x_last}" y2="{TRACK_Y}" stroke="url(#gt)" '
                f'stroke-width="6" stroke-linecap="round"/>')

    # Branches hang below the track.
    for j, (title, sub, ic, src) in enumerate(BRANCHES):
        x, on_at = cx(src), START + src * STEP + 0.25
        bx = x - BRANCH_W / 2
        back.append(f'<line x1="{x}" y1="{TRACK_Y + 8}" x2="{x}" y2="{BRANCH_Y - 4}" stroke="{c["edge"]}" '
                    f'stroke-width="2" stroke-dasharray="3 5"/>')
        name = lit(f"b{j}", on_at)
        back.append(f'<g class="on {name}"><line class="dash" x1="{x}" y1="{TRACK_Y + 8}" x2="{x}" '
                    f'y2="{BRANCH_Y - 4}" stroke="{ACCENT}" stroke-width="2.5"/></g>')
        front.append(f'<rect x="{bx}" y="{BRANCH_Y}" width="{BRANCH_W}" height="{BRANCH_H}" rx="26" '
                     f'fill="{c["card"]}" stroke="{c["edge"]}" stroke-width="1.5" filter="url(#sh)"/>')
        front.append(icon(ic, bx + 30, BRANCH_Y + 14, ACCENT, 24))
        front.append(f'<text x="{bx + 52}" y="{BRANCH_Y + 23}" font-size="14.5" font-weight="700">{escape(title)}</text>')
        front.append(f'<text class="muted" x="{bx + 52}" y="{BRANCH_Y + 40}" font-size="11.5">{escape(sub)}</text>')
        front.append(f'<g class="on pop {name}"><rect x="{bx}" y="{BRANCH_Y}" width="{BRANCH_W}" height="{BRANCH_H}" '
                     f'rx="26" fill="url(#g)"/>{icon(ic, bx + 30, BRANCH_Y + 14, "#ffffff", 24)}'
                     f'<text class="white" x="{bx + 52}" y="{BRANCH_Y + 23}" font-size="14.5" font-weight="700">'
                     f'{escape(title)}</text><text class="white" x="{bx + 52}" y="{BRANCH_Y + 40}" font-size="11.5" '
                     f'opacity="0.9">{escape(sub)}</text></g>')

    # Stage cards with a coloured overlay that pops in when the marker arrives.
    for i, (title, modules, ic) in enumerate(STAGES):
        x, mid, on_at = cx(i) - CARD_W / 2, cx(i), START + i * STEP
        name = lit(f"s{i}", on_at)
        if i == len(STAGES) - 1:   # a soft halo behind the final stage
            front.append(f'<g class="on {name}"><rect x="{x - 4}" y="{Y0 - 2}" width="{CARD_W + 8}" '
                         f'height="{CARD_H + 8}" rx="18" fill="{GRAD_FROM}" opacity="0.55" filter="url(#halo)"/></g>')
        front.append(f'<rect x="{x}" y="{Y0}" width="{CARD_W}" height="{CARD_H}" rx="14" fill="{c["card"]}" '
                     f'stroke="{c["edge"]}" stroke-width="1.5" filter="url(#sh)"/>')
        ty = Y0 + 70 - 8 * (len(title) - 1)

        def labels(cls: str, colour: str) -> str:
            out = [icon(ic, mid, Y0 + 14, colour)]
            out.append(f'<text {cls} x="{x + 12}" y="{Y0 + 22}" font-size="10.5" font-weight="700" '
                       f'letter-spacing="0.6" opacity="0.75">{i + 1:02d}</text>')
            out += [f'<text {cls} x="{mid}" y="{ty + 17 * k}" text-anchor="middle" font-size="14.5" '
                    f'font-weight="700">{escape(line)}</text>' for k, line in enumerate(title)]
            out.append(f'<text {cls or MUTED} x="{mid}" y="{Y0 + CARD_H - 13}" text-anchor="middle" '
                       f'font-size="11.5">Modules {modules}</text>')
            return "".join(out)

        front.append(labels("", ACCENT))
        front.append(f'<g class="on pop {name}"><rect x="{x}" y="{Y0}" width="{CARD_W}" height="{CARD_H}" rx="14" '
                     f'fill="url(#g)"/>{labels(WHITE, "#ffffff")}</g>')
        # Stop on the track: grey dot, then a filled one when reached.
        front.append(f'<circle cx="{mid}" cy="{TRACK_Y}" r="7" fill="{c["card"]}" stroke="{c["edge"]}" stroke-width="2"/>')
        front.append(f'<circle class="on pop {name}" cx="{mid}" cy="{TRACK_Y}" r="7" fill="url(#g)" '
                     f'stroke="#ffffff" stroke-width="2"/>')

    # The glowing marker that runs along the track.
    css.append(
        f"@keyframes run {{ 0%, {pct(START - 0.1)} {{ transform: translateX(0); opacity: 0 }} "
        f"{pct(START)} {{ transform: translateX(0); opacity: 1 }} "
        f"{pct(end_t)} {{ transform: translateX({length:.0f}px); opacity: 1 }} "
        f"{pct(end_t + 0.4)}, 100% {{ transform: translateX({length:.0f}px); opacity: 0 }} }}")
    css.append(f".run {{ animation: run {CYCLE}s linear infinite; opacity: 0; }}")
    front.append(f'<g class="run"><circle cx="{x_first}" cy="{TRACK_Y}" r="13" fill="{GRAD_FROM}" opacity="0.8" '
                 f'filter="url(#glow)"/><circle cx="{x_first}" cy="{TRACK_Y}" r="5.5" fill="#ffffff"/></g>')

    css.append("@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }")
    summary = ", then ".join(" ".join(t) for t, _, _ in STAGES)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-labelledby="title">\n'
        f'<!-- Generated by tools/build_journey_svg.py. Do not edit by hand. -->\n'
        f'<title id="title">Learning journey: {escape(summary)}. Labs branch from Building; projects branch '
        f'from Secure and govern.</title>\n'
        f'<defs>{"".join(defs)}</defs>\n'
        f'<style>\n' + "\n".join(css) + '\n</style>\n' + "\n".join(back + front) + "\n</svg>\n"
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
