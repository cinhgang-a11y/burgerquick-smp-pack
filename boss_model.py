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

PARTS = ["tyrant_body", "tyrant_neck", "tyrant_head", "tyrant_wing_l", "tyrant_wing_r",
         "tyrant_tail", "tyrant_tail_tip",
         "wyrm_head", "wyrm_segment", "wyrm_tail",
         "choir_skull", "famine_body", "famine_arm",
         "brute_torso", "brute_leg", "brute_arm"]

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
    """Starved: a thin blackened core with the skeleton pushing out through it."""
    els = [
        box([6.6, 7, -16], [9.4, 10.8, 28], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK),     # shrunken core
        box([6.9, 6.6, -12], [9.1, 7.3, 22], BELLY, BELLY, BELLY),                      # sagging belly strip
        box([6.4, 10.6, -14], [9.6, 11.6, 26], SCALE_DARK, SCALE_BLACK),                # hide over the spine
    ]
    # Rib cage: every rib stands proud of the body, with the dark hollow showing between them.
    for z in range(-13, 18, 3):
        for x0, x1 in ((4.7, 6.3), (9.7, 11.3)):
            els.append(box([x0, 6.6, z], [x1, 11, z + 1.1], BONE_LIGHT, BONE, BONE_DARK))       # rib
            els.append(box([x0 + 0.2, 6.1, z + 0.1], [x1 - 0.2, 7, z + 1], BONE, BONE_LIGHT))   # lower tip
        els.append(box([6.2, 10.7, z], [9.8, 11.7, z + 1.1], BONE, BONE_LIGHT, BONE_DARK))      # over the back
    # Spine: a row of knobbly vertebrae with spikes growing out of them.
    for i, z in enumerate(range(-14, 27, 2)):
        els.append(box([7.2, 11.4, z], [8.8, 12.6, z + 1.3], BONE_LIGHT, BONE, BONE_DARK))
        if i % 2 == 0:
            tall = 7 - abs(i - 7) * 0.3
            if i % 4 == 0:
                els += spike(8, z + 0.6, 12.5, tall, 0.85, GLOW, GLOW_WHITE)
            else:
                els += spike(8, z + 0.6, 12.5, tall * 0.8, 0.9, SPIKE, BONE_LIGHT)
    # Shoulder blades and hip bones jutting out of the hide.
    for x0, x1, side in ((3.6, 6.4, -1), (9.6, 12.4, 1)):
        for z0 in (-13, 13):
            els.append(box([x0, 9.5, z0], [x1, 13.4, z0 + 6], BONE, BONE_LIGHT, BONE_DARK))
            els.append(box([x0 + 0.3, 11, z0 + 1.2], [x1 - 0.3, 12.6, z0 + 4.8], BONE_DARK, BONE))
            els += spike_along(x1 if side > 0 else x0, z0 + 3, 12, 6, 1.1, "x", side, HORN, BONE_LIGHT)
    # Four long, heavy legs: thick bones with knobbly joints and big clawed feet.
    for x0 in (3.6, 9.8):
        for z0 in (-12, 14):
            els.append(box([x0, 3, z0], [x0 + 2.6, 8.8, z0 + 3.4], SCALE_BLACK))                    # thigh
            els.append(box([x0 - 0.4, 7.6, z0 - 0.3], [x0 + 3, 9.8, z0 + 3.7], BONE, BONE_LIGHT))   # hip joint
            els.append(box([x0 - 0.3, 2.1, z0 - 0.2], [x0 + 2.9, 4.1, z0 + 3.6], BONE, BONE_LIGHT)) # knee
            els.append(box([x0 + 0.3, -11, z0 + 0.5], [x0 + 2.3, 3, z0 + 2.9], SCALE_BLACK))        # shin
            els.append(box([x0 + 0.45, -10.6, z0 + 0.65], [x0 + 2.15, 2.4, z0 + 1.75], BONE_DARK, BONE))
            els.append(box([x0 - 0.5, -12.6, z0 - 1.2], [x0 + 3.1, -10.8, z0 + 4], SCALE_BLACK, SCALE_BLACK, BONE_DARK))
            for c in range(3):
                cx = x0 - 0.3 + c * 1.3
                els.append(box([cx, -12.8, z0 - 3.4], [cx + 0.9, -11.2, z0 - 0.6], CLAW, BONE_LIGHT))
    return els


