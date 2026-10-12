"""Burger Royale item icons (32x32 pixel art): heals, shields, grenade, trap, launch pad, ammo and
the build-mode tools. Used by generate.py (Java pack) and bedrock_royale.py (Bedrock pack).
`python royale_items.py` writes a preview sheet: royale_items_preview.png
"""
import math
import os

from PIL import Image, ImageDraw

S = 32
OUTLINE = (24, 20, 28, 255)


def _img():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def _outline(img):
    """Dark 1px outline around everything (like vanilla item sprites)."""
    px = img.load()
    out = img.copy()
    po = out.load()
    for x in range(S):
        for y in range(S):
            if px[x, y][3] > 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < S and 0 <= ny < S and px[nx, ny][3] > 0 and px[nx, ny][:3] != OUTLINE[:3]:
                    po[x, y] = OUTLINE
                    break
    return out


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)


def _bottle(body, liquid, cap, neck_w=4, body_box=(8, 12, 23, 28), round_body=True, label=None):
    im = _img()
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = body_box
    cx = (x0 + x1) // 2
    # neck + cap
    d.rectangle([cx - neck_w // 2, y0 - 6, cx + neck_w // 2 - 1, y0], fill=_shade(body, 0.9))
    d.rectangle([cx - neck_w // 2 - 1, y0 - 9, cx + neck_w // 2, y0 - 6], fill=cap)
    # body
    if round_body:
        d.ellipse([x0, y0, x1, y1], fill=body)
        d.ellipse([x0 + 2, y0 + (y1 - y0) // 3, x1 - 2, y1 - 2], fill=liquid)
    else:
        d.rounded_rectangle([x0, y0, x1, y1], radius=3, fill=body)
        d.rounded_rectangle([x0 + 2, y0 + (y1 - y0) // 3, x1 - 2, y1 - 2], radius=2, fill=liquid)
    # shine
    d.line([x0 + 3, y0 + 3, x0 + 3, y0 + 7], fill=(255, 255, 255, 200))
    if label:
        label(d)
    return _outline(im)


def bandages():
    im = _img()
    d = ImageDraw.Draw(im)
    d.ellipse([4, 9, 27, 26], fill=(236, 230, 214, 255))
    d.ellipse([10, 13, 21, 22], fill=(206, 196, 176, 255))
    d.ellipse([13, 15, 18, 20], fill=(150, 140, 124, 255))
    d.rectangle([20, 20, 29, 25], fill=(236, 230, 214, 255))       # loose end
    d.rectangle([12, 4, 19, 7], fill=(210, 40, 40, 255))           # red cross tag
    d.rectangle([14, 2, 17, 9], fill=(210, 40, 40, 255))
    return _outline(im)


def medkit():
    im = _img()
    d = ImageDraw.Draw(im)
    d.rectangle([11, 4, 20, 8], fill=(90, 90, 96, 255))            # handle
    d.rectangle([13, 6, 18, 8], fill=(0, 0, 0, 0))
    d.rounded_rectangle([3, 8, 28, 28], radius=3, fill=(232, 232, 236, 255))
    d.rectangle([3, 8, 28, 11], fill=(200, 200, 206, 255))
    d.rectangle([13, 13, 18, 26], fill=(214, 36, 36, 255))         # cross
    d.rectangle([9, 17, 22, 22], fill=(214, 36, 36, 255))
    return _outline(im)


def small_shield():
    return _bottle((150, 200, 255, 255), (60, 140, 255, 255), (230, 230, 240, 255), neck_w=4, body_box=(10, 14, 21, 28))


def shield_potion():
    return _bottle((170, 210, 255, 255), (36, 90, 235, 255), (240, 240, 250, 255), neck_w=6, body_box=(5, 11, 26, 29), round_body=False)


def slurp():
    def swirl(d):
        for i in range(10):
            a = i * 0.7
            d.point([16 + int(math.cos(a) * i * 0.5), 21 + int(math.sin(a) * i * 0.5)], fill=(120, 240, 220, 255))
    return _bottle((200, 170, 240, 255), (150, 70, 220, 255), (90, 220, 200, 255), neck_w=6, body_box=(6, 11, 25, 29), label=swirl)


def chug_jug():
    im = _img()
    d = ImageDraw.Draw(im)
    gold, dark = (240, 190, 50, 255), (170, 120, 20, 255)
    d.rectangle([12, 3, 19, 7], fill=dark)                         # cork
    d.ellipse([4, 7, 27, 30], fill=gold)                           # jug
    d.ellipse([8, 13, 23, 27], fill=(70, 150, 255, 255))           # blue liquid window
    d.ellipse([11, 15, 17, 20], fill=(170, 220, 255, 255))
    d.arc([22, 9, 31, 21], 270, 90, fill=dark, width=2)            # handle
    d.line([6, 12, 8, 10], fill=(255, 240, 180, 255))
    return _outline(im)


def grenade():
    im = _img()
    d = ImageDraw.Draw(im)
    d.ellipse([7, 9, 25, 29], fill=(80, 120, 50, 255))
    for y in range(12, 28, 4):                                     # pineapple grid
        d.line([8, y, 24, y], fill=(56, 86, 34, 255))
    for x in range(11, 24, 4):
        d.line([x, 10, x, 28], fill=(56, 86, 34, 255))
    d.rectangle([12, 5, 19, 9], fill=(150, 150, 156, 255))          # fuse cap
    d.rectangle([19, 4, 26, 6], fill=(170, 170, 176, 255))          # lever
    d.ellipse([22, 1, 28, 7], outline=(200, 200, 206, 255))         # pin ring
    d.line([10, 13, 12, 11], fill=(150, 190, 110, 255))
    return _outline(im)


def trap():
    im = _img()
    d = ImageDraw.Draw(im)
    d.polygon([(2, 24), (16, 18), (30, 24), (16, 30)], fill=(120, 124, 132, 255))   # plate (isometric)
    d.polygon([(2, 24), (16, 30), (16, 31), (2, 25)], fill=(80, 82, 90, 255))
    for (x, y) in ((9, 22), (16, 19), (23, 22), (16, 25), (9, 26), (23, 26)):
        d.polygon([(x - 2, y + 1), (x + 2, y + 1), (x, y - 9)], fill=(214, 214, 220, 255))
        d.line([x, y - 9, x + 1, y], fill=(150, 150, 160, 255))
    return _outline(im)


def launch_pad():
    im = _img()
    d = ImageDraw.Draw(im)
    d.polygon([(1, 22), (16, 15), (31, 22), (16, 29)], fill=(90, 200, 90, 255))
    d.polygon([(1, 22), (16, 29), (16, 31), (1, 24)], fill=(50, 140, 50, 255))
    d.polygon([(31, 22), (16, 29), (16, 31), (31, 24)], fill=(40, 110, 40, 255))
    d.polygon([(16, 2), (24, 11), (19, 11), (19, 21), (13, 21), (13, 11), (8, 11)], fill=(250, 250, 120, 255))   # up arrow
    return _outline(im)


def _bullets(colour, tip, n, w, h):
    im = _img()
    d = ImageDraw.Draw(im)
    gap = (S - n * w) // (n + 1)
    for i in range(n):
        x = gap + i * (w + gap)
        y = S - 3 - h
        d.rectangle([x, y + w // 2, x + w - 1, S - 4], fill=colour)
        d.ellipse([x, y, x + w - 1, y + w], fill=tip)
        d.line([x + 1, y + w, x + 1, S - 5], fill=_shade(colour, 1.3))
        d.rectangle([x, S - 6, x + w - 1, S - 4], fill=_shade(colour, 0.7))
    return _outline(im)


def ammo_light():
    return _bullets((170, 176, 186, 255), (200, 206, 214, 255), 4, 4, 12)


def ammo_medium():
    return _bullets((200, 160, 60, 255), (184, 120, 70, 255), 3, 5, 18)


def ammo_heavy():
    return _bullets((190, 100, 50, 255), (90, 90, 96, 255), 2, 7, 24)


def ammo_shells():
    im = _img()
    d = ImageDraw.Draw(im)
    for i, x in enumerate((5, 13, 21)):
        d.rectangle([x, 8, x + 6, 22], fill=(200, 40, 40, 255))
        d.rectangle([x, 22, x + 6, 28], fill=(220, 180, 60, 255))
        d.line([x + 1, 9, x + 1, 21], fill=(240, 90, 90, 255))
    return _outline(im)


def ammo_rockets():
    im = _img()
    d = ImageDraw.Draw(im)
    d.polygon([(4, 27), (22, 9), (26, 13), (8, 31)], fill=(110, 130, 80, 255))      # body
    d.polygon([(22, 9), (29, 2), (26, 13)], fill=(220, 60, 40, 255))               # nose
    d.polygon([(4, 27), (1, 23), (6, 25)], fill=(80, 90, 60, 255))
    d.polygon([(8, 31), (4, 31), (6, 28)], fill=(80, 90, 60, 255))
    d.line([6, 26, 22, 10], fill=(160, 180, 120, 255))
    return _outline(im)


def _holo(draw_fn):
    """Fortnite-style blue build icons."""
    im = _img()
    d = ImageDraw.Draw(im)
    draw_fn(d, (90, 200, 255, 255), (40, 120, 220, 255), (200, 240, 255, 255))
    return _outline(im)


def build_wall():
    return _holo(lambda d, a, b, c: (d.rectangle([5, 5, 26, 26], fill=b), d.rectangle([7, 7, 24, 24], fill=a),
                                     d.line([7, 16, 24, 16], fill=c), d.line([16, 7, 16, 24], fill=c)))


def build_floor():
    return _holo(lambda d, a, b, c: (d.polygon([(2, 18), (16, 10), (30, 18), (16, 26)], fill=b),
                                     d.polygon([(5, 18), (16, 12), (27, 18), (16, 24)], fill=a), d.line([10, 15, 22, 21], fill=c)))


def build_ramp():
    return _holo(lambda d, a, b, c: (d.polygon([(3, 27), (28, 27), (28, 5)], fill=b), d.polygon([(7, 25), (26, 25), (26, 9)], fill=a),
                                     [d.line([9 + i * 4, 25, 9 + i * 4, 25 - int(i * 3.2)], fill=c) for i in range(5)]))


def build_cone():
    return _holo(lambda d, a, b, c: (d.polygon([(2, 26), (16, 4), (30, 26)], fill=b), d.polygon([(6, 24), (16, 8), (26, 24)], fill=a),
                                     d.line([16, 8, 16, 24], fill=c)))


def build_edit():
    def f(d, a, b, c):
        for i in range(3):
            for j in range(3):
                col = a if (i, j) != (1, 1) else (0, 0, 0, 0)
                d.rectangle([5 + i * 8, 5 + j * 8, 11 + i * 8, 11 + j * 8], fill=col, outline=b)
        d.line([22, 22, 30, 30], fill=c, width=2)
    return _holo(f)


def build_back():
    im = _img()
    d = ImageDraw.Draw(im)
    d.polygon([(3, 16), (14, 6), (14, 12), (28, 12), (28, 20), (14, 20), (14, 26)], fill=(250, 200, 60, 255))
    return _outline(im)


# icon name -> drawing function
ICONS = {
    "fn_bandages": bandages, "fn_medkit": medkit, "fn_small_shield": small_shield, "fn_shield_potion": shield_potion,
    "fn_slurp": slurp, "fn_chug_jug": chug_jug, "fn_grenade": grenade, "fn_trap": trap, "fn_launch_pad": launch_pad,
    "fn_ammo_light": ammo_light, "fn_ammo_medium": ammo_medium, "fn_ammo_heavy": ammo_heavy, "fn_ammo_shells": ammo_shells,
    "fn_ammo_rockets": ammo_rockets,
    "fn_build_wall": build_wall, "fn_build_floor": build_floor, "fn_build_ramp": build_ramp, "fn_build_cone": build_cone,
    "fn_build_edit": build_edit, "fn_build_back": build_back,
}


def write_java(pack_assets):
    """Writes textures, models and item definitions into assets/burgerquick."""
    import json
    for name, fn in ICONS.items():
        tex = os.path.join(pack_assets, "textures", "item", name + ".png")
        os.makedirs(os.path.dirname(tex), exist_ok=True)
        fn().save(tex)
        for sub, obj in (("models/item", {"parent": "minecraft:item/generated", "textures": {"layer0": "burgerquick:item/" + name}}),
                         ("items", {"model": {"type": "minecraft:model", "model": "burgerquick:item/" + name}})):
            path = os.path.join(pack_assets, *sub.split("/"), name + ".json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(obj, f, indent=2)


if __name__ == "__main__":
    cols = 7
    rows = (len(ICONS) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * 36, rows * 36), (60, 60, 70, 255))
    for i, fn in enumerate(ICONS.values()):
        sheet.paste(fn(), ((i % cols) * 36 + 2, (i // cols) * 36 + 2), fn())
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "royale_items_preview.png"))
    print(len(ICONS), "icons")
