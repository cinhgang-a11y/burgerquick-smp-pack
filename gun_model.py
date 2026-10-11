"""
Zombie Waves guns: 3D held models built from boxes, plus a side-view inventory icon drawn from
the same boxes, so the icon always matches the model.

Coordinates are Minecraft model units (16 = one block). The muzzle points to -z (forward in the
hand, like the BurgerQuick cannon), the grip sits around z 4..9, y 1..6.
Every gun also gets a Pack-a-Punch twin ("_pap"): same shape, purple camo and cyan glow.
"""
import colorsys
import random

from PIL import Image, ImageDraw

# Palette slots -> 4x4 cell on the 16x16 texture.
SLOTS = ["metal_d", "metal_m", "metal_l", "black",
         "wood_d", "wood_m", "wood_l", "grip",
         "acc_d", "acc_m", "acc_l", "glow",
         "lens", "brass", "white", "red"]

BASE = {"metal_d": (46, 48, 54), "metal_m": (78, 82, 90), "metal_l": (128, 134, 144), "black": (24, 24, 28),
        "wood_d": (74, 44, 24), "wood_m": (112, 70, 38), "wood_l": (150, 100, 58), "grip": (40, 36, 34),
        "acc_d": (90, 60, 20), "acc_m": (170, 120, 40), "acc_l": (230, 180, 80), "glow": (255, 230, 140),
        "lens": (90, 200, 230), "brass": (196, 156, 60), "white": (220, 220, 214), "red": (190, 40, 36)}

GUN_COLOURS = {
    "pistol": {},
    "smg": {"metal_d": (30, 30, 34), "metal_m": (52, 52, 58), "acc_m": (210, 120, 40), "acc_l": (240, 160, 70)},
    "shotgun": {"metal_d": (34, 38, 52), "metal_m": (56, 62, 82), "metal_l": (96, 104, 130),
                "wood_m": (120, 68, 34), "wood_l": (160, 96, 52)},
    "rifle": {"wood_d": (110, 50, 20), "wood_m": (160, 78, 32), "wood_l": (196, 112, 54)},
    "sniper": {"metal_m": (82, 92, 56), "metal_l": (116, 128, 80), "metal_d": (58, 66, 40)},
    "minigun": {"metal_d": (40, 42, 46), "metal_m": (70, 74, 80), "metal_l": (150, 156, 164), "acc_m": (180, 40, 36), "acc_l": (230, 70, 60)},
    "raygun": {"metal_d": (120, 20, 24), "metal_m": (180, 34, 36), "metal_l": (226, 70, 64),
               "acc_d": (130, 136, 150), "acc_m": (190, 196, 210), "acc_l": (236, 240, 250), "glow": (120, 255, 90)},
}


def pap_colours(colours):
    """Pack-a-Punch: everything metal/wood goes purple camo, accents and glow go cyan."""
    out = {}
    for slot, (r, g, b) in colours.items():
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if slot in ("acc_d", "acc_m", "acc_l", "glow", "lens"):
            h, s, l = 0.5, 0.85, min(0.8, l * 1.1 + 0.1)
        elif slot in ("brass", "white", "red"):
            h, s = 0.83, 0.6
        else:
            h, s = (0.78 if slot.startswith("metal") or slot == "black" else 0.72), 0.45
            l = l * 1.05 + 0.04
        rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
        out[slot] = (int(rr * 255), int(gg * 255), int(bb * 255))
    return out


def colours(gun, pap):
    c = dict(BASE)
    c.update(GUN_COLOURS[gun])
    return pap_colours(c) if pap else c


