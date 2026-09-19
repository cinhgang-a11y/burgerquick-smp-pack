"""
The spiked 3D mace used by Worldbreaker and Earthquake Mace.

Shape based on the "framed cube head + rod handle" mace style: a cube head with a recessed
window on every side, a diamond knob on top, a long polished rod and a diamond pommel - plus
13 spikes. Coordinates are Minecraft model units (16 = one block); the generator scales the
held model on top of this.
"""
from PIL import Image, ImageDraw

# (frame dark, frame mid, frame light, window deep, window glow, rod dark, rod mid, rod light, spike dark, spike light)
PALETTES = {
    "worldbreaker": [(34, 28, 40), (58, 50, 66), (92, 84, 104), (90, 10, 0), (255, 120, 30),
                     (120, 20, 8), (230, 90, 20), (255, 200, 90), (150, 90, 10), (255, 225, 110)],
    "earthquake_mace": [(64, 56, 48), (104, 94, 80), (150, 138, 118), (70, 40, 10), (240, 170, 60),
                        (80, 50, 22), (150, 98, 48), (214, 164, 96), (90, 94, 102), (200, 206, 214)],
}

# UV regions in model units (0-16) on the 32x32 texture.
UV_SIDE = [0, 0, 8, 8]
UV_TOP = [8, 0, 16, 8]
UV_ROD = [0, 8, 2, 16]
UV_ROD_END = [2, 8, 4, 10]
UV_SPIKE = [4, 8, 6, 12]
UV_TIP = [6, 8, 8, 10]
UV_GOLD = [8, 8, 10, 10]


def texture(item_id):
    fd, fm, fl, wd, wg, rd, rm, rl, sd, sl = PALETTES[item_id]
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Head side: bevelled frame around a deep window with a glowing core.
    d.rectangle((0, 0, 15, 15), fill=fm)
    d.line((0, 0, 15, 0), fill=fl); d.line((0, 0, 0, 15), fill=fl)
    d.line((15, 0, 15, 15), fill=fd); d.line((0, 15, 15, 15), fill=fd)
    d.rectangle((3, 3, 12, 12), fill=fd)
    d.rectangle((4, 4, 11, 11), fill=wd)
    d.rectangle((6, 5, 9, 10), fill=wg)
    d.point([(7, 6), (8, 8)], fill=(255, 245, 200))
    d.point([(2, 2), (13, 2), (2, 13), (13, 13)], fill=fl)          # rivets
    # Head top: frame with a plate.
    d.rectangle((16, 0, 31, 15), fill=fm)
    d.rectangle((19, 3, 28, 12), fill=fd)
    d.rectangle((21, 5, 26, 10), fill=fl)
    d.line((16, 0, 31, 0), fill=fl); d.line((16, 15, 31, 15), fill=fd)
    # Rod: polished gradient strip with a highlight line.
    for y in range(16, 32):
        t = (y - 16) / 15
        c = tuple(int(rl[i] * (1 - t) + rd[i] * t) for i in range(3))
        d.line((0, y, 3, y), fill=c)
    d.line((1, 16, 1, 31), fill=rl)
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
    # Rod and grip end.
    els.append(box([7.4, -2, 7.4], [8.6, 10, 8.6], UV_ROD, UV_ROD_END))
    els.append(diamond(8, -3, 8, 2.2, UV_GOLD))                        # pommel
    els.append(box([7, 9, 7], [9, 10, 9], UV_ROD_END))                  # collar
    # Head: 7x7x7 framed cube.
    lo, hi, y0, y1 = 4.5, 11.5, 10, 17
    els.append(box([lo, y0, lo], [hi, y1, hi], UV_SIDE, UV_TOP))
    els.append(diamond(8, 18, 8, 2, UV_GOLD))                           # top knob
    mid = (y0 + y1) / 2
    # 4 big spikes straight out of each window (two-step taper).
    for axis, sign in (("x", 1), ("x", -1), ("z", 1), ("z", -1)):
        base_out, tip_out = 1.8, 3.4
        if axis == "x":
            x0 = hi if sign > 0 else lo - base_out
            els.append(box([x0, mid - 1, 7], [x0 + base_out, mid + 1, 9], UV_SPIKE))
            x1 = hi + base_out if sign > 0 else lo - tip_out
            els.append(box([x1, mid - 0.5, 7.5], [x1 + tip_out - base_out, mid + 0.5, 8.5], UV_TIP))
        else:
            z0 = hi if sign > 0 else lo - base_out
            els.append(box([7, mid - 1, z0], [9, mid + 1, z0 + base_out], UV_SPIKE))
            z1 = hi + base_out if sign > 0 else lo - tip_out
            els.append(box([7.5, mid - 0.5, z1], [8.5, mid + 0.5, z1 + tip_out - base_out], UV_TIP))
    # 4 spikes on the vertical edges, pointing diagonally outward.
    for cx, cz in ((lo, lo), (lo, hi), (hi, lo), (hi, hi)):
        els.append(box([cx - 1.9, mid - 0.6, cz - 0.6], [cx + 1.9, mid + 0.6, cz + 0.6], UV_SPIKE,
                       rotation={"origin": [cx, mid, cz], "axis": "y",
                                 "angle": -45 if (cx < 8) == (cz < 8) else 45}))
    # 4 spikes rising from the top corners.
    for cx, cz in ((lo + 0.9, lo + 0.9), (lo + 0.9, hi - 0.9), (hi - 0.9, lo + 0.9), (hi - 0.9, hi - 0.9)):
        els.append(box([cx - 0.6, y1, cz - 0.6], [cx + 0.6, y1 + 2.2, cz + 0.6], UV_SPIKE, UV_TIP))
    return els
