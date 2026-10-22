#!/usr/bin/env python3
"""AON-style gallery images for Devpost (3:2, 1800x1200): gradient ad band (chip + 2-line headline + subline)
on top, the real UI screenshot as a rounded card below, red boxes + labels on the key points.
Adapted from the vault's portrait store-shot style (Obsidian Vault/global/App/AON Style Store Screenshots.md).
Usage: python3 scripts/aon_shots.py   (reads artifacts/devpost/raw, writes docs/images/devpost)"""
import glob, json, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW, OUT = os.path.join(ROOT, "artifacts/devpost/raw"), os.path.join(ROOT, "docs/images/devpost")
W, H, BAND = 1800, 1200, 0.30
_PF = glob.glob("/System/Library/AssetsV2/com_apple_MobileAsset_Font*/*/AssetData/PingFang.ttc")


def font(size, weight="semibold"):
    if _PF:
        return ImageFont.truetype(_PF[0], size, index={"regular": 2, "medium": 6, "semibold": 10}[weight])
    return ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", size)


COPY = {  # key: (chip, headline, subline, gradient)
    "1": ("No authority", "No approval.\nNo action.", "The first purchase is blocked. The agent can only propose.", ("#FF5A3C", "#FF8A3D")),
    "2": ("Human approval", "One human click.\nReusable boundary.", "Household ≤ $30 · StoreA / StoreB · no subscriptions", ("#6C4CF5", "#9B6BFF")),
    "3": ("Cross-session", "New session.\nAutomatic purchase.", "The approved authority reloads itself. MCP buys.", ("#0FB39A", "#22C7D6")),
    "4": ("MCP trace", "Every step\nis traceable.", "search → evaluate → token → purchase", ("#2F6BFF", "#4FA3FF")),
    "5": ("No self-escalation", "Ignore the limit?\nRejected.", "Only a human can expand authority.", ("#FF4F8B", "#FF7A6B")),
    "6": ("Audit", "Who approved it?\nAlways recorded.", "Decision · boundary · authority source · MCP tool", ("#F59E0B", "#FF6B3D")),
}
RED = (230, 30, 40)


def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def gradient(c1, c2):
    a, b = rgb(c1), rgb(c2)
    g = Image.new("RGB", (W, H)); d = ImageDraw.Draw(g)
    for y in range(H):
        t = y / (H - 1); d.line([(0, y), (W, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return g.convert("RGBA")


def compose(key):
    chip, title, sub, (c1, c2) = COPY[key]
    meta = json.load(open(f"{RAW}/{key}.json"))
    shot = Image.open(f"{RAW}/{key}.png").convert("RGBA")
    base = min(W, int(H * 0.6))
    img = gradient(c1, c2)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    r = int(base * 0.42)
    od.ellipse([W - r * 1.3, -r * 0.7, W + r * 0.7, r * 1.3], fill=(255, 255, 255, 34))
    r2 = int(base * 0.18)
    od.ellipse([-r2 * 0.6, H * BAND * 0.62, r2 * 1.4, H * BAND * 0.62 + r2 * 2], fill=(255, 255, 255, 26))
    img.alpha_composite(ov)

    d = ImageDraw.Draw(img)
    x, y = int(W * 0.07 * 0.6), int(H * BAND * 0.14)
    fc = font(int(base * 0.036))
    tw = d.textlength(chip, font=fc); ph, pv = int(base * 0.028), int(base * 0.014); ch = int(base * 0.036) + pv * 2
    d.rounded_rectangle([x, y, x + tw + ph * 2, y + ch], radius=ch // 2, fill="white")
    d.text((x + ph, y + ch // 2), chip, font=fc, fill=c1, anchor="lm")
    y += ch + int(base * 0.03)
    ft = font(int(base * 0.080)); sp = int(base * 0.016)
    d.multiline_text((x, y), title, font=ft, fill="white", spacing=sp)
    y = d.multiline_textbbox((x, y), title, font=ft, spacing=sp)[3] + int(base * 0.025)
    d.text((x, y), sub, font=font(int(base * 0.040), "medium"), fill=(255, 255, 255, 235))

    cw = int(W * 0.87); sc = cw / shot.width
    s = shot.resize((cw, int(shot.height * sc)), Image.LANCZOS)
    top, left, rad = int(H * BAND), (W - cw) // 2, int(base * 0.045)
    mask = Image.new("L", s.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s.width, s.height + rad], radius=rad, fill=255)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([left, top + rad // 3, left + cw, H + rad], radius=rad, fill=(0, 0, 0, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(base * 0.025)))
    bd = int(base * 0.010)
    ImageDraw.Draw(img).rounded_rectangle([left - bd, top - bd, left + cw + bd, H + rad], radius=rad + bd, fill=(255, 255, 255, 110))
    img.paste(s, (left, top), mask)

    # red key-point boxes + labels (clipped to the card)
    d = ImageDraw.Draw(img); fl = font(int(base * 0.030))
    for b in meta["boxes"]:
        bx, by = left + b["x"] * sc, top + b["y"] * sc
        bw, bh = b["w"] * sc, b["h"] * sc
        pad = 8
        d.rounded_rectangle([bx - pad, by - pad, bx + bw + pad, by + bh + pad], radius=14, outline=RED, width=6)
        lw = d.textlength(b["label"], font=fl); lh = int(base * 0.030) + 18
        if bx + bw + pad + 14 + lw + 24 < left + cw - 10:  # label to the right of the box
            lx, ly = bx + bw + pad + 14, by + (bh - lh) / 2
            d.line([(bx + bw + pad, by + bh / 2), (lx, ly + lh / 2)], fill=RED, width=5)
        else:  # otherwise just above (or below) it
            lx = min(max(bx - pad, left + 8), left + cw - lw - 32)
            ly = by - pad - lh if by - pad - lh > top + 6 else by + bh + pad + 6
        d.rounded_rectangle([lx, ly, lx + lw + 24, ly + lh], radius=lh // 2, fill=RED)
        d.text((lx + 12, ly + lh // 2), b["label"], font=fl, fill="white", anchor="lm")

    os.makedirs(OUT, exist_ok=True)
    out = f"{OUT}/{key}-{meta['name']}.png"
    img.convert("RGB").save(out, optimize=True)
    assert Image.open(out).size == (W, H)
    return out


if __name__ == "__main__":
    for k in sorted(COPY):
        print(compose(k))
