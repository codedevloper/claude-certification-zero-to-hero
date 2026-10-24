#!/usr/bin/env python3
"""Draw the README's animated diagrams as light and dark SVGs.

Every diagram shares one visual language: white (or dark) cards with line icons, an
orange gradient for "active" states, and short CSS animations that loop. The animation
is plain CSS inside each SVG, so it plays on GitHub and on the website, and it stops
(showing the finished diagram) for readers who prefer reduced motion.

Counts shown in the banner come from the repository itself, so --check also catches a
banner that has fallen out of date.

  python tools/build_readme_visuals.py           # write images/<name>-{light,dark}.svg
  python tools/build_readme_visuals.py --check   # fail if any file is missing or stale (CI)
"""
from __future__ import annotations

import sys
from html import escape
from typing import Callable

import yaml

from common import FLASHCARDS_DIR, LABS_DIR, ROOT, Report, certifications, load_questions

OUT_DIR = ROOT / "images"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "light": {"card": "#ffffff", "edge": "#e1e4e8", "text": "#1f2328", "muted": "#656d76", "track": "#e6e8eb",
              "tint": "#fbe9df", "tint_text": "#b1452b", "blue_tint": "#e6eeff", "green_tint": "#e7f5ec",
              "amber_tint": "#fff4d6", "deco": "#fbe4d8", "shadow": "#1f2328", "shadow_opacity": 0.10,
              "shine": 0.55},
    "dark": {"card": "#161b22", "edge": "#30363d", "text": "#e6edf3", "muted": "#9198a1", "track": "#262c36",
             "tint": "#3a2219", "tint_text": "#f2a07c", "blue_tint": "#1b2540", "green_tint": "#12261a",
             "amber_tint": "#33290f", "deco": "#2a1a14", "shadow": "#000000", "shadow_opacity": 0.45,
             "shine": 0.12},
}
ORANGE = ("#f0915f", "#c4452f")
BLUE = ("#6f9bf5", "#3451c7")
GREEN, AMBER, ACCENT = "#2da44e", "#d4a72c", "#d9643f"
MUTED, WHITE = 'class="muted"', 'class="white"'

# 24x24 line icons (stroke only).
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
    "cap": '<path d="M2 9.5l10-5 10 5-10 5zM6 11.5v5c3 2.5 9 2.5 12 0v-5M22 9.5v6"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 16l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M12.5 15H17"/>',
    "layers": '<path d="M12 2.5l9 5-9 5-9-5zM3 12l9 5 9-5M3 16.5l9 5 9-5"/>',
    "flag": '<path d="M5 21V4M5 4h12l-2.5 4 2.5 4H5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "pr": '<circle cx="6" cy="5.5" r="2.5"/><circle cx="6" cy="18.5" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/>'
          '<path d="M6 8v8M18 16V9a3 3 0 0 0-3-3h-4M13 3.5L10.5 6 13 8.5"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
    "link": '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/>',
    "grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/>'
            '<rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><path d="M14 17l2 2 4-4"/>',
    "filecheck": '<path d="M14 3H6.5A1.5 1.5 0 0 0 5 4.5v15A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5V8zM14 3v5h5M9 14l2 2 4-4"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "laptop": '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19.5h20"/>',
    "key": '<circle cx="7.5" cy="15.5" r="4"/><path d="M10.5 12.5L20 3M16 7l2.5 2.5M14 9l2 2"/>',
}


