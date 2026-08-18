#!/usr/bin/env python3
"""Generate self-hosted "fun" art (emoji-free) into OUT_DIR:
  - terminal.svg  (animated typing console profile card)
  - galaxy.svg    (animated orbiting-skills "tech galaxy")

Both are animated SVG files served from the `output` branch, so they
never depend on flaky third-party hosts.
"""
import math
import os
import random

OUT_DIR = os.environ.get("OUT_DIR", "dist")


def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_terminal():
    W, pad_l, pad_top, lh, fs = 640, 22, 50, 24, 14
    charw = fs * 0.60

    lines = [
        ("cmd", "$ whoami"),
        ("out", "Shashwat Gupta - Co-Founder @ EmenteAI"),
        ("cmd", "$ role"),
        ("out", "Full-Stack Developer · AI Engineer · Open-Source Mentor"),
        ("cmd", "$ location"),
        ("out", "Rewa, India"),
        ("cmd", "$ stack"),
        ("out", "AI/ML · Full-Stack Web · Data Analysis · LoRA · MCP"),
        ("cmd", "$ wins"),
        ("out", "GSC Top 500 · IEEE 3rd · Hosted a 50+ hacker hackathon"),
    ]

    n = len(lines)
    H = pad_top + (n + 1) * lh + 18

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">'
    )
    # Window body + border
    svg.append(f'<rect width="{W}" height="{H}" rx="12" fill="#0d1117"/>')
    svg.append(
        f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="11" '
        'fill="none" stroke="#30363d"/>'
    )
    # Title bar
    svg.append(f'<rect width="{W}" height="30" rx="12" fill="#161b22"/>')
    svg.append(f'<rect y="18" width="{W}" height="12" fill="#161b22"/>')
    svg.append('<circle cx="18" cy="15" r="5" fill="#ff5f57"/>')
    svg.append('<circle cx="38" cy="15" r="5" fill="#febc2e"/>')
    svg.append('<circle cx="58" cy="15" r="5" fill="#28c840"/>')
    svg.append(
        f'<text x="{W / 2}" y="19" text-anchor="middle" '
        'font-family="Verdana,sans-serif" font-size="12" fill="#8b949e">'
        "profile.sh — bash</text>"
    )

    # Typing reveal for each line (loops every T seconds)
    T = 18.0
    hold_frac = (T - 0.4) / T
    t = 0.6
    for i, (kind, text) in enumerate(lines):
        y = pad_top + i * lh
        wpx = len(text) * charw + 6
        dur = len(text) * 0.05
        rs = t / T
        re = (t + dur) / T
        svg.append(
            f'<clipPath id="c{i}"><rect x="{pad_l}" y="{y - fs}" width="0" height="{lh}">'
            f'<animate attributeName="width" values="0;0;{wpx:.1f};{wpx:.1f};0" '
            f'keyTimes="0;{rs:.3f};{re:.3f};{hold_frac:.3f};1" dur="{T}s" '
            f'repeatCount="indefinite"/></rect></clipPath>'
        )
        if kind == "cmd":
            prompt, _, rest = text.partition(" ")
            svg.append(
                f'<text x="{pad_l}" y="{y}" clip-path="url(#c{i})" '
                f'font-family="Consolas,monospace" font-size="{fs}">'
                f'<tspan fill="#8b5cf6">{esc(prompt)}</tspan>'
                f'<tspan fill="#58a6ff"> {esc(rest)}</tspan></text>'
            )
        else:
            svg.append(
                f'<text x="{pad_l}" y="{y}" clip-path="url(#c{i})" '
                f'font-family="Consolas,monospace" font-size="{fs}" fill="#8b949e">'
                f"{esc(text)}</text>"
            )
        t += dur + 0.25

    # Final prompt with blinking cursor (shows each loop while lines hold)
    cy = pad_top + n * lh
    show_frac = min(t / T + 0.001, 1.0)
    svg.append(
        f'<g opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;1;0" '
        f'keyTimes="0;{t / T:.3f};{show_frac:.3f};0.970;1" dur="{T}s" '
        f'repeatCount="indefinite"/>'
        f'<text x="{pad_l}" y="{cy}" font-family="Consolas,monospace" font-size="{fs}">'
        f'<tspan fill="#8b5cf6">$</tspan> '
        f'<tspan fill="#c4b5fd" opacity="0">_'
        f'<animate attributeName="opacity" values="0;1;0;1" dur="1.1s" '
        f'repeatCount="indefinite"/></tspan>'
        f"</text></g>"
    )

    svg.append("</svg>")
    return "\n".join(svg)
