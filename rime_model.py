"""The Rimevault's own art: an iced stone brick block texture, and the Rime Golem.

The block texture overrides `mud_bricks`, which never generates naturally and which nobody on the
server crafts - so the frozen brick can exist without changing any block players already use.
"""
import random

from PIL import Image, ImageDraw

# 32x32 palette of 4x4 cells, same scheme as the tyrant sheet.
(ICE_DEEP, ICE_MID, ICE_PALE, ICE_GLOW, STONE_DARK, STONE_MID, STONE_PALE, FROST,
 METAL_DARK, METAL_MID, RUNE, EYE) = range(12)
COLOURS = {
    ICE_DEEP: (36, 78, 120),
    ICE_MID: (86, 150, 196),
    ICE_PALE: (168, 214, 240),
    ICE_GLOW: (198, 240, 255),
    STONE_DARK: (52, 58, 66),
    STONE_MID: (92, 100, 112),
    STONE_PALE: (146, 156, 170),
    FROST: (226, 244, 255),
    METAL_DARK: (58, 70, 84),
    METAL_MID: (110, 126, 146),
    RUNE: (120, 220, 255),
    EYE: (150, 245, 255),
}
GLOWING = {ICE_GLOW, RUNE, EYE, FROST}


def texture():
    """The palette sheet the golem models sample from."""
    img = Image.new("RGBA", (32, 32))
    px = img.load()
    rnd = random.Random(5)
    for cell, (r, g, b) in COLOURS.items():
        cx, cy = (cell % 8) * 4, (cell // 8) * 4
        for x in range(cx, cx + 4):
            for y in range(cy, cy + 4):
                n = 0 if cell in GLOWING else rnd.randint(-10, 10)
                # ice cells get a facet shine on the top-left
                if cell in (ICE_DEEP, ICE_MID, ICE_PALE) and (x - cx) + (y - cy) < 2:
                    n += 22
                px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), 255)
    return img


def iced_stone_bricks(jar=None):
    """The vanilla cracked stone brick, frozen in from the edges.

    The middle stays bare stone and the ice creeps in all round the border, heaviest in the corners,
    so a wall of these reads as stone that the cold has got into rather than a block of ice.
    """
    src = None
    if jar is not None:
        try:
            with jar.open("assets/minecraft/textures/block/cracked_stone_bricks.png") as f:
                src = Image.open(f).convert("RGBA").copy()
        except KeyError:
            src = None
    if src is None:
        src = _fallback_bricks()
    img = src.resize((16, 16)).convert("RGBA")
    px = img.load()
    rnd = random.Random(23)

    ICE = (206, 236, 252)
    DEEP = (140, 190, 224)
    REACH = 3.2                                         # how far in from the border ice creeps
    for y in range(16):
        for x in range(16):
            near = min(x, y, 15 - x, 15 - y)            # 0 on the border
            if near > REACH + 1:
                continue                                 # the middle of the face stays bare stone
            band = max(0.0, 1.0 - near / REACH)
            frost = band ** 1.3
            # Corners freeze hardest: both axes are near an edge at once.
            corner = max(0.0, 1 - min(x, 15 - x) / REACH) * max(0.0, 1 - min(y, 15 - y) / REACH)
            frost = min(1.0, frost + corner * 0.55)
            r, g, b, a = px[x, y]
            # Ice settles into the cracks and mortar, but only where it has already reached.
            if r + g + b < 250:
                frost = min(1.0, frost * 1.45)
            frost *= 0.6 + rnd.random() * 0.4           # ragged, not a clean ring
            if frost <= 0.05:
                continue
            tint = DEEP if frost < 0.5 else ICE
            px[x, y] = (int(r * (1 - frost) + tint[0] * frost),
                        int(g * (1 - frost) + tint[1] * frost),
                        int(b * (1 - frost) + tint[2] * frost), 255)
    # Crystals growing out of the corners, and a few flecks on the frozen band.
    for cx, cy in ((0, 0), (15, 0), (0, 15), (15, 15)):
        for i in range(3):
            dx = (1 if cx == 0 else -1) * rnd.randint(0, 2)
            dy = (1 if cy == 0 else -1) * rnd.randint(0, 2)
            x, y = cx + dx, cy + dy
            if 0 <= x < 16 and 0 <= y < 16:
                px[x, y] = (238, 250, 255, 255)
    for _ in range(10):
        x, y = rnd.randrange(16), rnd.randrange(16)
        if min(x, y, 15 - x, 15 - y) <= 2:
            px[x, y] = (228, 246, 255, 255)
    return img


