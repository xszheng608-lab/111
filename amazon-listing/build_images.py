#!/usr/bin/env python3
"""Compose four 900×600 Amazon secondary images from the product photo."""

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
YELLOW_DEEP = (242, 176, 18)
CREAM = (255, 250, 240)
WHITE = (255, 255, 255)
LINE = (232, 226, 210)
AMBER_BG = (255, 246, 224)

FONT_DIR = "/usr/share/fonts/opentype/noto"


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    name = {
        "regular": "NotoSansCJK-Regular.ttc",
        "medium": "NotoSansCJK-Medium.ttc",
        "bold": "NotoSansCJK-Bold.ttc",
    }[weight]
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size, index=2)


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
    draw.text((64, 78), "UNICITY  ·  UNIMATE", font=font("bold", 34), fill=NAVY, anchor="lm")
    label = page
    f = font("medium", 30)
    tw = draw.textlength(label, font=f)
    pill = (W - 64 - tw - 44, 52, W - 64, 104)
    rounded(draw, pill, 26, YELLOW)
    draw.text((pill[0] + 22, 78), label, font=f, fill=NAVY_DEEP, anchor="lm")


def blob(base: Image.Image, box, color):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=color)
    base.alpha_composite(layer)


def footer_note(draw, text, y=1142):
    draw.text((64, y), text, font=font("regular", 28), fill=MUTED, anchor="lm")


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
    header(d, "天然柠檬味")
    fit_paste(im, product, (20, 140, 860, 1080))
    d = ImageDraw.Draw(im)
    d.text((960, 210), "超浓缩马黛茶冲饮粉", font=font("medium", 36), fill=MUTED, anchor="lm")
    d.text((960, 300), "Unimate", font=font("bold", 92), fill=NAVY, anchor="lm")
    d.text((960, 380), "膳食补充剂", font=font("regular", 34), fill=INK, anchor="lm")

    rows = [
        ("3g", "每份马黛茶"),
        ("0g", "每份添加糖"),
        ("30", "独立条装"),
    ]
    y = 450
    for num, label in rows:
        shadow_card(im, (960, y, 1720, y + 168), 28)
        d = ImageDraw.Draw(im)
        rounded(d, (992, y + 24, 1112, y + 144), 22, NAVY)
        d.text((1052, y + 84), num, font=font("bold", 48), fill=WHITE, anchor="mm")
        d.text((1156, y + 84), label, font=font("bold", 44), fill=INK, anchor="lm")
        y += 192
    footer_note(d, "净含量 153 克（5.4 盎司）。数字与包装正面标示一致。")
    save(im, "01-核心卖点.jpg")


def image_prepare(product: Image.Image):
    im = new_canvas()
    blob(im, (1400, -200, 2100, 480), (255, 214, 80, 70))
    d = ImageDraw.Draw(im)
    header(d, "冲调方法")
    fit_paste(im, product, (10, 150, 720, 1040))
    d = ImageDraw.Draw(im)
    d.text((780, 200), "三步冲好一杯", font=font("bold", 64), fill=NAVY, anchor="lm")
    d.text((780, 270), "冷水或热水都可以", font=font("regular", 34), fill=MUTED, anchor="lm")

    steps = [
        ("1", "撕开一条", "取 1 条，沿封口撕开"),
        ("2", "倒入杯中", "整条粉末一次倒入"),
        ("3", "加水搅匀", "约 375 毫升热水或冷水"),
    ]
    y = 340
    for num, title, body in steps:
        shadow_card(im, (780, y, 1720, y + 210), 28)
        d = ImageDraw.Draw(im)
        d.ellipse((820, y + 45, 940, y + 165), fill=YELLOW)
        d.text((880, y + 105), num, font=font("bold", 54), fill=NAVY, anchor="mm")
        d.text((980, y + 78), title, font=font("bold", 42), fill=INK, anchor="lm")
        d.text((980, y + 138), body, font=font("regular", 32), fill=MUTED, anchor="lm")
        y += 234
    footer_note(d, "建议每日 1 条。水量可按口味增减，请以包装上的饮用说明为准。")
    save(im, "02-冲调方法.jpg")


