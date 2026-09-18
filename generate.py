"""
Builds the BurgerQuick SMP resource pack: one 16x16 texture, model and item definition
for every custom item in the CustomItems plugin.

    python generate.py

Writes ./BurgerQuickPack/ and ./BurgerQuick-Textures.zip
Everything lives in the "burgerquick" namespace, so no vanilla item is changed.
"""
import json
import os
import shutil
import zipfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "BurgerQuickPack")
RESOURCE_FORMAT = 88  # Minecraft 26.2
NS = "burgerquick"

# palette = (dark outline, main, light highlight, accent)
P = {
    "thunder": ((60, 40, 10), (255, 200, 40), (255, 245, 170), (120, 200, 255)),
    "frost": ((20, 70, 110), (120, 210, 255), (225, 250, 255), (255, 255, 255)),
    "inferno": ((90, 20, 0), (255, 110, 30), (255, 220, 120), (255, 240, 200)),
    "shadow": ((20, 15, 35), (85, 60, 140), (175, 140, 235), (230, 210, 255)),
    "earth": ((60, 40, 20), (150, 105, 60), (205, 165, 115), (120, 120, 120)),
    "blood": ((70, 0, 10), (190, 30, 40), (245, 120, 120), (255, 220, 220)),
    "boom": ((70, 35, 0), (230, 110, 20), (255, 190, 90), (60, 60, 60)),
    "storm": ((25, 30, 80), (80, 110, 220), (170, 200, 255), (255, 255, 255)),
    "nature": ((25, 60, 20), (80, 170, 60), (170, 230, 130), (220, 255, 200)),
    "heal": ((90, 30, 60), (240, 130, 170), (255, 210, 225), (255, 255, 255)),
    "void": ((15, 10, 30), (55, 45, 95), (130, 115, 200), (200, 190, 255)),
    "hermes": ((90, 70, 10), (235, 200, 70), (255, 240, 170), (255, 255, 255)),
    "berserk": ((70, 10, 10), (190, 40, 40), (245, 110, 100), (40, 40, 45)),
    "titan": ((105, 70, 0), (245, 190, 40), (255, 235, 150), (255, 80, 80)),
    "mythic": ((80, 0, 0), (235, 60, 30), (255, 190, 60), (255, 250, 180)),
    "steel": ((45, 50, 60), (135, 145, 160), (215, 225, 235), (90, 200, 255)),
    "smelter": ((80, 30, 10), (215, 95, 45), (255, 175, 110), (255, 230, 150)),
    "orbital": ((10, 45, 80), (40, 150, 230), (160, 225, 255), (255, 255, 255)),
    "plasma": ((70, 15, 70), (215, 55, 165), (255, 170, 230), (250, 255, 120)),
    "singular": ((15, 10, 30), (70, 35, 115), (160, 90, 220), (240, 220, 255)),
    "dragon": ((60, 10, 5), (185, 45, 25), (250, 130, 70), (255, 215, 130)),
    "glacier": ((20, 70, 110), (110, 195, 245), (215, 245, 255), (255, 255, 255)),
    "jugger": ((40, 45, 50), (120, 130, 140), (200, 210, 220), (250, 230, 120)),
    "celestial": ((110, 85, 10), (245, 210, 90), (255, 248, 200), (190, 235, 255)),
}


def px(img, x, y, c):
    if 0 <= x < 16 and 0 <= y < 16:
        img.putpixel((x, y), c + (255,) if len(c) == 3 else c)


def line(img, x1, y1, x2, y2, c):
    steps = max(abs(x2 - x1), abs(y2 - y1))
    for i in range(steps + 1):
        t = i / steps if steps else 0
        px(img, round(x1 + (x2 - x1) * t), round(y1 + (y2 - y1) * t), c)


def blade(img, pal, tip=(14, 1), base=(6, 9)):
    dark, mid, light, accent = pal
    line(img, tip[0], tip[1], base[0], base[1], mid)
    line(img, tip[0] - 1, tip[1], base[0] - 1, base[1], light)
    line(img, tip[0], tip[1] + 1, base[0], base[1] + 1, dark)
    px(img, tip[0], tip[1], accent)


