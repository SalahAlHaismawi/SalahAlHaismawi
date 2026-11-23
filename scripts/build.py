"""Build the SVG cards for the profile README.

Fetches live numbers from Hugging Face and GitHub, appends today's Nuqta
download count to data/history.json, and writes light and dark variants of
every card into assets/. Runs daily from .github/workflows/stats.yml.
"""
import datetime as dt
import json
import math
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
HISTORY = ROOT / "data" / "history.json"
HF_USER = "SalahALHaismawi"
GH_USER = "SalahAlHaismawi"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

THEMES = {
    "light": dict(bg="#ffffff", ink="#1f2328", muted="#59636e", faint="#d1d9e0",
                  bar="#d1d9e0", accent="#0f7a5c", accent2="#14a37a", tile="#f6f8fa"),
    "dark": dict(bg="#0d1117", ink="#e6edf3", muted="#9198a1", faint="#30363d",
                 bar="#30363d", accent="#2fbf8f", accent2="#5fd9ad", tile="#151b23"),
}

# Published benchmark results (model cards, KITAB-Bench and Misraj-DocOCR papers).
KITAB = [  # macro character error rate, lower is better
    ("Nuqta-Arabic-OCR 4B", 0.106, True),
    ("Nuqta-Arabic-OCR 0.8B", 0.117, True),
    ("Gemini-2.0-Flash", 0.130, False),
    ("AIN-7B", 0.200, False),
    ("GPT-4o", 0.310, False),
    ("Qwen-2.5-VL 7B", 0.492, False),
    ("Tesseract", 0.540, False),
    ("EasyOCR", 0.580, False),
]
MISRAJ = [  # MARS = (chrF + TEDS) / 2, higher is better
    ("Nuqta-Arabic-OCR 4B", 82.8, True),
    ("Baseer v2 (Misraj)", 77.8, False),
    ("Nuqta-Arabic-OCR 0.8B", 77.1, True),
    ("Baseer (paper)", 76.9, False),
    ("Gemini-2.5-Pro", 70.8, False),
    ("Azure Document Intelligence", 62.2, False),
    ("dots.ocr", 59.2, False),
    ("GPT-5", 54.8, False),
    ("Mistral OCR", 44.4, False),
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-stats"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    models = get(f"https://huggingface.co/api/models?author={HF_USER}"
                 "&expand[]=downloadsAllTime&expand[]=likes")
    repos = get(f"https://api.github.com/users/{GH_USER}/repos?per_page=100&type=owner")
    nuqta = sum(m.get("downloadsAllTime", 0) for m in models if "Nuqta" in m["id"])
    return dict(
        hf_total=sum(m.get("downloadsAllTime", 0) for m in models),
        hf_models=len(models),
        nuqta=nuqta,
        stars=sum(r["stargazers_count"] for r in repos if not r["fork"]),
        nuqta_stars=next((r["stargazers_count"] for r in repos if r["name"] == "nuqta-ocr"), 0),
    )


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def svg(w, h, body, t, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}">'
            f'<rect width="{w}" height="{h}" rx="10" fill="{t["bg"]}" stroke="{t["faint"]}"/>{body}</svg>')


