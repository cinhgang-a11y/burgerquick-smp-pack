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
    """A long, narrow torso caged in bone: ribs, a sternum plate and pauldrons over the shoulders."""
    els = [
        box([5, 5, -14], [11, 11.5, 26], SCALE_MID, SCALE_DARK, BELLY),                 # long slim torso
        box([5.6, 11.5, -12], [10.4, 12.6, 24], SCALE_DARK, SCALE_BLACK),               # back ridge
        box([4.5, 6.5, -8], [11.5, 10.5, 18], SCALE_LIGHT, SCALE_LIGHT, SCALE_MID),     # flank hide
    ]
    for z in range(-12, 24, 4):                                                         # belly plating
        els.append(box([5.8, 4.6, z], [10.2, 5.4, z + 3], BELLY, BELLY, BELLY))
    # Rib cage: each rib runs up the flank and closes over the spine.
    for z in range(-11, 23, 3):
        for x0, x1 in ((3.9, 5.3), (10.7, 12.1)):
            els.append(box([x0, 5, z], [x1, 11, z + 1.3], BONE, BONE_LIGHT, BONE_DARK))
        els.append(box([4.9, 10.6, z], [11.1, 11.9, z + 1.3], BONE_DARK, BONE))
    els.append(box([5.2, 4.1, -11], [10.8, 5.2, 8], BONE, BONE_LIGHT, BONE_DARK))       # sternum
    els.append(box([5.4, 12.4, -12], [10.6, 13.4, 24], BONE_DARK, BONE))                # vertebrae
    # Spine spikes: alternating bone and crystal, tallest over the shoulders.
    for i, z in enumerate(range(-12, 25, 3)):
        tall = 7.5 - abs(i - 4) * 0.45
        if i % 2:
            els += spike(8, z + 1, 13.4, tall * 0.8, 1.0, SPIKE, BONE_LIGHT)
        else:
            els += spike(8, z + 1, 13.4, tall, 0.9, GLOW, GLOW_WHITE)
    # Bone pauldrons over each shoulder and hip, with a spike sweeping back.
    for x0, x1, side in ((2.6, 4.6, -1), (11.4, 13.4, 1)):
        for z0 in (-11, 15):
            els.append(box([x0, 8, z0], [x1, 13, z0 + 7], BONE, BONE_LIGHT, BONE_DARK))
            els.append(box([x0 - 0.4, 9, z0 + 1], [x1 + 0.4, 11.5, z0 + 5], BONE_DARK, BONE))
            els += spike_along(x1 if side > 0 else x0, z0 + 3.5, 11.5, 5.5, 1.2, "x", side, HORN, BONE_LIGHT)
    # Four long, thin legs ending in bone claws.
    for x0 in (3.6, 10.6):
        for z0 in (-10, 16):
            els.append(box([x0, 2.5, z0], [x0 + 1.8, 7, z0 + 3], SCALE_DARK, SCALE_LIGHT))      # thigh
            els.append(box([x0 + 0.1, 2.2, z0 + 0.2], [x0 + 1.7, 6.6, z0 + 2.8], BONE_DARK, BONE))
            els.append(box([x0 + 0.3, -3.5, z0 + 0.4], [x0 + 1.5, 3, z0 + 2.4], SCALE_BLACK))   # shin
            els.append(box([x0 + 0.4, -3.2, z0 + 0.5], [x0 + 1.4, 2.4, z0 + 1.2], BONE_DARK, BONE))
            els.append(box([x0 - 0.3, -4.6, z0 - 0.6], [x0 + 2.1, -3.4, z0 + 3], SCALE_DARK, SCALE_DARK, BONE_DARK))
            for c in range(3):
                cx = x0 - 0.1 + c * 0.9
                els.append(box([cx, -4.8, z0 - 2.8], [cx + 0.6, -3.8, z0 - 0.4], CLAW, BONE_LIGHT))
    return els


