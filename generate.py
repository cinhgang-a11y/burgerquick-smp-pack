"""
Builds the BurgerQuick SMP resource pack.

Every texture is a recolour of the real Minecraft item texture, so the shapes, shading and
pixel style match the game exactly - only the colours change (and tool handles stay wooden).

    python generate.py

Writes ./BurgerQuickPack/, ./BurgerQuick-Textures.zip and ./preview.png
Everything lives in the "burgerquick" namespace, so no vanilla item is changed.
"""
import json
import os
import shutil
import zipfile

from PIL import Image

import boss_model
import gravesteel_model
import miniboss_model
import rime_model
import mace_model

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "BurgerQuickPack")
CLIENT_JAR = r"C:\Users\Ville\AppData\Roaming\.minecraft\versions\26.2\26.2.jar"
RESOURCE_FORMAT = 88  # Minecraft 26.2
NS = "burgerquick"

# Colour ramps: darkest -> brightest. Vanilla shading is kept by mapping each pixel's
# brightness onto the ramp.
RAMPS = {
    "thunder": [(74, 48, 8), (140, 96, 16), (206, 150, 28), (250, 205, 60), (255, 244, 170)],
    "frost": [(22, 64, 104), (44, 118, 174), (90, 176, 226), (158, 222, 248), (226, 250, 255)],
    "inferno": [(74, 16, 6), (140, 40, 10), (206, 78, 18), (246, 140, 36), (255, 214, 120)],
    "shadow": [(24, 18, 40), (52, 38, 84), (92, 66, 140), (140, 106, 200), (200, 176, 246)],
    "earth": [(52, 36, 20), (96, 68, 38), (146, 106, 62), (190, 150, 102), (228, 200, 158)],
    "blood": [(56, 6, 12), (108, 16, 24), (164, 30, 40), (212, 66, 70), (250, 150, 146)],
    "boom": [(64, 28, 4), (120, 56, 10), (184, 92, 18), (232, 140, 36), (255, 202, 116)],
    "storm": [(20, 26, 70), (40, 54, 128), (72, 96, 196), (124, 158, 238), (198, 222, 255)],
    "nature": [(20, 48, 16), (40, 92, 32), (70, 144, 52), (112, 192, 84), (176, 232, 146)],
    "heal": [(78, 20, 46), (134, 40, 82), (194, 74, 126), (238, 130, 172), (255, 198, 218)],
    "void": [(12, 8, 24), (34, 26, 62), (62, 50, 108), (104, 88, 168), (168, 152, 224)],
    "hermes": [(80, 58, 8), (140, 106, 18), (200, 160, 36), (244, 208, 78), (255, 242, 168)],
    "berserk": [(52, 8, 8), (104, 18, 18), (158, 34, 32), (206, 68, 60), (248, 132, 118)],
    "titan": [(86, 52, 4), (146, 96, 12), (204, 148, 26), (246, 198, 62), (255, 238, 150)],
    "mythic": [(60, 6, 6), (122, 18, 14), (186, 44, 24), (234, 96, 40), (255, 178, 96)],
    "steel": [(38, 44, 54), (74, 84, 98), (120, 132, 148), (172, 186, 202), (224, 234, 244)],
    "smelter": [(66, 22, 8), (124, 50, 16), (182, 84, 30), (228, 130, 58), (255, 190, 124)],
    "orbital": [(8, 38, 70), (16, 76, 132), (30, 126, 196), (86, 184, 238), (176, 232, 255)],
    "plasma": [(60, 10, 62), (110, 22, 106), (170, 42, 152), (216, 84, 194), (250, 168, 234)],
    "singular": [(14, 8, 28), (40, 22, 70), (74, 44, 122), (120, 78, 182), (186, 148, 236)],
    "dragon": [(48, 8, 6), (98, 22, 14), (154, 44, 24), (206, 84, 40), (248, 150, 90)],
    "glacier": [(20, 66, 104), (40, 116, 172), (84, 172, 224), (150, 218, 248), (222, 248, 255)],
    "jugger": [(34, 38, 44), (66, 74, 84), (108, 120, 134), (158, 172, 188), (212, 226, 238)],
    "celestial": [(84, 62, 8), (146, 112, 18), (206, 166, 38), (246, 214, 90), (255, 246, 190)],
    # Gravesteel: what the Hollow leaves behind. Dark steel with bone through it.
    "gravesteel": [(26, 24, 30), (58, 56, 60), (104, 100, 94), (166, 158, 140), (232, 226, 206)],
}

