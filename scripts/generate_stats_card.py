#!/usr/bin/env python3
"""Generate a self-hosted GitHub stats card SVG (emoji-free).

Fetches public account data from the GitHub REST API on GitHub's own
runners and renders a purple-themed stats card into OUT_DIR as
github-stats-card.svg. Served from the `stats` branch, so it never
depends on flaky third-party hosts.
"""
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

    items = [
        ("Repositories", pub_repos),
        ("Total Stars", total_stars),
        ("Followers", followers),
        ("Following", following),
        ("Public Gists", gists),
    ]

    w, h, pad = 640, 224, 30
    cols = 3
    cw = (w - 2 * pad) // cols

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
    )
    svg.append(
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#1b1030"/><stop offset="1" stop-color="#0d1117"/>'
        "</linearGradient></defs>"
    )
    svg.append(f'<rect width="{w}" height="{h}" rx="16" fill="url(#bg)"/>')
    svg.append(
        f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="14" '
        'fill="none" stroke="#30363d" stroke-width="1.5"/>'
    )
    svg.append(
        f'<text x="{pad}" y="{pad + 20}" font-family="Verdana,sans-serif" '
        'font-size="18" font-weight="700" fill="#8b5cf6">GitHub Stats</text>'
    )
    svg.append(
        f'<text x="{pad}" y="{pad + 44}" font-family="Verdana,sans-serif" '
        f'font-size="13" fill="#8b949e">{esc(name)}</text>'
    )

    for i, (label, value) in enumerate(items):
        col = i % cols
        row = i // cols
        x = pad + col * cw
        y = 118 + row * 52
        svg.append(
            f'<text x="{x}" y="{y}" font-family="Verdana,sans-serif" '
            f'font-size="26" font-weight="700" fill="#c9d1d9">{value}</text>'
        )
        svg.append(
            f'<text x="{x}" y="{y + 22}" font-family="Verdana,sans-serif" '
            f'font-size="12" fill="#8b949e">{esc(label)}</text>'
        )

    svg.append("</svg>")

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "github-stats-card.svg")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(svg))

    print(
        f"Wrote {out}: repos={pub_repos} stars={total_stars} "
        f"followers={followers} following={following} gists={gists}"
    )


if __name__ == "__main__":
    main()