def handle(img, pal, start=(6, 10), end=(2, 14), guard=True):
    dark, mid, light, accent = pal
    line(img, start[0], start[1], end[0], end[1], (90, 60, 35))
    line(img, start[0] - 1, start[1], end[0] - 1, end[1], (60, 40, 22))
    if guard:
        line(img, start[0] - 2, start[1] - 1, start[0] + 1, start[1] + 2, accent)


def sword(img, pal):
    blade(img, pal)
    handle(img, pal)


def dagger(img, pal):
    blade(img, pal, tip=(12, 3), base=(7, 8))
    handle(img, pal, start=(7, 9), end=(4, 12))


def katana(img, pal):
    dark, mid, light, accent = pal
    line(img, 14, 1, 5, 10, mid)
    line(img, 13, 1, 4, 10, light)
    line(img, 14, 2, 5, 11, dark)
    px(img, 15, 0, accent)
    handle(img, pal, start=(5, 11), end=(2, 14))


def axe(img, pal):
    dark, mid, light, accent = pal
    # wedge-shaped head, cutting edge on the right
    rows = {2: (9, 12), 3: (8, 13), 4: (8, 14), 5: (8, 13), 6: (9, 12)}
    for y, (x1, x2) in rows.items():
        for x in range(x1, x2 + 1):
            px(img, x, y, mid)
        px(img, x2, y, light)
        px(img, x1, y, dark)
    px(img, 14, 4, accent)
    line(img, 9, 6, 3, 14, (120, 88, 48))
    line(img, 8, 6, 2, 14, (78, 54, 28))


def mace(img, pal):
    dark, mid, light, accent = pal
    rows = {1: (9, 13), 2: (8, 14), 3: (8, 14), 4: (8, 14), 5: (8, 14), 6: (9, 13)}
    for y, (x1, x2) in rows.items():
        for x in range(x1, x2 + 1):
            px(img, x, y, mid)
        px(img, x1, y, dark)
        px(img, x2, y, dark)
    for x in range(9, 14):
        px(img, x, 2, light)
    px(img, 11, 0, accent)
    px(img, 15, 3, accent)
    px(img, 11, 7, accent)
    line(img, 8, 7, 2, 14, (120, 88, 48))
    line(img, 7, 7, 1, 14, (78, 54, 28))


def pickaxe(img, pal):
    dark, mid, light, accent = pal
    for i, x in enumerate(range(3, 14)):
        y = 4 + abs(x - 8) // 2
        px(img, x, y - 1, mid)
        px(img, x, y, dark)
        if x % 3 == 0:
            px(img, x, y - 2, light)
    px(img, 3, 3, accent)
    px(img, 13, 3, accent)
    line(img, 8, 5, 6, 14, (110, 75, 40))
    line(img, 9, 5, 7, 14, (75, 50, 26))


