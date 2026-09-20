"""
The Ender Tyrant boss model: five item models (body, head, left wing, right wing, tail) that the
BurgerBosses plugin shows with item display entities and animates every tick.

Every part is built so its hinge is the model centre (8, 8, 8): the plugin rotates each part around
that point (wing flaps, tail sway, head turning). The dragon faces north (-Z) in model space,
which item displays turn into "facing the way the entity looks".

Element coordinates must stay inside -16..32 or the client refuses the whole model, so the beast is
built as big as that box allows and the plugin scales it up from there (tyrant.model-scale).
"""
import random

from PIL import Image

PARTS = ["tyrant_body", "tyrant_head", "tyrant_wing_l", "tyrant_wing_r", "tyrant_tail"]

# 32x32 texture of 4x4-pixel colour cells (8 x 8 grid). Cell index -> colour.
(SCALE_BLACK, SCALE_DARK, SCALE_MID, SCALE_LIGHT, BELLY, MEMBRANE, MEMBRANE_EDGE, GLOW,
 GLOW_WHITE, BONE, BONE_DARK, BONE_LIGHT, EYE, CLAW, HORN, SPIKE) = range(16)
COLOURS = {
    SCALE_BLACK: (14, 10, 20),
    SCALE_DARK: (24, 17, 33),
    SCALE_MID: (44, 31, 60),
    SCALE_LIGHT: (72, 54, 99),
    BELLY: (78, 52, 84),
    MEMBRANE: (60, 16, 82),
    MEMBRANE_EDGE: (120, 42, 152),
    GLOW: (220, 60, 255),
    GLOW_WHITE: (255, 205, 255),
    BONE: (226, 216, 196),
    BONE_DARK: (150, 138, 116),
    BONE_LIGHT: (248, 243, 228),
    EYE: (255, 30, 140),
    CLAW: (206, 198, 184),
    HORN: (198, 186, 164),
    SPIKE: (118, 106, 132),
}
GLOWING = {GLOW, GLOW_WHITE, EYE}
SCALY = {SCALE_BLACK, SCALE_DARK, SCALE_MID, SCALE_LIGHT, BELLY}
BONY = {BONE, BONE_DARK, BONE_LIGHT, CLAW, HORN}