def neck():
    """The neck is its own part so it can be long: hinged at the body end, growing forward (-Z)."""
    els = []
    segments = [(15, 9, 2.7), (9, 3, 2.45), (3, -3, 2.2), (-3, -9, 1.95), (-9, -15.5, 1.75)]
    for i, (z0, z1, half) in enumerate(segments):
        els.append(box([8 - half, 8 - half, z1], [8 + half, 8 + half, z0], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK))
        els.append(box([8 - half + 0.3, 8 - half - 0.5, z1 + 0.5], [8 + half - 0.3, 8 - half + 0.4, z0 - 0.5],
                       BELLY, BELLY, BELLY))                                    # throat
        v = half + 0.85
        els.append(box([8 - v, 8 - v * 0.7, z1], [8 + v, 8 + v, z1 + 1.5], BONE_LIGHT, BONE, BONE_DARK))  # vertebra
        mid = (z0 + z1) / 2
        if i % 2:
            els += spike(8, mid, 8 + v - 0.3, 4.5 - i * 0.3, 0.8, SPIKE, BONE_LIGHT)
        else:
            els += spike(8, mid, 8 + v - 0.3, 5 - i * 0.3, 0.75, GLOW, GLOW_WHITE)
        els += spike_along(8 - half, mid, 8, 2.6, 0.6, "x", -1, SPIKE, BONE_LIGHT)
        els += spike_along(8 + half, mid, 8, 2.6, 0.6, "x", 1, SPIKE, BONE_LIGHT)
    return els


def tail_tip():
    """Carries on from where tyrant_tail ends, out to the blade."""
    els = []
    spans = [(-12, -5, 1.3), (-5, 2, 1.15), (2, 9, 1.0), (9, 15, 0.85), (15, 21, 0.7),
             (21, 26, 0.58), (26, 30, 0.45)]
    for i, (z0, z1, half) in enumerate(spans):
        els.append(box([8 - half, 8 - half, z0], [8 + half, 8 + half, z1], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK))
        v = half + 0.6
        els.append(box([8 - v, 8 - v * 0.7, z0 + 0.2], [8 + v, 8 + v, z0 + 1.2], BONE_LIGHT, BONE, BONE_DARK))
        mid = (z0 + z1) / 2
        if i % 2:
            els += spike(8, mid, 8 + v - 0.3, 3.6 - i * 0.3, half * 0.5, SPIKE, BONE_LIGHT)
        else:
            els += spike(8, mid, 8 + v - 0.3, 4 - i * 0.3, half * 0.45, GLOW, GLOW_WHITE)
        if i % 2 == 0:
            els += spike_along(8 - half, mid, 8, 3, 0.6, "x", -1, SPIKE, BONE_LIGHT)
            els += spike_along(8 + half, mid, 8, 3, 0.6, "x", 1, SPIKE, BONE_LIGHT)
    els.append(box([2.5, 7.5, 29], [13.5, 8.5, 32], GLOW, GLOW_WHITE))          # the blade
    els.append(box([4, 7.7, 30.5], [12, 8.3, 32], GLOW_WHITE, GLOW_WHITE))
    els += spike_along(2.7, 30.8, 8, 3.5, 1.0, "x", -1, GLOW, GLOW_WHITE)
    els += spike_along(13.3, 30.8, 8, 3.5, 1.0, "x", 1, GLOW, GLOW_WHITE)
    return els


