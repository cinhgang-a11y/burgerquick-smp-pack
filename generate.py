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
}

# item id -> (vanilla texture, ramp, model parent)
HANDHELD = "minecraft:item/handheld"
MACE = "minecraft:item/handheld_mace"
FLAT = "minecraft:item/generated"

# Items rendered bigger in hand / on the ground (1.0 = vanilla size).
SCALE = {"earthquake_mace": 2.0, "worldbreaker": 2.0}
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
        write(os.path.join(item_dir, item_id + ".json"),
              {"model": {"type": "minecraft:model", "model": f"{NS}:item/{item_id}"}})

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