def texture():
    """Scale cells get an overlapping-scales pattern, bone cells a grain, so the beast reads as
    scaly and bony even though every face only samples a 4x4 patch."""
    img = Image.new("RGBA", (32, 32))
    px = img.load()
    rnd = random.Random(11)
    # Rows of scales, offset every other row, each with a lit top edge and a dark underside.
    scale_shade = {(0, 0): 18, (1, 0): 10, (2, 0): 18, (3, 0): 10,
                   (0, 1): 0, (1, 1): -6, (2, 1): 0, (3, 1): -6,
                   (0, 2): -14, (1, 2): -20, (2, 2): -14, (3, 2): -20,
                   (0, 3): -6, (1, 3): 12, (2, 3): -6, (3, 3): 12}
    grain = {(0, 0): 14, (1, 1): -10, (2, 2): 12, (3, 3): -12, (2, 0): -8, (0, 3): 8}
    for cell, (r, g, b) in COLOURS.items():
        cx, cy = (cell % 8) * 4, (cell // 8) * 4
        for x in range(cx, cx + 4):
            for y in range(cy, cy + 4):
                local = (x - cx, y - cy)
                if cell in GLOWING:
                    n = 0
                elif cell in SCALY:
                    n = scale_shade[local] + rnd.randint(-4, 4)
                elif cell in BONY:
                    n = grain.get(local, 0) + rnd.randint(-5, 5)
                else:
                    n = rnd.randint(-8, 8)
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


def spike(cx, cz, y0, height, half, colour=SPIKE, tip=BONE_LIGHT, steps=3):
    """A tapering spike standing on (cx, cz) and growing upward from y0."""
    out = []
    for i in range(steps):
        h = height / steps
        w = half * (1 - i / steps)
        c = colour if i < steps - 1 else tip
        out.append(box([cx - w, y0 + h * i, cz - w], [cx + w, y0 + h * (i + 1), cz + w], c, tip))
    return out


def spike_along(cx, cz, y0, length, half, axis, sign, colour=SPIKE, tip=BONE_LIGHT, steps=3):
    """A tapering spike growing along x or z instead of up."""
    out = []
    for i in range(steps):
        seg = length / steps
        w = half * (1 - i / steps)
        c = colour if i < steps - 1 else tip
        a, b = y0 - w, y0 + w
        if axis == "x":
            lo = cx + sign * seg * i
            hi = cx + sign * seg * (i + 1)
            out.append(box([min(lo, hi), a, cz - w], [max(lo, hi), b, cz + w], c, tip))
        else:
            lo = cz + sign * seg * i
            hi = cz + sign * seg * (i + 1)
            out.append(box([cx - w, a, min(lo, hi)], [cx + w, b, max(lo, hi)], c, tip))
    return out


def body():
    els = [
        box([2.5, 3.5, -8], [13.5, 12.5, 22], SCALE_MID, SCALE_DARK, BELLY),            # torso
        box([3.5, 11.5, -6], [12.5, 13.5, 20], SCALE_DARK, SCALE_BLACK),                # hunched back
        box([2, 6, -2], [14, 11, 16], SCALE_LIGHT, SCALE_LIGHT, SCALE_MID),             # flank plates
        box([1.6, 7, 1], [14.4, 9.5, 12], SCALE_DARK, SCALE_DARK),                      # overlapping ridge
    ]
    for z in range(-6, 20, 4):                                                          # belly plating
        els.append(box([4.2, 3.1, z], [11.8, 4.2, z + 3], BELLY, BELLY, BELLY))
    # Bony ribs pushing through the hide on both flanks.
    for z in range(-4, 16, 4):
        for x0, x1 in ((1.4, 2.2), (13.8, 14.6)):
            els.append(box([x0, 5, z], [x1 + 0.4, 10.6, z + 1.4], BONE_DARK, BONE, BONE_DARK))
    # Spine: a bone ridge carrying alternating bone and glowing crystal spikes.
    els.append(box([7, 13.5, -6], [9, 14.5, 20], BONE_DARK, BONE))
    for i, z in enumerate(range(-6, 20, 3)):
        if i % 2:
            els += spike(8, z + 1, 14.5, 4.5, 1.1, SPIKE, BONE_LIGHT)
        else:
            els += spike(8, z + 1, 14.5, 6.0, 1.0, GLOW, GLOW_WHITE)
    # Shoulders and hips: armour plates with spikes sweeping backward.
    for x0, x1, side in ((1.2, 3.8, -1), (12.2, 14.8, 1)):
        for z0 in (-5, 13):
            els.append(box([x0, 8.5, z0], [x1, 13.5, z0 + 6], SCALE_LIGHT, SCALE_LIGHT, SCALE_DARK))
            els += spike_along(x1 if side > 0 else x0, z0 + 3, 11.5, 4.5, 1.2, "x", side)
    # Four legs, each with three claws.
    for x0 in (1.8, 11.2):
        for z0 in (-5, 13):
            els.append(box([x0, 4, z0], [x0 + 3, 9, z0 + 4.5], SCALE_DARK, SCALE_LIGHT))   # thigh
            els.append(box([x0 + 0.4, 0.5, z0 + 0.6], [x0 + 2.6, 4.5, z0 + 3.4], SCALE_BLACK))  # shin
            els.append(box([x0 - 0.2, -0.5, z0 - 0.4], [x0 + 3.2, 0.6, z0 + 4], SCALE_DARK, SCALE_DARK, BONE_DARK))
            for c in range(3):
                cx = x0 + 0.4 + c * 1.1
                els.append(box([cx, -0.6, z0 - 2.2], [cx + 0.7, 0.4, z0 - 0.2], CLAW, BONE_LIGHT))
    return els


def head():
    els = [
        box([5, 5, -2], [11, 11, 10], SCALE_MID, SCALE_LIGHT, BELLY),                   # neck
        box([4.4, 6, 0], [11.6, 9.5, 8], SCALE_DARK, SCALE_DARK),                       # neck plates
        box([3, 4.5, -14], [13, 12.5, -2], SCALE_DARK, SCALE_BLACK, SCALE_DARK),        # skull
        box([3.8, 12.5, -13], [12.2, 13.4, -3], SCALE_BLACK, SCALE_BLACK),              # skull plate
        box([4.6, 4.8, -15.8], [11.4, 9.6, -14], SCALE_MID, SCALE_LIGHT),               # snout
        box([4.2, 2.4, -15.5], [11.8, 5, -4], SCALE_BLACK, SCALE_BLACK, BELLY),         # lower jaw
        box([4.6, 4.9, -15.6], [11.4, 5.5, -6], BONE_DARK, BONE),                       # jaw bone line
        box([5.6, 7.6, -16], [6.6, 8.6, -15.8], GLOW),                                  # nostrils
        box([9.4, 7.6, -16], [10.4, 8.6, -15.8], GLOW),
        box([2.7, 8.6, -11.5], [3.2, 10.8, -7], EYE),                                   # eyes
        box([12.8, 8.6, -11.5], [13.3, 10.8, -7], EYE),
        box([2.5, 10.7, -12.2], [4.4, 12.1, -6.4], BONE_DARK, BONE),                    # brow ridges
        box([11.6, 10.7, -12.2], [13.5, 12.1, -6.4], BONE_DARK, BONE),
        box([3.4, 5.6, -12.8], [4.3, 9, -8.4], BONE_DARK, BONE),                        # cheek bones
        box([11.7, 5.6, -12.8], [12.6, 9, -8.4], BONE_DARK, BONE),
    ]
    # Teeth: short fangs along the upper and lower jaw, with two long tusks at the front.
    for i in range(5):
        x = 4.9 + i * 1.3
        els.append(box([x, 3.9, -15.2], [x + 0.8, 5.1, -13.8], BONE_LIGHT, BONE))       # upper
        els.append(box([x, 4.4, -13.4], [x + 0.7, 5.2, -12.2], BONE_LIGHT, BONE))
        els.append(box([x + 0.2, 4.6, -11.6], [x + 0.8, 5.4, -10.4], BONE, BONE_LIGHT))  # lower row
    for x in (4.9, 10.3):
        els.append(box([x, 2.8, -15.2], [x + 1, 5.2, -13.4], BONE_LIGHT, BONE))         # tusks
    # Horns: a big pair sweeping back, a smaller pair, cheek and jaw spikes.
    for x, s in ((3.4, -1), (12.6, 1)):
        els.append(box([min(x, x + s * 2), 11.8, -8.5], [max(x, x + s * 2), 14.4, -5], HORN, BONE_LIGHT))
        els += spike_along(x + s * 1.2, -2, 13.8, 8, 1.3, "z", 1, HORN, BONE_LIGHT)
        els.append(box([min(x + s * 0.2, x + s * 1.8), 9.8, -12.5], [max(x + s * 0.2, x + s * 1.8), 11.6, -10], HORN, BONE_LIGHT))
        els += spike_along(x + s * 0.8, -11, 10.6, 4, 0.9, "x", s, HORN, BONE_LIGHT)    # cheek spikes
        els += spike_along(x + s * 0.4, -6, 6.8, 3.4, 0.8, "x", s, SPIKE, BONE_LIGHT)   # jaw spikes
    # Crown of glowing crystal spikes down the middle of the skull.
    for i, z in enumerate((-11.5, -8.5, -5.5)):
        els += spike(8, z, 13.2, 5.5 - i * 0.7, 1.0, GLOW, GLOW_WHITE)
    for z in (0, 3, 6):                                                                 # neck spikes
        els += spike(8, z, 10.8, 3.6, 0.9, SPIKE, BONE_LIGHT)
    return els


def wing_right():
    """Right wing: grows toward +X from the hinge at the model centre."""
    els = [
        box([8, 6.8, -3], [32, 9.2, 1.5], SCALE_DARK, SCALE_LIGHT, SCALE_BLACK),        # arm bone
        box([8, 7.6, -1], [20, 8.6, 2], BONE_DARK, BONE),                               # humerus showing through
        box([9, 7.8, 1.5], [16, 8.2, 21], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),           # stepped membrane
        box([16, 7.8, 1.5], [24, 8.2, 18], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),
        box([24, 7.8, 1.5], [31, 8.2, 13], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),
        box([15.3, 7.4, 1], [16.7, 8.6, 21], BONE_DARK, BONE),                          # finger bones
        box([23.3, 7.4, 1], [24.7, 8.6, 18], BONE_DARK, BONE),
        box([30.3, 7.4, 1], [31.7, 8.6, 13], BONE_DARK, BONE),
        box([9, 8.2, 4], [30, 8.45, 5.2], GLOW),                                        # glowing vein
        box([11, 8.2, 9], [22, 8.4, 9.8], GLOW),
    ]
    # Claw at the wrist and barbs along the leading edge.
    els.append(box([29.5, 6.2, -4], [32, 9.8, -1], CLAW, BONE_LIGHT))
    els += spike_along(28.5, -3.6, 8, 3.5, 1.0, "x", 1, CLAW, BONE_LIGHT)
    for x in (12, 17, 22, 27):
        els += spike_along(x, -3, 8, 3.2, 0.9, "z", -1, SPIKE, BONE_LIGHT)
    # Torn membrane edge: a few notches of darker membrane.
    for x, z in ((13, 21), (19, 18), (26, 13)):
        els.append(box([x, 7.85, z - 1], [x + 3, 8.15, z + 1.5], MEMBRANE_EDGE, MEMBRANE_EDGE))
    return els


def mirror_x(elements):
    out = []
    for e in elements:
        f, t = e["from"], e["to"]
        faces = dict(e["faces"])
        faces["east"], faces["west"] = e["faces"]["west"], e["faces"]["east"]
        out.append({"from": [16 - t[0], f[1], f[2]], "to": [16 - f[0], t[1], t[2]], "faces": faces})
    return out


def tail():
    els = [
        box([4.5, 4.5, 8], [11.5, 11.5, 16], SCALE_MID, SCALE_DARK, BELLY),
        box([5.2, 5.2, 16], [10.8, 10.8, 23], SCALE_MID, SCALE_DARK, BELLY),
        box([6, 6, 23], [10, 10, 28], SCALE_DARK, SCALE_BLACK, BELLY),
        box([6.6, 6.6, 28], [9.4, 9.4, 31.5], SCALE_BLACK),
        box([4.1, 6.5, 9], [11.9, 9.5, 15], SCALE_LIGHT, SCALE_LIGHT, SCALE_MID),       # scale plates
        box([4.9, 6.8, 16], [11.1, 9.2, 22], SCALE_LIGHT, SCALE_LIGHT, SCALE_MID),
    ]
    for z in (9, 13, 17, 21, 25):                                                       # belly rings
        els.append(box([5.6, 4.6, z], [10.4, 5.4, z + 2], BELLY, BELLY, BELLY))
    # Spine spikes running to the tip, alternating bone and crystal, shrinking as they go.
    for i, z in enumerate((9, 12, 15, 18, 21, 24, 27)):
        top = 11.5 - i * 0.55
        if i % 2:
            els += spike(8, z, top, 5 - i * 0.4, 1.1 - i * 0.08, SPIKE, BONE_LIGHT)
        else:
            els += spike(8, z, top, 5.5 - i * 0.4, 1.0 - i * 0.07, GLOW, GLOW_WHITE)
    # Side barbs.
    for z in (12, 18, 24):
        els += spike_along(4.6, z, 8, 3.4, 0.9, "x", -1, SPIKE, BONE_LIGHT)
        els += spike_along(11.4, z, 8, 3.4, 0.9, "x", 1, SPIKE, BONE_LIGHT)
    # The tail blade: a broad glowing axe head with two barbs.
    els.append(box([3, 7.4, 28.5], [13, 8.6, 32], GLOW, GLOW_WHITE))
    els.append(box([4, 7.6, 30], [12, 8.4, 32], GLOW_WHITE, GLOW_WHITE))
    els += spike_along(3.2, 30.5, 8, 3, 1.0, "x", -1, GLOW, GLOW_WHITE)
    els += spike_along(12.8, 30.5, 8, 3, 1.0, "x", 1, GLOW, GLOW_WHITE)
    return els


def elements(part):
    return {
        "tyrant_body": body,
        "tyrant_head": head,
        "tyrant_wing_r": wing_right,
        "tyrant_wing_l": lambda: mirror_x(wing_right()),
        "tyrant_tail": tail,
    }[part]()
