#!/usr/bin/env python3
"""Generate a polished self-hosted GitHub stats card SVG (emoji-free).

Fetches public account data from the GitHub REST API on GitHub's own
runners and renders a purple-themed stats card into OUT_DIR as
github-stats-card.svg. Served from the `stats` branch, so it never
depends on flaky third-party hosts.
"""
import datetime
import json
import os
import urllib.request

USER = os.environ.get("INPUT_USER", "LionStone-1")
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
OUT_DIR = os.environ.get("OUT_DIR", "dist")


def api(path: str):
    headers = {"User-Agent": "profile-stats-card"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
        headers["Accept"] = "application/vnd.github+json"
    req = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100&sort=stars")

    pub_repos = int(user.get("public_repos", 0))
    followers = int(user.get("followers", 0))
    following = int(user.get("following", 0))
    gists = int(user.get("public_gists", 0))
    total_stars = int(sum(r.get("stargazers_count", 0) for r in repos))
    name = user.get("name") or USER
    login = user.get("login", USER)
    created = user.get("created_at", "")[:4]
    initial = (name[:1] or "G").upper()

    items = [
        ("Repositories", pub_repos),
        ("Total Stars", total_stars),
        ("Followers", followers),
        ("Following", following),
        ("Public Gists", gists),
        ("Since", created),
    ]

    w, h = 640, 264
    pad = 32
    cols = 3
    cw = (w - 2 * pad) // cols

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">'
    )
    svg.append("<defs>")
    svg.append(
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#191026"/>'
        '<stop offset="0.6" stop-color="#111111"/>'
        '<stop offset="1" stop-color="#0d1117"/>'
        "</linearGradient>"
    )
    svg.append(
        '<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#a78bfa"/>'
        '<stop offset="1" stop-color="#6d28d9"/>'
        "</linearGradient>"
    )
    svg.append("</defs>")

    svg.append(f'<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>')
    svg.append(
        f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="16" '
        'fill="none" stroke="#30363d" stroke-width="1.5"/>'
    )

    # Avatar monogram
    cx, cy, r = 44, 52, 25
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 2}" fill="url(#ring)"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#181622"/>')
    svg.append(
        f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" '
        'font-family="Verdana,sans-serif" font-size="26" font-weight="700" '
        f'fill="#c4b5fd">{esc(initial)}</text>'
    )

    # Name + login
    svg.append(
        f'<text x="86" y="50" font-family="Verdana,sans-serif" font-size="19" '
        f'font-weight="700" fill="#e6edf3">{esc(name)}</text>'
    )
    svg.append(
        f'<text x="86" y="72" font-family="Verdana,sans-serif" font-size="13" '
        f'fill="#8b949e">@{esc(login)}</text>'
    )

    # Right-side tag
    svg.append(
        f'<text x="{w - pad}" y="50" text-anchor="end" '
        'font-family="Verdana,sans-serif" font-size="12" fill="#8b5cf6" '
        'font-weight="700" letter-spacing="1">GITHUB STATS</text>'
    )

    # Divider
    svg.append(
        f'<line x1="{pad}" y1="98" x2="{w - pad}" y2="98" '
        'stroke="#21262d" stroke-width="1"/>'
    )

    # Metrics grid
    for i, (label, value) in enumerate(items):
        col = i % cols
        row = i // cols
        x = pad + col * cw
        y = 140 + row * 60
        svg.append(
            f'<text x="{x}" y="{y}" font-family="Verdana,sans-serif" '
            f'font-size="27" font-weight="700" fill="#e6edf3">{esc(value)}</text>'
        )
        svg.append(
            f'<text x="{x}" y="{y + 20}" font-family="Verdana,sans-serif" '
            f'font-size="12" fill="#8b949e">{esc(label)}</text>'
        )

    # Footer update line
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y")
    svg.append(
        f'<text x="{w / 2}" y="{h - 18}" text-anchor="middle" '
        'font-family="Verdana,sans-serif" font-size="10" fill="#484f58">'
        f"Updated daily via GitHub Actions · {today} UTC</text>"
    )

    svg.append("</svg>")

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "github-stats-card.svg")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(svg))

    print(
        f"Wrote {out}: {name} repos={pub_repos} stars={total_stars} "
        f"followers={followers} following={following} gists={gists} since={created}"
    )


if __name__ == "__main__":
    main()