def bow(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.arc((3, 1, 15, 14), start=270, end=90, fill=mid + (255,), width=2)
    d.arc((4, 2, 14, 13), start=270, end=90, fill=light + (255,), width=1)
    line(img, 5, 2, 5, 13, accent)
    px(img, 4, 7, dark)


def crossbow(img, pal):
    dark, mid, light, accent = pal
    # barrel
    for i in range(11):
        x, y = 3 + i, 11 - i
        px(img, x, y, mid)
        px(img, x, y - 1, light)
        px(img, x + 1, y, dark)
    # muzzle glow
    px(img, 14, 0, accent)
    px(img, 13, 0, accent)
    px(img, 13, 1, accent)
    # scope + grip
    for x, y in [(8, 5), (9, 5), (9, 4), (10, 4)]:
        px(img, x, y, accent)
    for x, y in [(3, 12), (4, 12), (3, 13), (4, 13), (5, 13), (2, 12)]:
        px(img, x, y, dark)
    px(img, 5, 11, light)


def rod(img, pal):
    dark, mid, light, accent = pal
    line(img, 3, 14, 11, 4, mid)
    line(img, 2, 14, 10, 4, dark)
    d = ImageDraw.Draw(img)
    d.ellipse((9, 0, 14, 5), fill=accent + (255,), outline=dark + (255,))
    px(img, 11, 2, light)


def wand(img, pal):
    dark, mid, light, accent = pal
    line(img, 3, 14, 10, 5, (120, 95, 60))
    line(img, 2, 14, 9, 5, (80, 60, 35))
    for dx, dy in [(0, 0), (1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]:
        px(img, 11 + dx, 3 + dy, accent if abs(dx) + abs(dy) > 1 else light)


def orb(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.ellipse((3, 3, 12, 12), fill=mid + (255,), outline=dark + (255,))
    d.ellipse((5, 5, 8, 8), fill=light + (255,))
    px(img, 10, 10, accent)


def bomb(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.ellipse((3, 5, 12, 14), fill=mid + (255,), outline=dark + (255,))
    d.ellipse((5, 7, 7, 9), fill=light + (255,))
    line(img, 9, 4, 11, 1, (120, 90, 50))
    px(img, 12, 0, accent)
    px(img, 11, 0, accent)


def apple(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.ellipse((3, 4, 12, 13), fill=mid + (255,), outline=dark + (255,))
    d.ellipse((5, 6, 7, 8), fill=light + (255,))
    line(img, 8, 4, 9, 2, (90, 60, 30))
    d.ellipse((9, 1, 12, 3), fill=(90, 180, 70, 255))
    px(img, 6, 11, accent)


def spyglass(img, pal):
    dark, mid, light, accent = pal
    for i in range(12):
        x, y = 2 + i, 13 - i
        px(img, x, y, mid)
        px(img, x + 1, y, light)
        px(img, x, y + 1, dark)
    for x, y in [(13, 1), (14, 1), (14, 2), (13, 2)]:
        px(img, x, y, accent)
    for x, y in [(2, 13), (2, 14), (3, 14)]:
        px(img, x, y, dark)
    px(img, 7, 8, accent)
    px(img, 8, 7, light)


def hook(img, pal):
    dark, mid, light, accent = pal
    line(img, 2, 14, 10, 5, (120, 90, 50))
    line(img, 1, 14, 9, 5, (80, 60, 35))
    line(img, 10, 5, 13, 5, accent)
    line(img, 13, 5, 13, 9, mid)
    line(img, 13, 9, 11, 10, mid)
    px(img, 11, 11, light)


def helmet(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.pieslice((2, 2, 13, 14), start=180, end=360, fill=mid + (255,), outline=dark + (255,))
    d.rectangle((2, 8, 13, 11), fill=mid + (255,), outline=dark + (255,))
    d.rectangle((5, 8, 10, 10), fill=(25, 25, 30, 255))
    line(img, 4, 5, 6, 4, light)
    px(img, 7, 3, accent)


def chestplate(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.rectangle((3, 3, 12, 13), fill=mid + (255,), outline=dark + (255,))
    d.rectangle((6, 3, 9, 5), fill=(0, 0, 0, 0))
    d.rectangle((1, 4, 3, 9), fill=mid + (255,), outline=dark + (255,))
    d.rectangle((12, 4, 14, 9), fill=mid + (255,), outline=dark + (255,))
    line(img, 5, 6, 5, 11, light)
    px(img, 8, 8, accent)
    px(img, 8, 9, accent)


def leggings(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.rectangle((3, 2, 12, 6), fill=mid + (255,), outline=dark + (255,))
    d.rectangle((3, 6, 6, 14), fill=mid + (255,), outline=dark + (255,))
    d.rectangle((9, 6, 12, 14), fill=mid + (255,), outline=dark + (255,))
    line(img, 4, 8, 4, 12, light)
    px(img, 8, 4, accent)


def boots(img, pal):
    dark, mid, light, accent = pal
    d = ImageDraw.Draw(img)
    d.rectangle((2, 5, 6, 12), fill=mid + (255,), outline=dark + (255,))
    d.rectangle((9, 5, 13, 12), fill=mid + (255,), outline=dark + (255,))
    d.rectangle((2, 12, 7, 14), fill=dark + (255,))
    d.rectangle((9, 12, 14, 14), fill=dark + (255,))
    px(img, 3, 7, light)
    px(img, 10, 7, light)
    px(img, 5, 6, accent)
    px(img, 12, 6, accent)


TEMPLATES = {
    "sword": sword, "dagger": dagger, "katana": katana, "axe": axe, "mace": mace, "pickaxe": pickaxe,
    "bow": bow, "crossbow": crossbow, "rod": rod, "wand": wand, "orb": orb, "bomb": bomb, "apple": apple,
    "spyglass": spyglass, "hook": hook, "helmet": helmet, "chestplate": chestplate, "leggings": leggings,
    "boots": boots,
}

# item id -> (template, palette, model parent)
HANDHELD = "minecraft:item/handheld"
FLAT = "minecraft:item/generated"
ITEMS = {
    "thunder_hammer": ("axe", "thunder", HANDHELD),
    "frost_blade": ("sword", "frost", HANDHELD),
    "inferno_staff": ("rod", "inferno", HANDHELD),
    "shadow_katana": ("katana", "shadow", HANDHELD),
    "earthquake_mace": ("mace", "earth", HANDHELD),
    "vampire_dagger": ("dagger", "blood", HANDHELD),
    "explosive_bow": ("bow", "boom", FLAT),
    "storm_bow": ("bow", "storm", FLAT),
    "grappling_hook": ("hook", "nature", HANDHELD),
    "healing_wand": ("wand", "heal", HANDHELD),
    "void_pearl": ("orb", "void", FLAT),
    "grenade": ("bomb", "nature", FLAT),
    "hermes_boots": ("boots", "hermes", FLAT),
    "berserker_chestplate": ("chestplate", "berserk", FLAT),
    "titan_apple": ("apple", "titan", FLAT),
    "worldbreaker": ("mace", "mythic", HANDHELD),
    "excavator": ("pickaxe", "steel", HANDHELD),
    "smelter_pickaxe": ("pickaxe", "smelter", HANDHELD),
    "orbital_strike_cannon": ("spyglass", "orbital", HANDHELD),
    "plasma_railgun": ("crossbow", "plasma", HANDHELD),
    "singularity_grenade": ("orb", "singular", FLAT),
}
for set_id, pal in [("dragonscale", "dragon"), ("glacier", "glacier"), ("shadow", "shadow"),
                    ("juggernaut", "jugger"), ("celestial", "celestial")]:
    for piece, tpl in [("helmet", "helmet"), ("chestplate", "chestplate"), ("leggings", "leggings"), ("boots", "boots")]:
        ITEMS[f"{set_id}_{piece}"] = (tpl, pal, FLAT)


def main():
    if os.path.exists(PACK):
        shutil.rmtree(PACK)
    tex_dir = os.path.join(PACK, "assets", NS, "textures", "item")
    model_dir = os.path.join(PACK, "assets", NS, "models", "item")
    item_dir = os.path.join(PACK, "assets", NS, "items")
    for d in (tex_dir, model_dir, item_dir):
        os.makedirs(d, exist_ok=True)

    sheet = Image.new("RGBA", (16 * 7, 16 * 6), (30, 30, 34, 255))
    for i, (item_id, (template, palette, parent)) in enumerate(ITEMS.items()):
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        TEMPLATES[template](img, P[palette])
        img.save(os.path.join(tex_dir, item_id + ".png"))
        sheet.paste(img, ((i % 7) * 16, (i // 7) * 16), img)

        write(os.path.join(model_dir, item_id + ".json"),
              {"parent": parent, "textures": {"layer0": f"{NS}:item/{item_id}"}})
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
