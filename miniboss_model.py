"""The two mini-bosses: the Hollow's Marrow Watcher and the Rimevault's Rime Colossus.

Both are built as limb sets for MobModels (torso, leg, arm), so the plugin can walk them. The head
is part of the torso, as on the Rime Golem; the plugin adds the Watcher's eye glow as particles.
"""
import random

from PIL import Image

# One 32x32 sheet per mini-boss, 4x4 cells.
(DARK, MID, LIGHT, CRACK, GLOW, GLOW_DIM, BONE, RUST,
 ICE_DEEP, ICE_MID, ICE_PALE, SHINE) = range(12)

WATCHER = {
    DARK: (36, 33, 40),             # the stone it is cut from, near black
    MID: (62, 57, 66),
    LIGHT: (92, 85, 96),
    CRACK: (214, 84, 34),           # molten rock showing through the cracks
    GLOW: (255, 148, 64),           # the eye
    GLOW_DIM: (150, 66, 24),
    BONE: (186, 180, 158),
    RUST: (66, 48, 38),
    ICE_DEEP: (30, 28, 32),
    ICE_MID: (40, 36, 42),
    ICE_PALE: (58, 52, 60),
    SHINE: (120, 112, 120),
}

COLOSSUS = {
    DARK: (54, 62, 76),             # frozen stone
    MID: (92, 102, 118),
    LIGHT: (138, 150, 166),
    CRACK: (150, 214, 240),
    GLOW: (206, 246, 255),
    GLOW_DIM: (150, 204, 232),
    BONE: (214, 236, 248),
    RUST: (38, 78, 112),
    ICE_DEEP: (22, 48, 76),
    ICE_MID: (70, 130, 176),
    ICE_PALE: (168, 214, 240),
    SHINE: (236, 250, 255),
}

GLOWING = {GLOW, CRACK, SHINE}


def texture(palette, seed):
    img = Image.new("RGBA", (32, 32))
    px = img.load()
    rnd = random.Random(seed)
    for cellid, (r, g, b) in palette.items():
        cx, cy = (cellid % 8) * 4, (cellid // 8) * 4
        for x in range(cx, cx + 4):
            for y in range(cy, cy + 4):
                n = 0 if cellid in GLOWING else rnd.randint(-11, 11)
                if (x - cx) + (y - cy) < 2 and cellid not in GLOWING:
                    n += 14                      # light catches the top-left of every face
                px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)),
                            max(0, min(255, b + n)), 255)
    return img