def header(t):
    w, h = 840, 190
    dots = []
    # A dot field that fades to the left: the "nuqta" (dot) motif.
    for gx in range(26):
        for gy in range(9):
            x, y = 470 + gx * 13.5, 28 + gy * 17
            fade = gx / 25
            wave = 0.5 + 0.5 * math.sin(gx * 0.55 + gy * 0.9)
            r = 1.2 + 2.6 * fade * wave
            hot = (gx * 7 + gy * 11) % 23 == 0 and gx > 8
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
                        f'fill="{t["accent"] if hot else t["muted"]}" '
                        f'opacity="{(0.9 if hot else 0.12 + 0.35 * fade):.2f}"/>')
    body = "".join(dots) + (
        f'<text x="36" y="78" font-family="{FONT}" font-size="34" font-weight="700" fill="{t["ink"]}">Salah AlHaismawi</text>'
        f'<text x="36" y="110" font-family="{FONT}" font-size="16" fill="{t["muted"]}">Applied ML engineer · document AI, LLM training, speech</text>'
        f'<rect x="36" y="134" width="196" height="28" rx="14" fill="{t["accent"]}" opacity="0.14"/>'
        f'<circle cx="52" cy="148" r="4" fill="{t["accent"]}"/>'
        f'<text x="64" y="153" font-family="{FONT}" font-size="13" font-weight="600" fill="{t["accent"]}">Building Nuqta Arabic OCR</text>'
    )
    return svg(w, h, body, t, "Salah AlHaismawi, applied ML engineer")


def stats(t, s):
    w, h = 840, 132
    tiles = [
        (fmt(s["hf_total"]), "model downloads", "Hugging Face, all time"),
        (fmt(s["nuqta"]), "Nuqta OCR downloads", "since launch, Oct 2026"),
        ("#1", "Arabic OCR", "KITAB-Bench · Misraj-DocOCR"),
        (str(s["stars"]), "GitHub stars", f'{s["hf_models"]} models on Hugging Face'),
    ]
    tw, gap, x0 = 186, 12, 24
    body = ""
    for i, (big, name, sub) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        col = t["accent"] if i == 2 else t["ink"]
        body += (f'<rect x="{x}" y="20" width="{tw}" height="92" rx="8" fill="{t["tile"]}"/>'
                 f'<text x="{x + 16}" y="62" font-family="{FONT}" font-size="30" font-weight="700" fill="{col}">{big}</text>'
                 f'<text x="{x + 16}" y="83" font-family="{FONT}" font-size="13" font-weight="600" fill="{t["ink"]}">{name}</text>'
                 f'<text x="{x + 16}" y="100" font-family="{FONT}" font-size="11.5" fill="{t["muted"]}">{sub}</text>')
    return svg(w, h, body, t, "Profile statistics")


def bars(t, title, sub, rows, lower_better, unit_fmt, source):
    w = 840
    top, rh, lw = 86, 30, 230
    h = top + rh * len(rows) + 44
    vmax = max(v for _, v, _ in rows)
    span = w - lw - 110
    body = (f'<text x="28" y="40" font-family="{FONT}" font-size="18" font-weight="700" fill="{t["ink"]}">{title}</text>'
            f'<text x="28" y="62" font-family="{FONT}" font-size="12.5" fill="{t["muted"]}">{sub}</text>')
    for i, (name, v, ours) in enumerate(rows):
        y = top + i * rh
        bw = max(4, span * v / vmax)
        fill = t["accent"] if ours else t["bar"]
        weight = "700" if ours else "400"
        ink = t["ink"] if ours else t["muted"]
        body += (f'<text x="{lw - 12}" y="{y + 15}" text-anchor="end" font-family="{FONT}" font-size="13" '
                 f'font-weight="{weight}" fill="{ink}">{name}</text>'
                 f'<rect x="{lw}" y="{y + 3}" width="{bw:.1f}" height="17" rx="4" fill="{fill}"/>'
                 f'<text x="{lw + bw + 8:.1f}" y="{y + 16}" font-family="{MONO}" font-size="12.5" '
                 f'font-weight="{weight}" fill="{ink}">{unit_fmt(v)}</text>')
    body += (f'<text x="28" y="{h - 18}" font-family="{FONT}" font-size="11" fill="{t["muted"]}">{source}</text>')
    return svg(w, h, body, t, title)