# item id -> (vanilla texture, ramp, model parent)
HANDHELD = "minecraft:item/handheld"
MACE = "minecraft:item/handheld_mace"
FLAT = "minecraft:item/generated"

# Items rendered bigger in hand / on the ground (1.0 = vanilla size).
SCALE = {"earthquake_mace": 1.3, "worldbreaker": 1.3}
ITEMS = {
    "thunder_hammer": ("netherite_axe", "thunder", HANDHELD),
    "frost_blade": ("diamond_sword", "frost", HANDHELD),
    "inferno_staff": ("blaze_rod", "inferno", HANDHELD),
    "shadow_katana": ("netherite_sword", "shadow", HANDHELD),
    "earthquake_mace": ("mace", "earth", MACE),
    "vampire_dagger": ("iron_sword", "blood", HANDHELD),
    "explosive_bow": ("bow", "boom", FLAT),
    "storm_bow": ("bow", "storm", FLAT),
    "grappling_hook": ("fishing_rod", "nature", HANDHELD),
    "healing_wand": ("blaze_rod", "heal", HANDHELD),
    "void_pearl": ("ender_pearl", "void", FLAT),
    "grenade": ("fire_charge", "nature", FLAT),
    "hermes_boots": ("diamond_boots", "hermes", FLAT),
    "berserker_chestplate": ("netherite_chestplate", "berserk", FLAT),
    "titan_apple": ("golden_apple", "titan", FLAT),
    "worldbreaker": ("mace", "mythic", MACE),
    "excavator": ("diamond_pickaxe", "steel", HANDHELD),
    "smelter_pickaxe": ("diamond_pickaxe", "smelter", HANDHELD),
    "orbital_strike_cannon": ("spyglass", "orbital", HANDHELD),
    "plasma_railgun": ("crossbow_standby", "plasma", HANDHELD),
    "singularity_grenade": ("echo_shard", "singular", FLAT),
}
ARMOR_BASE = {
    "dragonscale": ("netherite", "dragon"),
    "glacier": ("diamond", "glacier"),
    "shadow": ("leather", "shadow"),
    "juggernaut": ("netherite", "jugger"),
    "celestial": ("golden", "celestial"),
}
for set_id, (base, ramp) in ARMOR_BASE.items():
    for piece in ("helmet", "chestplate", "leggings", "boots"):
        ITEMS[f"{set_id}_{piece}"] = (f"{base}_{piece}", ramp, FLAT)


def is_wood(r, g, b):
    """Tool handles: keep vanilla wood so the items still read as tools."""
    return r > g > b and (r - b) > 25 and r < 190 and g < 150


def recolour(img, ramp):
    out = img.copy().convert("RGBA")
    pixels = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a == 0 or is_wood(r, g, b):
                continue
            # Vanilla brightness -> ramp step, so highlights and shadows survive.
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            step = min(len(ramp) - 1, max(0, int(lum * len(ramp))))
            nr, ng, nb = ramp[step]
            pixels[x, y] = (nr, ng, nb, a)
    return out


def resolve_display(jar, model):
    """Collects the display transforms a vanilla model inherits, nearest parent wins."""
    display = {}
    seen = set()
    while model and model not in seen:
        seen.add(model)
        path = "assets/minecraft/models/" + model.split(":")[-1] + ".json"
        try:
            data = json.loads(jar.read(path))
        except KeyError:
            break
        for slot, transform in data.get("display", {}).items():
            display.setdefault(slot, transform)
        model = data.get("parent")
    return display