def uv(cellid):
    cx, cy = (cellid % 8) * 2, (cellid // 8) * 2
    return [cx, cy, cx + 2, cy + 2]


def box(frm, to, side, top=None, rotation=None):
    top = top if top is not None else side
    faces = {f: {"uv": uv(side), "texture": "#main"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": uv(top), "texture": "#main"}
    faces["down"] = {"uv": uv(side), "texture": "#main"}
    element = {"from": frm, "to": to, "faces": faces}
    if rotation:
        element["rotation"] = rotation
    return element


# ---------------------------------------------------------------- the Marrow Watcher
# Same layout as the Rime Golem's limb set: the torso hinges at the hips (y 8) and builds up, with
# its head on top; legs and arms hang down from their hinge at the model centre. The plugin puts the
# hip and shoulder joints there and swings them.

def watcher_torso():
    """Hunched, cracked, and topped with a head that is mostly eye."""
    return [
        box([4, 8, 4], [12, 10.5, 11], DARK, MID),                  # hips
        box([2, 10, 3], [14, 21, 12], MID, LIGHT),                  # chest slab
        box([3, 21, 4], [13, 23.5, 11], DARK, MID),                 # hunched shoulders
        box([0.5, 19.5, 3.5], [3.5, 23.5, 11.5], LIGHT, LIGHT),     # shoulder blocks
        box([12.5, 19.5, 3.5], [15.5, 23.5, 11.5], LIGHT, LIGHT),
        # Molten cracks showing through the stone, front and back.
        box([3.5, 14, 2.6], [12.5, 15.4, 3.2], CRACK, CRACK),
        box([6, 15.4, 2.6], [7.4, 19.5, 3.2], CRACK, CRACK),
        box([9, 10.5, 2.6], [10.4, 14, 3.2], CRACK, CRACK),
        box([4.5, 12.5, 11.8], [11.5, 13.8, 12.4], CRACK, CRACK),
        # A twisted spine of bone up the back, leaning with the hunch.
        box([7, 15, 11.5], [9, 23, 13], BONE, BONE,
            rotation={"origin": [8, 15, 12], "axis": "x", "angle": -22.5}),
        box([5.5, 20, 11.5], [7, 22.5, 12.6], BONE, BONE),
        box([9.5, 18, 11.5], [11, 20.5, 12.6], BONE, BONE),
        box([2.6, 10, 4.5], [3.4, 17, 10.5], RUST, RUST),           # rusted banding
        box([12.6, 10, 4.5], [13.4, 17, 10.5], RUST, RUST),
        # The head: a stone skull with one giant burning eye filling the face.
        box([4, 23, 4], [12, 30, 12], MID, LIGHT),
        box([5, 30, 5], [11, 31.6, 11], DARK, MID),                 # crown
        box([3.4, 28, 3.4], [12.6, 29.2, 12], LIGHT, LIGHT),        # heavy brow ridge
        box([4.3, 23.6, 3.3], [11.7, 28.2, 4.2], GLOW_DIM, GLOW_DIM),  # socket
        box([4.9, 24.4, 2.6], [11.1, 27.4, 3.4], GLOW, GLOW),       # the eye
        box([5.9, 27.4, 2.8], [10.1, 28, 3.4], GLOW, GLOW),         # rounded top
        box([5.9, 23.8, 2.8], [10.1, 24.4, 3.4], GLOW, GLOW),       # rounded bottom
        box([6.6, 25.1, 2.1], [9.4, 26.7, 2.7], SHINE, SHINE),      # its white-hot core
        box([2, 27, 6], [3.8, 31, 9], BONE, BONE,                   # horns
            rotation={"origin": [3.8, 27, 7.5], "axis": "z", "angle": 22.5}),
        box([12.2, 27, 6], [14, 31, 9], BONE, BONE,
            rotation={"origin": [12.2, 27, 7.5], "axis": "z", "angle": -22.5}),
    ]


def watcher_leg():
    return [
        box([6, 6, 6], [10, 9.5, 10], DARK, MID),                   # hip joint
        box([5.5, 0, 5.5], [10.5, 7, 10.5], MID, LIGHT),            # thigh
        box([6, -0.5, 5.2], [10, 0.5, 5.6], CRACK, CRACK),          # crack at the knee
        box([6, -4.5, 6], [10, 0, 10], DARK, MID),                  # shin
        box([5, -6, 4], [11, -4.5, 11], LIGHT, LIGHT),              # foot
        box([5.2, 1, 6.5], [5.6, 6, 9.5], RUST, RUST),
    ]


def watcher_arm():
    return [
        box([5.6, 5.6, 5.6], [10.4, 10.4, 10.4], DARK, MID),        # shoulder
        box([6, -2, 6], [10, 6, 10], MID, LIGHT),                   # upper arm
        box([6.2, -3, 5.7], [9.8, -2, 6.1], CRACK, CRACK),          # crack at the elbow
        box([6.2, -9, 6.2], [9.8, -2, 9.8], DARK, MID),             # forearm
        box([4.8, -14, 4.8], [11.2, -9, 11.2], LIGHT, LIGHT),       # a fist like a boulder
        box([4.2, -13.5, 5.5], [4.9, -10, 10.5], BONE, BONE),       # knuckle spurs
        box([11.1, -13.5, 5.5], [11.8, -10, 10.5], BONE, BONE),
    ]


# ---------------------------------------------------------------- the Rime Colossus
# Heavy and square, grown over with ice, with a small head sunk between huge shoulders.

def colossus_torso():
    return [
        box([3.5, 8, 3.5], [12.5, 11, 11.5], DARK, MID),            # hips
        box([1.5, 10.5, 2.5], [14.5, 22, 12.5], MID, LIGHT),        # a slab of a chest
        box([2.5, 22, 3.5], [13.5, 24.5, 11.5], DARK, MID),         # shoulder yoke
        box([-0.5, 19, 2.5], [2.5, 24.5, 12.5], LIGHT, ICE_PALE),   # shoulder blocks
        box([13.5, 19, 2.5], [16.5, 24.5, 12.5], LIGHT, ICE_PALE),
        # Ice grown over the front, heaviest at the top.
        box([3, 15, 1.8], [13, 20.5, 2.6], ICE_PALE, GLOW),
        box([5.5, 20, 0.8], [7.5, 24, 2], ICE_PALE, GLOW,
            rotation={"origin": [6.5, 20, 1.4], "axis": "z", "angle": -22.5}),
        box([8.5, 20.5, 0.8], [10.5, 25, 2], ICE_PALE, GLOW,
            rotation={"origin": [9.5, 20.5, 1.4], "axis": "z", "angle": 22.5}),
        # A ridge of ice down the back.
        box([6.5, 18, 12.5], [9.5, 23, 14.5], ICE_MID, ICE_PALE),
        box([6.8, 23, 12.8], [9.2, 26, 14], ICE_PALE, GLOW),
        box([4, 12, 12.5], [6, 16, 13.8], ICE_MID, ICE_PALE),
        box([10, 12, 12.5], [12, 16, 13.8], ICE_MID, ICE_PALE),
        box([2, 10.5, 3], [3, 19, 12], ICE_DEEP, ICE_DEEP),         # dark seams down the sides
        box([13, 10.5, 3], [14, 19, 12], ICE_DEEP, ICE_DEEP),
        # Head, low between the shoulders.
        box([5, 24, 4.5], [11, 29.5, 10.5], ICE_DEEP, ICE_MID),
        box([4.6, 27.5, 4], [11.4, 28.6, 5], LIGHT, LIGHT),         # brow
        box([5.8, 26, 4], [7.2, 27, 4.6], GLOW, GLOW),              # eyes
        box([8.8, 26, 4], [10.2, 27, 4.6], GLOW, GLOW),
        box([6, 29.5, 6], [10, 31.5, 10], ICE_PALE, GLOW),          # crown of ice
    ]


def colossus_leg():
    return [
        box([5.5, 6, 5.5], [10.5, 9.5, 10.5], DARK, MID),           # hip
        box([4.8, 0, 4.8], [11.2, 7, 11.2], MID, LIGHT),            # thigh, thick as a pillar
        box([4.4, -1, 4], [11.6, 0.8, 5], ICE_PALE, GLOW),          # ice across the knee
        box([5.2, -4.5, 5.2], [10.8, 0, 10.8], DARK, MID),          # shin
        box([4, -6, 3], [12, -4.5, 12], LIGHT, ICE_PALE),           # slab of a foot
        box([4.6, -6, 2.2], [11.4, -4.8, 3.1], ICE_MID, ICE_PALE),  # frozen toe
    ]


def colossus_arm():
    return [
        box([5.2, 5.2, 5.2], [10.8, 10.8, 10.8], DARK, MID),        # shoulder
        box([5.4, -2, 5.4], [10.6, 6, 10.6], MID, LIGHT),           # upper arm
        box([5, -3.5, 5], [11, -1.5, 11], ICE_MID, ICE_PALE),       # band at the elbow
        box([5.6, -9.5, 5.6], [10.4, -3.5, 10.4], DARK, MID),       # forearm
        box([3.8, -14, 3.8], [12.2, -9.5, 12.2], LIGHT, ICE_PALE),  # fist
        # The ice it hits with, grown out over the knuckles.
        box([3.2, -15.5, 4.5], [6, -13, 11.5], ICE_PALE, GLOW),
        box([10, -15.5, 4.5], [12.8, -13, 11.5], ICE_PALE, GLOW),
        box([6, -16, 6], [10, -14, 10], ICE_MID, GLOW),
    ]


PARTS = {
    "watcher_torso": watcher_torso,
    "watcher_leg": watcher_leg,
    "watcher_arm": watcher_arm,
    "colossus_torso": colossus_torso,
    "colossus_leg": colossus_leg,
    "colossus_arm": colossus_arm,
}
