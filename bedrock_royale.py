"""Bedrock resource pack + Geyser custom item mappings for Burger Royale.

Bedrock players (via Geyser) see the guns and pickaxe skins with their own icons instead of plain
hoes and iron pickaxes. Reads the flat item icons from BurgerQuickPack and the weapon list from the
plugin's weapons.json, and writes:
  dist-bedrock/BurgerRoyale-Bedrock.mcpack   -> plugins/Geyser-Spigot/packs/
  dist-bedrock/burger_royale_items.json      -> plugins/Geyser-Spigot/custom_mappings/
Run: python bedrock_royale.py [--install <royale-server dir>]
"""
import json
import os
import shutil
import sys
import uuid
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "BurgerQuickPack", "assets", "burgerquick", "textures", "item")
MODELS = os.path.join(HERE, "BurgerQuickPack", "assets", "burgerquick", "models", "item")
WEAPONS = os.path.join(os.path.dirname(HERE), "burger-royale-plugin", "src", "main", "resources", "weapons.json")
OUT = os.path.join(HERE, "dist-bedrock")
NS = "burgerquick"
# Stable pack ids, so Bedrock clients update the cached pack instead of piling up copies.
HEADER_UUID = "6f1c9a52-3e0b-4d1a-9a77-2b5e1c0d4a11"
MODULE_UUID = "a3b7e2c4-8d19-4f6e-b0c2-7e5d9f1a2b33"
VERSION = [1, 2, 0]

# Weapon class -> the vanilla hoe the plugin builds it on (Weapon.hoe()).
HOE = {"pistol": "wooden_hoe", "smg": "stone_hoe", "rifle": "golden_hoe", "shotgun": "iron_hoe",
       "sniper": "diamond_hoe", "launcher": "netherite_hoe"}
PICKAXES = {"default": "Default Pickaxe", "raiders_revenge": "Raider's Revenge", "ac_dc": "AC/DC",
            "reaper": "Reaper", "candy_axe": "Candy Axe", "pick_squeak": "Pick Squeak"}


FACES = {"north": "north", "south": "south", "east": "west", "west": "east", "up": "up", "down": "down"}