def scaled_display(jar, parent, factor):
    """Same placement as vanilla, just bigger. The GUI icon is left alone so it fits its slot."""
    out = {}
    for slot, transform in resolve_display(jar, parent).items():
        if slot in ("gui", "head", "fixed"):
            continue
        scale = transform.get("scale", [1, 1, 1])
        copy = dict(transform)
        copy["scale"] = [round(v * factor, 3) for v in scale]
        out[slot] = copy
    return out



# ---------------------------------------------------------------------------------------------
# 3D in-hand models. The inventory icon stays the flat recoloured sprite (like the vanilla
# spyglass); only the version in your hand is 3D. Each model uses a small palette texture:
# a 4x4 grid of 4x4-pixel colour cells.
WOOD = [(92, 60, 32), (122, 84, 46), (150, 108, 62), (60, 38, 20)]
GRIP = [(40, 32, 30), (58, 46, 42), (74, 60, 54), (28, 22, 20)]
METAL = [(70, 74, 82), (110, 116, 126), (160, 166, 176), (46, 48, 54)]

MODEL_3D = {
    # item id: (shape, head ramp, accent ramp)
    "worldbreaker": ("mace", "mythic", "thunder"),
    "earthquake_mace": ("mace", "earth", "steel"),
    "thunder_hammer": ("hammer", "thunder", "orbital"),
    "orbital_strike_cannon": ("cannon", "orbital", "frost"),
    "plasma_railgun": ("railgun", "plasma", "thunder"),
}



# Gravesteel gear: the tier above netherite. Every piece exists four times over, because the
# Rimevault freezes it a stage further with each upgrade.
GRAVESTEEL_PIECES = {
    "gravesteel_sword": ("netherite_sword", HANDHELD),
    "gravesteel_mace": ("mace", MACE),
    "gravesteel_pickaxe": ("netherite_pickaxe", HANDHELD),
    "gravesteel_axe": ("netherite_axe", HANDHELD),
    "gravesteel_shovel": ("netherite_shovel", HANDHELD),
    "gravesteel_hoe": ("netherite_hoe", HANDHELD),
    "gravesteel_helmet": ("netherite_helmet", FLAT),
    "gravesteel_chestplate": ("netherite_chestplate", FLAT),
    "gravesteel_leggings": ("netherite_leggings", FLAT),
    "gravesteel_boots": ("netherite_boots", FLAT),
    "gravesteel_ingot": ("netherite_ingot", FLAT),
    "raw_gravesteel": ("netherite_scrap", FLAT),
}
GRAVESTEEL_STAGES = 4           # 0 = bare metal, 3 = frozen solid


def recolour_all(img, ramp):
    """Like recolour, but without the wood guard - gravesteel has no handle to keep brown."""
    out = img.copy().convert("RGBA")
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            step = min(len(ramp) - 1, max(0, int(lum * len(ramp))))
            px[x, y] = ramp[step] + (a,)
    return out


def frosted(img, stage):
    """Blends a gravesteel texture toward ice, and lets frost grow on it as the stage climbs."""
    if stage <= 0:
        return img
    out = img.copy()
    px = out.load()
    w, h = out.size
    rnd = __import__("random").Random(1000 + stage)
    weight = stage / (GRAVESTEEL_STAGES - 1)            # 0 -> 1 across the stages
    ice = RAMPS["glacier"]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            step = min(len(ice) - 1, max(0, int(lum * len(ice))))
            ir, ig, ib = ice[step]
            blend = weight * 0.8
            px[x, y] = (int(r * (1 - blend) + ir * blend),
                        int(g * (1 - blend) + ig * blend),
                        int(b * (1 - blend) + ib * blend), a)
    # Frost crust: a few pale flecks at stage 1, a rime along the edges by stage 3.
    flecks = int(6 * weight * 4)
    for _ in range(flecks):
        x, y = rnd.randrange(w), rnd.randrange(h)
        if px[x, y][3] == 0:
            continue
        px[x, y] = (232, 250, 255, 255)
    return out