def head():
    """A long starved neck of bare vertebrae and a gaunt skull with sunken cheeks."""
    els = [
        box([6.6, 6.6, -3], [9.4, 9.8, 5], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK),      # skull base, meets the neck
        box([4.2, 5, -14], [11.8, 11.8, -2], SCALE_DARK, SCALE_BLACK, SCALE_DARK),      # skull
        box([3.8, 8.4, -14.6], [12.2, 12.2, -3], BONE_LIGHT, BONE, BONE_DARK),          # bone mask
        box([4.6, 11.8, -12], [11.4, 12.8, -4], BONE, BONE_LIGHT),                      # crest plate
        box([5.4, 4.8, -15.8], [10.6, 8.8, -14], SCALE_DARK, SCALE_MID),                # snout
        box([5.2, 8.2, -16], [10.8, 9.4, -13], BONE_LIGHT, BONE, BONE_DARK),            # snout bone
        box([5, 2.4, -15.5], [11, 4.8, -4], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK),     # lower jaw
        box([5.2, 4.4, -15.6], [10.8, 5.2, -5], BONE_LIGHT, BONE),                      # jaw bone
        box([4.4, 5.6, -13.5], [5.2, 8.6, -6], BONE, BONE_LIGHT, BONE_DARK),            # cheekbones
        box([10.8, 5.6, -13.5], [11.6, 8.6, -6], BONE, BONE_LIGHT, BONE_DARK),
        box([5.2, 5.8, -12.6], [5.9, 8.2, -7], SCALE_BLACK, SCALE_BLACK),               # hollow cheeks
        box([10.1, 5.8, -12.6], [10.8, 8.2, -7], SCALE_BLACK, SCALE_BLACK),
        box([4.5, 7.6, -12.4], [5.1, 10.4, -7.4], SCALE_BLACK, SCALE_BLACK),            # sunken eye sockets
        box([10.9, 7.6, -12.4], [11.5, 10.4, -7.4], SCALE_BLACK, SCALE_BLACK),
        box([4.3, 8.4, -11.6], [4.8, 9.8, -8.4], EYE),                                  # eyes deep inside
        box([11.2, 8.4, -11.6], [11.7, 9.8, -8.4], EYE),
        box([4.1, 10.2, -12.6], [5.6, 11.6, -7], BONE_LIGHT, BONE),                     # brow ridges
        box([10.4, 10.2, -12.6], [11.9, 11.6, -7], BONE_LIGHT, BONE),
        box([5.9, 7.2, -16], [6.8, 8, -15.8], GLOW),                                    # nostrils
        box([9.2, 7.2, -16], [10.1, 8, -15.8], GLOW),
    ]
    # The joint where the neck plugs in.
    els.append(box([6.1, 6.1, 2.5], [9.9, 10.3, 4.5], BONE_LIGHT, BONE, BONE_DARK))
    # Teeth: bared along both jaws, with two long tusks.
    for i in range(5):
        x = 5.4 + i * 1.1
        els.append(box([x, 3.7, -15.2], [x + 0.7, 4.9, -13.8], BONE_LIGHT, BONE))
        els.append(box([x, 4.2, -13.4], [x + 0.6, 5, -12.2], BONE_LIGHT, BONE))
        els.append(box([x + 0.2, 4.4, -11.6], [x + 0.7, 5.2, -10.4], BONE, BONE_LIGHT))
    for x in (5.4, 9.9):
        els.append(box([x, 2.6, -15.2], [x + 0.9, 5, -13.2], BONE_LIGHT, BONE))
    # Horns: long, swept back, with cheek and jaw spikes.
    for x, s in ((4.2, -1), (11.8, 1)):
        els.append(box([min(x, x + s * 2), 11.6, -9], [max(x, x + s * 2), 14.4, -5], HORN, BONE_LIGHT))
        els += spike_along(x + s * 1.2, -3, 13.8, 12, 1.3, "z", 1, HORN, BONE_LIGHT)
        els.append(box([min(x + s * 0.2, x + s * 1.6), 9.4, -12.6], [max(x + s * 0.2, x + s * 1.6), 11.2, -10], HORN, BONE_LIGHT))
        els += spike_along(x + s * 0.7, -11.2, 10.2, 5, 0.85, "x", s, HORN, BONE_LIGHT)
        els += spike_along(x + s * 0.3, -6, 6.4, 4.5, 0.75, "x", s, SPIKE, BONE_LIGHT)
    for i, z in enumerate((-11.5, -8.5, -5.5)):                                         # crown
        els += spike(8, z, 12.7, 7 - i * 0.8, 0.95, GLOW, GLOW_WHITE)
    return els