def head():
    """A long neck and a bone-masked skull."""
    els = [
        box([6, 6, -2], [10, 10, 20], SCALE_MID, SCALE_LIGHT, BELLY),                   # long neck
        box([5.5, 6.6, 0], [10.5, 9.5, 18], SCALE_DARK, SCALE_DARK),                    # neck hide plates
        box([4, 5, -14], [12, 11.5, -2], SCALE_DARK, SCALE_BLACK, SCALE_DARK),          # skull
        box([3.6, 8.2, -14.6], [12.4, 12.2, -3], BONE, BONE_LIGHT, BONE_DARK),          # bone mask
        box([4.4, 11.8, -12], [11.6, 12.8, -4], BONE_DARK, BONE),                       # crest plate
        box([5, 4.9, -15.8], [11, 9, -14], SCALE_MID, SCALE_LIGHT),                     # snout
        box([4.8, 8.4, -16], [11.2, 9.6, -13], BONE, BONE_LIGHT, BONE_DARK),            # snout bone
        box([4.6, 2.6, -15.5], [11.4, 5, -4], SCALE_BLACK, SCALE_BLACK, BELLY),         # lower jaw
        box([4.8, 4.6, -15.6], [11.2, 5.4, -5], BONE_DARK, BONE),                       # jaw bone
        box([5.6, 7.4, -16], [6.6, 8.3, -15.8], GLOW),                                  # nostrils
        box([9.4, 7.4, -16], [10.4, 8.3, -15.8], GLOW),
        box([3.5, 8.6, -12], [4, 10.6, -7.5], EYE),                                     # eyes
        box([12, 8.6, -12], [12.5, 10.6, -7.5], EYE),
        box([3.3, 10.4, -12.6], [5, 11.8, -6.8], BONE_LIGHT, BONE),                     # brow ridges
        box([11, 10.4, -12.6], [12.7, 11.8, -6.8], BONE_LIGHT, BONE),
    ]
    # Neck bone rings, thinning toward the body.
    for i, z in enumerate((0, 4, 8, 12, 16)):
        w = 0.7 - i * 0.05
        els.append(box([6 - w, 6 - w, z], [10 + w, 10 + w, z + 1.4], BONE_DARK, BONE))
        els += spike(8, z + 0.7, 10 + w, 3.6 - i * 0.3, 0.8, SPIKE, BONE_LIGHT)
    # Teeth: short fangs along both jaws, two long tusks at the front.
    for i in range(5):
        x = 5.1 + i * 1.2
        els.append(box([x, 3.9, -15.2], [x + 0.8, 5, -13.8], BONE_LIGHT, BONE))
        els.append(box([x, 4.4, -13.4], [x + 0.7, 5.2, -12.2], BONE_LIGHT, BONE))
        els.append(box([x + 0.2, 4.6, -11.6], [x + 0.8, 5.4, -10.4], BONE, BONE_LIGHT))
    for x in (5.1, 10.1):
        els.append(box([x, 2.8, -15.2], [x + 1, 5.2, -13.2], BONE_LIGHT, BONE))
    # Horns: a long swept pair, a second pair, cheek and jaw spikes.
    for x, s in ((3.8, -1), (12.2, 1)):
        els.append(box([min(x, x + s * 2.2), 11.6, -9], [max(x, x + s * 2.2), 14.6, -5], HORN, BONE_LIGHT))
        els += spike_along(x + s * 1.3, -3, 14, 11, 1.4, "z", 1, HORN, BONE_LIGHT)      # main horns
        els.append(box([min(x + s * 0.2, x + s * 1.8), 9.6, -12.6], [max(x + s * 0.2, x + s * 1.8), 11.4, -10], HORN, BONE_LIGHT))
        els += spike_along(x + s * 0.9, -11.2, 10.4, 5, 0.9, "x", s, HORN, BONE_LIGHT)  # cheek spikes
        els += spike_along(x + s * 0.4, -6, 6.6, 4, 0.8, "x", s, SPIKE, BONE_LIGHT)     # jaw spikes
    for i, z in enumerate((-11.5, -8.5, -5.5)):                                         # crown
        els += spike(8, z, 12.8, 6.5 - i * 0.8, 1.0, GLOW, GLOW_WHITE)
    return els