def gravesteel_ore(jar):
    """Deepslate with gravesteel showing through it.

    The veins are blobs rather than vanilla's scattered dots, and each one is lit on its top-left
    edge, so the metal reads as a seam running through the rock instead of gravel stuck to it.
    """
    with jar.open("assets/minecraft/textures/block/deepslate.png") as f:
        img = Image.open(f).convert("RGBA").copy()
    if img.size != (16, 16):                            # animated or hi-res: take the first frame
        img = img.crop((0, 0, 16, 16))
    px = img.load()
    # Darken the host rock a little so the metal has something to stand against.
    for y in range(16):
        for x in range(16):
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * 0.72), int(g * 0.72), int(b * 0.76), a)

    ramp = RAMPS["gravesteel"]
    rnd = __import__("random").Random(77)
    for _ in range(5):
        cx, cy = rnd.randrange(2, 14), rnd.randrange(2, 14)
        r = rnd.choice((1, 1, 2))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy > r * r + (1 if r > 1 else 0):
                    continue
                x, y = (cx + dx) % 16, (cy + dy) % 16
                lit = dx + dy <= -r                     # top-left face of the blob catches light
                edge = abs(dx) == r or abs(dy) == r
                tone = ramp[3] if lit else ramp[1] if edge else ramp[2]
                px[x, y] = tone + (255,)
        # A single cold spark in the middle - the same blue the Rimevault will bring out of it.
        px[cx % 16, cy % 16] = (176, 214, 226, 255)
    return img


# The gravesteel pieces that are modelled in 3D: the hammer and the four plates. Everything else
# stays a sprite, the same as its vanilla shape.
GRAVESTEEL_3D = {"gravesteel_mace", "gravesteel_helmet", "gravesteel_chestplate",
                 "gravesteel_leggings", "gravesteel_boots"}

# Armour is worn, not swung: it wants a steady look-at rather than the hammer's grip transform.
ARMOUR_DISPLAY = {
    "thirdperson_righthand": {"rotation": [0, -90, 25], "translation": [0, 3.5, 0.5],
                              "scale": [0.6, 0.6, 0.6]},
    "thirdperson_lefthand": {"rotation": [0, 90, -25], "translation": [0, 3.5, 0.5],
                             "scale": [0.6, 0.6, 0.6]},
    "firstperson_righthand": {"rotation": [0, -135, 25], "translation": [0, 3, 0],
                              "scale": [0.55, 0.55, 0.55]},
    "firstperson_lefthand": {"rotation": [0, 135, -25], "translation": [0, 3, 0],
                             "scale": [0.55, 0.55, 0.55]},
    "head": {"rotation": [0, 0, 0], "translation": [0, 13, 0], "scale": [1.05, 1.05, 1.05]},
}


def write_gravesteel_3d(item_id, piece, stage, tex_dir, model_dir):
    """The held model for one piece at one stage, plus the palette it samples."""
    if piece == "gravesteel_mace":
        gravesteel_model.mace_texture(stage).save(os.path.join(tex_dir, item_id + "_3d.png"))
        elements = gravesteel_model.mace_elements(stage)
        display = json.loads(json.dumps(HELD_DISPLAY))
        for slot, lift in GRIP_SHIFT["mace"].items():
            display[slot]["translation"][1] += lift
    else:
        gravesteel_model.texture(stage).save(os.path.join(tex_dir, item_id + "_3d.png"))
        elements = gravesteel_model.ARMOUR[piece](stage)
        display = json.loads(json.dumps(ARMOUR_DISPLAY))
    write(os.path.join(model_dir, item_id + "_3d.json"), {
        "textures": {"main": f"{NS}:item/{item_id}_3d", "particle": f"{NS}:item/{item_id}"},
        "gui_light": "front",
        "display": display,
        "elements": elements,
    })