def attachable(pack, model):
    """Converts models/item/<model>_3d.json (plain cuboids) into a Bedrock attachable."""
    src = os.path.join(MODELS, model + "_3d.json")
    tex = os.path.join(TEX, model + "_3d.png")
    if not os.path.exists(src) or not os.path.exists(tex):
        return False
    from PIL import Image
    j = json.load(open(src, encoding="utf-8"))
    tw, th = Image.open(tex).size
    ku, kv = tw / 16.0, th / 16.0
    cubes = []
    for e in j["elements"]:
        f, t = e["from"], e["to"]
        uv = {}
        for face, d in e.get("faces", {}).items():
            u0, v0, u1, v1 = d.get("uv", [0, 0, 16, 16])
            bface = FACES[face]
            if face in ("up", "down"):
                # Bedrock draws up/down faces flipped compared to Java.
                uv[bface] = {"uv": [u1 * ku, v1 * kv], "uv_size": [(u0 - u1) * ku, (v0 - v1) * kv]}
            else:
                uv[bface] = {"uv": [u0 * ku, v0 * kv], "uv_size": [(u1 - u0) * ku, (v1 - v0) * kv]}
        cubes.append({"origin": [-t[0] + 8, f[1], f[2] - 8], "size": [t[0] - f[0], t[1] - f[1], t[2] - f[2]], "uv": uv})
    name = NS + "_" + model
    root = "bq_" + model
    geo = {"format_version": "1.16.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry." + name, "texture_width": tw, "texture_height": th,
                        "visible_bounds_width": 4, "visible_bounds_height": 4.5, "visible_bounds_offset": [0, 0.75, 0]},
        "bones": [
            {"name": root, "binding": "c.item_slot == 'head' ? 'head' : q.item_slot_to_bone_name(c.item_slot)", "pivot": [0, 8, 0]},
            {"name": root + "_x", "parent": root, "pivot": [0, 8, 0]},
            {"name": root + "_y", "parent": root + "_x", "pivot": [0, 8, 0]},
            {"name": root + "_z", "parent": root + "_y", "pivot": [0, 8, 0]},
            {"name": root + "_body", "parent": root + "_z", "pivot": [0, 8, 0], "cubes": cubes},
        ]}]}
    os.makedirs(os.path.join(pack, "models", "entity"), exist_ok=True)
    json.dump(geo, open(os.path.join(pack, "models", "entity", model + ".geo.json"), "w"), indent=1)
    shutil.copy(tex, os.path.join(pack, "textures", "items", model + "_3d.png"))

    disp = j.get("display", {})

    def bones(d, base_rot, base_pos, base_scale):
        r = d.get("rotation", [0, 0, 0]); tr = d.get("translation", [0, 0, 0]); sc = d.get("scale", [1, 1, 1])
        return {
            root: {"rotation": base_rot, "position": base_pos, "scale": base_scale},
            root + "_x": {"rotation": [-r[0], 0, 0], "position": [-tr[0], tr[1], tr[2]], "scale": [sc[0], sc[1], sc[2]]},
            root + "_y": {"rotation": [0, -r[1], 0]},
            root + "_z": {"rotation": [0, 0, r[2]]},
        }
    anims = {
        "thirdperson_main_hand": bones(disp.get("thirdperson_righthand", {}), [90, 0, 0], [0, 13, -3], 1),
        "thirdperson_off_hand": bones(disp.get("thirdperson_lefthand", {}), [90, 0, 0], [0, 13, -3], 1),
        "firstperson_main_hand": bones(disp.get("firstperson_righthand", {}), [90, 60, -40], [4, 10, 4], 1.5),
        "firstperson_off_hand": bones(disp.get("firstperson_lefthand", {}), [90, 60, -40], [4, 10, 4], 1.5),
        "head": bones(disp.get("head", {}), [0, 0, 0], [0, 19.9, 0], 0.625),
    }
    os.makedirs(os.path.join(pack, "animations"), exist_ok=True)
    json.dump({"format_version": "1.8.0", "animations": {
        "animation." + name + "." + k: {"loop": True, "bones": v} for k, v in anims.items()}},
        open(os.path.join(pack, "animations", model + ".animation.json"), "w"), indent=1)
    os.makedirs(os.path.join(pack, "attachables"), exist_ok=True)
    json.dump({"format_version": "1.10.0", "minecraft:attachable": {"description": {
        "identifier": NS + ":" + model,
        "materials": {"default": "entity_alphatest", "enchanted": "entity_alphatest_glint"},
        "textures": {"default": "textures/items/" + model + "_3d", "enchanted": "textures/misc/enchanted_item_glint"},
        "geometry": {"default": "geometry." + name},
        "scripts": {
            "pre_animation": ["v.main_hand = c.item_slot == 'main_hand';", "v.off_hand = c.item_slot == 'off_hand';", "v.head = c.item_slot == 'head';"],
            "animate": [{"thirdperson_main_hand": "v.main_hand && !c.is_first_person"}, {"thirdperson_off_hand": "v.off_hand && !c.is_first_person"},
                        {"firstperson_main_hand": "v.main_hand && c.is_first_person"}, {"firstperson_off_hand": "v.off_hand && c.is_first_person"},
                        {"head": "v.head"}]},
        "animations": {k: "animation." + name + "." + k for k in anims},
        "render_controllers": ["controller.render.item_default"]}}},
        open(os.path.join(pack, "attachables", model + ".attachable.json"), "w"), indent=1)
    return True


EXTRA = [
    ("paper", "fn_bandages", "Bandages"), ("red_shulker_box", "fn_medkit", "Med Kit"),
    ("potion", "fn_small_shield", "Small Shield Potion"), ("potion", "fn_shield_potion", "Shield Potion"),
    ("potion", "fn_slurp", "Slurp Juice"), ("potion", "fn_chug_jug", "Chug Jug"),
    ("fire_charge", "fn_grenade", "Grenade"), ("iron_trapdoor", "fn_trap", "Damage Trap"), ("slime_block", "fn_launch_pad", "Launch Pad"),
    ("iron_nugget", "fn_ammo_light", "Light Bullets"), ("gold_nugget", "fn_ammo_medium", "Medium Bullets"),
    ("copper_ingot", "fn_ammo_heavy", "Heavy Bullets"), ("red_dye", "fn_ammo_shells", "Shells"), ("firework_rocket", "fn_ammo_rockets", "Rockets"),
    ("brick_wall", "fn_build_wall", "Wall"), ("smooth_stone_slab", "fn_build_floor", "Floor"), ("oak_stairs", "fn_build_ramp", "Ramp"),
    ("light_gray_glazed_terracotta", "fn_build_cone", "Cone"), ("shears", "fn_build_edit", "Edit"), ("iron_sword", "fn_build_back", "Back to weapons"),
]


