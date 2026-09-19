"""
The Ender Tyrant boss model: five item models (body, head, left wing, right wing, tail) that the
BurgerBosses plugin shows with item display entities and animates every tick.

Every part is built so its hinge is the model centre (8, 8, 8): the plugin rotates each part around
that point (wing flaps, tail sway, head turning). The dragon faces north (-Z) in model space,
which item displays turn into "facing the way the entity looks".
"""
import random

from PIL import Image

PARTS = ["tyrant_body", "tyrant_head", "tyrant_wing_l", "tyrant_wing_r", "tyrant_tail"]

# 32x32 texture of 4x4-pixel colour cells (8 x 8 grid). Cell index -> colour.
SCALE_DARK, SCALE_MID, SCALE_LIGHT, BELLY, MEMBRANE, MEMBRANE_EDGE, GLOW, GLOW_WHITE, BONE, BONE_DARK, EYE = range(11)
COLOURS = {
    SCALE_DARK: (22, 16, 30),
    SCALE_MID: (42, 30, 58),
    SCALE_LIGHT: (70, 52, 96),
    BELLY: (74, 50, 80),
    MEMBRANE: (64, 18, 86),
    MEMBRANE_EDGE: (118, 40, 150),
    GLOW: (220, 60, 255),
    GLOW_WHITE: (255, 205, 255),
    BONE: (226, 216, 196),
    BONE_DARK: (160, 148, 126),
    EYE: (255, 30, 140),
}
GLOWING = {GLOW, GLOW_WHITE, EYE}


def texture():
    img = Image.new("RGBA", (32, 32))
    px = img.load()
    rnd = random.Random(11)
    for cell, (r, g, b) in COLOURS.items():
        cx, cy = (cell % 8) * 4, (cell // 8) * 4
        for x in range(cx, cx + 4):
            for y in range(cy, cy + 4):
                n = 0 if cell in GLOWING else rnd.randint(-8, 8)
                # a scale pattern: every other pixel slightly darker
                if cell in (SCALE_DARK, SCALE_MID, SCALE_LIGHT) and (x + y) % 2 == 0:
                    n -= 10
                px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), 255)
    return img


def uv(cell):
    col, row = cell % 8, cell // 8
    return [col * 2, row * 2, col * 2 + 2, row * 2 + 2]


