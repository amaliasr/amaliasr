#!/usr/bin/env python3
"""Generate the animated SVGs for the profile README.

- Embeds the cute rounded font "Fredoka" (if found in assets/fonts/) so the
  text looks the same everywhere, even inside GitHub's <img> sandbox.
- Writes the love counter: BASE_LOVES + current stargazer count.

Run locally:   python3 scripts/build.py
In CI:         see .github/workflows/build.yml (downloads the font first).
"""
import base64
import json
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
BASE_LOVES = 31
REPO = os.environ.get("GITHUB_REPOSITORY", "amaliasr/amaliasr")

FAMILY = "'Fredoka', 'Comic Sans MS', 'Chalkboard SE', 'Comic Neue', 'Segoe UI', sans-serif"

NAVY = "#3b5b8c"
SOFT = "#6f8fbf"
PINK = "#ff8fbf"
BLUE = "#7cc4ff"


# ---------------------------------------------------------------- helpers
def font_css() -> str:
    css = []
    for weight in (500, 700):
        f = FONTS / f"fredoka-{weight}.ttf"
        if f.exists():
            b64 = base64.b64encode(f.read_bytes()).decode()
            css.append(
                "@font-face{font-family:'Fredoka';font-weight:%d;"
                "src:url(data:font/ttf;base64,%s) format('truetype');}" % (weight, b64)
            )
    return "".join(css)


def loves() -> int:
    stars = 0
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}")
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=15) as r:
            stars = int(json.load(r).get("stargazers_count", 0))
    except Exception as e:  # offline / rate limited -> base value
        print("star lookup skipped:", e)
    return BASE_LOVES + stars


def cloud(x, y, s=1.0, opacity=1.0):
    """A generic fluffy cloud made of circles."""
    return (
        f'<g transform="translate({x} {y}) scale({s})" opacity="{opacity}">'
        '<ellipse cx="0" cy="18" rx="62" ry="20" fill="#fff"/>'
        '<circle cx="-30" cy="6" r="24" fill="#fff"/>'
        '<circle cx="2" cy="-6" r="32" fill="#fff"/>'
        '<circle cx="34" cy="8" r="22" fill="#fff"/>'
        "</g>"
    )


def drifting_cloud(y, s, op, dur, begin):
    return (
        f'<g>{cloud(0, y, s, op)}'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="-180 0;1380 0" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>'
    )


HEART = (
    "M0 10 C-14 0 -22 -7 -22 -15 C-22 -20.5 -17.5 -24 -12.5 -24 "
    "C-9 -24 -6 -22 0 -17 C6 -22 9 -24 12.5 -24 C17.5 -24 22 -20.5 22 -15 "
    "C22 -7 14 0 0 10 Z"
)


