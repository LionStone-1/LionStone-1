#!/usr/bin/env python3
"""Generate self-hosted contribution art (emoji-free) into OUT_DIR:
  - heatmap.svg       (light theme) animated contribution calendar
  - heatmap-dark.svg  (dark theme)  animated contribution calendar
  - wave.svg          (animated gradient wave divider)

All three are static/animated SVG files served from the `output` branch,
so they never depend on flaky third-party hosts.
"""
import datetime
import math
import os
import re
import urllib.request

USER = os.environ.get("INPUT_USER", "LionStone-1")
OUT_DIR = os.environ.get("OUT_DIR", "dist")

UA = {"User-Agent": "contribution-art"}

LIGHT = {
    "levels": ["#ebedf0", "#d3c0f7", "#b393f5", "#8b5cf6", "#6d28d9"],
    "text": "#57606a",
    "title": "#24292f",
    "total": "#6d28d9",
}
DARK = {
    "levels": ["#161b22", "#3b1d73", "#55289e", "#7c3aed", "#a78bfa"],
    "text": "#8b949e",
    "title": "#e6edf3",
    "total": "#a78bfa",
}


def fetch_contributions():
    url = f"https://github.com/users/{USER}/contributions"
    req = urllib.request.Request(url, headers=UA)
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    levels = {}
    for m in re.finditer(r"<td[^>]*>", html):
        block = m.group(0)
        dm = re.search(r'data-date="([0-9-]+)"', block)
        dl = re.search(r'data-level="(\d)"', block)
        if dm and dl:
            levels[dm.group(1)] = int(dl.group(1))
    total_hdr = None
    th = re.search(
        r'js-contribution-activity-description[^>]*>\s*([\d,]+)\s*contributions?',
        html,
    )
    if th:
        total_hdr = int(th.group(1).replace(",", ""))
    return levels, total_hdr


def render_heatmap(levels, total_hdr, palette):
    today = datetime.date.today()
    dates = sorted(d for d in levels if d)
    if not dates:
        dates = [today.isoformat()]
    start = datetime.date.fromisoformat(dates[0])
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)

    total_days = (today - start).days
    cols = total_days // 7 + 1

    cell, step, pad = 11, 14, 24
    width = 2 * pad + cols * step
    grid_h = 7 * step
    height = pad + grid_h + 44

    def day_level(iso):
        lvl = levels.get(iso, 0)
        return min(4, max(0, int(lvl)))

    lines = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    lines.append("<style>rect.day{shape-rendering:geometricPrecision}</style>")

    # Title + total
    if total_hdr is not None:
        total = total_hdr
        label = f"{total} contributions in the last year"
    else:
        total = sum(1 for v in levels.values() if v > 0)
        label = f"{total} active days in the last year"

    lines.append(
        f'<text x="{pad}" y="18" font-family="Verdana,sans-serif" font-size="13" '
        f'font-weight="700" fill="{palette["title"]}">Contributions</text>'
    )
    lines.append(
        f'<text x="{width - pad}" y="18" text-anchor="end" '
        f'font-family="Verdana,sans-serif" font-size="12" fill="{palette["total"]}">{label}</text>'
    )

    # Grid cells
    for d_off in range(0, total_days + 1):
        dt = start + datetime.timedelta(days=d_off)
        col = d_off // 7
        row = (dt.weekday() + 1) % 7
        x = pad + col * step
        y = pad + row * step
        fill = palette["levels"][day_level(dt.isoformat())]
        lines.append(
            f'<rect class="day" x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'rx="2" fill="{fill}"/>'
        )

    # Left day labels (Mon / Wed / Fri)
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        ly = pad + row * step + 10
        lines.append(
            f'<text x="{pad - 6}" y="{ly}" text-anchor="end" '
            f'font-family="Verdana,sans-serif" font-size="9" fill="{palette["text"]}">{name}</text>'
        )

    # Animated sweep highlight band
    band = 46
    lines.append(
        f'<rect y="{pad}" height="{grid_h}" width="{band}" fill="#ffffff" opacity="0.10">'
        f'<animate attributeName="x" values="{pad};{width - pad - band};{pad}" '
        f'dur="7s" repeatCount="indefinite"/>'
        f"</rect>"
    )

    lines.append("</svg>")
    return "\n".join(lines)
def render_wave():
    w, h, periods, amp, base = 1440, 96, 4, 20, 54
    n = 180

    def wave_path(phase):
        pts = [
            (w * i / n, base + amp * math.sin(2 * math.pi * periods * i / n + phase))
            for i in range(n + 1)
        ]
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
        for x, y in pts[1:]:
            d += f" L {x:.1f} {y:.1f}"
        d += f" L {w} {h} L 0 {h} Z"
        return d

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        'preserveAspectRatio="none" width="100%" height="96" aria-hidden="true">',
        f'<path d="{wave_path(0.0)}" fill="#8b5cf6" opacity="0.30">'
        f'<animateTransform attributeName="transform" attributeType="XML" '
        f'type="translate" from="0 0" to="-{w // periods} 0" dur="9s" '
        f'repeatCount="indefinite"/></path>',
        f'<path d="{wave_path(math.pi)}" fill="#7c3aed" opacity="0.18">'
        f'<animateTransform attributeName="transform" attributeType="XML" '
        f'type="translate" from="0 0" to="-{w // periods} 0" dur="13s" '
        f'begin="-3s" repeatCount="indefinite"/></path>',
        "</svg>",
    ]
    return "\n".join(lines)


def main():
    levels, total_hdr = fetch_contributions()
    os.makedirs(OUT_DIR, exist_ok=True)

    for name, palette in (("heatmap.svg", LIGHT), ("heatmap-dark.svg", DARK)):
        svg = render_heatmap(levels, total_hdr, palette)
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
            fh.write(svg)

    with open(os.path.join(OUT_DIR, "wave.svg"), "w", encoding="utf-8") as fh:
        fh.write(render_wave())

    total = total_hdr if total_hdr is not None else sum(
        1 for v in levels.values() if v > 0
    )
    print(
        f"Wrote heatmap(+dark) and wave to {OUT_DIR}; "
        f"days parsed={len(levels)}, contributions={total}"
    )


if __name__ == "__main__":
    main()