class Canvas:
    """Collects defs, CSS and shapes for one SVG, with helpers for the shared animations."""

    def __init__(self, theme: str, width: int, height: int, cycle: float):
        self.c, self.w, self.h, self.cycle = THEMES[theme], width, height, cycle
        self.css: list[str] = [
            f"text {{ font-family: {FONT}; fill: {self.c['text']}; }}",
            f".muted {{ fill: {self.c['muted']}; }}",
            ".white { fill: #ffffff; }",
            ".pop, .grow { transform-box: fill-box; transform-origin: center; }",
            ".grow { transform-origin: left center; }",
            ".dr { stroke-dasharray: 100; stroke-dashoffset: 0; }",
            "@keyframes flowdash { to { stroke-dashoffset: -14; } }",
            ".dash { stroke-dasharray: 5 9; animation: flowdash 0.6s linear infinite; }",
        ]
        self.defs: list[str] = []
        self.body: list[str] = []
        for gid, (a, b), x2, y2 in [("g", ORANGE, 1, 1), ("gt", ORANGE, 1, 0), ("gb", BLUE, 1, 1), ("gbt", BLUE, 1, 0)]:
            self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" '
                             f'stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
        self.defs.append(f'<filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="3" '
                         f'stdDeviation="4" flood-color="{self.c["shadow"]}" flood-opacity="{self.c["shadow_opacity"]}"/>'
                         f'</filter>')
        self.defs.append('<filter id="glow" x="-200%" y="-200%" width="500%" height="500%">'
                         '<feGaussianBlur stdDeviation="5"/></filter>')
        self.defs.append('<filter id="halo" x="-30%" y="-30%" width="160%" height="160%">'
                         '<feGaussianBlur stdDeviation="9"/></filter>')

    # -- timing ------------------------------------------------------------------------------
    def pct(self, t: float) -> str:
        return f"{100 * max(0.0, min(t, self.cycle)) / self.cycle:.2f}%"

    def pop(self, name: str, on_at: float, hold_until: float, fade: float = 0.5) -> str:
        """Pop in with a small overshoot at `on_at`, stay, fade out at `hold_until`."""
        p = self.pct
        self.css.append(
            f"@keyframes {name} {{ 0%, {p(on_at)} {{ opacity: 0; transform: scale(0.9) }} "
            f"{p(on_at + 0.18)} {{ opacity: 1; transform: scale(1.05) }} "
            f"{p(on_at + 0.32)}, {p(hold_until)} {{ opacity: 1; transform: scale(1) }} "
            f"{p(hold_until + fade)}, 100% {{ opacity: 0; transform: scale(1) }} }}")
        self.css.append(f".{name} {{ animation: {name} {self.cycle}s ease-out infinite; }}")
        return name

    def window(self, name: str, on_at: float, off_at: float, ramp: float = 0.25) -> str:
        """Visible from `on_at` to `off_at` (opacity only)."""
        p = self.pct
        self.css.append(
            f"@keyframes {name} {{ 0%, {p(on_at - ramp)} {{ opacity: 0 }} {p(on_at)}, {p(off_at)} {{ opacity: 1 }} "
            f"{p(off_at + ramp)}, 100% {{ opacity: 0 }} }}")
        self.css.append(f".{name} {{ animation: {name} {self.cycle}s ease-in-out infinite; }}")
        return name

    def draw(self, name: str, start: float, end: float, hold_until: float, fade: float = 0.5) -> str:
        """Stroke draws itself between `start` and `end` (paths use pathLength=100 and class dr)."""
        p = self.pct
        self.css.append(
            f"@keyframes {name} {{ 0%, {p(start)} {{ stroke-dashoffset: 100; opacity: 1 }} "
            f"{p(end)}, {p(hold_until)} {{ stroke-dashoffset: 0; opacity: 1 }} "
            f"{p(hold_until + fade)} {{ stroke-dashoffset: 0; opacity: 0 }} 100% {{ stroke-dashoffset: 100; opacity: 0 }} }}")
        self.css.append(f".{name} {{ animation: {name} {self.cycle}s ease-in-out infinite; }}")
        return name

    def grow(self, name: str, start: float, hold_until: float, dur: float = 0.6, fade: float = 0.5) -> str:
        """Bars grow from the left edge."""
        p = self.pct
        self.css.append(
            f"@keyframes {name} {{ 0%, {p(start)} {{ transform: scaleX(0); opacity: 1 }} "
            f"{p(start + dur)}, {p(hold_until)} {{ transform: scaleX(1); opacity: 1 }} "
            f"{p(hold_until + fade)}, 100% {{ transform: scaleX(1); opacity: 0 }} }}")
        self.css.append(f".{name} {{ animation: {name} {self.cycle}s cubic-bezier(.2,.8,.2,1) infinite; }}")
        return name

    # -- shapes ------------------------------------------------------------------------------
    def icon(self, name: str, x: float, y: float, colour: str, size: float = 24) -> str:
        """Icon centred horizontally on x, top edge at y."""
        return (f'<g transform="translate({x - size / 2:.1f} {y:.1f}) scale({size / 24:.3f})" fill="none" '
                f'stroke="{colour}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')

    def card(self, x: float, y: float, w: float, h: float, rx: float = 14, shadow: bool = True, extra: str = "") -> str:
        f = ' filter="url(#sh)"' if shadow else ""
        return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{self.c["card"]}" '
                f'stroke="{self.c["edge"]}" stroke-width="1.5"{f}{extra}/>')

    @staticmethod
    def text(x: float, y: float, s: str, size: float = 14, weight: int = 400, anchor: str = "start",
             attrs: str = "") -> str:
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        return f'<text {attrs} x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}"{a}>{escape(s)}</text>'

    def svg(self, title: str) -> str:
        self.css.append("@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }")
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
            f'height="{self.h}" role="img" aria-labelledby="title">\n'
            f'<!-- Generated by tools/build_readme_visuals.py. Do not edit by hand. -->\n'
            f'<title id="title">{escape(title)}</title>\n'
            f'<defs>{"".join(self.defs)}</defs>\n'
            f'<style>\n' + "\n".join(self.css) + '\n</style>\n' + "\n".join(self.body) + "\n</svg>\n"
        )


def est_width(s: str, size: float, bold: bool = True) -> float:
    """Rough text width for layout (system UI fonts)."""
    return len(s) * size * (0.58 if bold else 0.53)


# ================================================================== 1. banner
def repo_counts() -> list[str]:
    questions = len(load_questions())
    cards = sum(len(yaml.safe_load(p.read_text(encoding="utf-8"))["cards"])
                for p in sorted((FLASHCARDS_DIR / "decks").glob("*.yaml")))
    labs = len([p for p in LABS_DIR.glob("lab-*") if p.is_dir()])
    projects = len([p for p in (ROOT / "20-real-world-projects").glob("0*") if p.is_dir()])
    tracks = len(certifications("supported"))
    return ["16 modules", f"{questions} practice questions", f"{cards} flashcards", f"{labs} labs",
            f"{projects} projects", f"{tracks} exam tracks"]