# ---------------------------------------------------------------- hero
def hero(fonts: str) -> str:
    sparkles = "".join(
        f'<g transform="translate({x} {y})"><path d="M0 -8 L2 -2 L8 0 L2 2 L0 8 L-2 2 L-8 0 L-2 -2Z" fill="{c}">'
        f'<animate attributeName="opacity" values=".2;1;.2" dur="{d}s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animateTransform attributeName="transform" type="scale" values=".6;1.2;.6" dur="{d}s" begin="{b}s" repeatCount="indefinite"/></path></g>'
        for x, y, c, d, b in [
            (70, 60, PINK, 2.6, 0), (520, 70, "#ffd76e", 3.2, .6), (640, 330, BLUE, 2.8, 1.1),
            (820, 60, PINK, 3.6, .3), (1150, 120, "#ffd76e", 2.4, 1.4), (420, 380, PINK, 3.0, .9),
            (1160, 360, BLUE, 3.4, .2),
        ]
    )
    rising = "".join(
        f'<g opacity="0"><animateTransform attributeName="transform" type="translate" '
        f'values="{x} 150;{x + dx} 40" dur="3.6s" begin="{b}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;1;0" dur="3.6s" begin="{b}s" repeatCount="indefinite"/>'
        f'<path d="{HEART}" fill="{c}" transform="scale({s})"/></g>'
        for x, dx, s, c, b in [(950, -20, .5, PINK, 0), (1040, 15, .4, "#ffb3d1", 1.2), (1090, -10, .35, PINK, 2.4)]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420" role="img" aria-label="Hi, I'm Amalia, Product Manager">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#bfe3ff"/><stop offset=".6" stop-color="#e3f3ff"/><stop offset="1" stop-color="#fdf0f7"/>
    </linearGradient>
    <linearGradient id="name" x1="0" x2="1">
      <stop offset="0" stop-color="#5b8def"><animate attributeName="stop-color" values="#5b8def;#ff7ab6;#5b8def" dur="6s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#ff7ab6"><animate attributeName="stop-color" values="#ff7ab6;#5b8def;#ff7ab6" dur="6s" repeatCount="indefinite"/></stop>
    </linearGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#7aa8e0" flood-opacity=".35"/></filter>
    <clipPath id="card"><rect width="1200" height="420" rx="32"/></clipPath>
    <style>{fonts}
      .t {{ font-family: {FAMILY}; }}
      @keyframes rise {{ from {{ opacity:0; transform:translateY(22px); }} to {{ opacity:1; transform:translateY(0); }} }}
      @keyframes wave {{ 0%,60%,100% {{ transform:rotate(0); }} 10%,30% {{ transform:rotate(18deg); }} 20%,40% {{ transform:rotate(-10deg); }} }}
      @keyframes bob {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-14px); }} }}
      @keyframes blink {{ 0%,49% {{ opacity:1; }} 50%,100% {{ opacity:0; }} }}
      .a1 {{ opacity:0; animation:rise .8s ease-out .2s forwards; }}
      .a2 {{ opacity:0; animation:rise .8s ease-out .5s forwards; }}
      .a3 {{ opacity:0; animation:rise .8s ease-out .8s forwards; }}
      .a4 {{ opacity:0; animation:rise .8s ease-out 1.1s forwards; }}
      .hand {{ transform-box:fill-box; transform-origin:70% 80%; animation:wave 2.4s ease-in-out 1s infinite; }}
      .bob {{ animation:bob 4s ease-in-out infinite; }}
      .cur {{ animation:blink 1s steps(1) infinite; }}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="1200" height="420" fill="url(#sky)"/>
    {drifting_cloud(70, .9, .85, 38, -5)}
    {drifting_cloud(330, 1.3, .9, 52, -30)}
    {drifting_cloud(170, .6, .7, 30, -18)}
    {drifting_cloud(380, .8, .8, 44, -8)}
    {sparkles}

    <!-- mascot: Puffy the little cloud (original) -->
    <g class="bob" filter="url(#soft)">
      <ellipse cx="1010" cy="290" rx="150" ry="52" fill="#fff"/>
      <circle cx="905" cy="255" r="62" fill="#fff"/>
      <circle cx="1000" cy="215" r="88" fill="#fff"/>
      <circle cx="1100" cy="250" r="66" fill="#fff"/>
      <ellipse cx="968" cy="252" rx="7" ry="10" fill="{NAVY}">
        <animate attributeName="ry" values="10;10;1;10" keyTimes="0;.9;.95;1" dur="4s" repeatCount="indefinite"/>
      </ellipse>
      <ellipse cx="1042" cy="252" rx="7" ry="10" fill="{NAVY}">
        <animate attributeName="ry" values="10;10;1;10" keyTimes="0;.9;.95;1" dur="4s" repeatCount="indefinite"/>
      </ellipse>
      <circle cx="971" cy="248" r="2.5" fill="#fff"/><circle cx="1045" cy="248" r="2.5" fill="#fff"/>
      <path d="M994 270 Q1005 282 1016 270" fill="none" stroke="{NAVY}" stroke-width="4" stroke-linecap="round"/>
      <ellipse cx="945" cy="274" rx="14" ry="8" fill="{PINK}" opacity=".55"/>
      <ellipse cx="1065" cy="274" rx="14" ry="8" fill="{PINK}" opacity=".55"/>
      <g transform="translate(1092 158)">
        <path d="M0 -14 L4 -4 L14 -3 L6 4 L9 14 L0 8 L-9 14 L-6 4 L-14 -3 L-4 -4Z" fill="#ffd76e">
          <animateTransform attributeName="transform" type="rotate" values="-12;12;-12" dur="3s" repeatCount="indefinite"/>
        </path>
      </g>
    </g>
    {rising}

    <g class="a1"><text x="80" y="120" class="t" font-size="24" font-weight="500" fill="{SOFT}" letter-spacing="2">Halo, dunia!</text>
      <text class="hand" x="252" y="122" font-size="28">👋</text></g>
    <text class="a2 t" x="76" y="212" font-size="92" font-weight="700" fill="url(#name)">I'm Amalia</text>
    <text class="a3 t" x="80" y="264" font-size="30" font-weight="500" fill="{NAVY}">Product Manager</text>
    <g class="a4">
      <rect x="80" y="296" width="520" height="52" rx="26" fill="#fff" fill-opacity=".8" stroke="{BLUE}" stroke-opacity=".5" stroke-width="2"/>
      <text x="108" y="330" class="t" font-size="21" font-weight="500" fill="{NAVY}">turning ideas into products people love ♡<tspan class="cur" fill="{PINK}"> |</tspan></text>
    </g>
  </g>