def _fallback_bricks():
    """Used if the client jar is not to hand: a plain stone brick course."""
    img = Image.new("RGBA", (16, 16), (122, 122, 122, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for y in range(16):
        for x in range(16):
            shade = rnd.randint(-10, 10)
            img.putpixel((x, y), (122 + shade, 122 + shade, 122 + shade, 255))
    for row in range(4):
        y0 = row * 4
        d.line((0, y0, 15, y0), fill=(92, 92, 92))
        offset = 0 if row % 2 == 0 else 4
        for seam in range(2):
            x = (offset + seam * 8) % 16
            d.line((x, y0, x, y0 + 3), fill=(92, 92, 92))
    return img


def uv(cell):
    col, row = cell % 8, cell // 8
    return [col * 2, row * 2, col * 2 + 2, row * 2 + 2]


def box(frm, to, side, top=None, bottom=None):
    faces = {f: {"uv": uv(side), "texture": "#main"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": uv(top if top is not None else side), "texture": "#main"}
    faces["down"] = {"uv": uv(bottom if bottom is not None else side), "texture": "#main"}
    return {"from": frm, "to": to, "faces": faces}


def golem_torso():
    """Hinged at the hips; shoulders 14 above. A slab of ice bound in frozen iron."""
    els = [
        box([3, 8, 4], [13, 22, 12], ICE_MID, ICE_PALE, ICE_DEEP),              # ice core
        box([2.4, 9, 3.4], [13.6, 20, 12.6], STONE_MID, STONE_PALE, STONE_DARK),  # stone shell
        box([2, 20, 3], [14, 23.5, 13], METAL_MID, METAL_DARK),                 # shoulder band
        box([4.5, 11, 3], [11.5, 18, 3.8], RUNE),                               # rune down the chest
        box([5, 23.5, 5], [11, 29, 11], ICE_DEEP, ICE_MID),                     # head
        box([4.6, 24, 4.4], [11.4, 28, 5.4], STONE_PALE, STONE_MID, STONE_DARK),  # face plate
        box([5.6, 25.4, 4], [7, 26.8, 4.6], EYE),                               # eyes
        box([9, 25.4, 4], [10.4, 26.8, 4.6], EYE),
        box([6, 29, 6], [10, 31, 10], ICE_PALE, ICE_GLOW),                      # crown of ice
    ]
    for side in (-1, 1):                                                        # shoulder spikes
        els.append(box([min(8 + side * 5, 8 + side * 7), 21, 6],
                       [max(8 + side * 5, 8 + side * 7), 24, 10], ICE_PALE, ICE_GLOW))
    return els


def golem_leg():
    return [
        box([6, 6, 6], [10, 9.5, 10], METAL_MID, METAL_DARK),                   # hip
        box([6.2, 0, 6.2], [9.8, 7, 9.8], ICE_MID, ICE_PALE),                   # thigh
        box([5.8, -2.5, 5.8], [10.2, 0.5, 10.2], STONE_MID, STONE_PALE),        # knee
        box([6.4, -7.5, 6.4], [9.6, -2, 9.6], ICE_DEEP, ICE_MID),               # shin
        box([5.4, -9.5, 4.6], [10.6, -7, 11], STONE_PALE, STONE_MID),          # foot
    ]


def golem_arm():
    return [
        box([5.8, 5.8, 5.8], [10.2, 10.2, 10.2], METAL_MID, METAL_DARK),        # shoulder
        box([6.2, -2, 6.2], [9.8, 7, 9.8], ICE_MID, ICE_PALE),                  # upper arm
        box([5.8, -4.5, 5.8], [10.2, -1.5, 10.2], STONE_MID, STONE_PALE),       # elbow
        box([6.4, -11, 6.4], [9.6, -4, 9.6], ICE_DEEP, ICE_MID),                # forearm
        box([5, -14.5, 5], [11, -10.5, 11], STONE_PALE, STONE_MID, STONE_DARK),  # fist
        box([5.6, -15.5, 5.6], [10.4, -14, 10.4], ICE_GLOW, ICE_GLOW),          # frozen knuckles
    ]


PARTS = {"golem_torso": golem_torso, "golem_leg": golem_leg, "golem_arm": golem_arm}