def banner(theme: str) -> str:
    cv = Canvas(theme, 1020, 290, 6.0)
    c, b = cv.c, cv.body
    cv.defs.append('<clipPath id="clip"><rect x="1" y="1" width="1018" height="288" rx="22"/></clipPath>')
    cv.defs.append(f'<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff" '
                   f'stop-opacity="0"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="{c["shine"]}"/>'
                   f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>')
    cv.css += [
        f"@keyframes sweep {{ 0% {{ transform: translateX(-260px) skewX(-20deg) }} {cv.pct(1.6)}, 100% "
        f"{{ transform: translateX(1250px) skewX(-20deg) }} }}",
        f".sweep {{ animation: sweep {cv.cycle}s ease-in-out infinite; }}",
        "@keyframes breathe { 0%, 100% { opacity: 0.35; transform: scale(0.96) } 50% { opacity: 0.8; transform: scale(1.04) } }",
        ".breathe { animation: breathe 3s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }",
        "@keyframes chipin { from { opacity: 0; transform: translateY(10px) scale(0.9) } to { opacity: 1; transform: none } }",
        ".chip { animation: chipin 0.5s cubic-bezier(.2,.8,.2,1) both; transform-box: fill-box; transform-origin: center; }",
        "@keyframes rise { from { opacity: 0; transform: translateY(12px) } to { opacity: 1; transform: none } }",
        ".rise { animation: rise 0.7s ease-out both; }",
    ]
    b.append(f'<g clip-path="url(#clip)">')
    b.append(cv.card(1, 1, 1018, 288, rx=22, shadow=False))
    b.append(f'<circle cx="960" cy="40" r="210" fill="{c["deco"]}"/><circle cx="1010" cy="300" r="90" '
             f'fill="{c["deco"]}" opacity="0.7"/>')
    b.append('<rect class="sweep" x="0" y="-20" width="150" height="330" fill="url(#shine)"/>')
    b.append(f'<rect x="1" y="1" width="8" height="288" fill="url(#g)"/></g>')
    b.append(cv.text(48, 58, "UNOFFICIAL STUDY GUIDE  ·  OPEN SOURCE", 13, 700,
                     attrs=f'class="rise" letter-spacing="1.4" style="fill:{ACCENT}"'))
    b.append(cv.text(46, 114, "Claude Certification", 48, 800, attrs='class="rise" style="animation-delay:.1s"'))
    b.append(cv.text(46, 168, "Zero to Hero", 48, 800,
                     attrs='class="rise" style="fill:url(#gt);animation-delay:.2s"'))
    b.append(cv.text(48, 206, "From your first prompt to production-ready AI architecture", 18,
                     attrs='class="muted rise" style="animation-delay:.3s"'))
    x = 48.0
    for i, label in enumerate(repo_counts()):
        w = est_width(label, 14) + 30
        b.append(f'<g class="chip" style="animation-delay:{0.45 + 0.12 * i:.2f}s"><rect x="{x:.1f}" y="228" '
                 f'width="{w:.1f}" height="34" rx="17" fill="{c["tint"]}" stroke="{ACCENT}" stroke-opacity="0.35"/>'
                 + cv.text(x + w / 2, 250, label, 14, 700, "middle", f'style="fill:{c["tint_text"]}"') + '</g>')
        x += w + 10
    b.append('<rect class="breathe" x="846" y="46" width="128" height="128" rx="32" fill="#f0915f" filter="url(#halo)"/>')
    b.append('<rect x="856" y="56" width="108" height="108" rx="28" fill="url(#g)"/>')
    b.append(cv.icon("cap", 910, 80, "#ffffff", 60))
    return cv.svg("Claude Certification Zero to Hero: an unofficial, open-source study guide. "
                  + ", ".join(repo_counts()) + ".")


# ================================================================== 2. learning journey
JOURNEY = [
    (("Foundations",), "00–02", "book"), (("Prompting &", "context"), "03–05", "chat"),
    (("Building",), "06–09", "code"), (("Systems",), "10–11", "nodes"),
    (("Secure &", "govern"), "12–13", "shield"), (("Operate",), "14–15", "pulse"),
    (("Certify",), "16–18", "trophy"),
]
JOURNEY_BRANCHES = [("Labs 01–20", "hands-on, free in mock mode", "flask", 2),
                    ("Projects 01–05", "real-world builds", "rocket", 4)]


def journey(theme: str) -> str:
    cv = Canvas(theme, 1020, 300, 6.0)
    c, back, front = cv.c, [], []
    card_w, card_h, gap, x0, y0, track_y = 124, 118, 22, 10, 14, 160
    bw, bh, by = 232, 52, 222
    start, step, hold = 0.25, 0.5, 5.0
    cx = lambda i: x0 + i * (card_w + gap) + card_w / 2  # noqa: E731
    end_t = start + (len(JOURNEY) - 1) * step
    x_first, x_last = cx(0), cx(len(JOURNEY) - 1)
    length = x_last - x_first

    back.append(f'<line x1="{x_first}" y1="{track_y}" x2="{x_last}" y2="{track_y}" stroke="{c["track"]}" '
                f'stroke-width="6" stroke-linecap="round"/>')
    back.append(f'<path class="dr {cv.draw("trk", start, end_t, hold)}" pathLength="100" d="M{x_first} {track_y}H{x_last}" '
                f'stroke="url(#gt)" stroke-width="6" stroke-linecap="round" fill="none"/>')

    for j, (title, sub, ic, src) in enumerate(JOURNEY_BRANCHES):
        x, on_at = cx(src), start + src * step + 0.25
        bx = x - bw / 2
        name = cv.pop(f"b{j}", on_at, hold)
        back.append(f'<line x1="{x}" y1="{track_y + 8}" x2="{x}" y2="{by - 4}" stroke="{c["edge"]}" '
                    f'stroke-width="2" stroke-dasharray="3 5"/>')
        back.append(f'<g class="{name}"><line class="dash" x1="{x}" y1="{track_y + 8}" x2="{x}" y2="{by - 4}" '
                    f'stroke="{ACCENT}" stroke-width="2.5"/></g>')
        front.append(cv.card(bx, by, bw, bh, rx=26))
        front.append(cv.icon(ic, bx + 30, by + 14, ACCENT))
        front.append(cv.text(bx + 52, by + 23, title, 14.5, 700))
        front.append(cv.text(bx + 52, by + 40, sub, 11.5, attrs=MUTED))
        front.append(f'<g class="pop {name}"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="26" fill="url(#g)"/>'
                     + cv.icon(ic, bx + 30, by + 14, "#ffffff") + cv.text(bx + 52, by + 23, title, 14.5, 700, attrs=WHITE)
                     + cv.text(bx + 52, by + 40, sub, 11.5, attrs=WHITE + ' opacity="0.9"') + '</g>')

    for i, (title, modules, ic) in enumerate(JOURNEY):
        x, mid, on_at = cx(i) - card_w / 2, cx(i), start + i * step
        name = cv.pop(f"s{i}", on_at, hold)
        if i == len(JOURNEY) - 1:
            front.append(f'<g class="{name}"><rect x="{x - 4}" y="{y0 - 2}" width="{card_w + 8}" height="{card_h + 8}" '
                         f'rx="18" fill="{ORANGE[0]}" opacity="0.55" filter="url(#halo)"/></g>')
        front.append(cv.card(x, y0, card_w, card_h))
        ty = y0 + 70 - 8 * (len(title) - 1)

        def labels(cls: str, colour: str) -> str:
            out = [cv.icon(ic, mid, y0 + 14, colour, 26),
                   cv.text(x + 12, y0 + 22, f"{i + 1:02d}", 10.5, 700, attrs=f'{cls} letter-spacing="0.6" opacity="0.75"')]
            out += [cv.text(mid, ty + 17 * k, line, 14.5, 700, "middle", cls) for k, line in enumerate(title)]
            out.append(cv.text(mid, y0 + card_h - 13, f"Modules {modules}", 11.5, anchor="middle", attrs=cls or MUTED))
            return "".join(out)

        front.append(labels("", ACCENT))
        front.append(f'<g class="pop {name}"><rect x="{x}" y="{y0}" width="{card_w}" height="{card_h}" rx="14" '
                     f'fill="url(#g)"/>{labels(WHITE, "#ffffff")}</g>')
        front.append(f'<circle cx="{mid}" cy="{track_y}" r="7" fill="{c["card"]}" stroke="{c["edge"]}" stroke-width="2"/>')
        front.append(f'<circle class="pop {name}" cx="{mid}" cy="{track_y}" r="7" fill="url(#g)" stroke="#ffffff" '
                     f'stroke-width="2"/>')

    p = cv.pct
    cv.css.append(
        f"@keyframes run {{ 0%, {p(start - 0.1)} {{ transform: translateX(0); opacity: 0 }} "
        f"{p(start)} {{ transform: translateX(0); opacity: 1 }} {p(end_t)} {{ transform: translateX({length:.0f}px); opacity: 1 }} "
        f"{p(end_t + 0.4)}, 100% {{ transform: translateX({length:.0f}px); opacity: 0 }} }}")
    cv.css.append(f".run {{ animation: run {cv.cycle}s linear infinite; opacity: 0; }}")
    front.append(f'<g class="run"><circle cx="{x_first}" cy="{track_y}" r="13" fill="{ORANGE[0]}" opacity="0.8" '
                 f'filter="url(#glow)"/><circle cx="{x_first}" cy="{track_y}" r="5.5" fill="#ffffff"/></g>')
    cv.body += back + front
    summary = ", then ".join(" ".join(t) for t, _, _ in JOURNEY)
    return cv.svg(f"Learning journey: {summary}. Labs branch from Building; projects branch from Secure and govern.")


# ================================================================== 3. find your path
PROFILES = [  # (icon, who, start with, goal index)
    ("sparkle", "New to AI", "Modules 00–02", 0),
    ("briefcase", "Business or knowledge worker", "Modules 03–05", 0),
    ("terminal", "Software or DevOps engineer", "Modules 03–06", 1),
    ("shield", "Security or DevSecOps engineer", "Module 12", 3),
    ("layers", "Solution or enterprise architect", "Module 13", 2),
    ("flag", "Technical leader", "Modules 13 and 15", 3),
]
GOALS = [("CCAO-F", "Associate – Foundations", "cap"), ("CCAR-F", "Architect – Foundations", "cap"),
         ("CCAR-P", "Architect – Professional", "cap"), ("Skills path", "labs · projects · interview prep", "target")]


def find_path(theme: str) -> str:
    cv = Canvas(theme, 1020, 400, 6.6)
    c, back, front = cv.c, [], []
    px, pw, mx, mw, gx, gw = 10, 284, 384, 186, 700, 310
    y0, rh, rg = 42, 46, 12
    gh = 72
    ggap = (len(PROFILES) * rh + (len(PROFILES) - 1) * rg - len(GOALS) * gh) / (len(GOALS) - 1)
    hold = 5.6
    for x, label in [(px + 4, "YOU ARE…"), (mx + 4, "START WITH"), (gx + 4, "AIM FOR")]:
        front.append(cv.text(x, 22, label, 12, 700, attrs=f'{MUTED} letter-spacing="1.2"'))
    goal_y = [y0 + k * (gh + ggap) for k in range(len(GOALS))]
    first_hit: dict[int, float] = {}
    for i, (ic, who, start_with, goal) in enumerate(PROFILES):
        t = 0.3 + 0.72 * i
        first_hit.setdefault(goal, t + 0.62)
        y, gy = y0 + i * (rh + rg), goal_y[goal] + gh / 2
        mid = y + rh / 2
        line1 = f"M{px + pw + 2} {mid}H{mx - 4}"
        line2 = f"M{mx + mw + 2} {mid}C{mx + mw + 70} {mid} {gx - 70} {gy} {gx - 4} {gy}"
        for d in (line1, line2):
            back.append(f'<path d="{d}" stroke="{c["track"]}" stroke-width="2.5" fill="none"/>')
        back.append(f'<path class="dr {cv.draw(f"l{i}a", t + 0.1, t + 0.3, hold)}" pathLength="100" d="{line1}" '
                    f'stroke="url(#gt)" stroke-width="3" fill="none" stroke-linecap="round"/>')
        back.append(f'<path class="dr {cv.draw(f"l{i}b", t + 0.36, t + 0.66, hold)}" pathLength="100" d="{line2}" '
                    f'stroke="url(#gt)" stroke-width="3" fill="none" stroke-linecap="round"/>')
        pn, mn = cv.pop(f"p{i}", t, hold), cv.pop(f"m{i}", t + 0.3, hold)
        for x, w, txt, icn, name, size in [(px, pw, who, ic, pn, 13.5), (mx, mw, start_with, "book", mn, 13.5)]:
            front.append(cv.card(x, y, w, rh, rx=23))
            front.append(cv.icon(icn, x + 26, y + 12, ACCENT, 22))
            front.append(cv.text(x + 46, mid + 5, txt, size, 650))
            front.append(f'<g class="pop {name}"><rect x="{x}" y="{y}" width="{w}" height="{rh}" rx="23" fill="url(#g)"/>'
                         + cv.icon(icn, x + 26, y + 12, "#ffffff", 22) + cv.text(x + 46, mid + 5, txt, size, 650, attrs=WHITE)
                         + '</g>')
    for k, (code, name, ic) in enumerate(GOALS):
        y = goal_y[k]
        gn = cv.pop(f"g{k}", first_hit[k], hold)
        front.append(f'<g class="{gn}"><rect x="{gx - 3}" y="{y - 2}" width="{gw + 6}" height="{gh + 6}" rx="18" '
                     f'fill="{ORANGE[0]}" opacity="0.45" filter="url(#halo)"/></g>')
        front.append(cv.card(gx, y, gw, gh))
        front.append(cv.icon(ic, gx + 34, y + 22, ACCENT, 28))
        front.append(cv.text(gx + 64, y + 32, code, 18, 800))
        front.append(cv.text(gx + 64, y + 52, name, 12.5, attrs=MUTED))
        front.append(f'<g class="pop {gn}"><rect x="{gx}" y="{y}" width="{gw}" height="{gh}" rx="14" fill="url(#g)"/>'
                     + cv.icon(ic, gx + 34, y + 22, "#ffffff", 28) + cv.text(gx + 64, y + 32, code, 18, 800, attrs=WHITE)
                     + cv.text(gx + 64, y + 52, name, 12.5, attrs=WHITE + ' opacity="0.9"') + '</g>')
    cv.body += back + front
    routes = "; ".join(f"{who}: start with {s}, aim for {GOALS[g][0]}" for _, who, s, g in PROFILES)
    return cv.svg(f"Find your path. {routes}.")


# ================================================================== 4. mock-exam demo
OPTIONS = [("A", "Retry the identical call until it succeeds"),
           ("B", "Return the error as a tool result so Claude can change approach"),
           ("C", "Drop the error silently and carry on with the task"),
           ("D", "Restart the whole session from the beginning")]
DOMAIN_SCORES = [("D1 Agentic architecture", 86), ("D2 Tool design & MCP", 80), ("D3 Claude Code", 75),
                 ("D4 Prompts & structured output", 82), ("D5 Context & reliability", 55)]


def mock_exam(theme: str) -> str:
    cv = Canvas(theme, 1020, 410, 8.0)
    c, b = cv.c, cv.body
    hold = 7.2
    # Question card
    b.append(cv.card(10, 10, 600, 390, rx=18))
    b.append(cv.text(34, 46, "CCAR-F  ·  Domain 1  ·  Question 12 of 60", 13, 700, attrs=MUTED))
    b.append(f'<rect x="494" y="26" width="92" height="28" rx="14" fill="{c["tint"]}"/>')
    b.append(cv.icon("clock", 514, 31, c["tint_text"], 18))
    b.append(cv.text(530, 45, "38:12", 13.5, 700, attrs=f'style="fill:{c["tint_text"]}"'))
    b.append(f'<rect x="34" y="64" width="552" height="6" rx="3" fill="{c["track"]}"/>'
             f'<rect x="34" y="64" width="110" height="6" rx="3" fill="url(#gt)"/>')
    b.append(cv.text(34, 104, "A subagent keeps calling a tool that returns the same error.", 16, 700))
    b.append(cv.text(34, 126, "What should the agent loop do next?", 16, 700))
    oy = [146 + k * 46 for k in range(len(OPTIONS))]
    sel, ok, why = cv.pop("sel", 1.55, hold), cv.pop("ok", 2.25, hold), cv.pop("why", 2.75, hold)
    for (letter, txt), y in zip(OPTIONS, oy):
        b.append(f'<rect x="34" y="{y}" width="552" height="38" rx="10" fill="{c["card"]}" stroke="{c["edge"]}" stroke-width="1.5"/>')
        b.append(f'<circle cx="56" cy="{y + 19}" r="12" fill="none" stroke="{c["edge"]}" stroke-width="1.5"/>')
        b.append(cv.text(56, y + 23.5, letter, 12.5, 700, "middle", MUTED))
        if letter == "B":
            b.append(f'<g class="pop {sel}"><rect x="34" y="{y}" width="552" height="38" rx="10" fill="{c["tint"]}" '
                     f'stroke="{ACCENT}" stroke-width="2"/><circle cx="56" cy="{y + 19}" r="12" fill="url(#g)"/>'
                     + cv.text(56, y + 23.5, letter, 12.5, 700, "middle", WHITE) + '</g>')
            b.append(f'<g class="pop {ok}"><rect x="34" y="{y}" width="552" height="38" rx="10" fill="{c["green_tint"]}" '
                     f'stroke="{GREEN}" stroke-width="2"/><circle cx="56" cy="{y + 19}" r="12" fill="{GREEN}"/>'
                     + cv.icon("check", 56, y + 11, "#ffffff", 16) + '</g>')
        b.append(cv.text(78, y + 24, txt, 14))
    ey = oy[-1] + 52
    b.append(f'<g class="pop {why}"><rect x="34" y="{ey}" width="552" height="46" rx="10" fill="{c["green_tint"]}"/>'
             + cv.icon("check", 56, ey + 11, GREEN, 22)
             + cv.text(78, ey + 20, "Correct. Errors go back to Claude as tool results (is_error),", 13, 650)
             + cv.text(78, ey + 37, "so it can try a different approach instead of looping.", 13, attrs=MUTED) + '</g>')
    # Cursor: travels to option B and clicks.
    tx, ty = 360 - 450, oy[1] + 22 - 330
    p = cv.pct
    cv.css.append(
        f"@keyframes cur {{ 0%, {p(0.5)} {{ transform: translate(0,0); opacity: 0 }} {p(0.7)} {{ transform: translate(0,0); opacity: 1 }} "
        f"{p(1.45)} {{ transform: translate({tx}px,{ty}px); opacity: 1 }} {p(1.55)} {{ transform: translate({tx}px,{ty}px) scale(0.85); opacity: 1 }} "
        f"{p(1.7)} {{ transform: translate({tx}px,{ty}px); opacity: 1 }} {p(2.4)}, 100% {{ transform: translate({tx}px,{ty}px); opacity: 0 }} }}")
    cv.css.append(f".cur {{ animation: cur {cv.cycle}s ease-in-out infinite; opacity: 0; }}")
    b.append(f'<g class="cur"><path transform="translate(450 330)" d="M0 0L0 18L4.5 13.5L7.6 20.5L10.6 19.2L7.6 12.4L13.4 12.4Z" '
             f'fill="{c["text"]}" stroke="{c["card"]}" stroke-width="1.5" stroke-linejoin="round"/></g>')
    # Results card
    b.append(cv.card(630, 10, 380, 390, rx=18))
    b.append(cv.text(654, 46, "Your results", 16, 800))
    b.append(cv.text(654, 66, "CCAR-F mock exam A · practice score", 12.5, attrs=MUTED))
    rcx, rcy, r = 714, 136, 46
    b.append(f'<circle cx="{rcx}" cy="{rcy}" r="{r}" fill="none" stroke="{c["track"]}" stroke-width="11"/>')
    cv.css.append(
        f"@keyframes ring {{ 0%, {p(3.1)} {{ stroke-dashoffset: 100; opacity: 1 }} {p(4.1)}, {p(hold)} {{ stroke-dashoffset: 22; opacity: 1 }} "
        f"{p(hold + 0.5)}, 100% {{ stroke-dashoffset: 22; opacity: 0 }} }}")
    cv.css.append(f".ring {{ stroke-dasharray: 100; stroke-dashoffset: 22; animation: ring {cv.cycle}s ease-out infinite; }}")
    b.append(f'<circle class="ring" pathLength="100" cx="{rcx}" cy="{rcy}" r="{r}" fill="none" stroke="url(#g)" '
             f'stroke-width="11" stroke-linecap="round" transform="rotate(-90 {rcx} {rcy})"/>')
    score = cv.pop("score", 3.9, hold)
    b.append(f'<g class="pop {score}">' + cv.text(rcx, rcy + 9, "78%", 26, 800, "middle") + '</g>')
    b.append(cv.text(784, 128, "47 of 60 correct", 15, 750))
    b.append(cv.text(784, 150, "Weakest domain flagged below", 12.5, attrs=MUTED))
    for k, (label, val) in enumerate(DOMAIN_SCORES):
        y = 200 + k * 34
        b.append(cv.text(654, y, label, 12.5, 650))
        b.append(cv.text(986, y, f"{val}%", 12.5, 700, "end", MUTED))
        b.append(f'<rect x="654" y="{y + 8}" width="332" height="8" rx="4" fill="{c["track"]}"/>')
        colour = f'fill="{AMBER}"' if val < 70 else 'fill="url(#gt)"'
        b.append(f'<rect class="grow {cv.grow(f"d{k}", 4.2 + 0.15 * k, hold)}" x="654" y="{y + 8}" '
                 f'width="{332 * val / 100:.1f}" height="8" rx="4" {colour}/>')
    weak = cv.pop("weak", 5.3, hold)
    wy = 200 + 4 * 34 + 24
    b.append(f'<g class="pop {weak}"><rect x="654" y="{wy}" width="190" height="26" rx="13" fill="{c["amber_tint"]}" '
             f'stroke="{AMBER}"/>' + cv.text(749, wy + 17.5, "Review next: Domain 5", 12.5, 700, "middle",
                                             f'style="fill:{AMBER}"') + '</g>')
    return cv.svg("Practice exam demo: a CCAR-F question is answered, the correct option turns green with an "
                  "explanation, then a results panel shows a 78% practice score, per-domain bars and the weakest "
                  "domain to review next.")


# ================================================================== 5. quality pipeline
CHECKS = [("list", "Questions", "schema and keys"), ("link", "Links", "internal and external"),
          ("grid", "Coverage", "every objective"), ("filecheck", "Exam facts", "match the registry"),
          ("flask", "Labs", "run in mock mode"), ("lock", "Secrets", "gitleaks + scanner")]


def pipeline(theme: str) -> str:
    cv = Canvas(theme, 1020, 220, 6.0)
    c, back, front = cv.c, [], []
    y, x_start, x_end, hold = 100, 168, 860, 5.2
    t0, t1 = 0.3, 4.0
    at = lambda x: t0 + (x - x_start) / (x_end - x_start) * (t1 - t0)  # noqa: E731
    back.append(f'<line x1="{x_start}" y1="{y}" x2="{x_end}" y2="{y}" stroke="{c["track"]}" stroke-width="6" stroke-linecap="round"/>')
    back.append(f'<path class="dr {cv.draw("trk", t0, t1, hold)}" pathLength="100" d="M{x_start} {y}H{x_end}" '
                f'stroke="{GREEN}" stroke-width="6" stroke-linecap="round" fill="none"/>')
    front.append(cv.card(10, 52, 150, 96, rx=16))
    front.append(cv.icon("pr", 39, 64, ACCENT, 26))
    front.append(cv.text(26, 106, "Pull request", 14.5, 750))
    front.append(cv.text(26, 126, "your change", 12.5, attrs=MUTED))
    for i, (ic, name, sub) in enumerate(CHECKS):
        x = 236 + i * 112
        n = cv.pop(f"c{i}", at(x), hold)
        front.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{c["card"]}" stroke="{c["edge"]}" stroke-width="1.5" filter="url(#sh)"/>')
        front.append(cv.icon(ic, x, y - 12, ACCENT, 24))
        front.append(f'<g class="pop {n}"><circle cx="{x}" cy="{y}" r="30" fill="{GREEN}"/>'
                     + cv.icon("check", x, y - 13, "#ffffff", 26) + '</g>')
        front.append(cv.text(x, y + 56, name, 13.5, 750, "middle"))
        front.append(cv.text(x, y + 74, sub, 11.5, anchor="middle", attrs=MUTED))
    done = cv.pop("done", t1, hold)
    front.append(f'<rect x="872" y="70" width="138" height="60" rx="30" fill="{c["card"]}" stroke="{c["edge"]}" '
                 f'stroke-width="1.5" stroke-dasharray="5 4"/>')
    front.append(cv.text(941, 105, "Waiting…", 13.5, 650, "middle", MUTED))
    front.append(f'<g class="{done}"><rect x="868" y="66" width="146" height="68" rx="34" fill="{GREEN}" opacity="0.5" '
                 f'filter="url(#halo)"/></g>')
    front.append(f'<g class="pop {done}"><rect x="872" y="70" width="138" height="60" rx="30" fill="{GREEN}"/>'
                 + cv.icon("check", 898, 88, "#ffffff", 24) + cv.text(916, 96, "Ready", 14, 800, attrs=WHITE)
                 + cv.text(916, 114, "to merge", 12.5, 600, attrs=WHITE) + '</g>')
    p = cv.pct
    span = x_end - x_start
    cv.css.append(
        f"@keyframes run {{ 0%, {p(t0 - 0.1)} {{ transform: translateX(0); opacity: 0 }} {p(t0)} {{ transform: translateX(0); opacity: 1 }} "
        f"{p(t1)} {{ transform: translateX({span}px); opacity: 1 }} {p(t1 + 0.3)}, 100% {{ transform: translateX({span}px); opacity: 0 }} }}")
    cv.css.append(f".run {{ animation: run {cv.cycle}s linear infinite; opacity: 0; }}")
    front.append(f'<g class="run"><circle cx="{x_start}" cy="{y}" r="12" fill="{GREEN}" opacity="0.7" filter="url(#glow)"/>'
                 f'<circle cx="{x_start}" cy="{y}" r="5" fill="#ffffff"/></g>')
    cv.body += back + front
    return cv.svg("Quality pipeline: every pull request passes six automated checks (questions, links, coverage, "
                  "exam facts, labs and secrets) before it is ready to merge.")


# ================================================================== 6. study plans
PLANS = [(7, "7-day accelerated", "CCAO-F", "3–4 h a day", "~25 h", ""),
         (15, "15-day preparation", "CCAO-F", "2 h a day", "~30 h", ""),
         (30, "30-day structured", "CCAO-F", "1–1.5 h a day", "~38 h", "Best for beginners"),
         (60, "60-day comprehensive", "CCAR-P", "1.5–2 h a day", "~110 h", ""),
         (90, "90-day enterprise", "CCAR-P", "1.5–2 h a day + labs", "~170 h", "")]


def study_plans(theme: str) -> str:
    cv = Canvas(theme, 1020, 310, 7.0)
    c, b = cv.c, cv.body
    bx, bmax, y0, step, bh, hold = 236, 600, 56, 46, 26, 6.2
    per_day = bmax / 90
    for k, (label, grad) in enumerate([("CCAO-F plans", "url(#g)"), ("CCAR-P plans", "url(#gb)")]):
        x = 10 + k * 150
        b.append(f'<circle cx="{x + 8}" cy="20" r="7" fill="{grad}"/>')
        b.append(cv.text(x + 22, 25, label, 13, 650))
    b.append(cv.text(1010, 25, "Bar length = calendar days", 12.5, anchor="end", attrs=MUTED))
    axis_y = y0 + len(PLANS) * step - 6
    for d in (0, 30, 60, 90):
        x = bx + d * per_day
        b.append(f'<line x1="{x:.1f}" y1="{y0 - 12}" x2="{x:.1f}" y2="{axis_y}" stroke="{c["track"]}" stroke-width="1.5"/>')
        b.append(cv.text(x, axis_y + 20, f"{d} days", 12, anchor="middle", attrs=MUTED))
    for i, (days, name, track, daily, total, tag) in enumerate(PLANS):
        y = y0 + i * step
        grad = "url(#gt)" if track == "CCAO-F" else "url(#gbt)"
        b.append(cv.text(10, y + 12, name, 14, 750))
        b.append(cv.text(10, y + 29, f"{track} · {daily}", 12, attrs=MUTED))
        w = days * per_day
        b.append(f'<rect x="{bx}" y="{y}" width="{bmax}" height="{bh}" rx="13" fill="{c["track"]}" opacity="0.55"/>')
        b.append(f'<rect class="grow {cv.grow(f"r{i}", 0.3 + 0.32 * i, hold)}" x="{bx}" y="{y}" width="{w:.1f}" '
                 f'height="{bh}" rx="13" fill="{grad}"/>')
        n = cv.pop(f"t{i}", 0.75 + 0.32 * i, hold)
        lx = bx + w + 12
        group = cv.text(lx, y + 18, total, 14, 800)
        if tag:
            tw = est_width(tag, 12) + 22
            group += (f'<rect x="{lx + 56}" y="{y + 1}" width="{tw:.1f}" height="24" rx="12" fill="{c["green_tint"]}" '
                      f'stroke="{GREEN}"/>' + cv.text(lx + 56 + tw / 2, y + 17.5, tag, 12, 700, "middle",
                                                     f'style="fill:{GREEN}"'))
        b.append(f'<g class="pop {n}">{group}</g>')
    return cv.svg("Study plans compared: " + "; ".join(f"{n}, {t}, {d}, {tot} in total" for _, n, t, d, tot, _ in PLANS)
                  + ". The 30-day plan is best for complete beginners.")


# ================================================================== 7. mock and live modes
MODES = [("laptop", "Mock mode (default)", ["No API key and no cost", "Runs fully offline",
                                             "Deterministic replies, so labs are repeatable"], "url(#g)", "tint"),
         ("key", "Live mode", ["Your own API key: CLAUDE_LAB_MODE=live", "Real Claude responses",
                               "Uses API credits, clearly marked"], "url(#gb)", "blue_tint")]


def lab_modes(theme: str) -> str:
    cv = Canvas(theme, 1020, 250, 6.4)
    c, b = cv.c, cv.body
    windows = [(0.25, 2.8), (3.3, 5.8)]
    for k, (ic, title, bullets, grad, tint) in enumerate(MODES):
        x, y, w, h = 10 + k * 510, 72, 500, 168
        on, off = windows[k]
        name = cv.window(f"m{k}", on, off)
        b.append(cv.card(x, y, w, h, rx=18))
        b.append(f'<g class="{name}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{c[tint]}" '
                 f'stroke="{grad}" stroke-width="2.5"/></g>')
        b.append(f'<rect x="{x + 22}" y="{y + 20}" width="44" height="44" rx="12" fill="{grad}"/>')
        b.append(cv.icon(ic, x + 44, y + 30, "#ffffff", 24))
        b.append(cv.text(x + 80, y + 48, title, 18, 800))
        for j, line in enumerate(bullets):
            ly = y + 92 + j * 26
            b.append(cv.icon("check", x + 34, ly - 14, GREEN if k == 0 else BLUE[1], 18))
            b.append(cv.text(x + 52, ly, line, 14))
    # Toggle switch between the two panels.
    tx, ty = 470, 18
    b.append(cv.text(tx - 14, ty + 24, "MOCK", 13, 800, "end", attrs=f'letter-spacing="1" style="fill:{ACCENT}"'))
    b.append(cv.text(tx + 94, ty + 24, "LIVE", 13, 800, attrs=f'letter-spacing="1" style="fill:{BLUE[1]}"'))
    b.append(f'<rect x="{tx}" y="{ty}" width="80" height="36" rx="18" fill="url(#g)"/>')
    b.append(f'<g class="{cv.window("tb", 3.1, 5.9, 0.3)}"><rect x="{tx}" y="{ty}" width="80" height="36" rx="18" fill="url(#gb)"/></g>')
    p = cv.pct
    cv.css.append(
        f"@keyframes knob {{ 0%, {p(2.85)} {{ transform: translateX(0) }} {p(3.25)}, {p(5.85)} {{ transform: translateX(44px) }} "
        f"{p(6.25)}, 100% {{ transform: translateX(0) }} }}")
    cv.css.append(f".knob {{ animation: knob {cv.cycle}s cubic-bezier(.5,0,.2,1) infinite; }}")
    b.append(f'<circle class="knob" cx="{tx + 18}" cy="{ty + 18}" r="14" fill="#ffffff" filter="url(#sh)"/>')
    return cv.svg("Lab modes: mock mode is the default, needs no API key, costs nothing, runs offline and gives "
                  "repeatable replies; live mode uses your own API key (CLAUDE_LAB_MODE=live), calls the real Claude "
                  "and uses API credits.")


DIAGRAMS: dict[str, Callable[[str], str]] = {
    "readme-banner": banner,
    "learning-journey": journey,
    "find-your-path": find_path,
    "mock-exam-demo": mock_exam,
    "quality-pipeline": pipeline,
    "study-plans": study_plans,
    "lab-modes": lab_modes,
}


def main(check: bool) -> int:
    report = Report("README visuals")
    for name, build in DIAGRAMS.items():
        for theme in THEMES:
            path = OUT_DIR / f"{name}-{theme}.svg"
            svg = build(theme)
            if check:
                if not path.exists() or path.read_text(encoding="utf-8") != svg:
                    report.error(f"{path.relative_to(ROOT)} is missing or stale: run python tools/build_readme_visuals.py")
            else:
                path.write_text(svg, encoding="utf-8")
                print(f"wrote {path.relative_to(ROOT)}")
    report.print()
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