</svg>
'''


# ---------------------------------------------------------------- process
def process(fonts: str) -> str:
    steps = [
        ("🔍", "Discover", "talk to users", "#ff9ec7"),
        ("🎯", "Define", "frame the problem", "#ffb38a"),
        ("🛠️", "Build", "ship with the team", "#ffd76e"),
        ("📊", "Measure", "let data speak", "#8fd8b8"),
        ("🔁", "Iterate", "better every loop", BLUE),
    ]
    nodes = ""
    for i, (emo, title, sub, col) in enumerate(steps):
        x = 120 + i * 240
        nodes += f'''
  <g class="n" style="animation-delay:{.3 + i * .45:.2f}s">
    <circle cx="{x}" cy="128" r="36" fill="#fff" stroke="{col}" stroke-width="4"/>
    <text x="{x}" y="139" text-anchor="middle" font-size="30">{emo}</text>
    <text x="{x}" y="192" text-anchor="middle" class="t" font-size="22" font-weight="700" fill="{NAVY}">{title}</text>
    <text x="{x}" y="216" text-anchor="middle" class="t" font-size="16" font-weight="500" fill="{SOFT}">{sub}</text>
  </g>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="240" viewBox="0 0 1200 240" role="img" aria-label="How I work: Discover, Define, Build, Measure, Iterate">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eaf6ff"/><stop offset="1" stop-color="#fdf0f7"/></linearGradient>
    <linearGradient id="ln" gradientUnits="userSpaceOnUse" x1="120" y1="0" x2="1080" y2="0"><stop offset="0" stop-color="#ff9ec7"/><stop offset=".5" stop-color="#ffd76e"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
    <style>{fonts}
      .t {{ font-family: {FAMILY}; }}
      @keyframes pop {{ 0% {{ opacity:0; transform:scale(.5); }} 70% {{ transform:scale(1.1); }} 100% {{ opacity:1; transform:scale(1); }} }}
      @keyframes draw {{ to {{ stroke-dashoffset:0; }} }}
      .n {{ opacity:0; transform-box:fill-box; transform-origin:center; animation:pop .6s ease-out forwards; }}
      .p {{ stroke-dasharray:960; stroke-dashoffset:960; animation:draw 2.4s ease-in-out .3s forwards; }}
    </style>
  </defs>
  <rect width="1200" height="240" rx="28" fill="url(#bg)"/>
  <text x="56" y="46" class="t" font-size="20" font-weight="700" fill="{PINK}">✿ how I work</text>
  <path class="p" d="M120 128 H1080" stroke="url(#ln)" stroke-width="6" fill="none" stroke-linecap="round" stroke-dasharray="960"/>
  <path d="{HEART}" fill="{PINK}" transform="scale(.45)">
    <animateMotion path="M120 128 H1080" dur="5s" begin="2.7s" repeatCount="indefinite"/>
  </path>{nodes}