def wing_right():
    """Right wing: grows toward +X from the hinge at the model centre. Long bone arm, deep membrane."""
    els = [
        box([8, 7, -4], [32, 9.2, 0.5], SCALE_DARK, SCALE_LIGHT, SCALE_BLACK),          # arm
        box([8, 7.4, -3.4], [31, 8.8, 0], BONE, BONE_LIGHT, BONE_DARK),                 # arm bone
        box([9, 7.8, 0.5], [17, 8.2, 30], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),           # deep membrane
        box([17, 7.8, 0.5], [25, 8.2, 25], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),
        box([25, 7.8, 0.5], [31.5, 8.2, 18], MEMBRANE, MEMBRANE, MEMBRANE_EDGE),
        box([16.2, 7.3, 0], [17.8, 8.7, 30], BONE, BONE_LIGHT, BONE_DARK),              # finger bones
        box([24.2, 7.3, 0], [25.8, 8.7, 25], BONE, BONE_LIGHT, BONE_DARK),
        box([30.7, 7.3, 0], [32, 8.7, 18], BONE, BONE_LIGHT, BONE_DARK),
        box([9, 8.2, 3], [30, 8.45, 4.4], GLOW),                                        # glowing veins
        box([11, 8.2, 10], [24, 8.4, 11], GLOW),
        box([13, 8.2, 18], [22, 8.4, 19], GLOW),
        box([29.5, 6, -5], [32, 10, -1.5], CLAW, BONE_LIGHT),                           # wrist claw
    ]
    els += spike_along(28.5, -4.6, 8, 3.5, 1.0, "x", 1, CLAW, BONE_LIGHT)
    for x in (12, 17, 22, 27, 30):                                                      # leading-edge barbs
        els += spike_along(x, -4, 8, 4, 0.9, "z", -1, SPIKE, BONE_LIGHT)
    for x, z in ((14, 29), (21, 24), (28, 17)):                                         # torn trailing edge
        els.append(box([x, 7.85, z - 1.5], [x + 3.5, 8.15, z + 1], MEMBRANE_EDGE, MEMBRANE_EDGE))
    return els


def tail():
    """A very long whip of a tail: bone rings, barbs, and a glowing blade."""
    els = []
    # Segments from where it meets the body out to the tip, tapering all the way.
    spans = [(-12, -4, 3.2), (-4, 4, 2.9), (4, 11, 2.5), (11, 18, 2.1), (18, 24, 1.7),
             (24, 29, 1.3), (29, 32, 0.9)]
    for z0, z1, half in spans:
        els.append(box([8 - half, 8 - half, z0], [8 + half, 8 + half, z1], SCALE_MID, SCALE_DARK, BELLY))
        els.append(box([8 - half - 0.35, 8 - half + 0.5, z0 + 0.4], [8 + half + 0.35, 8 + half - 0.5, z0 + 1.6],
                       BONE_DARK, BONE))                                                # bone ring
        els.append(box([8 - half + 0.4, 8 - half - 0.3, z0 + 1], [8 + half - 0.4, 8 - half + 0.4, z1 - 0.5],
                       BELLY, BELLY, BELLY))                                            # underside
    # Spikes down the whole length, alternating bone and crystal.
    for i, (z0, z1, half) in enumerate(spans):
        top = 8 + half
        if i % 2:
            els += spike(8, (z0 + z1) / 2, top, 5.5 - i * 0.5, half * 0.35, SPIKE, BONE_LIGHT)
        else:
            els += spike(8, (z0 + z1) / 2, top, 6 - i * 0.5, half * 0.32, GLOW, GLOW_WHITE)
        if i % 2 == 0 and i < 6:                                                        # side barbs
            els += spike_along(8 - half, (z0 + z1) / 2, 8, 3.8, 0.85, "x", -1, SPIKE, BONE_LIGHT)
            els += spike_along(8 + half, (z0 + z1) / 2, 8, 3.8, 0.85, "x", 1, SPIKE, BONE_LIGHT)
    # The blade at the tip.
    els.append(box([2.5, 7.4, 28.5], [13.5, 8.6, 32], GLOW, GLOW_WHITE))
    els.append(box([4, 7.6, 30], [12, 8.4, 32], GLOW_WHITE, GLOW_WHITE))
    els += spike_along(2.7, 30.5, 8, 3.5, 1.0, "x", -1, GLOW, GLOW_WHITE)
    els += spike_along(13.3, 30.5, 8, 3.5, 1.0, "x", 1, GLOW, GLOW_WHITE)
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
