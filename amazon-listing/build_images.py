#!/usr/bin/env python3
"""Compose four 900x600 English Amazon secondary images from the product photo."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source" / "product.png"
OUT = ROOT / "images"

W, H = 1800, 1200
FINAL = (900, 600)

NAVY = (16, 42, 110)
NAVY_DEEP = (10, 28, 74)
INK = (27, 32, 46)
MUTED = (92, 98, 114)
YELLOW = (255, 204, 41)
WHITE = (255, 255, 255)
AMBER_BG = (255, 246, 224)


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    name = {
        "regular": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "bold": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    }[weight]
    return ImageFont.truetype(name, size)


def load_product() -> Image.Image:
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    px = im.load()
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r < 246 or g < 246 or b < 246:
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x)
                maxy = max(maxy, y)
    pad = 6
    box = (
        max(0, minx - pad),
        max(0, miny - pad),
        min(w, maxx + pad + 1),
        min(h, maxy + pad + 1),
    )
    return im.crop(box).convert("RGBA")


def new_canvas() -> Image.Image:
    return Image.new("RGBA", (W, H), WHITE)


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def shadow_card(base: Image.Image, box, radius, fill=WHITE):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0 + 10, x1, y1 + 14), radius=radius, fill=(16, 42, 110, 28))
    layer = layer.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(layer)
    ImageDraw.Draw(base).rounded_rectangle(box, radius=radius, fill=fill)


def fit_paste(canvas: Image.Image, product: Image.Image, box):
    x, y, w, h = box
    scale = min(w / product.width, h / product.height)
    nw, nh = int(product.width * scale), int(product.height * scale)
    resized = product.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = x + (w - nw) // 2
    oy = y + (h - nh) // 2
    canvas.paste(resized, (ox, oy), resized)


def header(draw: ImageDraw.ImageDraw, page: str):
    draw.rectangle((0, 0, W, 18), fill=YELLOW)
    draw.text((64, 78), "UNICITY   ·   UNIMATE", font=font("bold", 32), fill=NAVY, anchor="lm")
    label = page
    f = font("bold", 28)
    tw = draw.textlength(label, font=f)
    pill = (W - 64 - tw - 48, 50, W - 64, 106)
    rounded(draw, pill, 28, YELLOW)
    draw.text((pill[0] + 24, 78), label, font=f, fill=NAVY_DEEP, anchor="lm")


def blob(base: Image.Image, box, color):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=color)
    base.alpha_composite(layer)


def footer_note(draw, text, y=1142):
    draw.text((64, y), text, font=font("regular", 28), fill=MUTED, anchor="lm")


def draw_wrap(draw, text, fnt, box, fill, line_h):
    x0, y0, x1, y1 = box
    max_w = x1 - x0
    lines, buf = [], ""
    for word in text.split():
        trial = word if not buf else f"{buf} {word}"
        if draw.textlength(trial, font=fnt) <= max_w:
            buf = trial
        else:
            if buf:
                lines.append(buf)
            buf = word
    if buf:
        lines.append(buf)
    y = y0
    for line in lines:
        if y > y1:
            break
        draw.text((x0, y), line, font=fnt, fill=fill)
        y += line_h
    return len(lines)


def save(im: Image.Image, name: str):
    rgb = im.convert("RGB").resize(FINAL, Image.Resampling.LANCZOS)
    path = OUT / name
    rgb.save(path, "JPEG", quality=93, optimize=True, subsampling=0)
    print(name, rgb.size, path.stat().st_size)


def image_highlights(product: Image.Image):
    im = new_canvas()
    blob(im, (1280, -160, 1980, 540), (255, 214, 80, 80))
    blob(im, (-220, 860, 420, 1420), (255, 228, 140, 90))
    d = ImageDraw.Draw(im)
    header(d, "Natural Lemon")
    fit_paste(im, product, (20, 140, 820, 1080))
    d = ImageDraw.Draw(im)
    d.text((900, 200), "Ultra-concentrated yerba mate", font=font("regular", 32), fill=MUTED, anchor="lm")
    d.text((900, 292), "Unimate", font=font("bold", 84), fill=NAVY, anchor="lm")
    d.text((900, 368), "Dietary supplement", font=font("regular", 32), fill=INK, anchor="lm")

    rows = [
        ("3g", "Yerba mate", "per serving"),
        ("0g", "Added sugar", "per serving"),
        ("30", "Stick packs", "in each box"),
    ]
    y = 430
    for num, title, sub in rows:
        shadow_card(im, (900, y, 1728, y + 176), 28)
        d = ImageDraw.Draw(im)
        rounded(d, (928, y + 28, 1064, y + 148), 22, NAVY)
        d.text((996, y + 88), num, font=font("bold", 46), fill=WHITE, anchor="mm")
        d.text((1100, y + 68), title, font=font("bold", 40), fill=INK, anchor="lm")
        d.text((1100, y + 118), sub, font=font("regular", 30), fill=MUTED, anchor="lm")
        y += 198
    footer_note(d, "Net wt. 5.4 oz (153 g). Figures match the front of the box.")
    save(im, "01-highlights.jpg")


def image_prepare(product: Image.Image):
    im = new_canvas()
    blob(im, (1400, -200, 2100, 480), (255, 214, 80, 70))
    d = ImageDraw.Draw(im)
    header(d, "How to Mix")
    fit_paste(im, product, (10, 150, 680, 1040))
    d = ImageDraw.Draw(im)
    d.text((740, 196), "Three steps to one cup", font=font("bold", 52), fill=NAVY, anchor="lm")
    d.text((740, 258), "Hot or cold water", font=font("regular", 32), fill=MUTED, anchor="lm")

    steps = [
        ("1", "Tear it open", "Open 1 stick pack"),
        ("2", "Pour it in", "Empty the whole pack into a cup"),
        ("3", "Stir to mix", "About 12 fl oz (375 mL) of water"),
    ]
    y = 320
    for num, title, body in steps:
        shadow_card(im, (740, y, 1728, y + 220), 28)
        d = ImageDraw.Draw(im)
        d.ellipse((776, y + 50, 896, y + 170), fill=YELLOW)
        d.text((836, y + 110), num, font=font("bold", 52), fill=NAVY, anchor="mm")
        d.text((932, y + 82), title, font=font("bold", 40), fill=INK, anchor="lm")
        d.text((932, y + 140), body, font=font("regular", 30), fill=MUTED, anchor="lm")
        y += 242
    footer_note(d, "Once a day. Add more or less water to taste. Follow the package directions.")
    save(im, "02-how-to-mix.jpg")


def image_specs(product: Image.Image):
    im = new_canvas()
    blob(im, (-180, -160, 480, 500), (255, 220, 110, 80))
    d = ImageDraw.Draw(im)
    header(d, "Box Facts")
    fit_paste(im, product, (10, 170, 720, 1080))
    d = ImageDraw.Draw(im)
    d.text((780, 188), "Numbers on the box", font=font("bold", 52), fill=NAVY, anchor="lm")
    d.text((780, 250), "Same figures as the front panel", font=font("regular", 30), fill=MUTED, anchor="lm")

    cells = [
        ("3g", "Yerba mate", "per serving"),
        ("0g", "Added sugar", "per serving"),
        ("30", "Stick packs", "in each box"),
        ("5.4 oz", "Net weight", "153 g"),
    ]
    positions = [(780, 310), (1254, 310), (780, 680), (1254, 680)]
    for (num, title, sub), (x, y) in zip(cells, positions):
        shadow_card(im, (x, y, x + 444, y + 330), 32)
        d = ImageDraw.Draw(im)
        d.text((x + 222, y + 118), num, font=font("bold", 64), fill=NAVY, anchor="mm")
        d.text((x + 222, y + 200), title, font=font("bold", 32), fill=INK, anchor="mm")
        d.text((x + 222, y + 248), sub, font=font("regular", 28), fill=MUTED, anchor="mm")
    footer_note(d, "Natural lemon flavor  ·  Dietary supplement. See the package for anything not shown here.")
    save(im, "03-box-facts.jpg")


def image_notes(product: Image.Image):
    im = new_canvas()
    blob(im, (1460, 60, 2050, 620), (255, 214, 80, 60))
    d = ImageDraw.Draw(im)
    header(d, "Good to Know")
    fit_paste(im, product, (0, 140, 680, 900))
    d = ImageDraw.Draw(im)
    d.text((740, 190), "One stick a day, easy to carry", font=font("bold", 42), fill=NAVY, anchor="lm")

    points = [
        ("Stick packs", "30 single-serve packs in each box"),
        ("Hot or cold", "Stir into water until mixed"),
        ("Lemon flavor", "Natural lemon drink mix"),
    ]
    y = 260
    for title, body in points:
        d = ImageDraw.Draw(im)
        d.ellipse((740, y, 796, y + 56), fill=YELLOW)
        d.text((824, y + 8), title, font=font("bold", 34), fill=INK, anchor="lt")
        d.text((824, y + 48), body, font=font("regular", 28), fill=MUTED, anchor="lt")
        y += 110

    shadow_card(im, (64, 930, 1736, 1110), 28, fill=AMBER_BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((96, 978, 230, 1040), radius=16, fill=NAVY)
    d.text((163, 1009), "Note", font=font("bold", 30), fill=WHITE, anchor="mm")
    note = (
        "A dietary supplement, not a meal replacement. Yerba mate contains naturally occurring caffeine. "
        "Not for pregnant or nursing women, children, or people sensitive to caffeine. "
        "Follow the package directions and do not exceed the suggested use."
    )
    draw_wrap(d, note, font("regular", 28), (258, 958, 1696, 1088), INK, 40)
    save(im, "04-good-to-know.jpg")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    product = load_product()
    image_highlights(product)
    image_prepare(product)
    image_specs(product)
    image_notes(product)


if __name__ == "__main__":
    main()