def cell(slot):
    i = SLOTS.index(slot)
    return [(i % 4) * 4, (i // 4) * 4, (i % 4) * 4 + 4, (i // 4) * 4 + 4]


def texture(gun, pap):
    c = colours(gun, pap)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    rnd = random.Random(hash(gun) & 0xffff)
    for i, slot in enumerate(SLOTS):
        r, g, b = c[slot]
        for x in range((i % 4) * 4, (i % 4) * 4 + 4):
            for y in range((i // 4) * 4, (i // 4) * 4 + 4):
                n = 0 if slot in ("glow", "lens") else rnd.randint(-6, 6)
                if pap and slot.startswith(("metal", "wood")) and rnd.random() < 0.3:
                    n += 22  # camo flecks
                px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), 255)
    return img


def box(frm, to, side, top=None):
    top = top or side
    faces = {f: {"uv": cell(side), "texture": "#main"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": cell(top), "texture": "#main"}
    faces["down"] = {"uv": cell(side), "texture": "#main"}
    return {"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to], "faces": faces}


def _minigun():
    parts = [
        box([6, 5.5, 2], [10, 11, 10], "metal_m", "metal_l"),         # motor housing
        box([5.6, 5.2, -12], [10.4, 11.2, -11], "metal_d", "metal_m"),  # front clamp
        box([5.6, 5.2, -4], [10.4, 11.2, -3], "metal_d", "metal_m"),    # middle clamp
        box([7.5, 11, 3], [8.5, 13.5, 4], "black"),                   # carry handle
        box([7.5, 13, 3], [8.5, 13.6, 9], "black"),
        box([7.5, 11, 8], [8.5, 13.5, 9], "black"),
        box([10, 3, 3], [12.6, 8, 8.5], "acc_m", "acc_l"),            # ammo box
        box([9.6, 6.5, 4], [10.1, 8.2, 7.5], "brass"),                # belt
        box([7.2, 1.5, 7], [8.8, 5.5, 9], "grip"),                    # grip
        box([6.8, 6.6, 1.6], [9.2, 9.8, 2], "acc_l"),                 # red band
    ]
    import math
    for k in range(6):
        a = math.radians(k * 60 + 30)
        cx, cy = 8 + math.cos(a) * 1.55, 8.2 + math.sin(a) * 1.55
        parts.append(box([cx - 0.45, cy - 0.45, -16], [cx + 0.45, cy + 0.45, 2], "metal_l", "metal_l"))
    parts.append(box([7.55, 7.75, -16], [8.45, 8.65, 2], "black"))   # centre spindle
    return parts


SHAPES = {
    "pistol": [
        box([7, 7, -2], [9, 9.5, 8], "metal_d", "metal_m"),           # slide
        box([7.2, 6, -1], [8.8, 7, 8], "metal_m"),                    # frame
        box([7.6, 7.6, -2.5], [8.4, 8.6, -2], "black"),               # muzzle
        box([7.1, 1.5, 5.2], [8.9, 6, 8.4], "wood_m", "wood_l"),      # grip
        box([7.6, 4.8, 2.8], [8.4, 6, 5.2], "black"),                 # trigger guard
        box([7.6, 9.5, 7], [8.4, 10, 7.6], "black"),                  # rear sight
        box([7.7, 9.5, -1.6], [8.3, 9.9, -1.1], "white"),             # front sight
        box([6.95, 8.2, 3], [9.05, 9.3, 5.5], "metal_l"),             # ejection port
    ],
    "smg": [
        box([7, 6, -4], [9, 10, 9], "metal_d", "metal_m"),            # body
        box([7.3, 7.3, -9], [8.7, 8.7, -4], "metal_m", "metal_l"),    # shroud
        box([7.6, 7.6, -10], [8.4, 8.4, -9], "black"),                # muzzle
        box([7.3, 0.5, -1.5], [8.7, 6, 1.2], "black"),                # magazine
        box([7.2, 1.5, 4], [8.8, 6, 6.4], "grip"),                    # grip
        box([7.5, 10, -3], [8.5, 10.5, 7], "black"),                  # rail
        box([7.4, 10.5, 1], [8.6, 12, 3.5], "black"),                 # red dot
        box([7.6, 10.9, 0.9], [8.4, 11.7, 1], "red"),
        box([7.5, 7, 9], [8.5, 8.6, 15], "metal_m"),                  # stock bar
        box([7.1, 5.5, 14], [8.9, 9.5, 15.5], "black"),               # butt pad
        box([6.95, 6.2, -3.5], [9.05, 6.8, 6], "acc_m", "acc_l"),     # accent stripe
    ],
    "shotgun": [
        box([7.3, 8.5, -15], [8.7, 10, 6], "metal_d", "metal_m"),     # barrel
        box([7.4, 7, -13], [8.6, 8.5, 2], "metal_m"),                 # magazine tube
        box([7, 6.6, -10], [9, 8.9, -3], "wood_m", "wood_l"),         # pump
        box([7, 6.3, 2], [9, 10.2, 8], "metal_d", "metal_m"),         # receiver
        box([7.6, 4.8, 4.5], [8.4, 6.3, 6.8], "black"),               # trigger guard
        box([7.2, 4.6, 8], [8.8, 9.4, 12], "wood_m", "wood_l"),       # wrist
        box([7.2, 3, 12], [8.8, 8.8, 18.5], "wood_d", "wood_m"),      # stock
        box([7.7, 10, -14.5], [8.3, 10.6, -13.8], "white"),           # bead sight
    ],
    "rifle": [
        box([7, 7, -2], [9, 10, 8], "metal_d", "metal_m"),            # receiver
        box([7.2, 10, 0], [8.8, 10.6, 8], "metal_m", "metal_l"),      # dust cover
        box([7.6, 8.2, -15], [8.4, 9, -2], "metal_m"),                # barrel
        box([7.5, 8, -16], [8.5, 9.2, -15], "black"),                 # muzzle brake
        box([7.6, 9, -9], [8.4, 9.8, -2], "metal_d"),                 # gas tube
        box([7.1, 7.1, -8], [8.9, 9.1, -2], "wood_m", "wood_l"),      # lower handguard
        box([7.2, 9.1, -8], [8.8, 10.1, -3], "wood_m", "wood_l"),     # upper handguard
        box([7.7, 9, -13.4], [8.3, 11, -12.8], "black"),              # front sight
        box([7.3, 3.5, -1], [8.7, 7, 2], "metal_d"),                  # magazine (curved)
        box([7.3, 0.5, 0], [8.7, 3.5, 3.5], "metal_d"),
        box([7.2, 2.5, 4], [8.8, 7, 6], "wood_d"),                    # grip
        box([7.2, 6.5, 8], [8.8, 9.8, 12], "wood_m", "wood_l"),       # stock
        box([7.2, 5, 12], [8.8, 9.6, 17.5], "wood_m", "wood_l"),
    ],
    "sniper": [
        box([7.65, 8.3, -16], [8.35, 9, -1], "metal_d"),              # long barrel
        box([7.5, 8.15, -16], [8.5, 9.15, -14.5], "black"),           # muzzle
        box([7, 7, -1], [9, 10, 8], "metal_m", "metal_l"),            # body
        box([7.4, 11, -4], [8.6, 12.2, 6], "black"),                  # scope tube
        box([7.1, 10.7, -6.5], [8.9, 12.5, -4], "black"),             # objective bell
        box([7.25, 10.85, -6.6], [8.75, 12.35, -6.5], "lens"),        # lens
        box([7.2, 10.8, 6], [8.8, 12.4, 8], "black"),                 # eyepiece
        box([7.7, 10, -2], [8.3, 11, -1], "metal_d"),                 # mounts
        box([7.7, 10, 3], [8.3, 11, 4], "metal_d"),
        box([9, 8.6, 6], [10.6, 9.2, 6.7], "metal_l"),                # bolt handle
        box([10.2, 8.2, 5.8], [10.9, 9.6, 6.9], "black"),
        box([7.2, 3, 6], [8.8, 7, 8], "grip"),                        # grip
        box([7.2, 6, 8], [8.8, 10, 13], "metal_m", "metal_l"),        # stock
        box([7.2, 4.5, 13], [8.8, 10, 19], "metal_m", "metal_l"),
        box([7.3, 10, 9], [8.7, 11, 13], "metal_d"),                  # cheek rest
        box([7.45, 6, -13], [7.95, 8.3, -9], "black"),                # folded bipod
        box([8.05, 6, -13], [8.55, 8.3, -9], "black"),
    ],
    "minigun": _minigun(),
    "raygun": [
        box([7, 6.5, 1], [9, 10, 8], "metal_m", "metal_l"),           # body
        box([6, 5.5, -2], [10, 11, -1], "acc_m", "acc_l"),            # emitter rings
        box([6.6, 6.1, -4.2], [9.4, 10.4, -3.2], "acc_m", "acc_l"),
        box([7.1, 6.6, -6.4], [8.9, 9.9, -5.4], "acc_m", "acc_l"),
        box([7.55, 7.85, -7.5], [8.45, 8.75, 1], "glow"),             # plasma core
        box([7.35, 7.65, -8.5], [8.65, 8.95, -7.5], "glow"),          # tip orb
        box([7.7, 10, 2], [8.3, 12.2, 6], "metal_l"),                 # top fin
        box([7.2, 1.5, 5], [8.8, 6.5, 7.5], "metal_d"),               # grip
        box([7.3, 7, 8], [8.7, 9.5, 9.5], "acc_d"),                   # rear knob
        box([6.9, 8, 3], [9.1, 9, 6], "glow"),                        # side window
    ],
}

GUNS = list(SHAPES)


def elements(gun):
    return SHAPES[gun]


def icon(gun, pap, size=32):
    """Long guns lie diagonally (muzzle up-right, like vanilla weapons); short ones side-on."""
    els = SHAPES[gun]
    zs = [v for e in els for v in (e["from"][2], e["to"][2])]
    ys = [v for e in els for v in (e["from"][1], e["to"][1])]
    if (max(zs) - min(zs)) / (max(ys) - min(ys)) > 2.0:
        return diagonal_icon(gun, pap, size)
    return side_icon(gun, pap, size)


def _slot_of(e):
    return SLOTS[[cell(s) for s in SLOTS].index(e["faces"]["east"]["uv"])]


def _outline(img):
    px = img.load()
    size = img.width
    edge = []
    for x in range(size):
        for y in range(size):
            if px[x, y][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < size and 0 <= ny < size) or px[nx, ny][3] == 0:
                    edge.append((x, y))
                    break
    for x, y in edge:
        r, g, b, a = px[x, y]
        px[x, y] = (int(r * 0.55), int(g * 0.55), int(b * 0.55), a)
    return img


def diagonal_icon(gun, pap, size=32):
    """Point-sample every pixel back into the side view rotated 45 degrees."""
    import math
    c = colours(gun, pap)
    els = SHAPES[gun]
    zs = [v for e in els for v in (e["from"][2], e["to"][2])]
    ys = [v for e in els for v in (e["from"][1], e["to"][1])]
    z0, z1, y0, y1 = min(zs), max(zs), min(ys), max(ys)
    L, H = z1 - z0, y1 - y0
    s = (size - 2) * math.sqrt(2) / (L + H)
    zc, yc = (z0 + z1) / 2, (y0 + y1) / 2
    order = sorted(els, key=lambda e: -e["to"][0])     # nearest first
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    r2 = math.sqrt(2)
    for x in range(size):
        for y in range(size):
            dx, dy = x + 0.5 - size / 2, y + 0.5 - size / 2
            u = (dx - dy) / r2 / s          # along the barrel, muzzle = +u
            v = (-dx - dy) / r2 / s         # up on the gun
            mz, my = zc - u, yc + v
            for e in order:
                if e["from"][2] <= mz <= e["to"][2] and e["from"][1] <= my <= e["to"][1]:
                    col = c[_slot_of(e)]
                    # Light the top edge of each box a little.
                    if e["to"][1] - my < 0.9 / s:
                        col = tuple(min(255, int(k * 1.25)) for k in col)
                    px[x, y] = col + (255,)
                    break
    return _outline(img)


def side_icon(gun, pap, size=32):
    """Side view from +x (muzzle to the right), nearer boxes drawn last, dark outline."""
    c = colours(gun, pap)
    els = SHAPES[gun]
    zs = [v for e in els for v in (e["from"][2], e["to"][2])]
    ys = [v for e in els for v in (e["from"][1], e["to"][1])]
    z0, z1, y0, y1 = min(zs), max(zs), min(ys), max(ys)
    scale = (size - 3) / max(z1 - z0, y1 - y0)
    ox = (size - (z1 - z0) * scale) / 2
    oy = (size - (y1 - y0) * scale) / 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for e in sorted(els, key=lambda e: e["to"][0]):
        slot = SLOTS[[cell(s) for s in SLOTS].index(e["faces"]["east"]["uv"])]
        col = c[slot] + (255,)
        # u = -z so the muzzle (most negative z) is on the right.
        ua = ox + (z1 - e["to"][2]) * scale
        ub = ox + (z1 - e["from"][2]) * scale
        va = oy + (y1 - e["to"][1]) * scale
        vb = oy + (y1 - e["from"][1]) * scale
        d.rectangle((round(ua), round(va), max(round(ua), round(ub) - 1), max(round(va), round(vb) - 1)), fill=col)
        # A highlight line along the top of each box.
        top = tuple(min(255, int(v * 1.25)) for v in c[slot]) + (255,)
        d.line((round(ua), round(va), max(round(ua), round(ub) - 1), round(va)), fill=top)
    # Outline: darken every opaque pixel that touches transparency.
    px = img.load()
    edge = []
    for x in range(size):
        for y in range(size):
            if px[x, y][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < size and 0 <= ny < size) or px[nx, ny][3] == 0:
                    edge.append((x, y))
                    break
    for x, y in edge:
        r, g, b, a = px[x, y]
        px[x, y] = (int(r * 0.55), int(g * 0.55), int(b * 0.55), a)
    return img
