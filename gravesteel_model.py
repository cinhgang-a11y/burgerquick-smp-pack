"""3D models for the gravesteel set: the war hammer and the four armour pieces.

Every piece exists in four frost stages. The ice is not just a palette shift - each stage grows more
crystal on the model itself, so an Everfrost helm is visibly crusted where a plain one is bare
bone-steel. Coordinates are Minecraft model units (16 = one block).
"""
import random

from PIL import Image, ImageDraw

import mace_model

# 32x32 palette of 4x4 cells, same scheme as the other model sheets here.
(PLATE_DARK, PLATE_MID, PLATE_LIGHT, BONE, ICE_MID, ICE_PALE, GLOW, SHADOW,
 RIVET, FROST, RUNE, EDGE) = range(12)
BASE = {
    # The same ramp the gravesteel sprites use - the first pass was so dark the plates read as holes.
    PLATE_DARK: (58, 56, 60),
    PLATE_MID: (104, 100, 94),
    PLATE_LIGHT: (166, 158, 140),
    BONE: (216, 210, 188),
    ICE_MID: (86, 150, 196),
    ICE_PALE: (168, 214, 240),
    GLOW: (198, 240, 255),
    SHADOW: (18, 18, 22),
    RIVET: (176, 170, 150),
    FROST: (226, 244, 255),
    RUNE: (120, 220, 255),
    EDGE: (232, 226, 206),
}
GLOWING = {GLOW, RUNE, FROST}
STAGES = 4


def frozen(colour, stage):
    """Pulls a colour toward the ice as the stage climbs - the same curve the sprites use."""
    if stage <= 0:
        return colour
    weight = stage / (STAGES - 1) * 0.7
    ice = BASE[ICE_PALE] if sum(colour) > 380 else BASE[ICE_MID]
    return tuple(int(colour[i] * (1 - weight) + ice[i] * weight) for i in range(3))


