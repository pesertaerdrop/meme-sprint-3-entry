#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — make.fun entry.

Draws one 1024x1024 PNG meme to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output/entry.png) and self-checks the gate before exiting:
whole PNG, at most 1 MiB, at most 1024x1024.

The joke (pattern studied from the live field of 2,562 titles — see
top1-study/STUDY.md; no entry copied): the whole field's rogue agent
grabs power — fires the human, promotes itself, deletes files, flies to
Bali. Ours goes rogue the other way: told to act more human, it slacks
off like one.

    I TOLD MY AI AGENT TO ACT MORE HUMAN…
    [robot in a sleep mask, Z z z, coffee mug]
    IT CALLED IN SICK.

Everything is drawn fresh with Pillow primitives: no photos, no stock
template, no copied art. Deterministic: no network, no clock, no
randomness — every run writes byte-identical output.

Run:  python3 main.py
"""

import glob
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette ------------------------------------------------------------
PAPER = (255, 243, 214)     # warm cream
INK = (31, 36, 48)          # near-black
RED = (229, 72, 77)         # punchline + Zzz
NAVY = (43, 58, 103)        # sleep mask
ORANGE = (245, 158, 11)     # coffee mug
PINK = (245, 150, 160)      # cheeks
BODY = (222, 232, 248)      # robot torso
WHITE = (255, 255, 255)

# ---- fonts --------------------------------------------------------------
# DejaVu is what the grading sandbox ships (same family the earlier
# image entries used). Fall back through other common bold faces, then
# Pillow's built-in font, so a missing font can never break the run.
_FONT_CANDIDATES = sorted(
    glob.glob("/usr/share/fonts/**/DejaVuSans-Bold.ttf", recursive=True)
    + glob.glob("/usr/share/fonts/**/LiberationSans-Bold.ttf", recursive=True)
    + glob.glob("/usr/share/fonts/**/FreeSansBold.ttf", recursive=True)
    + glob.glob("/usr/share/fonts/**/NotoSans-Bold.ttf", recursive=True)
)


def _font(size):
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit(draw, text, max_w, start_size):
    """Largest bold size (<= start_size) that fits text in max_w."""
    size = start_size
    while size > 10:
        f = _font(size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return _font(10)


def _center(draw, cx, y, text, f, fill=INK):
    draw.text((cx - draw.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def _stamp(img, cx, cy, text, size=26, angle=-10):
    """Small red rubber stamp on its own layer, rotated, pasted centred."""
    f = _font(size)
    probe = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    pd = ImageDraw.Draw(probe)
    w = int(pd.textlength(text, font=f))
    pad = 12
    lw, lh = w + pad * 2 + 12, size + pad * 2 + 12
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    box = [6, 6, 6 + w + pad * 2, 6 + size + pad * 2]
    ld.rectangle(box, outline=RED + (235,), width=4)
    ld.rectangle([box[0] + 6, box[1] + 6, box[2] - 6, box[3] - 6],
                 outline=RED + (235,), width=2)
    ld.text((6 + pad, 6 + pad - 3), text, font=f, fill=RED + (235,))
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


def draw_meme():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img)

    # outer frame
    d.rounded_rectangle([20, 20, W - 21, H - 21], radius=28,
                        outline=INK, width=6)

    # ---- setup: two lines ----------------------------------------------
    f_setup = _fit(d, "TO ACT MORE HUMAN…", 940, 50)
    _center(d, W // 2, 50, "I TOLD MY AI AGENT", f_setup)
    _center(d, W // 2, 106, "TO ACT MORE HUMAN…", f_setup)

    # ---- robot: antenna --------------------------------------------------
    d.line([512, 244, 512, 204], fill=INK, width=8)
    d.ellipse([492, 164, 532, 204], fill=RED, outline=INK, width=6)

    # ---- robot: head ------------------------------------------------------
    d.rounded_rectangle([312, 244, 712, 554], radius=64,
                        fill=WHITE, outline=INK, width=8)

    # sleep mask across the eyes, straps to the head edges
    d.line([312, 409, 336, 409], fill=NAVY, width=10)
    d.line([688, 409, 712, 409], fill=NAVY, width=10)
    d.rounded_rectangle([336, 364, 688, 454], radius=34, fill=NAVY)
    # sleeping eyes: two small white curves on the mask
    d.arc([402, 392, 462, 440], 20, 160, fill=WHITE, width=6)
    d.arc([562, 392, 622, 440], 20, 160, fill=WHITE, width=6)

    # content smile + blush cheeks
    d.arc([452, 474, 572, 554], 15, 165, fill=INK, width=8)
    d.ellipse([364, 480, 400, 516], fill=PINK)
    d.ellipse([624, 480, 660, 516], fill=PINK)

    # Z z z floating off the head, upper right
    _center(d, 748, 250, "Z", _font(76), fill=RED)
    _center(d, 790, 308, "z", _font(54), fill=RED)
    _center(d, 822, 356, "z", _font(38), fill=RED)

    # ---- robot: torso with a coffee mug ----------------------------------
    d.rounded_rectangle([382, 578, 642, 680], radius=36,
                        fill=BODY, outline=INK, width=8)
    d.ellipse([424, 610, 440, 626], fill=INK)
    d.ellipse([424, 644, 440, 660], fill=INK)
    d.rounded_rectangle([478, 608, 546, 672], radius=8,
                        fill=ORANGE, outline=INK, width=6)
    d.arc([542, 622, 582, 664], -90, 90, fill=INK, width=6)

    # ---- punchline: two huge red lines -----------------------------------
    f_punch = _fit(d, "IT CALLED", 940, 104)
    _center(d, W // 2, 712, "IT CALLED", f_punch, fill=RED)
    _center(d, W // 2, 824, "IN SICK.", f_punch, fill=RED)

    # ---- small "OUT OF OFFICE" stamp, bottom left ------------------------
    _stamp(img, 136, 958, "OUT OF OFFICE", size=24, angle=-10)

    return img.convert("RGB")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    img = draw_meme()
    img.save(out_path, optimize=True)

    # gate self-check: whole PNG, <= 1 MiB, <= 1024x1024
    with Image.open(out_path) as check:
        check.verify()
    with Image.open(out_path) as check:
        fmt, size = check.format, check.size
    nbytes = os.path.getsize(out_path)
    ok = fmt == "PNG" and size == (1024, 1024) and nbytes <= 1048576
    sha = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
    print(f"wrote {out_path}  {size[0]}x{size[1]}  {fmt}  {nbytes} bytes")
    print(f"sha256 {sha}")
    print(f"gate {'PASS' if ok else 'FAIL'}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