def render_galaxy():
    w, h, cx, cy = 640, 520, 320, 250
    skills = [
        ("Python", "#3776AB", -150),
        ("C++", "#00599C", -90),
        ("JavaScript", "#F7DF1E", -30),
        ("React", "#61DAFB", 30),
        ("Firebase", "#FFCA28", 90),
        ("ML / LoRA", "#8b5cf6", 150),
    ]

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">'
    )
    svg.append(
        '<defs><radialGradient id="g" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#a78bfa"/><stop offset="0.55" stop-color="#7c3aed"/>'
        '<stop offset="1" stop-color="#1b1030" stop-opacity="0"/></radialGradient></defs>'
    )

    # Twinkling stars
    random.seed(7)
    for _ in range(40):
        x = random.uniform(0, w)
        y = random.uniform(0, h)
        r = random.uniform(0.4, 1.4)
        op = random.uniform(0.15, 0.5)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#8b949e" opacity="{op:.2f}"/>')

    # Rotating dashed orbit rings
    for radius, dur in ((95, "26s"), (150, "40s")):
        svg.append(
            f'<g><animateTransform attributeName="transform" type="rotate" '
            f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="{dur}" repeatCount="indefinite"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#30363d" '
            f'stroke-dasharray="3 6" stroke-width="1"/></g>'
        )

    # Orbiting planets
    for radius, dur, col, rad, start in (
        (95, "26s", "#a78bfa", 5, 0),
        (95, "26s", "#61DAFB", 3, 180),
        (150, "40s", "#c4b5fd", 5, 90),
        (150, "40s", "#ffca28", 3, 270),
    ):
        svg.append(
            f'<g><animateTransform attributeName="transform" type="rotate" '
            f'from="{start} {cx} {cy}" to="{start + 360} {cx} {cy}" dur="{dur}" '
            f'repeatCount="indefinite"/>'
            f'<circle cx="{cx + radius}" cy="{cy}" r="{rad}" fill="{col}"/></g>'
        )

    # Center glow + core
    svg.append(
        f'<circle cx="{cx}" cy="{cy}" r="34" fill="url(#g)">'
        f'<animate attributeName="opacity" values="0.85;1;0.85" dur="4s" '
        f'repeatCount="indefinite"/></circle>'
    )
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="#0d1117"/>')
    svg.append(
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" '
        'font-family="Verdana,sans-serif" font-size="13" font-weight="700" '
        'fill="#c4b5fd">SG</text>'
    )

    # Skill labels (upright) around the orbits
    radius = 178
    for name, col, deg in skills:
        a = math.radians(deg)
        x = cx + radius * math.cos(a)
        y = cy + radius * math.sin(a)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{col}"/>')
        svg.append(
            f'<text x="{x:.1f}" y="{y + 20:.1f}" text-anchor="middle" '
            f'font-family="Verdana,sans-serif" font-size="12" fill="#8b949e">'
            f"{esc(name)}</text>"
        )

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn in (("terminal.svg", render_terminal), ("galaxy.svg", render_galaxy)):
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
            fh.write(fn())
    print(f"Wrote terminal.svg and galaxy.svg to {OUT_DIR}")


if __name__ == "__main__":
    main()