def wing_right():
    """Right wing: long and slender, grown toward +X from the hinge at the model centre.

    Built like a real wing - shoulder, humerus, elbow, two forearm bones, a wrist with a claw, then
    finger spars carrying a membrane whose chord shrinks toward the tip. The whole thing is under a
    unit thick, so it reads as a wing and not a slab.
    """
    els = [
        box([8, 7.1, -2.2], [12, 8.9, 1.4], SCALE_BLACK, SCALE_BLACK),                  # wasted shoulder
        box([8.5, 7.5, -1.4], [15, 8.5, 0.6], BONE_LIGHT, BONE, BONE_DARK),             # humerus
        box([14.3, 7.2, -1.8], [16.1, 8.8, 1.1], BONE, BONE_LIGHT),                     # elbow knob
        box([16, 7.6, -1.7], [23, 8.4, -0.7], BONE_LIGHT, BONE, BONE_DARK),             # radius
        box([16, 7.6, 0.2], [23, 8.4, 1.2], BONE_LIGHT, BONE, BONE_DARK),               # ulna
        box([22.4, 7.2, -1.9], [24.1, 8.8, 1.5], BONE, BONE_LIGHT),                     # wrist
        box([23.4, 7, -3.6], [26, 9, -1.7], CLAW, BONE_LIGHT),                          # wrist claw
        box([24, 7.6, -1.5], [32, 8.4, -0.5], BONE_LIGHT, BONE, BONE_DARK),             # leading spar
    ]
    els += spike_along(25.6, -2.6, 8, 3.2, 0.75, "x", 1, CLAW, BONE_LIGHT)              # claw tip
    # Membrane: four panels, the chord shrinking toward the tip. Thin - 0.3 of a unit.
    panels = [(9, 16, 10), (16, 22, 8), (22, 27.5, 6), (27.5, 31.1, 3.8)]
    for i, (x0, x1, chord) in enumerate(panels):
        els.append(box([x0, 7.85, 0.6], [x1, 8.15, chord], MEMBRANE, MEMBRANE, MEMBRANE_EDGE))
        els.append(box([x0, 7.8, chord - 0.6], [x1, 8.2, chord], MEMBRANE_EDGE, MEMBRANE_EDGE))  # rim
        # Finger spar along the panel's outer edge, with a knuckle where it meets the arm.
        els.append(box([x1 - 0.45, 7.65, -0.5], [x1 + 0.45, 8.35, chord], BONE_LIGHT, BONE, BONE_DARK))
        els.append(box([x1 - 0.75, 7.45, -0.3], [x1 + 0.75, 8.55, 1.2], BONE, BONE_LIGHT))       # knuckle
        # Scalloped, torn trailing edge.
        steps = 3
        for k in range(steps):
            sx = x0 + (x1 - x0) * k / steps
            ex = sx + (x1 - x0) / steps * 0.62
            drop = 1.5 - i * 0.25
            els.append(box([sx, 7.87, chord], [ex, 8.13, chord + drop], MEMBRANE_EDGE, MEMBRANE_EDGE))
    # Glowing veins running out along the membrane.
    els.append(box([9, 8.15, 1.6], [30, 8.28, 2.2], GLOW))
    els.append(box([12, 8.15, 4.4], [26, 8.26, 4.9], GLOW))
    els.append(box([17, 8.15, 6.6], [23.5, 8.26, 7], GLOW))
    # Small barbs along the leading edge.
    for x in (13, 18, 24, 29):
        els += spike_along(x, -1.8, 8, 2.6, 0.55, "z", -1, SPIKE, BONE_LIGHT)
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



# ---------------------------------------------------------------- the Gravebound Wyrm
# A burrowing thing: an armoured ring of a head with mandibles, a body of repeated segments, and a
# tail that ends in a stinger. Shares the tyrant texture - same bones, same crystal.