def image_specs(product: Image.Image):
    im = new_canvas()
    blob(im, (-180, -160, 480, 500), (255, 220, 110, 80))
    d = ImageDraw.Draw(im)
    header(d, "包装规格")
    fit_paste(im, product, (20, 180, 760, 1080))
    d = ImageDraw.Draw(im)
    d.text((820, 190), "看包装上的数字", font=font("bold", 58), fill=NAVY, anchor="lm")
    d.text((820, 258), "与盒子正面的标示一致", font=font("regular", 32), fill=MUTED, anchor="lm")

    cells = [
        ("3g", "每份马黛茶"),
        ("0g", "每份添加糖"),
        ("30", "独立条装"),
        ("153g", "净含量"),
    ]
    positions = [(820, 320), (1260, 320), (820, 680), (1260, 680)]
    for (num, label), (x, y) in zip(cells, positions):
        shadow_card(im, (x, y, x + 410, y + 320), 32)
        d = ImageDraw.Draw(im)
        d.text((x + 205, y + 125), num, font=font("bold", 78), fill=NAVY, anchor="mm")
        d.text((x + 205, y + 220), label, font=font("medium", 34), fill=INK, anchor="mm")
    footer_note(d, "5.4 盎司  ·  天然柠檬味  ·  膳食补充剂。未标出的营养数据请以实物包装为准。")
    save(im, "03-包装规格.jpg")


def image_notes(product: Image.Image):
    im = new_canvas()
    blob(im, (1460, 80, 2050, 640), (255, 214, 80, 60))
    d = ImageDraw.Draw(im)
    header(d, "饮用提示")
    fit_paste(im, product, (0, 130, 700, 900))
    d = ImageDraw.Draw(im)
    d.text((760, 190), "每天一条，方便携带", font=font("bold", 52), fill=NAVY, anchor="lm")

    points = [
        ("独立包装", "一盒 30 条，按次取用"),
        ("冷热皆宜", "热水或冷水搅匀即可"),
        ("柠檬口味", "天然柠檬味冲饮粉"),
    ]
    y = 250
    for title, body in points:
        d = ImageDraw.Draw(im)
        d.ellipse((760, y + 4, 812, y + 56), fill=YELLOW)
        d.text((836, y + 30), title, font=font("bold", 36), fill=INK, anchor="lm")
        d.text((1060, y + 30), body, font=font("regular", 32), fill=MUTED, anchor="lm")
        y += 88

    shadow_card(im, (64, 930, 1736, 1105), 28, fill=AMBER_BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((96, 962, 248, 1012), radius=16, fill=NAVY)
    d.text((172, 987), "请注意", font=font("bold", 30), fill=WHITE, anchor="mm")
    note = "本品是膳食补充剂，不能代替正餐。马黛茶含天然咖啡因。孕妇、哺乳期妇女、儿童及对咖啡因敏感者不建议使用。请按包装说明冲调，不要超量饮用。"
    draw_wrap(d, note, font("regular", 30), (272, 968, 1690, 1084), INK, 44)
    save(im, "04-饮用提示.jpg")


def draw_wrap(draw, text, fnt, box, fill, line_h):
    x0, y0, x1, y1 = box
    max_w = x1 - x0
    lines, buf = [], ""
    for ch in text:
        trial = buf + ch
        if draw.textlength(trial, font=fnt) <= max_w:
            buf = trial
        else:
            lines.append(buf)
            buf = ch
    if buf:
        lines.append(buf)
    y = y0
    for line in lines:
        if y > y1:
            break
        draw.text((x0, y), line, font=fnt, fill=fill)
        y += line_h


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    product = load_product()
    image_highlights(product)
    image_prepare(product)
    image_specs(product)
    image_notes(product)


if __name__ == "__main__":
    main()