def main():
    weapons = [w for w in json.load(open(WEAPONS, encoding="utf-8"))["weapons"] if "model" in w]
    entries = []   # (java item, model id, display name, handheld)
    for w in weapons:
        entries.append(("minecraft:" + HOE.get(w["class"], "copper_hoe"), "fn_" + w["id"], w["name"], True))
    for pid, name in PICKAXES.items():
        entries.append(("minecraft:iron_pickaxe", "fn_pick_" + pid, name, True))
    # Heals, shields, grenade, gadgets, ammo and build tools (royale_items.py icons).
    for java, model, name in EXTRA:
        entries.append(("minecraft:" + java, model, name, False))

    shutil.rmtree(OUT, ignore_errors=True)
    pack = os.path.join(OUT, "pack")
    os.makedirs(os.path.join(pack, "textures", "items"))
    texture_data, mappings = {}, {}
    for java, model, name, handheld in entries:
        src = os.path.join(TEX, model + ".png")
        if not os.path.exists(src):
            print("missing icon", src)
            continue
        shutil.copy(src, os.path.join(pack, "textures", "items", model + ".png"))
        icon = NS + "." + model
        texture_data[icon] = {"textures": ["textures/items/" + model]}
        mappings.setdefault(java, []).append({
            "type": "definition",
            "model": NS + ":" + model,
            "bedrock_identifier": NS + ":" + model,
            "display_name": name,
            "bedrock_options": {"icon": icon, "display_handheld": handheld, "allow_offhand": False, "creative_category": "equipment"},
        })

    # 3D guns: Java model -> Bedrock geometry + attachable (held in hand, first and third person).
    for w in weapons:
        if attachable(pack, "fn_" + w["id"]):
            pass
        else:
            print("no 3D model for", w["id"])

    json.dump({"resource_pack_name": "Burger Royale", "texture_name": "atlas.items", "texture_data": texture_data},
              open(os.path.join(pack, "textures", "item_texture.json"), "w"), indent=2)
    json.dump({
        "format_version": 2,
        "header": {"name": "Burger Royale", "description": "Guns and pickaxe skins for Burger Royale", "uuid": HEADER_UUID,
                   "version": VERSION, "min_engine_version": [1, 21, 0]},
        "modules": [{"type": "resources", "uuid": MODULE_UUID, "version": VERSION}],
    }, open(os.path.join(pack, "manifest.json"), "w"), indent=2)
    icon_src = os.path.join(TEX, "fn_scar.png")
    if os.path.exists(icon_src):
        from PIL import Image
        Image.open(icon_src).convert("RGBA").resize((128, 128), Image.NEAREST).save(os.path.join(pack, "pack_icon.png"))

    mcpack = os.path.join(OUT, "BurgerRoyale-Bedrock.mcpack")
    with zipfile.ZipFile(mcpack, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(pack):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, pack).replace(os.sep, "/"))
    mapping_file = os.path.join(OUT, "burger_royale_items.json")
    json.dump({"format_version": 2, "items": mappings}, open(mapping_file, "w"), indent=2)
    print("Built", mcpack, "with", len(texture_data), "items;", mapping_file)

    if "--install" in sys.argv:
        server = sys.argv[sys.argv.index("--install") + 1]
        geyser = os.path.join(server, "plugins", "Geyser-Spigot")
        os.makedirs(os.path.join(geyser, "packs"), exist_ok=True)
        os.makedirs(os.path.join(geyser, "custom_mappings"), exist_ok=True)
        shutil.copy(mcpack, os.path.join(geyser, "packs"))
        shutil.copy(mapping_file, os.path.join(geyser, "custom_mappings"))
        print("Installed into", geyser)


if __name__ == "__main__":
    main()