def wyrm_head():
    """Blunt armoured skull, hinged at the model centre, facing -Z like everything else."""
    els = [
        box([3, 3, -4], [13, 13, 8], SCALE_DARK, SCALE_BLACK, BELLY),               # skull
        box([2.4, 4, -2], [13.6, 12, 6], BONE, BONE_LIGHT, BONE_DARK),              # armour band
        box([4, 4, -8], [12, 12, -4], SCALE_BLACK, SCALE_BLACK),                    # snout ring
    ]
    # The maw: a glowing ring of teeth you can see down.
    for i in range(12):
        a = 2 * 3.14159 * i / 12
        cx = 8 + 3.4 * __import__("math").cos(a)
        cy = 8 + 3.4 * __import__("math").sin(a)
        els.append(box([cx - 0.7, cy - 0.7, -9.4], [cx + 0.7, cy + 0.7, -7.4], BONE_LIGHT, BONE))
    els.append(box([5.6, 5.6, -8.6], [10.4, 10.4, -7.8], GLOW, GLOW_WHITE))         # gullet
    # Four mandibles spreading off the snout.
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        bx, by = 8 + dx * 5, 8 + dy * 5
        for s in range(4):
            w = 1.6 - s * 0.3
            els.append(box([bx - w + dx * s * 0.6, by - w + dy * s * 0.6, -9 - s * 1.8],
                           [bx + w + dx * s * 0.9, by + w + dy * s * 0.9, -7.4 - s * 1.8],
                           HORN if s < 3 else BONE_LIGHT, BONE_LIGHT))
    # Eyes set back in the armour.
    for dx in (-1, 1):
        ex = 8 + dx * 4.6
        els.append(box([min(ex, ex + dx * 0.6), 9.5, -3], [max(ex, ex + dx * 0.6), 11, -0.5], EYE))
    # Plates and spikes over the top.
    for z in (-2, 2, 6):
        els += spike(8, z, 13, 3.5, 1.0, SPIKE, BONE_LIGHT)
        els.append(box([4, 12.6, z - 1], [12, 13.6, z + 1], BONE_DARK, BONE))
    return els


def wyrm_segment():
    """One body ring: armour plates around a softer core, with barbs. Repeated down the body."""
    els = [
        box([4, 4, -5], [12, 12, 5], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK),        # core
        box([3.2, 3.2, -3.5], [12.8, 12.8, 3.5], SCALE_MID, SCALE_DARK, BELLY),     # muscle
        box([2.6, 4.6, -2.5], [13.4, 11.4, 2.5], BONE, BONE_LIGHT, BONE_DARK),      # armour ring
        box([4.6, 2.6, -2.5], [11.4, 13.4, 2.5], BONE, BONE_LIGHT, BONE_DARK),
    ]
    # Barbs at the four corners of the ring, angled outward.
    for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        for s in range(3):
            w = 1.3 - s * 0.35
            els.append(box([8 + dx * (4.5 + s * 1.4) - w, 8 + dy * (4.5 + s * 1.4) - w, -1 - w],
                           [8 + dx * (4.5 + s * 1.4) + w, 8 + dy * (4.5 + s * 1.4) + w, 1 + w],
                           SPIKE if s < 2 else BONE_LIGHT, BONE_LIGHT))
    els.append(box([7, 7, -5.2], [9, 9, -4.8], GLOW))                               # light between rings
    return els


def wyrm_tail():
    """Tapers away to a stinger."""
    els = []
    spans = [(-6, 0, 3.6), (0, 6, 2.9), (6, 12, 2.2), (12, 18, 1.6), (18, 23, 1.1)]
    for i, (z0, z1, half) in enumerate(spans):
        els.append(box([8 - half, 8 - half, z0], [8 + half, 8 + half, z1], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK))
        els.append(box([8 - half - 0.5, 8 - half + 0.6, z0 + 0.3], [8 + half + 0.5, 8 + half - 0.6, z0 + 1.6],
                       BONE, BONE_LIGHT, BONE_DARK))
        if i % 2 == 0:
            els += spike(8, (z0 + z1) / 2, 8 + half, 3 - i * 0.4, half * 0.4, SPIKE, BONE_LIGHT)
    # The stinger.
    for s in range(4):
        w = 1.0 - s * 0.22
        els.append(box([8 - w, 8 - w, 23 + s * 2], [8 + w, 8 + w, 25 + s * 2],
                       GLOW if s % 2 == 0 else HORN, GLOW_WHITE))
    return els



