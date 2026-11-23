"""Build the SVG cards for the profile README.

Fetches live numbers from Hugging Face, appends today's Nuqta download count
to data/history.json, and writes light and dark variants of each card into
assets/. Runs daily from .github/workflows/stats.yml.
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
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
ARABIC = "'Noto Naskh Arabic','Geeza Pro','Noto Sans Arabic','Segoe UI',Tahoma,sans-serif"

THEMES = {
    "light": dict(bg="#ffffff", ink="#1f2328", muted="#59636e", faint="#d1d9e0", dot="#8c959f",
                  accent="#0f7a5c", red="#cf222e", fire="#e8590c", fire2="#f59f00"),
    "dark": dict(bg="#0d1117", ink="#e6edf3", muted="#9198a1", faint="#30363d", dot="#6e7681",
                 accent="#2fbf8f", red="#f85149", fire="#ff7b31", fire2="#ffc53d"),
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    models = get(f"https://huggingface.co/api/models?author={HF_USER}&expand[]=downloadsAllTime")
    dl = {m["id"].split("/")[1]: m.get("downloadsAllTime", 0) for m in models}
    return dict(total=sum(dl.values()), models=len(dl),
                nuqta=sum(v for k, v in dl.items() if "Nuqta" in k),
                fire=dl.get("yolov26-fire-detection", 0))


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def frame(w, h, body, t, label, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}">{style}'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{t["bg"]}" stroke="{t["faint"]}"/>'
            f'{body}</svg>')


def text(x, y, s, t, size=13, color="ink", weight=400, family=FONT, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{t[color]}" {extra}>{s}</text>')


def hero(t, s):
    w, h = 840, 220
    style = ("<style>"
             ".d{transform-box:fill-box;transform-origin:center;animation:s 3.6s linear infinite}"
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
    items = [f"{fmt(s['total'])} downloads", f"{s['models']} open models", "vision · language · speech"]
    chips, x = "", 40
    for it in items:
        chips += (f'<circle cx="{x + 4}" cy="172" r="3.5" fill="{t["accent"]}"/>'
                  + text(x + 14, 176.5, it, t, 12.5, family=MONO))
        x += 14 + len(it) * 7.6 + 22
    body = ("".join(dots)
            + text(40, 92, "Salah AlHaismawi", t, 38, weight=700, extra='letter-spacing="-0.5"')
            + text(40, 126, "Applied ML engineer. I train models and ship them.", t, 17, "muted")
            + chips)
    return frame(w, h, body, t, "Salah AlHaismawi. Applied ML engineer.", style)


def tile(t, tag, title, lines, metrics, art, label):
    """metrics: list of (value, label) pairs, or a string shown as one mono line."""
    w, h = 410, 210
    body = (text(24, 38, tag, t, 11, "accent", 600, MONO, extra='letter-spacing="1.2"')
            + text(24, 70, title, t, 21, weight=700, extra='letter-spacing="-0.3"'))
    for i, ln in enumerate(lines):
        body += text(24, 96 + i * 18, ln, t, 13, "muted")
    if isinstance(metrics, str):
        body += text(24, 182, metrics, t, 11.5, "ink", 400, MONO)
    else:
        for i, (val, lab) in enumerate(metrics):
            x = 24 + i * 104
            body += text(x, 168, val, t, 22, weight=700) + text(x, 187, lab, t, 11, "muted")
    return frame(w, h, body + art, t, label)


def art_nuqta(t):
    return (f'<rect x="262" y="58" width="124" height="70" rx="6" fill="none" stroke="{t["accent"]}" '
            f'stroke-width="1.5" stroke-dasharray="5 4"/>'
            + text(324, 106, "نقطة", t, 38, "ink", 700, ARABIC, "middle")
            + f'<rect x="262" y="40" width="58" height="16" rx="3" fill="{t["accent"]}"/>'
            + text(268, 52, "ar 0.99", t, 10, "bg", 600, MONO)
            + text(324, 152, "→ nuqta", t, 12, "muted", 400, MONO, "middle"))


def art_doctor(t):
    pts = [(266, 64), (282, 92), (298, 110), (314, 120), (330, 126), (346, 129), (352, 72),
           (358, 128), (374, 130), (388, 131)]
    line = " ".join(f"{x},{y}" for x, y in pts)
    return (f'<line x1="262" y1="140" x2="392" y2="140" stroke="{t["faint"]}"/>'
            f'<line x1="262" y1="50" x2="262" y2="140" stroke="{t["faint"]}"/>'
            f'<polyline points="{line}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="352" cy="72" r="9" fill="none" stroke="{t["red"]}" stroke-width="1.5"/>'
            + text(392, 44, "spike @ 2847", t, 10.5, "red", 600, MONO, "end")
            + text(262, 158, "loss", t, 10.5, "muted", 400, MONO))


def art_fire(t):
    flame = ("M326 136 C298 132 292 104 310 86 C312 98 318 102 324 100 C316 84 322 64 340 54 "
             "C338 72 356 80 356 102 C356 122 346 136 326 136 Z")
    inner = "M326 134 C314 132 310 118 320 108 C322 116 328 116 330 112 C336 118 340 132 326 134 Z"
    return (f'<rect x="282" y="44" width="92" height="100" rx="4" fill="none" stroke="{t["fire"]}" stroke-width="1.8"/>'
            f'<rect x="282" y="28" width="72" height="16" rx="3" fill="{t["fire"]}"/>'
            + text(288, 40, "fire 0.95", t, 10, "bg", 600, MONO)
            + f'<path d="{flame}" fill="{t["fire"]}" opacity="0.9"/><path d="{inner}" fill="{t["fire2"]}"/>')


def art_talon(t):
    experts = [56, 82, 108, 134]
    on = {1, 3}
    out = (f'<circle cx="276" cy="104" r="9" fill="{t["accent"]}"/>'
           + text(276, 132, "token", t, 10, "muted", 400, MONO, "middle")
           + f'<rect x="304" y="90" width="26" height="28" rx="5" fill="none" stroke="{t["dot"]}" stroke-width="1.3"/>'
           + text(317, 132, "router", t, 10, "muted", 400, MONO, "middle")
           + f'<line x1="285" y1="104" x2="304" y2="104" stroke="{t["dot"]}" stroke-width="1.3"/>')
    for i, y in enumerate(experts):
        lit = i in on
        c = t["accent"] if lit else t["faint"]
        out += (f'<line x1="330" y1="104" x2="352" y2="{y + 8}" stroke="{c}" stroke-width="{1.8 if lit else 1}"/>'
                f'<rect x="352" y="{y}" width="34" height="16" rx="4" fill="{c if lit else "none"}" '
                f'fill-opacity="{0.25 if lit else 1}" stroke="{c}" stroke-width="1.3"/>')
    return out + text(369, 168, "experts", t, 10, "muted", 400, MONO, "middle")


TILES = {
    "nuqta": lambda t, s: tile(t, "DOCUMENT AI", "Nuqta OCR",
                               ["Open-source Arabic OCR that", "keeps tashkeel as printed."],
                               [("#1", "KITAB · Misraj"), (fmt(s["nuqta"]), "downloads")],
                               art_nuqta(t), "Nuqta OCR"),
    "doctor": lambda t, s: tile(t, "TRAINING", "training-doctor",
                                ["Catches silent training failures", "and tells you the fix."],
                                "plateaus · spikes · NaNs · divergence",
                                art_doctor(t), "training-doctor"),
    "fire": lambda t, s: tile(t, "COMPUTER VISION", "Fire detection",
                              ["Real-time fire and smoke detector", "built on YOLOv26."],
                              [("94.9%", "mAP@50"), (fmt(s["fire"]), "downloads")],
                              art_fire(t), "YOLOv26 fire detection"),
    "talon": lambda t, s: tile(t, "LLMS", "Talon",
                               ["A language model written and", "trained from scratch."],
                               "RoPE · GQA · SwiGLU · MoE",
                               art_talon(t), "Talon LLM"),
}


def main():
    s = fetch()
    hist = json.loads(HISTORY.read_text()) if HISTORY.exists() else {}
    hist[dt.date.today().isoformat()] = s["nuqta"]
    HISTORY.parent.mkdir(exist_ok=True)
    HISTORY.write_text(json.dumps(dict(sorted(hist.items())), indent=1) + "\n")
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (ASSETS / f"hero-{name}.svg").write_text(hero(t, s))
        for k, fn in TILES.items():
            (ASSETS / f"{k}-{name}.svg").write_text(fn(t, s))
    print(json.dumps(s))


if __name__ == "__main__":
    main()
