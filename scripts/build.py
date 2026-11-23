"""Build the SVG cards for the profile README.

Fetches live numbers from Hugging Face and GitHub, appends today's Nuqta
download count to data/history.json, and writes light and dark variants of
each card into assets/. Runs daily from .github/workflows/stats.yml.
"""
import datetime as dt
import json
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
                  dot="#8c959f", accent="#0f7a5c", band="#0f7a5c"),
    "dark": dict(bg="#0d1117", ink="#e6edf3", muted="#9198a1", faint="#30363d",
                 dot="#6e7681", accent="#2fbf8f", band="#2fbf8f"),
}

# Published results: KITAB-Bench (macro CER, lower is better) and
# Misraj-DocOCR (MARS, higher is better). Nuqta at its recommended input size.
KITAB = [("Nuqta 4B", "0.106", True), ("Nuqta 0.8B", "0.117", True),
         ("Gemini-2.0-Flash", "0.130", False), ("AIN-7B", "0.200", False),
         ("GPT-4o", "0.310", False), ("Qwen-2.5-VL 7B", "0.492", False)]
MISRAJ = [("Nuqta 4B", "82.8", True), ("Baseer v2", "77.8", False),
          ("Nuqta 0.8B", "77.1", True), ("Baseer", "76.9", False),
          ("Gemini-2.5-Pro", "70.8", False), ("Azure Doc. Intelligence", "62.2", False)]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-stats"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    models = get(f"https://huggingface.co/api/models?author={HF_USER}&expand[]=downloadsAllTime")
    return dict(nuqta=sum(m.get("downloadsAllTime", 0) for m in models if "Nuqta" in m["id"]))


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def frame(w, h, body, t, label, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}">{style}'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{t["bg"]}" stroke="{t["faint"]}"/>'
            f'{body}</svg>')


def hero(t, s):
    w, h = 840, 220
    style = ("<style>"
             f".d{{transform-box:fill-box;transform-origin:center;animation:s 3.6s linear infinite}}"
             f"@keyframes s{{0%{{fill:{t['dot']}}}6%{{fill:{t['accent']};opacity:1;transform:scale(1.7)}}"
             f"16%{{fill:{t['dot']}}}100%{{fill:{t['dot']}}}}}"
             "@media (prefers-reduced-motion:reduce){.d{animation:none}}"
             "</style>")
    dots = []
    cols, rows = 26, 10
    for gx in range(cols):
        for gy in range(rows):
            x, y = 482 + gx * 13, 34 + gy * 17
            fade = gx / (cols - 1)
            dots.append(f'<circle class="d" style="animation-delay:{(cols - 1 - gx) * 0.09:.2f}s" cx="{x}" cy="{y}" '
                        f'r="{1.0 + 2.0 * fade:.2f}" fill="{t["dot"]}" opacity="{0.18 + 0.47 * fade:.2f}"/>')
    items = [f"{fmt(s['nuqta'])} downloads", "#1 KITAB-Bench", "#1 Misraj-DocOCR"]
    stats, x = "", 40
    for it in items:
        stats += (f'<circle cx="{x + 4}" cy="172" r="3.5" fill="{t["accent"]}"/>'
                  f'<text x="{x + 14}" y="176.5" font-family="{MONO}" font-size="12.5" fill="{t["ink"]}">{it}</text>')
        x += 14 + len(it) * 7.6 + 22
    body = ("".join(dots)
            + f'<text x="40" y="92" font-family="{FONT}" font-size="38" font-weight="700" letter-spacing="-0.5" '
              f'fill="{t["ink"]}">Salah AlHaismawi</text>'
            + f'<text x="40" y="126" font-family="{FONT}" font-size="17" fill="{t["muted"]}">'
              f'ML engineer. Teaching models to read Arabic.</text>'
            + stats)
    return frame(w, h, body, t, "Salah AlHaismawi. ML engineer. Teaching models to read Arabic.", style)


def board(t):
    w, h, pad, gap = 840, 296, 24, 24
    pw = (w - 2 * pad - gap) / 2
    body = ""
    for i, (title, sub, rows) in enumerate([
            ("KITAB-Bench", "character error rate · lower is better", KITAB),
            ("Misraj-DocOCR", "MARS · higher is better", MISRAJ)]):
        x0 = pad + i * (pw + gap)
        body += (f'<text x="{x0}" y="46" font-family="{FONT}" font-size="15" font-weight="700" fill="{t["ink"]}">{title}</text>'
                 f'<text x="{x0}" y="66" font-family="{FONT}" font-size="12" fill="{t["muted"]}">{sub}</text>')
        for r, (name, val, ours) in enumerate(rows):
            y = 84 + r * 28
            if ours:
                body += f'<rect x="{x0 - 8}" y="{y}" width="{pw + 16}" height="26" rx="6" fill="{t["band"]}" opacity="0.10"/>'
            elif r:
                body += f'<line x1="{x0}" x2="{x0 + pw}" y1="{y}" y2="{y}" stroke="{t["faint"]}"/>'
            col = t["accent"] if ours else t["muted"]
            wt = "700" if ours else "400"
            body += (f'<circle cx="{x0 + 5}" cy="{y + 13}" r="3.5" fill="{t["accent"] if ours else t["faint"]}"/>'
                     f'<text x="{x0 + 20}" y="{y + 17.5}" font-family="{MONO}" font-size="12" fill="{t["muted"]}">{r + 1}</text>'
                     f'<text x="{x0 + 40}" y="{y + 17.5}" font-family="{FONT}" font-size="13.5" font-weight="{wt}" '
                     f'fill="{t["ink"] if ours else t["muted"]}">{name}</text>'
                     f'<text x="{x0 + pw}" y="{y + 17.5}" text-anchor="end" font-family="{MONO}" font-size="13" '
                     f'font-weight="{wt}" fill="{col}">{val}</text>')
    body += (f'<text x="{pad}" y="{h - 20}" font-family="{FONT}" font-size="11" fill="{t["muted"]}">'
             f'Published results from KITAB-Bench, the Baseer paper and Baseer v2. Nuqta at its recommended input size.</text>')
    return frame(w, h, body, t, "Nuqta ranks first on KITAB-Bench and Misraj-DocOCR")


def main():
    s = fetch()
    hist = json.loads(HISTORY.read_text()) if HISTORY.exists() else {}
    hist[dt.date.today().isoformat()] = s["nuqta"]
    HISTORY.parent.mkdir(exist_ok=True)
    HISTORY.write_text(json.dumps(dict(sorted(hist.items())), indent=1) + "\n")
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (ASSETS / f"hero-{name}.svg").write_text(hero(t, s))
        (ASSETS / f"board-{name}.svg").write_text(board(t))
    print(json.dumps(s))


if __name__ == "__main__":
    main()