# ---------------------------------------------------------------- the Ossuary Choir
# Floating skulls that sing. Small, so several can hang in the air at once.


def choir_skull():
    """A skull that floats and sings. Hinge at the model centre; it faces -Z like everything else."""
    els = [
        box([4, 5.5, -5], [12, 13, 5], SCALE_BLACK, SCALE_BLACK, SCALE_DARK),       # cranium core
        box([3.5, 6, -5.6], [12.5, 12.6, 4.6], BONE_LIGHT, BONE, BONE_DARK),        # bone shell
        box([4.4, 12.4, -4.6], [11.6, 13.6, 3.6], BONE, BONE_LIGHT),                # crown
        box([4.8, 5, -6.4], [11.2, 9.8, -5], BONE_LIGHT, BONE),                     # muzzle
        box([5.2, 4.9, -7.2], [10.8, 8.6, -6.2], BONE, BONE_LIGHT),
        box([4.6, 3.2, -6.8], [11.4, 5.2, 3], SCALE_BLACK, BONE_DARK, SCALE_BLACK), # jaw
        box([4.8, 3.6, -6.6], [11.2, 5, 1], BONE_LIGHT, BONE),                      # jaw bone
        box([3.2, 9.6, -5.2], [4.4, 12, 1], BONE, BONE_LIGHT),                      # cheek arches
        box([11.6, 9.6, -5.2], [12.8, 12, 1], BONE, BONE_LIGHT),
    ]
    # Sunken sockets with the light still in them.
    for dx in (-1, 1):
        ex = 8 + dx * 2
        els.append(box([min(ex, ex + dx * 2.2), 8.2, -6.2], [max(ex, ex + dx * 2.2), 11.2, -4.4],
                       SCALE_BLACK, SCALE_BLACK))
        els.append(box([min(ex + dx * 0.4, ex + dx * 1.6), 8.8, -6.4],
                       [max(ex + dx * 0.4, ex + dx * 1.6), 10.4, -5.6], GLOW))
    for i in range(6):                                                              # teeth
        x = 5 + i * 1.05
        els.append(box([x, 5, -6.4], [x + 0.65, 6.4, -5.4], BONE_LIGHT, BONE))      # upper
        els.append(box([x, 3.6, -6.2], [x + 0.6, 4.9, -5.2], BONE, BONE_LIGHT))     # lower
    for z in (-3, 0.5, 4):                                                          # crown horns
        els += spike(8, z, 13.4, 4 - abs(z) * 0.2, 0.9, HORN, BONE_LIGHT)
    for side in (-1, 1):                                                            # side horns sweeping back
        els += spike_along(8 + side * 5.5, 0, 11, 5, 1.0, "x", side, HORN, BONE_LIGHT)
    return els