def write_gravesteel(jar, tex_dir, model_dir, item_dir):
    for piece, (base, parent) in GRAVESTEEL_PIECES.items():
        with jar.open(f"assets/minecraft/textures/item/{base}.png") as f:
            source = Image.open(f).convert("RGBA").copy()
        metal = recolour_all(source, RAMPS["gravesteel"])
        stages = 1 if piece in ("gravesteel_ingot", "raw_gravesteel") else GRAVESTEEL_STAGES
        for stage in range(stages):
            item_id = piece if stage == 0 else f"{piece}_{stage}"
            frosted(metal, stage).save(os.path.join(tex_dir, item_id + ".png"))
            write(os.path.join(model_dir, item_id + ".json"),
                  {"parent": parent, "textures": {"layer0": f"{NS}:item/{item_id}"}})
            flat = {"type": "minecraft:model", "model": f"{NS}:item/{item_id}"}
            if piece in GRAVESTEEL_3D:
                write_gravesteel_3d(item_id, piece, stage, tex_dir, model_dir)
                definition = {"model": {
                    "type": "minecraft:select",
                    "property": "minecraft:display_context",
                    "cases": [{"when": ["gui", "ground", "fixed", "on_shelf"], "model": flat}],
                    "fallback": {"type": "minecraft:model", "model": f"{NS}:item/{item_id}_3d"},
                }}
            else:
                definition = {"model": flat}
            write(os.path.join(item_dir, item_id + ".json"), definition)


def write_gravesteel_worn(jar):
    """The armour as it looks on the body: one equipment asset per frost stage."""
    humanoid = os.path.join(PACK, "assets", NS, "textures", "entity", "equipment", "humanoid")
    leggings = os.path.join(PACK, "assets", NS, "textures", "entity", "equipment",
                            "humanoid_leggings")
    baby = os.path.join(PACK, "assets", NS, "textures", "entity", "equipment", "humanoid_baby")
    equipment = os.path.join(PACK, "assets", NS, "equipment")
    for folder in (humanoid, leggings, baby, equipment):
        os.makedirs(folder, exist_ok=True)
    for stage in range(GRAVESTEEL_STAGES):
        asset = f"gravesteel_{stage}"
        body = gravesteel_model.worn_layer(jar, stage, 1)
        body.save(os.path.join(humanoid, asset + ".png"))
        body.save(os.path.join(baby, asset + ".png"))
        gravesteel_model.worn_layer(jar, stage, 2).save(os.path.join(leggings, asset + ".png"))
        write(os.path.join(equipment, asset + ".json"), {"layers": {
            layer: [{"texture": f"{NS}:{asset}"}]
            for layer in ("humanoid", "humanoid_baby", "humanoid_leggings")
        }})


def palette_texture(head, accent):
    """Row 0 wood, row 1 head shades, row 2 accent shades, row 3 grip/metal."""
    rows = [WOOD, head[:4], accent[1:5], [GRIP[1], GRIP[2], METAL[1], METAL[2]]]
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    rnd = __import__("random").Random(7)
    for cy, row in enumerate(rows):
        for cx, c in enumerate(row):
            for x in range(cx * 4, cx * 4 + 4):
                for y in range(cy * 4, cy * 4 + 4):
                    n = rnd.randint(-7, 7)
                    px[x, y] = (max(0, min(255, c[0] + n)), max(0, min(255, c[1] + n)), max(0, min(255, c[2] + n)), 255)
    return img


def cell(cx, cy):
    return [cx * 4, cy * 4, cx * 4 + 4, cy * 4 + 4]