def box(frm, to, side, top=None, bottom=None):
    faces = {f: {"uv": uv(side), "texture": "#main"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": uv(top if top is not None else side), "texture": "#main"}
    faces["down"] = {"uv": uv(bottom if bottom is not None else side), "texture": "#main"}
    return {"from": frm, "to": to, "faces": faces}


def body():
    els = [
        box([3, 4, -6], [13, 12, 22], SCALE_MID, SCALE_LIGHT, BELLY),             # torso
        box([4, 3.5, -4], [12, 4, 20], BELLY),                                      # belly plates
        box([2, 9, -4], [4, 12.5, 5], SCALE_LIGHT, SCALE_LIGHT),                    # shoulders
        box([12, 9, -4], [14, 12.5, 5], SCALE_LIGHT, SCALE_LIGHT),
    ]
    for z in range(-4, 20, 5):                                                     # glowing back spines
        els.append(box([7, 12, z], [9, 15, z + 2], SCALE_DARK, GLOW))
        els.append(box([7.5, 15, z + 0.5], [8.5, 17, z + 1.5], GLOW, GLOW_WHITE))
    for x0 in (2.5, 11.5):                                                          # legs + claws
        for z0 in (-3, 14):
            els.append(box([x0, 0.5, z0], [x0 + 2, 4, z0 + 4], SCALE_DARK))
            els.append(box([x0 - 0.3, -0.5, z0 - 1], [x0 + 2.3, 0.5, z0 + 1], BONE, BONE, BONE_DARK))
    return els


def head():
    els = [
        box([5.5, 5.5, -2], [10.5, 10.5, 9], SCALE_MID, SCALE_LIGHT, BELLY),        # neck
        box([7.5, 10.5, -1], [8.5, 13, 1], GLOW, GLOW_WHITE),                       # neck spines
        box([7.5, 10.5, 3], [8.5, 12.5, 5], GLOW, GLOW_WHITE),
        box([3.5, 5, -14], [12.5, 12, -2], SCALE_DARK, SCALE_LIGHT, SCALE_DARK),    # skull
        box([5, 5, -15.8], [11, 9.5, -14], SCALE_MID, SCALE_LIGHT),                   # snout
        box([4.5, 2.5, -15.5], [11.5, 5, -4], SCALE_DARK, SCALE_DARK, BELLY),       # jaw
        box([5, 4.6, -15.7], [11, 5.4, -15.5], BONE),                               # teeth
        box([3.3, 9, -11], [3.6, 10.6, -7.5], EYE),                                 # eyes
        box([12.4, 9, -11], [12.7, 10.6, -7.5], EYE),
        box([5.6, 7.6, -16], [6.6, 8.6, -15.8], GLOW),                              # nostrils
        box([9.4, 7.6, -16], [10.4, 8.6, -15.8], GLOW),
        box([3.5, 12, -6], [5.5, 14, -3], BONE, BONE, BONE_DARK),                   # horns sweeping back
        box([3.8, 13, -3], [5, 14.5, 3], BONE, BONE, BONE_DARK),
        box([10.5, 12, -6], [12.5, 14, -3], BONE, BONE, BONE_DARK),
        box([11, 13, -3], [12.2, 14.5, 3], BONE, BONE, BONE_DARK),
        box([7.5, 12, -11], [8.5, 15, -8], GLOW, GLOW_WHITE),                       # crown spike
    ]
    return els


def wing_right():
    """Right wing: grows toward +X from the hinge at the model centre."""
    return [
        box([8, 7, -2], [32, 9, 1], SCALE_LIGHT, SCALE_LIGHT, SCALE_DARK),          # arm (leading edge)
        box([9, 7.8, 0], [16, 8.2, 20], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),         # stepped membrane
        box([16, 7.8, 0], [24, 8.2, 17], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),
        box([24, 7.8, 0], [31, 8.2, 12], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),
        box([15.5, 7.5, 0], [16.5, 8.5, 20], BONE_DARK, BONE),                      # finger bones
        box([23.5, 7.5, 0], [24.5, 8.5, 17], BONE_DARK, BONE),
        box([30.5, 7.5, 0], [31.5, 8.5, 12], BONE_DARK, BONE),
        box([29.5, 6.5, -3.5], [32, 9.5, -1], BONE, BONE),                          # wing claw
        box([9, 8.2, 3], [30, 8.4, 4], GLOW),                                       # glowing vein
    ]


def mirror_x(elements):
    out = []
    for e in elements:
        f, t = e["from"], e["to"]
        faces = dict(e["faces"])
        faces["east"], faces["west"] = e["faces"]["west"], e["faces"]["east"]
        out.append({"from": [16 - t[0], f[1], f[2]], "to": [16 - f[0], t[1], t[2]], "faces": faces})
    return out


def tail():
    return [
        box([5, 5, 8], [11, 11, 16], SCALE_MID, SCALE_LIGHT, BELLY),
        box([5.8, 5.8, 16], [10.2, 10.2, 23], SCALE_MID, SCALE_LIGHT, BELLY),
        box([6.5, 6.5, 23], [9.5, 9.5, 29], SCALE_MID, SCALE_LIGHT, BELLY),
        box([7.2, 7.2, 29], [8.8, 8.8, 32], SCALE_DARK),
        box([7.5, 11, 10], [8.5, 13, 12], GLOW, GLOW_WHITE),
        box([7.5, 10.2, 18], [8.5, 12, 20], GLOW, GLOW_WHITE),
        box([7.5, 9.5, 25], [8.5, 11, 27], GLOW, GLOW_WHITE),
        box([4, 7.6, 28], [12, 8.4, 32], GLOW, GLOW_WHITE),                        # tail blade
    ]


def elements(part):
    return {
        "tyrant_body": body,
        "tyrant_head": head,
        "tyrant_wing_r": wing_right,
        "tyrant_wing_l": lambda: mirror_x(wing_right()),
        "tyrant_tail": tail,
    }[part]()