def famine_body():
    """A starved giant, hinged at the hips: legs reach down 22, shoulders sit 20 above."""
    math = __import__("math")
    els = [
        box([5, 6, 5.5], [11, 11, 10.5], SCALE_BLACK, SCALE_BLACK, BELLY),          # pelvis
        box([4.4, 5.6, 5], [11.6, 9, 11], BONE, BONE_LIGHT, BONE_DARK),             # hip bone
        box([6.5, 10, 6.5], [9.5, 28, 9.5], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK), # spine
        box([2.5, 25.5, 5.5], [13.5, 28.5, 10.5], BONE, BONE_LIGHT, BONE_DARK),     # shoulder yoke
        box([3.5, 24, 6], [12.5, 26, 10], BONE_DARK, BONE),
        box([7.3, 14, 4.6], [8.7, 22, 5.4], GLOW),                                  # the hunger in it
    ]
    # Ribcage: dense arcs off the spine, so they actually join it.
    for i, y in enumerate(range(12, 25, 3)):
        reach = 4.6 - abs(i - 2) * 0.45
        for side in (-1, 1):
            steps = 12
            for st in range(steps + 1):
                t = st / steps
                dx = side * reach * math.sin(t * 1.9)
                dz = -3.6 * math.sin(t * 2.4)
                dy = y + math.sin(t * 1.2) * 1.6
                els.append(box([8 + dx - 0.5, dy - 0.5, 8 + dz - 0.5],
                               [8 + dx + 0.5, dy + 0.5, 8 + dz + 0.5],
                               BONE_LIGHT if st < steps - 2 else BONE, BONE))
        els.append(box([7.2, y - 0.6, 7.2], [8.8, y + 0.6, 8.8], BONE, BONE_LIGHT))  # vertebra
    # Legs down to the ground, with knees and long feet.
    for side in (-1, 1):
        lx = 8 + side * 2.4
        els.append(box([min(lx, lx + side * 2), -4, 6.5], [max(lx, lx + side * 2), 7, 9.5],
                       SCALE_BLACK, SCALE_BLACK))                                    # thigh
        els.append(box([min(lx - side * 0.4, lx + side * 2.4), -5.5, 6],
                       [max(lx - side * 0.4, lx + side * 2.4), -3.5, 10], BONE, BONE_LIGHT))  # knee
        els.append(box([min(lx + side * 0.2, lx + side * 1.8), -13.5, 7],
                       [max(lx + side * 0.2, lx + side * 1.8), -4.5, 9], SCALE_BLACK, SCALE_BLACK))
        els.append(box([min(lx + side * 0.35, lx + side * 1.65), -13.1, 7.2],
                       [max(lx + side * 0.35, lx + side * 1.65), -5, 8.2], BONE_DARK, BONE))  # shin bone
        els.append(box([min(lx - side * 0.6, lx + side * 2.6), -15.5, 5.5],
                       [max(lx - side * 0.6, lx + side * 2.6), -13, 11.5], BONE, BONE_LIGHT))  # foot
        for toe in range(3):
            tx = lx - side * 0.4 + side * toe * 1.1
            els.append(box([min(tx, tx + side * 0.8), -15.7, 3.6],
                           [max(tx, tx + side * 0.8), -14.1, 5.8], CLAW, BONE_LIGHT))
    for y in (14, 19, 24):                                                          # spine spikes
        els += spike(8, 10.2, y, 3, 0.8, SPIKE, BONE_LIGHT)
    return els


def famine_arm():
    """One arm, hinged at the shoulder: hangs 22 down, ending in a grabbing hand."""
    els = [
        box([6.6, 6.6, 6.6], [9.4, 9.4, 9.4], BONE, BONE_LIGHT),                    # shoulder ball
        box([7, -3, 7], [9, 8, 9], SCALE_BLACK, SCALE_BLACK),                       # upper arm
        box([7.2, -2.6, 7.2], [8.8, 7, 8.8], BONE_DARK, BONE),
        box([6.6, -5, 6.6], [9.4, -2.5, 9.4], BONE, BONE_LIGHT),                    # elbow
        box([7.2, -13, 7.2], [8.8, -4.5, 8.8], SCALE_BLACK, SCALE_BLACK),           # forearm
        box([7.4, -12.6, 7.4], [8.6, -5, 8.6], BONE_DARK, BONE),
        box([6.2, -15.5, 6.2], [9.8, -12.5, 9.8], BONE, BONE_LIGHT),                # hand
    ]
    for dx, dz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):                             # fingers
        for st in range(3):
            w = 0.5 - st * 0.1
            cx = 8 + dx * (1.2 + st * 0.55)
            cz = 8 + dz * (1.2 + st * 0.55)
            els.append(box([cx - w, -15.9, cz - w], [cx + w, -14.2 + st * 0.4, cz + w],
                           CLAW, BONE_LIGHT))
    return els


