"""
The 3D war hammer used by Worldbreaker and Earthquake Mace.

Shape: a heavy sledgehammer head (broad striking faces on both sides, bevelled frame with a
glowing window), a single big spike standing on top of it, and a light blue wrapped handle with a
diamond pommel. Coordinates are Minecraft model units (16 = one block); the generator scales the
held model on top of this.
"""
from PIL import Image, ImageDraw

# (frame dark, frame mid, frame light, window deep, window glow, rod dark, rod mid, rod light,
#  spike dark, spike light). Rod colours are light blue on both hammers, as asked.
PALETTES = {
    "worldbreaker": [(34, 28, 40), (58, 50, 66), (92, 84, 104), (90, 10, 0), (255, 120, 30),
                     (26, 86, 132), (86, 176, 228), (186, 236, 255), (150, 90, 10), (255, 225, 110)],
    "earthquake_mace": [(64, 56, 48), (104, 94, 80), (150, 138, 118), (70, 40, 10), (240, 170, 60),
                        (30, 96, 124), (96, 184, 214), (196, 240, 255), (90, 94, 102), (200, 206, 214)],
}

# UV regions in model units (0-16) on the 32x32 texture.
UV_SIDE = [0, 0, 8, 8]        # striking face: frame + window
UV_TOP = [8, 0, 16, 8]        # head top/cheek plate
UV_ROD = [0, 8, 2, 16]        # handle, with wrap bands
UV_ROD_END = [2, 8, 4, 10]
UV_SPIKE = [4, 8, 6, 12]
UV_TIP = [6, 8, 8, 10]
UV_GOLD = [8, 8, 10, 10]


def texture(item_id):
    fd, fm, fl, wd, wg, rd, rm, rl, sd, sl = PALETTES[item_id]
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Striking face: bevelled frame around a deep window with a glowing core.
    d.rectangle((0, 0, 15, 15), fill=fm)
    d.line((0, 0, 15, 0), fill=fl); d.line((0, 0, 0, 15), fill=fl)
    d.line((15, 0, 15, 15), fill=fd); d.line((0, 15, 15, 15), fill=fd)
    d.rectangle((3, 3, 12, 12), fill=fd)
    d.rectangle((4, 4, 11, 11), fill=wd)
    d.rectangle((6, 5, 9, 10), fill=wg)
    d.point([(7, 6), (8, 8)], fill=(255, 245, 200))
    d.point([(2, 2), (13, 2), (2, 13), (13, 13)], fill=fl)          # rivets
    # Head top / cheek: plated steel with a ridge.
    d.rectangle((16, 0, 31, 15), fill=fm)
    d.rectangle((19, 3, 28, 12), fill=fd)
    d.rectangle((21, 5, 26, 10), fill=fl)
    d.line((16, 0, 31, 0), fill=fl); d.line((16, 15, 31, 15), fill=fd)
    # Handle: light blue gradient with darker wrap bands and a highlight line.
    for y in range(16, 32):
        t = (y - 16) / 15
        c = tuple(int(rl[i] * (1 - t) + rd[i] * t) for i in range(3))
        d.line((0, y, 3, y), fill=c)
    d.line((1, 16, 1, 31), fill=rl)
    for y in (18, 22, 26, 30):                                      # grip wrap
        d.line((0, y, 3, y), fill=rd)
    d.rectangle((4, 16, 7, 19), fill=rm)
    # Spike body and tip, gold trim.
    for y in range(16, 24):
        t = (y - 16) / 7
        d.line((8, y, 11, y), fill=tuple(int(sl[i] * (1 - t) + sd[i] * t) for i in range(3)))
    d.rectangle((12, 16, 15, 19), fill=sl)
    d.rectangle((16, 16, 19, 19), fill=sl)
    d.point([(17, 17)], fill=(255, 255, 255))
    return img


def _faces(uv_side, uv_top=None, uv_bottom=None):
    faces = {f: {"uv": uv_side, "texture": "#main"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": uv_top or uv_side, "texture": "#main"}
    faces["down"] = {"uv": uv_bottom or uv_top or uv_side, "texture": "#main"}
    return faces


def box(frm, to, uv_side, uv_top=None, rotation=None):
    element = {"from": frm, "to": to, "faces": _faces(uv_side, uv_top)}
    if rotation:
        element["rotation"] = rotation
    return element


def diamond(cx, cy, cz, size, uv):
    """A cube turned 45 degrees so it reads as a diamond from the side."""
    h = size / 2
    return box([cx - h, cy - h, cz - h], [cx + h, cy + h, cz + h], uv,
               rotation={"origin": [cx, cy, cz], "axis": "y", "angle": 45})


def elements():
    els = []
    # Handle: long wrapped rod with a collar under the head and a diamond pommel.
    els.append(box([7.4, -2, 7.4], [8.6, 10.5, 8.6], UV_ROD, UV_ROD_END))
    els.append(diamond(8, -3, 8, 2.4, UV_GOLD))                         # pommel
    els.append(box([7, 9.5, 7], [9, 10.5, 9], UV_ROD_END))              # collar
    # Hammer head: a broad block with a striking face on each side (-x and +x).
    y0, y1 = 10.5, 16.5
    els.append(box([3.5, y0, 5.5], [12.5, y1, 10.5], UV_TOP, UV_TOP))   # body of the head
    for x0, x1 in ((2.5, 3.5), (12.5, 13.5)):                           # flared striking faces
        els.append(box([x0, y0 - 0.6, 4.9], [x1, y1 + 0.6, 11.1], UV_SIDE, UV_TOP))
    els.append(box([4.5, y0 - 0.4, 5.2], [11.5, y0 + 0.4, 10.8], UV_TOP, UV_TOP))    # underside lip
    # One spike, standing on top of the head.
    els.append(box([6.8, y1, 6.8], [9.2, y1 + 2.4, 9.2], UV_SPIKE, UV_SPIKE))
    els.append(box([7.2, y1 + 2.4, 7.2], [8.8, y1 + 5.6, 8.8], UV_SPIKE, UV_SPIKE))
    els.append(box([7.7, y1 + 5.6, 7.7], [8.3, y1 + 9, 8.3], UV_TIP, UV_TIP))
    els.append(diamond(8, y1 + 0.7, 8, 1.8, UV_GOLD))                   # collar around the spike foot
    return els