</svg>
'''


# ---------------------------------------------------------------- love button
def love_button(fonts: str, n: int) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="96" viewBox="0 0 420 96" role="img" aria-label="Send some love: {n} loves">
  <defs>
    <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#ff9ec7"/><stop offset="1" stop-color="#ffb8d6"/></linearGradient>
    <linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <filter id="d" x="-20%" y="-40%" width="140%" height="180%"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#ff7ab6" flood-opacity=".4"/></filter>
    <clipPath id="c"><rect x="12" y="14" width="396" height="64" rx="32"/></clipPath>
    <style>{fonts}
      .t {{ font-family: {FAMILY}; }}
      @keyframes beat {{ 0%,100% {{ transform:scale(1); }} 14% {{ transform:scale(1.3); }} 28% {{ transform:scale(1); }} 42% {{ transform:scale(1.18); }} 56% {{ transform:scale(1); }} }}
      .h {{ transform-box:fill-box; transform-origin:center; animation:beat 1.4s ease-in-out infinite; }}
    </style>
  </defs>
  <rect x="12" y="14" width="396" height="64" rx="32" fill="url(#g)" filter="url(#d)"/>
  <g clip-path="url(#c)"><rect y="14" width="90" height="64" fill="url(#sh)"><animate attributeName="x" values="-90;420" dur="2.8s" repeatCount="indefinite"/></rect></g>
  <g transform="translate(58 50)"><path class="h" d="{HEART}" fill="#fff"/></g>
  {"".join(f'<g opacity="0"><animateTransform attributeName="transform" type="translate" values="{x} 34;{x + dx} 6" dur="2.2s" begin="{b}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;0" dur="2.2s" begin="{b}s" repeatCount="indefinite"/><path d="{HEART}" fill="#fff" transform="scale(.3)"/></g>' for x, dx, b in [(44, -6, 0), (70, 8, .7), (58, 0, 1.4)])}
  <text x="98" y="56" class="t" font-size="24" font-weight="700" fill="#fff">Send some love</text>
  <rect x="318" y="28" width="76" height="36" rx="18" fill="#fff"/>
  <text x="356" y="53" text-anchor="middle" class="t" font-size="20" font-weight="700" fill="#ff6fae">{n}</text>
</svg>
'''


def love_badge(fonts: str, n: int) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="170" height="40" viewBox="0 0 170 40" role="img" aria-label="{n} loves">
  <defs><style>{fonts}
    .t {{ font-family: {FAMILY}; }}
    @keyframes beat {{ 0%,100% {{ transform:scale(1); }} 20% {{ transform:scale(1.25); }} 40% {{ transform:scale(1); }} }}
    .h {{ transform-box:fill-box; transform-origin:center; animation:beat 1.6s ease-in-out infinite; }}
  </style></defs>
  <rect x="1" y="1" width="168" height="38" rx="19" fill="#fff0f7" stroke="#ff9ec7" stroke-width="2"/>
  <g transform="translate(26 22) scale(.55)"><path class="h" d="{HEART}" fill="#ff7ab6"/></g>
  <text x="46" y="27" class="t" font-size="17" font-weight="700" fill="#ff6fae">{n} loves</text>
</svg>
'''


def divider() -> str:
    dots = "".join(
        f'<g transform="translate({x} 14)"><path d="{HEART}" fill="{c}" transform="scale(.32)">'
        f'<animate attributeName="opacity" values=".3;1;.3" dur="2.4s" begin="{i * .3:.1f}s" repeatCount="indefinite"/></path></g>'
        for i, (x, c) in enumerate([(560, "#ff9ec7"), (600, "#ffd76e"), (640, BLUE)])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="30" viewBox="0 0 1200 30">
  <defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#ff9ec7" stop-opacity="0"/><stop offset=".25" stop-color="#ff9ec7"/><stop offset=".75" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient></defs>
  <rect x="60" y="14" width="460" height="3" rx="1.5" fill="url(#g)"/>
  <rect x="680" y="14" width="460" height="3" rx="1.5" fill="url(#g)"/>
  {dots}
</svg>
'''


def main():
    fonts = font_css()
    n = loves()
    ASSETS.mkdir(exist_ok=True)
    out = {
        "hero.svg": hero(fonts),
        "process.svg": process(fonts),
        "love.svg": love_button(fonts, n),
        "love-badge.svg": love_badge(fonts, n),
        "divider.svg": divider(),
    }
    for name, svg in out.items():
        (ASSETS / name).write_text(svg, encoding="utf-8")
    print(f"built {len(out)} svgs | loves={n} | font={'embedded' if fonts else 'fallback'}")


if __name__ == "__main__":
    main()