def brute_torso():
    """Torso, shoulders and head, hinged at the hips. Shoulders sit 14 above the hinge."""
    els = [
        box([4, 8, 5], [12, 22, 11], SCALE_BLACK, SCALE_BLACK, SCALE_BLACK),        # ribs and gut
        box([3.4, 9, 4.4], [12.6, 20, 11.6], BONE, BONE_LIGHT, BONE_DARK),          # chest plate
        box([3, 20, 4], [13, 23, 12], BONE_DARK, BONE),                             # shoulder yoke
        box([5.5, 23, 6], [10.5, 29, 10.5], SCALE_BLACK, SCALE_BLACK),              # head
        box([5, 23.5, 5.4], [11, 28.5, 8], BONE_LIGHT, BONE, BONE_DARK),            # skull mask
        box([5.8, 25, 4.8], [10.2, 27, 5.6], SCALE_BLACK, SCALE_BLACK),             # eye slot
        box([6.3, 25.4, 4.6], [7.3, 26.4, 5.2], EYE),
        box([8.7, 25.4, 4.6], [9.7, 26.4, 5.2], EYE),
        box([6.2, 21, 4.6], [9.8, 23, 6], BONE, BONE_LIGHT),                        # collar
    ]
    for side in (-1, 1):                                                            # horns
        els += spike_along(8 + side * 3, 6.5, 28, 3.5, 0.9, "x", side, HORN, BONE_LIGHT)
    for y in (11, 15, 19):                                                          # back spines
        els += spike(8, 10.6, y, 3, 0.8, SPIKE, BONE_LIGHT)
    return els


def brute_leg():
    """One leg, hinged at the hip: 14 down to the sole."""
    return [
        box([6.4, 6.4, 6.4], [9.6, 9.4, 9.6], BONE, BONE_LIGHT),                    # hip joint
        box([6.6, 0, 6.6], [9.4, 7, 9.4], SCALE_BLACK, SCALE_BLACK),                # thigh
        box([6.8, 0.4, 6.8], [9.2, 6.6, 9.2], BONE_DARK, BONE),
        box([6.4, -2, 6.4], [9.6, 0.5, 9.6], BONE, BONE_LIGHT),                     # knee
        box([6.8, -6.5, 6.8], [9.2, -1.5, 9.2], SCALE_BLACK, SCALE_BLACK),          # shin
        box([6.2, -8, 5.4], [9.8, -6, 10.4], BONE, BONE_LIGHT, BONE_DARK),          # foot
        box([6.6, -8.2, 3.8], [9.4, -6.6, 5.6], CLAW, BONE_LIGHT),                  # toes
    ]


def brute_arm():
    """One arm, hinged at the shoulder: heavy, ends in a fist of bone."""
    return [
        box([6.2, 6.2, 6.2], [9.8, 9.8, 9.8], BONE, BONE_LIGHT),                    # shoulder
        box([6.6, -1, 6.6], [9.4, 7, 9.4], SCALE_BLACK, SCALE_BLACK),               # upper arm
        box([6.8, -0.6, 6.8], [9.2, 6.6, 9.2], BONE_DARK, BONE),
        box([6.4, -3, 6.4], [9.6, -0.5, 9.6], BONE, BONE_LIGHT),                    # elbow
        box([6.8, -8, 6.8], [9.2, -2.5, 9.2], SCALE_BLACK, SCALE_BLACK),            # forearm
        box([5.8, -11, 5.8], [10.2, -7.5, 10.2], BONE, BONE_LIGHT),                 # fist
        box([6.4, -12, 6.4], [9.6, -10.5, 9.6], CLAW, BONE_LIGHT),                  # knuckles
    ]

def elements(part):
    return {
        "tyrant_body": body,
        "tyrant_neck": neck,
        "tyrant_head": head,
        "tyrant_tail_tip": tail_tip,
        "wyrm_head": wyrm_head,
        "wyrm_segment": wyrm_segment,
        "wyrm_tail": wyrm_tail,
        "choir_skull": choir_skull,
        "famine_body": famine_body,
        "famine_arm": famine_arm,
        "brute_torso": brute_torso,
        "brute_leg": brute_leg,
        "brute_arm": brute_arm,
        "tyrant_wing_r": wing_right,
        "tyrant_wing_l": lambda: mirror_x(wing_right()),
        "tyrant_tail": tail,
    }[part]()