def texture(stage):
    """The palette sheet the armour models sample from."""
    img = Image.new("RGBA", (32, 32))
    px = img.load()
    rnd = random.Random(11 + stage)
    for cellid, colour in BASE.items():
        r, g, b = colour if cellid in (ICE_MID, ICE_PALE, GLOW, FROST, RUNE) else frozen(colour, stage)
        cx, cy = (cellid % 8) * 4, (cellid // 8) * 4
        for x in range(cx, cx + 4):
            for y in range(cy, cy + 4):
                n = 0 if cellid in GLOWING else rnd.randint(-9, 9)
                # Plate cells catch the light on their top-left corner.
                if cellid in (PLATE_MID, PLATE_LIGHT, BONE) and (x - cx) + (y - cy) < 2:
                    n += 18
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


def shard(x, y, z, size, tall, cell=ICE_PALE, angle=45):
    """A crystal: a wide foot sunk into the plate and a thin blade standing out of it."""
    h = size / 2
    rot = {"origin": [x, y, z], "axis": "y", "angle": angle}
    foot = box([x - h, y - 0.4, z - h], [x + h, y + tall * 0.45, z + h], cell, GLOW, rot)
    tip = box([x - h * 0.45, y + tall * 0.45, z - h * 0.45],
              [x + h * 0.45, y + tall, z + h * 0.45], GLOW, GLOW, rot)
    return [foot, tip]


def ice_on(spots, stage, size=1.1, tall=2.0):
    """Grows crystals on the listed spots: none bare, all of them frozen through."""
    if stage <= 0:
        return []
    take = {1: 2, 2: 4, 3: len(spots)}[stage]
    out = []
    for i, (x, y, z) in enumerate(spots[:take]):
        grow = 0.75 + 0.25 * stage
        out.extend(shard(x, y, z, size * grow, tall * grow,
                         ICE_PALE if i % 2 else ICE_MID, 45 if i % 2 else -45))
    return out


# ------------------------------------------------------------------ the hammer

MACE_PALETTES = {}
for _s in range(STAGES):
    _plate = frozen(BASE[PLATE_MID], _s)
    MACE_PALETTES[f"gravesteel_mace_{_s}"] = [
        frozen(BASE[PLATE_DARK], _s), _plate, frozen(BASE[PLATE_LIGHT], _s),
        frozen((40, 60, 80), _s), BASE[GLOW] if _s else (150, 190, 210),
        frozen((46, 46, 52), _s), frozen((96, 96, 102), _s), frozen(BASE[BONE], _s),
        frozen(BASE[PLATE_DARK], _s), frozen(BASE[EDGE], _s)]
mace_model.PALETTES.update(MACE_PALETTES)


def mace_texture(stage):
    return mace_model.texture(f"gravesteel_mace_{stage}")


def mace_elements(stage):
    """The war hammer shape, with ice growing out of the head as the stage climbs."""
    els = list(mace_model.elements())
    y1 = 16.5
    spots = [(5.2, y1, 5.5), (10.8, y1, 10.5), (5.2, y1, 10.5),
             (10.8, y1, 5.5), (8, y1 - 2.5, 2.4), (8, y1 - 2.5, 13.6)]
    els.extend(ice_on(spots, stage, size=1.3, tall=2.4))
    return els


# ------------------------------------------------------------------ the armour

def helmet(stage):
    """A helm built as a shell - side walls, back and crown - so the face is genuinely open."""
    els = [
        box([3.5, 12.2, 3.4], [12.5, 15, 12.6], PLATE_MID, PLATE_LIGHT),    # crown
        box([3.5, 5, 3.4], [5.6, 12.4, 12.6], PLATE_MID, PLATE_LIGHT),      # cheek walls
        box([10.4, 5, 3.4], [12.5, 12.4, 12.6], PLATE_MID, PLATE_LIGHT),
        box([5.6, 5, 10.4], [10.4, 12.4, 12.6], PLATE_MID, PLATE_LIGHT),    # back of the head
        box([5.6, 10.6, 3.4], [10.4, 12.4, 5.4], PLATE_DARK, PLATE_MID),    # brow over the opening
        box([7.2, 5.6, 3.4], [8.8, 10.6, 4.6], PLATE_LIGHT, PLATE_LIGHT),   # nose guard
        box([7.4, 4.3, 3.5], [8.6, 5.6, 4.4], BONE, EDGE),                  # its bone tip
        box([3.4, 14.8, 3.3], [12.6, 15.8, 12.7], PLATE_LIGHT, PLATE_LIGHT),  # crown rim
        box([3.4, 4.2, 10.3], [12.6, 5.3, 12.7], PLATE_DARK, PLATE_MID),    # neck flare
        # Horns: two lengths a side, leaned out so they sweep off the temples.
        box([1.2, 9.6, 6.2], [3.5, 12.2, 8.6], BONE, EDGE,
            rotation={"origin": [3.5, 9.6, 7.4], "axis": "z", "angle": 22.5}),
        box([-0.4, 11.6, 6.5], [1.6, 14.2, 8.3], EDGE, EDGE,
            rotation={"origin": [1.6, 11.6, 7.4], "axis": "z", "angle": 22.5}),
        box([12.5, 9.6, 6.2], [14.8, 12.2, 8.6], BONE, EDGE,
            rotation={"origin": [12.5, 9.6, 7.4], "axis": "z", "angle": -22.5}),
        box([14.4, 11.6, 6.5], [16.4, 14.2, 8.3], EDGE, EDGE,
            rotation={"origin": [14.4, 11.6, 7.4], "axis": "z", "angle": -22.5}),
        box([7.4, 15.5, 4.4], [8.6, 17.2, 11.6], BONE, EDGE),               # crest
    ]
    els.extend(ice_on([(4.6, 15.8, 4.4), (11.4, 15.8, 11.6), (4.5, 9, 3.3), (11.5, 9, 3.3),
                       (8, 17.2, 7.8), (4.6, 12.4, 11), (11.4, 12.4, 5)], stage))
    return els


def chestplate(stage):
    """A cuirass: deep chest, waist drawn in under it, belt below that, pauldrons out to the sides.

    Nothing overlaps - each piece sits on the one under it, so the silhouette stays a body shape
    instead of a pile of plates.
    """
    els = [
        box([3.4, 1.6, 3.7], [12.6, 3.4, 12.3], PLATE_DARK, RIVET),         # belt
        box([7.1, 1.8, 3.9], [8.9, 2.9, 4.3], RUNE, GLOW),                  # buckle
        box([3.7, 3, 4], [12.3, 14, 12], PLATE_MID, PLATE_LIGHT),           # torso
        box([5.6, 13.8, 5.6], [10.4, 15.6, 10.4], PLATE_DARK, PLATE_MID),   # collar
        # Pauldrons hang off the sides of the chest, capped in bone.
        box([1.2, 9.4, 4.6], [3.6, 13.6, 11.4], PLATE_MID, PLATE_LIGHT),
        box([12.4, 9.4, 4.6], [14.8, 13.6, 11.4], PLATE_MID, PLATE_LIGHT),
        box([1, 13.6, 5], [3.8, 14.6, 11], BONE, EDGE),
        box([12.2, 13.6, 5], [15, 14.6, 11], BONE, EDGE),
        # Bone down the breast with a rib either side, all standing proud of the chest face.
        box([7.2, 7.4, 3.4], [8.8, 13.6, 4], BONE, EDGE),
        box([5.2, 11.4, 3.4], [7.2, 12.6, 4], BONE, EDGE),
        box([8.8, 11.4, 3.4], [10.8, 12.6, 4], BONE, EDGE),
        box([4, 8.8, 3.6], [6.4, 9.7, 4], PLATE_DARK, PLATE_DARK),
        box([9.6, 8.8, 3.6], [12, 9.7, 4], PLATE_DARK, PLATE_DARK),
    ]
    els.extend(ice_on([(2.4, 14.6, 6.4), (13.6, 14.6, 9.6), (4.6, 14, 4.4), (11.4, 14, 4.4),
                       (8, 15.6, 8), (5, 3.2, 11), (11, 3.2, 5)], stage, size=1.2, tall=2.4))
    return els


def leggings(stage):
    """A belt with two long thigh plates hanging off it, kneecapped in dark steel."""
    els = [
        box([3.8, 12, 4.2], [12.2, 14.2, 11.8], PLATE_DARK, RIVET),         # belt
        box([3.6, 14, 4], [12.4, 15.2, 12], PLATE_LIGHT, PLATE_LIGHT),
        box([4.2, 2.5, 4.6], [7.4, 12.4, 11.4], PLATE_MID, PLATE_LIGHT),    # thighs
        box([8.6, 2.5, 4.6], [11.8, 12.4, 11.4], PLATE_MID, PLATE_LIGHT),
        box([4, 3.4, 4.4], [7.6, 5, 11.6], PLATE_DARK, PLATE_DARK),         # knee caps
        box([8.4, 3.4, 4.4], [12, 5, 11.6], PLATE_DARK, PLATE_DARK),
        box([5, 2.5, 4.3], [6.6, 11.8, 4.8], BONE, EDGE),                   # bone strips
        box([9.4, 2.5, 4.3], [11, 11.8, 4.8], BONE, EDGE),
        box([7.4, 9, 4.4], [8.6, 12.4, 11.6], PLATE_LIGHT, PLATE_LIGHT),    # centre plate
    ]
    els.extend(ice_on([(4.4, 11.6, 5.2), (11.6, 11.6, 10.8), (5, 5, 4.6), (11, 5, 4.6),
                       (8, 14.8, 8), (5.6, 2.8, 11)], stage, size=1.1, tall=2.2))
    return els


def boots(stage):
    """A pair: cuffed at the top, plated over the toes, studded in bone."""
    els = [
        box([3.6, 0, 3.6], [7.4, 4.6, 11.6], PLATE_MID, PLATE_LIGHT),       # boots
        box([8.6, 0, 3.6], [12.4, 4.6, 11.6], PLATE_MID, PLATE_LIGHT),
        box([3.3, 4.6, 3.3], [7.7, 7.4, 11.9], PLATE_DARK, RIVET),          # cuffs
        box([8.3, 4.6, 3.3], [12.7, 7.4, 11.9], PLATE_DARK, RIVET),
        box([3.2, 7.2, 3.2], [7.8, 8.2, 12], BONE, EDGE),                   # cuff trim
        box([8.2, 7.2, 3.2], [12.8, 8.2, 12], BONE, EDGE),
        box([3.4, 0, 2.4], [7.6, 2.8, 3.6], PLATE_LIGHT, PLATE_LIGHT),      # toe caps
        box([8.4, 0, 2.4], [12.6, 2.8, 3.6], PLATE_LIGHT, PLATE_LIGHT),
        box([4, 2.8, 2.6], [7, 3.5, 3.5], BONE, EDGE),                      # toe studs
        box([9, 2.8, 2.6], [12, 3.5, 3.5], BONE, EDGE),
    ]
    els.extend(ice_on([(4.2, 7.4, 4.6), (11.8, 7.4, 4.6), (5.2, 7.8, 10.6), (10.8, 7.8, 10.6),
                       (5.4, 3.5, 2.9), (10.6, 3.5, 2.9)], stage, size=1.0, tall=1.9))
    return els


ARMOUR = {
    "gravesteel_helmet": helmet,
    "gravesteel_chestplate": chestplate,
    "gravesteel_leggings": leggings,
    "gravesteel_boots": boots,
}


# ------------------------------------------------------------------ worn armour

def worn_layer(jar, stage, layer):
    """Recolours the vanilla netherite armour layer, so the set looks right on the body too.

    Layer 1 is helmet/chest/boots, layer 2 the leggings. The plate goes bone-steel and then ices
    over with the stage, and a few frost flecks are scattered where the ice would settle.
    """
    with jar.open(f"assets/minecraft/textures/entity/equipment/humanoid"
                  f"{'_leggings' if layer == 2 else ''}/netherite.png") as f:
        src = Image.open(f).convert("RGBA").copy()
    out = src.copy()
    px = out.load()
    w, h = out.size
    rnd = random.Random(400 + stage * 7 + layer)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            # Netherite's own texture is very dark, so lift the midtones or the whole set reads
            # black on the body instead of bone-steel.
            lum = min(1.0, ((0.299 * r + 0.587 * g + 0.114 * b) / 255) ** 0.65 * 1.12)
            ramp = [BASE[PLATE_DARK], BASE[PLATE_MID], BASE[PLATE_MID], BASE[PLATE_LIGHT], BASE[EDGE]]
            step = min(len(ramp) - 1, max(0, int(lum * len(ramp))))
            px[x, y] = frozen(ramp[step], stage) + (a,)
    if stage > 0:
        for _ in range(int(14 * stage)):
            x, y = rnd.randrange(w), rnd.randrange(h)
            if px[x, y][3] == 0:
                continue
            px[x, y] = BASE[FROST] + (255,)
    return out