def box(frm, to, side, top=None):
    """A cuboid using one palette cell on the sides and (optionally) a lighter one on top/bottom."""
    top = top or side
    faces = {f: {"uv": cell(*side), "texture": "#main"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": cell(*top), "texture": "#main"}
    faces["down"] = {"uv": cell(*side), "texture": "#main"}
    return {"from": frm, "to": to, "faces": faces}


WOOD_C, WOOD_D, GRIP_C, METAL_C, METAL_L = (1, 0), (0, 0), (0, 3), (2, 3), (3, 3)
HEAD_D, HEAD_M, HEAD_L, HEAD_XL = (0, 1), (1, 1), (2, 1), (3, 1)
ACC_M, ACC_L, ACC_XL = (1, 2), (2, 2), (3, 2)

SHAPES = {
    "mace": [
        box([7.25, -2, 7.25], [8.75, 14, 8.75], WOOD_C, WOOD_D),
        box([7, 1, 7], [9, 6, 9], GRIP_C),
        box([6.75, -3.5, 6.75], [9.25, -2, 9.25], METAL_C, METAL_L),
        box([6.5, 13, 6.5], [9.5, 14.5, 9.5], METAL_C, METAL_L),
        box([4.5, 14.5, 4.5], [11.5, 21.5, 11.5], HEAD_M, HEAD_L),
        box([5.5, 21.5, 5.5], [10.5, 22.5, 10.5], HEAD_L, HEAD_XL),
        box([4.3, 17, 7], [11.7, 19, 9], ACC_L),               # glowing band
        box([7, 17, 4.3], [9, 19, 11.7], ACC_L),
        box([2.5, 16.5, 7.25], [4.5, 19.5, 8.75], HEAD_D, HEAD_M),  # side spikes
        box([11.5, 16.5, 7.25], [13.5, 19.5, 8.75], HEAD_D, HEAD_M),
        box([7.25, 16.5, 2.5], [8.75, 19.5, 4.5], HEAD_D, HEAD_M),
        box([7.25, 16.5, 11.5], [8.75, 19.5, 13.5], HEAD_D, HEAD_M),
        box([7.25, 22.5, 7.25], [8.75, 25, 8.75], ACC_M, ACC_XL),     # top spike
    ],
    "hammer": [
        box([7.25, -3, 7.25], [8.75, 15, 8.75], WOOD_C, WOOD_D),
        box([7, 0, 7], [9, 5, 9], GRIP_C),
        box([6.75, -4, 6.75], [9.25, -3, 9.25], METAL_C, METAL_L),
        box([2, 15, 5.5], [14, 21, 10.5], HEAD_M, HEAD_L),
        box([1, 14.5, 5], [2, 21.5, 11], HEAD_D, HEAD_M),
        box([14, 14.5, 5], [15, 21.5, 11], HEAD_D, HEAD_M),
        box([7.5, 14.9, 5.4], [8.5, 21.1, 10.6], ACC_L, ACC_XL),     # lightning band
        box([4, 21, 7], [12, 21.5, 9], HEAD_L, HEAD_XL),
    ],
    "cannon": [
        box([6, 6, -8], [10, 10, 12], HEAD_M, HEAD_L),                # barrel
        box([5.5, 5.5, -9], [10.5, 10.5, -7], HEAD_D, HEAD_M),       # muzzle ring
        box([6.5, 6.5, -9.2], [9.5, 9.5, -9], ACC_XL),               # glowing muzzle
        box([5, 5, 8], [11, 11, 15], HEAD_D, HEAD_M),                # breech
        box([5.8, 5.8, -2], [10.2, 10.2, -1], ACC_L),                # energy rings
        box([5.8, 5.8, 3], [10.2, 10.2, 4], ACC_L),
        box([7, 10, 2], [9, 12, 7], METAL_C, METAL_L),               # scope
        box([7.25, 12, 2.5], [8.75, 12.5, 6.5], ACC_M, ACC_XL),
        box([7, 1, 9], [9, 5, 12], GRIP_C),                          # grip
    ],
    "railgun": [
        box([6, 5, 3], [10, 10, 15], HEAD_D, HEAD_M),                # body
        box([5.5, 7, -8], [7, 9, 8], HEAD_M, HEAD_L),                # left rail
        box([9, 7, -8], [10.5, 9, 8], HEAD_M, HEAD_L),               # right rail
        box([7.3, 7.5, -7], [8.7, 8.5, 4], ACC_XL),                  # plasma core
        box([5, 6.5, -4], [11, 9.5, -3], ACC_L),                     # coils
        box([5, 6.5, 0], [11, 9.5, 1], ACC_L),
        box([7, 10, 6], [9, 11.5, 11], METAL_C, METAL_L),            # sight
        box([7, 1, 10], [9, 5, 13], GRIP_C),                         # grip
    ],
}

# Held display: the model's own coordinates, nudged into the hand like the vanilla spyglass.
HELD_DISPLAY = {
    "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, -2, 0], "scale": [1, 1, 1]},
    "thirdperson_lefthand": {"rotation": [0, 0, 0], "translation": [0, -2, 0], "scale": [1, 1, 1]},
    "firstperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
    "firstperson_lefthand": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
}


# How far (in 1/16 block) to raise each shape in the hand.
GRIP_SHIFT = {
    "mace": {"thirdperson_righthand": 6, "thirdperson_lefthand": 6,
             "firstperson_righthand": 5, "firstperson_lefthand": 5},
}


def write_3d(item_id, tex_dir, model_dir):
    shape, head, accent = MODEL_3D[item_id]
    if shape == "mace":
        mace_model.texture(item_id).save(os.path.join(tex_dir, item_id + "_3d.png"))
        elements = mace_model.elements()
    else:
        palette_texture(RAMPS[head], RAMPS[accent]).save(os.path.join(tex_dir, item_id + "_3d.png"))
        elements = SHAPES[shape]
    display = json.loads(json.dumps(HELD_DISPLAY))
    # Maces: slide the model up so the hand grips the bottom of the handle, not just under the head.
    grip = GRIP_SHIFT.get(shape)
    if grip:
        for slot, lift in grip.items():
            display[slot]["translation"][1] += lift
    factor = SCALE.get(item_id, 1.0)
    for transform in display.values():
        transform["scale"] = [round(v * factor, 3) for v in transform["scale"]]
    write(os.path.join(model_dir, item_id + "_3d.json"), {
        "textures": {"main": f"{NS}:item/{item_id}_3d", "particle": f"{NS}:item/{item_id}"},
        "gui_light": "front",
        "display": display,
        "elements": elements,
    })


def item_definition(item_id):
    flat = {"type": "minecraft:model", "model": f"{NS}:item/{item_id}"}
    if item_id not in MODEL_3D:
        return {"model": flat}
    return {"model": {
        "type": "minecraft:select",
        "property": "minecraft:display_context",
        "cases": [{"when": ["gui", "ground", "fixed", "on_shelf"], "model": flat}],
        "fallback": {"type": "minecraft:model", "model": f"{NS}:item/{item_id}_3d"},
    }}


def main():
    jar = zipfile.ZipFile(CLIENT_JAR)

    if os.path.exists(PACK):
        shutil.rmtree(PACK)
    tex_dir = os.path.join(PACK, "assets", NS, "textures", "item")
    model_dir = os.path.join(PACK, "assets", NS, "models", "item")
    item_dir = os.path.join(PACK, "assets", NS, "items")
    for d in (tex_dir, model_dir, item_dir):
        os.makedirs(d, exist_ok=True)

    sheet = Image.new("RGBA", (16 * 7, 16 * 6), (30, 30, 34, 255))
    for i, (item_id, (base, ramp, parent)) in enumerate(ITEMS.items()):
        with jar.open(f"assets/minecraft/textures/item/{base}.png") as f:
            src = Image.open(f).convert("RGBA")
        src = src.crop((0, 0, 16, 16))  # ignore animation strips
        img = recolour(src, RAMPS[ramp])
        img.save(os.path.join(tex_dir, item_id + ".png"))
        sheet.paste(img, ((i % 7) * 16, (i // 7) * 16), img)

        model = {"parent": parent, "textures": {"layer0": f"{NS}:item/{item_id}"}}
        if item_id in SCALE:
            model["display"] = scaled_display(jar, parent, SCALE[item_id])
        write(os.path.join(model_dir, item_id + ".json"), model)
        write(os.path.join(item_dir, item_id + ".json"), item_definition(item_id))
        if item_id in MODEL_3D:
            write_3d(item_id, tex_dir, model_dir)

    # Ender Tyrant boss: five animated parts sharing one texture (shown by the BurgerBosses plugin).
    boss_model.texture().save(os.path.join(tex_dir, "tyrant.png"))
    for part in boss_model.PARTS:
        write(os.path.join(model_dir, part + ".json"), {
            "textures": {"main": f"{NS}:item/tyrant", "particle": f"{NS}:item/tyrant"},
            "elements": boss_model.elements(part),
        })
        write(os.path.join(item_dir, part + ".json"),
              {"model": {"type": "minecraft:model", "model": f"{NS}:item/{part}"}})

    # Gravesteel: a full set, and the frost creeping over it one upgrade at a time.
    write_gravesteel(jar, tex_dir, model_dir, item_dir)

    # The two mini-bosses: one palette each, then their limb sets.
    miniboss_model.texture(miniboss_model.WATCHER, 21).save(os.path.join(tex_dir, "watcher.png"))
    miniboss_model.texture(miniboss_model.COLOSSUS, 22).save(os.path.join(tex_dir, "colossus.png"))
    for part, build in miniboss_model.PARTS.items():
        palette = "watcher" if part.startswith("watcher") else "colossus"
        write(os.path.join(model_dir, part + ".json"), {
            "textures": {"main": f"{NS}:item/{palette}", "particle": f"{NS}:item/{palette}"},
            "elements": build(),
        })
        write(os.path.join(item_dir, part + ".json"),
              {"model": {"type": "minecraft:model", "model": f"{NS}:item/{part}"}})

    # Rimevault: the golem's parts, and the iced stone brick that the vault is built from.
    rime_model.texture().save(os.path.join(tex_dir, "rime.png"))
    for part in rime_model.PARTS:
        write(os.path.join(model_dir, part + ".json"), {
            "textures": {"main": f"{NS}:item/rime", "particle": f"{NS}:item/rime"},
            "elements": rime_model.PARTS[part](),
        })
        write(os.path.join(item_dir, part + ".json"),
              {"model": {"type": "minecraft:model", "model": f"{NS}:item/{part}"}})

    # A vanilla block texture, swapped on mud bricks: they never generate naturally and nobody
    # crafts them, so the frozen brick costs us no block players already use.
    vanilla_blocks = os.path.join(PACK, "assets", "minecraft", "textures", "block")
    os.makedirs(vanilla_blocks, exist_ok=True)
    rime_model.iced_stone_bricks(jar).save(os.path.join(vanilla_blocks, "mud_bricks.png"))
    # Packed mud is the other block nothing on the server uses: it carries gravesteel ore.
    gravesteel_ore(jar).save(os.path.join(vanilla_blocks, "packed_mud.png"))
    write_gravesteel_worn(jar)

    write(os.path.join(PACK, "pack.mcmeta"), {
        "pack": {
            "description": "BurgerQuick SMP - custom item textures",
            "pack_format": RESOURCE_FORMAT,
            "min_format": RESOURCE_FORMAT,
            "max_format": RESOURCE_FORMAT,
        }
    })
    icon = os.path.join(os.path.dirname(HERE), "paper-server-26.2", "server-icon.png")
    if os.path.exists(icon):
        shutil.copy(icon, os.path.join(PACK, "pack.png"))

    zip_path = os.path.join(HERE, "BurgerQuick-Textures.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(PACK):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, PACK))
    sheet.resize((16 * 7 * 6, 16 * 6 * 6), Image.NEAREST).save(os.path.join(HERE, "preview.png"))
    print(f"{len(ITEMS)} textures -> {zip_path} ({os.path.getsize(zip_path)} bytes)")


def write(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2)


if __name__ == "__main__":
    main()