def history_chart(t, hist):
    w, h = 840, 270
    pts = sorted(hist.items())
    x0, x1, y0, y1 = 70, w - 40, 222, 100
    d0 = dt.date.fromisoformat(pts[0][0])
    days = [(dt.date.fromisoformat(d) - d0).days for d, _ in pts]
    span = max(days[-1], 1)
    vmax = max(v for _, v in pts)
    step = 5000 if vmax > 10000 else 1000
    ymax = math.ceil(vmax / step) * step or step
    X = lambda d: x0 + (x1 - x0) * d / span
    Y = lambda v: y0 - (y0 - y1) * v / ymax
    grid = ""
    for v in range(0, ymax + 1, step):
        grid += (f'<line x1="{x0}" x2="{x1}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{t["faint"]}"/>'
                 f'<text x="{x0 - 10}" y="{Y(v) + 4:.1f}" text-anchor="end" font-family="{MONO}" '
                 f'font-size="11" fill="{t["muted"]}">{fmt(v)}</text>')
    line = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, (_, v) in zip(days, pts))
    area = f"{X(days[0]):.1f},{y0} {line} {X(days[-1]):.1f},{y0}"
    last_d, last_v = pts[-1]
    months = ""
    m = dt.date(d0.year, d0.month, 1)
    while True:
        m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
        dd = (m - d0).days
        if dd > span:
            break
        months += (f'<text x="{X(dd):.1f}" y="{y0 + 20}" text-anchor="middle" font-family="{FONT}" '
                   f'font-size="11" fill="{t["muted"]}">{m.strftime("%b %Y")}</text>')
    body = (f'<text x="28" y="40" font-family="{FONT}" font-size="18" font-weight="700" fill="{t["ink"]}">'
            f'Nuqta OCR downloads since launch</text>'
            f'<text x="28" y="60" font-family="{FONT}" font-size="12.5" fill="{t["muted"]}">'
            f'All four models on Hugging Face, cumulative. Updated daily.</text>'
            f'{grid}{months}'
            f'<polygon points="{area}" fill="{t["accent"]}" opacity="0.12"/>'
            f'<polyline points="{line}" fill="none" stroke="{t["accent"]}" stroke-width="2.5" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            + "".join(f'<circle cx="{X(d):.1f}" cy="{Y(v):.1f}" r="2.5" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="1.5"/>' for d, (_, v) in zip(days, pts)) +
            f'<circle cx="{X(days[-1]):.1f}" cy="{Y(last_v):.1f}" r="5" fill="{t["accent"]}"/>'
            f'<text x="{X(days[-1]) - 10:.1f}" y="{Y(last_v) - 12:.1f}" text-anchor="end" font-family="{FONT}" '
            f'font-size="13" font-weight="700" fill="{t["ink"]}">{last_v:,} on {dt.date.fromisoformat(last_d).strftime("%d %b")}</text>')
    return svg(w, h, body, t, "Nuqta OCR downloads since launch")


def main():
    s = fetch()
    hist = json.loads(HISTORY.read_text()) if HISTORY.exists() else {}
    hist[dt.date.today().isoformat()] = s["nuqta"]
    HISTORY.parent.mkdir(exist_ok=True)
    HISTORY.write_text(json.dumps(dict(sorted(hist.items())), indent=1) + "\n")
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        out = {
            "header": header(t),
            "stats": stats(t, s),
            "kitab": bars(t, "KITAB-Bench: character error rate", "13 Arabic OCR datasets, macro average. Lower is better.",
                          KITAB, True, lambda v: f"{v:.3f}",
                          "Source: KITAB-Bench published results; Nuqta at its recommended input size."),
            "misraj": bars(t, "Misraj-DocOCR: MARS score", "Whole-document Arabic OCR: text (chrF) and tables (TEDS). Higher is better.",
                           MISRAJ, False, lambda v: f"{v:.1f}",
                           "Source: Misraj Baseer paper and Baseer v2 release; Nuqta at its recommended input size."),
            "downloads": history_chart(t, hist),
        }
        for k, v in out.items():
            (ASSETS / f"{k}-{name}.svg").write_text(v)
    print(json.dumps(s))


if __name__ == "__main__":
    main()
