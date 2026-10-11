"""
Zombies guns: 3D held models built from boxes, plus an inventory icon drawn from the same boxes.

Every gun comes from the plugin's guns.json ("model" block: template, barrel length, stock,
magazine, scope, extras and three colours), so adding a gun there adds its model here.
Coordinates are Minecraft model units (16 = one block). The muzzle points to -z (forward in
the hand), the grip sits around z 4..8, y 1..6. Each gun also gets a Pack-a-Punch twin
("_pap"): same shape, purple camo and cyan glow.
"""
import colorsys
import json
import math
import os
import random

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GUNS_JSON = os.path.join(os.path.dirname(HERE), "zombie-waves-plugin", "src", "main", "resources", "guns.json")

SLOTS = ["metal_d", "metal_m", "metal_l", "black",
         "wood_d", "wood_m", "wood_l", "grip",
         "acc_d", "acc_m", "acc_l", "glow",
         "lens", "brass", "white", "red"]

ROYALE_JSON = os.path.join(os.path.dirname(HERE), "burger-royale-plugin", "src", "main", "resources", "weapons.json")

# Model id -> spec. Zombies guns are "zw_<id>" (plus a Pack-a-Punch twin), Burger Royale weapons "fn_<id>".
SPECS = {}
with open(GUNS_JSON, encoding="utf-8") as f:
    for g in json.load(f)["guns"]:
        SPECS["zw_" + g["id"]] = g
if os.path.exists(ROYALE_JSON):
    with open(ROYALE_JSON, encoding="utf-8") as f:
        for g in json.load(f)["weapons"]:
            SPECS["fn_" + g["id"]] = g
GUNS = list(SPECS)


# ---------------------------------------------------------------------- colours

def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def colours(gun, pap):
    m, w, a = (_hex(x) for x in SPECS[gun]["model"]["c"])
    c = {"metal_d": _shade(m, 0.72), "metal_m": m, "metal_l": _shade(m, 1.4), "black": (24, 24, 28),
         "wood_d": _shade(w, 0.75), "wood_m": w, "wood_l": _shade(w, 1.3), "grip": (38, 34, 32),
         "acc_d": _shade(a, 0.72), "acc_m": a, "acc_l": _shade(a, 1.3), "glow": _shade(a, 1.15),
         "lens": (90, 200, 230), "brass": (196, 156, 60), "white": (222, 222, 214), "red": (200, 40, 36)}
    return pap_colours(c) if pap else c


def pap_colours(colours):
    """Pack-a-Punch: metal and wood go purple camo, accents and glow go cyan."""
    out = {}
    for slot, (r, g, b) in colours.items():
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if slot in ("acc_d", "acc_m", "acc_l", "glow", "lens"):
            h, s, l = 0.5, 0.85, min(0.8, l * 1.1 + 0.1)
        elif slot in ("brass", "white", "red"):
            h, s = 0.83, 0.6
        else:
            h, s = (0.78 if slot.startswith("metal") or slot == "black" else 0.72), 0.45
            l = l * 1.05 + 0.04
        rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
        out[slot] = (int(rr * 255), int(gg * 255), int(bb * 255))
    return out


def cell(slot):
    i = SLOTS.index(slot)
    return [(i % 4) * 4, (i // 4) * 4, (i % 4) * 4 + 4, (i // 4) * 4 + 4]


def texture(gun, pap):
    c = colours(gun, pap)
    img = Image.new("RGBA", (16, 16))
    px = img.load()
    rnd = random.Random(sum(map(ord, gun)))
    for i, slot in enumerate(SLOTS):
        r, g, b = c[slot]
        for x in range((i % 4) * 4, (i % 4) * 4 + 4):
            for y in range((i // 4) * 4, (i // 4) * 4 + 4):
                n = 0 if slot in ("glow", "lens") else rnd.randint(-6, 6)
                if pap and slot.startswith(("metal", "wood")) and rnd.random() < 0.3:
                    n += 22  # camo flecks
                if slot.startswith("wood") and not pap and y % 2 == 0:
                    n -= 6   # grain
                px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), 255)
    return img


def box(frm, to, side, top=None):
    top = top or side
    frm = [max(-16.0, min(32.0, v)) for v in frm]
    to = [max(-16.0, min(32.0, v)) for v in to]
    faces = {f: {"uv": cell(side), "texture": "#main"} for f in ("north", "south", "east", "west")}
    faces["up"] = {"uv": cell(top), "texture": "#main"}
    faces["down"] = {"uv": cell(side), "texture": "#main"}
    return {"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to], "faces": faces}


# ---------------------------------------------------------------------- shared parts

def stock(kind, y0=6.0, y1=9.8, z0=8.0, long=15.0):
    if kind == "wood":
        return [box([7.2, y0, z0], [8.8, y1, z0 + 4], "wood_m", "wood_l"),
                box([7.2, y0 - 1.6, z0 + 4], [8.8, y1 - 0.2, long + 2], "wood_m", "wood_l"),
                box([7.1, y0 - 1.8, long + 1.6], [8.9, y1, long + 2.4], "wood_d")]
    if kind == "metal":
        return [box([7.3, y0 + 0.8, z0], [8.7, y1 - 0.4, long], "metal_d", "metal_m"),
                box([7.1, y0 - 0.6, long - 0.8], [8.9, y1, long + 0.6], "black")]
    if kind == "wire":
        return [box([7.6, y1 - 1.2, z0], [8.4, y1 - 0.5, long - 1], "metal_m"),
                box([7.6, y0 + 0.4, z0 + 1], [8.4, y0 + 1.1, long - 1], "metal_m"),
                box([7.5, y0 + 0.4, long - 1.6], [8.5, y1 - 0.5, long - 0.6], "metal_d")]
    if kind == "thumb":
        return [box([7.2, y0 - 0.5, z0], [8.8, y1, z0 + 3], "wood_m", "wood_l"),
                box([7.2, y0 - 2.5, z0 + 3], [8.8, y0 + 0.6, long + 2], "wood_m"),
                box([7.2, y1 - 1.6, z0 + 5], [8.8, y1, long + 2], "wood_m", "wood_l"),
                box([7.2, y0 - 2.5, long + 1], [8.8, y1, long + 2], "wood_d")]
    return []


def mag(kind, z=-0.5, y=6.5):
    if kind == "box":
        return [box([7.3, y - 5.5, z], [8.7, y, z + 2.3], "black")]
    if kind == "curved":
        return [box([7.3, y - 3.5, z], [8.7, y, z + 2.4], "metal_d"),
                box([7.3, y - 6.5, z + 1.0], [8.7, y - 3.5, z + 3.4], "metal_d")]
    if kind == "drum":
        return [box([6.5, y - 5, z - 1.2], [9.5, y, z + 3.2], "metal_d", "metal_m"),
                box([6.3, y - 3.6, z - 0.2], [9.7, y - 1.4, z + 2.2], "metal_l")]
    if kind == "belt":
        return [box([9.2, y - 3.2, z], [11.6, y + 1.2, z + 5.5], "acc_m", "acc_l"),
                box([8.9, y + 0.4, z + 1], [9.3, y + 2.6, z + 4], "brass")]
    if kind == "top":
        return [box([7.2, y + 3.5, z - 1], [8.8, y + 4.6, z + 7], "acc_m", "acc_l")]
    return []


def grip(z=4.0, slot="grip"):
    return [box([7.2, 1.5, z], [8.8, 6.5, z + 2.4], slot),
            box([7.6, 4.8, z - 2.2], [8.4, 5.8, z], "black")]   # trigger guard


def scope(kind, z0=-4.0, z1=6.0, y=10.0):
    if kind == "dot":
        return [box([7.4, y, z0 + 4], [8.6, y + 1.6, z0 + 6.5], "black"),
                box([7.6, y + 0.4, z0 + 3.9], [8.4, y + 1.2, z0 + 4], "red")]
    if kind == "long":
        return [box([7.4, y + 1, z0], [8.6, y + 2.2, z1], "black"),
                box([7.1, y + 0.7, z0 - 2.5], [8.9, y + 2.5, z0], "black"),
                box([7.25, y + 0.85, z0 - 2.6], [8.75, y + 2.35, z0 - 2.5], "lens"),
                box([7.2, y + 0.8, z1], [8.8, y + 2.4, z1 + 2], "black"),
                box([7.7, y, z0 + 2], [8.3, y + 1, z0 + 3], "metal_d"),
                box([7.7, y, z1 - 3], [8.3, y + 1, z1 - 2], "metal_d")]
    return []


# ---------------------------------------------------------------------- templates

def t_pistol(m):
    L = m.get("len", 0)
    x = m.get("x", [])
    w = 0.2 if "big" in x else 0
    parts = [
        box([7 - w, 7, -2 - L], [9 + w, 9.6 + w, 8], "metal_m", "metal_l"),          # slide
        box([7.2, 6, -1 - L], [8.8, 7, 8], "metal_d"),                                # frame
        box([7.6, 7.6, -2.5 - L], [8.4, 8.6, -2 - L], "black"),                       # muzzle
        box([7.1, 1.5, 5.2], [8.9, 6, 8.4], "wood_m", "wood_l"),                      # grip
        box([7.6, 4.8, 2.8], [8.4, 6, 5.2], "black"),                                 # trigger guard
        box([7.6, 9.6 + w, 7], [8.4, 10.1 + w, 7.6], "black"),                        # rear sight
        box([7.7, 9.6 + w, -1.6 - L], [8.3, 10 + w, -1.1 - L], "white"),              # front sight
        box([6.95 - w, 8.2, 3], [9.05 + w, 9.3, 5.5], "metal_l"),                     # ejection port
    ]
    if "extmag" in x:
        parts.append(box([7.3, -1.5, 5.6], [8.7, 1.5, 8], "black"))
    return parts


def t_revolver(m):
    L = m.get("len", 5)
    return [
        box([7.4, 8.2, -L - 1], [8.6, 9.4, 1], "metal_m", "metal_l"),                # barrel
        box([7.3, 9.4, -L - 1], [8.7, 9.9, 1], "metal_l"),                            # top rib
        box([6.8, 6.8, 1], [9.2, 9.6, 4.5], "metal_l", "metal_m"),                    # cylinder
        box([7.2, 6.2, 1], [8.8, 9.8, 7], "metal_m"),                                 # frame
        box([7.6, 9.6, 6], [8.4, 10.6, 7.2], "metal_d"),                              # hammer
        box([7.1, 1.5, 6], [8.9, 6.5, 9], "wood_m", "wood_l"),                        # grip
        box([7.6, 4.8, 3.5], [8.4, 6.2, 6], "metal_d"),                               # trigger guard
        box([7.7, 9.9, -L - 0.6], [8.3, 10.6, -L], "metal_d"),                        # front sight
    ]


def t_smg(m):
    L = m.get("len", 5)
    x = m.get("x", [])
    bull = m.get("stock") == "bullpup"
    body_end = 13 if bull else 8
    parts = [
        box([7, 6.5, -2], [9, 10, body_end], "metal_m", "metal_l"),                   # receiver
        box([7.6, 7.6, -2 - L], [8.4, 8.4, -2], "metal_d"),                           # barrel
        box([7.5, 7.5, -2.6 - L], [8.5, 8.5, -2 - L], "black"),                       # muzzle
        box([7.7, 10, -1.5], [8.3, 10.8, -0.8], "black"),                             # front sight
    ]
    if "shroud" in x:
        parts.append(box([7.3, 7.3, -1.2 - L], [8.7, 8.7, -2], "metal_d", "metal_m"))
    if "block" in x:
        parts.append(box([7, 4.5, -2], [9, 6.5, 3], "metal_m", "acc_m"))
    if "grip" in x:
        parts.append(box([7.4, 3.6, -1.5 - L * 0.4], [8.6, 6.5, -0.2 - L * 0.4], "wood_m" if m.get("stock") == "wood" else "black"))
    gz = 1.5 if bull else 4
    parts += grip(gz)
    mk = m.get("mag", "box")
    if mk == "grip":
        parts.append(box([7.3, -1.2, gz + 0.2], [8.7, 1.5, gz + 2.2], "black"))
    else:
        parts += mag(mk, z=(8.5 if bull else -0.5))
    if not bull:
        parts += stock(m.get("stock", "none"), long=14)
    else:
        parts.append(box([7.1, 5.2, 12.2], [8.9, 10.2, 13.4], "black"))
    parts += scope(m.get("scope", "none"))
    if m.get("stock") == "wood" and "grip" not in x:
        parts.append(box([7.1, 6.8, -1.5 - L * 0.5], [8.9, 8.2, -2], "wood_m", "wood_l"))
    return parts


def t_rifle(m):
    L = m.get("len", 10)
    x = m.get("x", [])
    bull = m.get("stock") == "bullpup"
    wood = m.get("stock") == "wood" or "longwood" in x
    end = 13 if bull else 8
    parts = [
        box([7, 7, -2], [9, 10, end], "metal_m", "metal_l"),                          # receiver
        box([7.6, 8.2, -2 - L], [8.4, 9, -2], "metal_d"),                             # barrel
        box([7.5, 8, -2.8 - L], [8.5, 9.2, -2 - L], "black"),                         # muzzle
        box([7.7, 9, -1.4 - L], [8.3, 10.8, -0.8 - L], "black"),                      # front sight
    ]
    hg = "wood_m" if wood else "metal_d"
    parts.append(box([7.1, 7.1, -2 - L * 0.55], [8.9, 9.3, -2], hg, "wood_l" if wood else "metal_m"))
    if "longwood" in x:
        parts.append(box([7.2, 6.4, -L * 0.85], [8.8, 8.2, 8], "wood_m", "wood_l"))
    if "handle" in x:
        parts += [box([7.5, 10, 0], [8.5, 11.8, 1], "metal_d"), box([7.5, 11.2, 0], [8.5, 11.8, 6], "metal_d"),
                  box([7.5, 10, 5], [8.5, 11.8, 6], "metal_d")]
    if "rail" in x:
        parts.append(box([7.5, 10, -1], [8.5, 10.5, end - 1], "black"))
    gz = 1.5 if bull else 4
    parts += grip(gz, "wood_d" if wood and not bull else "grip")
    parts += mag(m.get("mag", "box"), z=(8.5 if bull else -1), y=7)
    if bull:
        parts.append(box([7.1, 5.8, 12.4], [8.9, 10.4, 13.6], "black"))
    else:
        parts += stock(m.get("stock", "wood"), y0=6.5, y1=9.8, long=15)
    parts += scope(m.get("scope", "none"), y=10)
    return parts


def t_shotgun(m):
    L = m.get("len", 12)
    x = m.get("x", [])
    bull = m.get("stock") == "bullpup"
    parts = [box([7, 6.4, 2], [9, 10.2, 13 if bull else 8], "metal_d", "metal_m")]      # receiver
    if "double" in x:
        parts += [box([6.6, 8.6, -2 - L], [7.9, 10, 2], "metal_m", "metal_l"),
                  box([8.1, 8.6, -2 - L], [9.4, 10, 2], "metal_m", "metal_l"),
                  box([6.9, 7.2, -L * 0.6], [9.1, 8.6, 2], "wood_m", "wood_l")]
    else:
        parts += [box([7.3, 8.6, -2 - L], [8.7, 10, 2], "metal_m", "metal_l"),
                  box([7.4, 7.2, -L], [8.6, 8.6, 2], "metal_d")]
    parts.append(box([7.7, 10, -1.6 - L], [8.3, 10.6, -1 - L], "white"))                 # bead
    if "pump" in x:
        parts.append(box([7, 6.8, -L * 0.6], [9, 8.9, -2], "wood_m", "wood_l"))
    if "heatshield" in x:
        parts.append(box([7.2, 9.8, -L * 0.9], [8.8, 10.5, -2], "metal_l"))
    if "drum" in x:
        parts += mag("drum", z=0, y=6.4)
    gz = 1.5 if bull else 4.5
    parts += grip(gz, "wood_d" if m.get("stock") == "wood" else "grip")
    if not bull:
        parts += stock(m.get("stock", "wood"), y0=5, y1=9.4, long=16)
    else:
        parts.append(box([7.1, 5.6, 12.4], [8.9, 10.2, 13.6], "black"))
    return parts


def t_lmg(m):
    L = m.get("len", 12)
    x = m.get("x", [])
    parts = [
        box([6.8, 6.5, -2], [9.2, 10.5, 9], "metal_m", "metal_l"),                    # receiver
        box([7.55, 8.2, -2 - L], [8.45, 9, -2], "metal_d"),                           # barrel
        box([7.4, 8, -3 - L], [8.6, 9.2, -2 - L], "black"),                           # flash hider
        box([7.1, 6.8, -2 - L * 0.4], [8.9, 9.4, -2], "metal_d"),                     # handguard
        box([6.7, 10.5, 0], [9.3, 11.2, 7], "metal_d"),                               # feed cover
    ]
    if "shroud" in x:
        parts.append(box([7.2, 7.8, -1 - L], [8.8, 9.4, -2], "metal_l", "metal_m"))
    if "bipod" in x:
        parts += [box([7.2, 4.6, -L + 0.5], [7.7, 8.2, -L + 1.5], "black"),
                  box([8.3, 4.6, -L + 0.5], [8.8, 8.2, -L + 1.5], "black")]
    if "handle" in x:
        parts += [box([7.6, 10.5, -1], [8.4, 12.4, -0.2], "black"), box([7.6, 12, -1], [8.4, 12.6, 3], "black")]
    parts += grip(5, "wood_d" if m.get("stock") == "wood" else "grip")
    parts += mag(m.get("mag", "box"), z=0, y=7)
    parts += stock(m.get("stock", "metal"), y0=6, y1=10, z0=9, long=16)
    return parts


def t_sniper(m):
    L = m.get("len", 14)
    x = m.get("x", [])
    wood = m.get("stock") == "wood" or "longwood" in x
    parts = [
        box([7.65, 8.3, -2 - L], [8.35, 9, -1], "metal_d"),                           # long barrel
        box([7, 7, -1], [9, 10, 8], "metal_m", "metal_l"),                            # receiver
    ]
    if "brake" in x:
        parts.append(box([7.3, 7.9, -3.5 - L], [8.7, 9.4, -2 - L], "black"))
    else:
        parts.append(box([7.55, 8.2, -2.6 - L], [8.45, 9.1, -2 - L], "black"))
    if "longwood" in x:
        parts.append(box([7.2, 6.4, -L * 0.8], [8.8, 8.3, 8], "wood_m", "wood_l"))
    if "bolt" in x:
        parts += [box([9, 8.6, 6], [10.6, 9.2, 6.7], "metal_l"), box([10.2, 8.2, 5.8], [10.9, 9.6, 6.9], "black")]
    if "bipod" in x:
        parts += [box([7.45, 6, -L + 1], [7.95, 8.3, -L + 5], "black"), box([8.05, 6, -L + 1], [8.55, 8.3, -L + 5], "black")]
    if "coil" in x:
        for k in range(4):
            z = -L + 2 + k * 3
            parts.append(box([7.2, 7.8, z], [8.8, 9.5, z + 1], "glow"))
    parts += grip(6, "wood_d" if wood else "grip")
    parts += mag(m.get("mag", "none"), z=0.5, y=7)
    parts += stock(m.get("stock", "wood"), y0=6, y1=10, long=16)
    if m.get("scope", "none") == "long":
        parts += scope("long", z0=-4, z1=5, y=10)
    else:
        parts += [box([7.7, 9, -1 - L], [8.3, 10.4, -0.4 - L], "black"), box([7.6, 10, 5], [8.4, 10.8, 6], "black")]
    return parts


def t_launcher(m):
    L = m.get("len", 12)
    x = m.get("x", [])
    if "tube" in x:   # LAW: one fat olive tube
        return [box([6.8, 7, -L], [9.2, 9.8, 9], "acc_m", "acc_l"),
                box([6.6, 6.8, -L], [9.4, 10, -L + 1.2], "metal_d"),
                box([6.6, 6.8, 7.8], [9.4, 10, 9], "metal_d"),
                box([7.6, 9.8, -2], [8.4, 11.6, 0], "acc_d"),
                box([7.2, 2.5, 2], [8.8, 7, 4.2], "grip")]
    if "warhead" in x:  # RPG-7
        return [box([7.4, 7.6, -L + 2], [8.6, 9, 12], "metal_m", "metal_l"),
                box([7.2, 7.4, -4], [8.8, 9.2, 2], "wood_m", "wood_l"),
                box([6.6, 6.6, -L - 2], [9.4, 10, -L + 2], "acc_m", "acc_l"),
                box([7.2, 7.2, -L - 4], [8.8, 9.4, -L - 2], "acc_d"),
                box([7.6, 7.8, -L - 5], [8.4, 8.8, -L - 4], "acc_l"),
                box([7, 7, 10], [9, 9.6, 13], "metal_d"),
                box([7.2, 2.5, 2], [8.8, 7.4, 4.2], "grip"),
                box([7.6, 9.2, 0], [8.4, 11, 2], "black")]
    # China Lake: wide pump-action tube with a wooden stock.
    return [box([7, 7.4, -L], [9, 9.8, 4], "metal_m", "metal_l"),
            box([6.8, 7.2, -L - 0.6], [9.2, 10, -L], "black"),
            box([7.3, 5.8, -L + 1], [8.7, 7.4, 2], "metal_d"),
            box([7, 5.6, -L * 0.6], [9, 7.6, -1], "wood_m", "wood_l"),
            box([7, 6.4, 4], [9, 10, 8], "metal_d", "metal_m"),
            box([7.6, 9.8, -2], [8.4, 11.4, 1], "acc_m")] + grip(5, "wood_d") + stock("wood", y0=5.5, y1=9.6, long=16)


# ---------------------------------------------------------------------- wonder weapons

def t_raygun(m):
    return [
        box([7, 6.5, 1], [9, 10, 8], "metal_m", "metal_l"),
        box([6, 5.5, -2], [10, 11, -1], "acc_m", "acc_l"),
        box([6.6, 6.1, -4.2], [9.4, 10.4, -3.2], "acc_m", "acc_l"),
        box([7.1, 6.6, -6.4], [8.9, 9.9, -5.4], "acc_m", "acc_l"),
        box([7.55, 7.85, -7.5], [8.45, 8.75, 1], "glow"),
        box([7.35, 7.65, -8.5], [8.65, 8.95, -7.5], "glow"),
        box([7.7, 10, 2], [8.3, 12.2, 6], "metal_l"),
        box([7.2, 1.5, 5], [8.8, 6.5, 7.5], "metal_d"),
        box([7.3, 7, 8], [8.7, 9.5, 9.5], "acc_d"),
        box([6.9, 8, 3], [9.1, 9, 6], "glow"),
    ]


def t_raygun2(m):
    return [
        box([6.8, 6.5, -1], [9.2, 10.4, 8], "metal_m", "metal_l"),
        box([7.1, 9.3, -8], [8.9, 10.1, -1], "acc_m", "acc_l"),
        box([7.1, 6.8, -8], [8.9, 7.6, -1], "acc_m", "acc_l"),
        box([7.5, 7.8, -7], [8.5, 9.1, -1], "glow"),
        box([7.3, 7.6, -9], [8.7, 9.3, -8], "glow"),
        box([6.6, 10.4, 1], [9.4, 11.2, 6], "acc_d"),
        box([7.2, 1.5, 4.6], [8.8, 6.5, 7], "metal_d"),
        box([6.7, 8, 2], [9.3, 9, 5], "glow"),
    ]


def t_thundergun(m):
    return [
        box([6.2, 5.5, -3], [9.8, 10.8, 9], "metal_m", "metal_l"),                    # body
        box([5.6, 5, -6], [10.4, 11.4, -3], "acc_d", "acc_m"),                        # turbine housing
        box([6.2, 5.6, -6.2], [9.8, 10.8, -6], "glow"),                               # intake glow
        box([6.8, 6.2, -9], [9.2, 10.2, -6], "metal_d"),                              # barrel
        box([7.2, 6.6, -9.2], [8.8, 9.8, -9], "glow"),
        box([5.8, 6, 1], [6.2, 10.2, 7], "wood_m"),                                   # side planks
        box([9.8, 6, 1], [10.2, 10.2, 7], "wood_m"),
        box([7.4, 10.8, -1], [8.6, 12.4, 6], "metal_d"),                              # top handle
        box([7.2, 1.5, 5], [8.8, 5.5, 7.5], "wood_d"),                                # grip
        box([7, 6, 9], [9, 10, 13], "acc_m", "acc_l"),                                # rear tank
    ]


def t_wunderwaffe(m):
    return [
        box([7, 6.8, -2], [9, 9.6, 8], "metal_m", "metal_l"),                         # body
        box([7.6, 7.6, -9], [8.4, 8.4, -2], "metal_d"),                               # barrel
        box([7, 7, -10], [7.6, 9.4, -9], "brass"),                                    # prongs
        box([8.4, 7, -10], [9, 9.4, -9], "brass"),
        box([7.2, 9.6, -2], [8.8, 12.6, 1], "lens", "glow"),                          # vacuum tubes
        box([7.2, 9.6, 2.5], [8.8, 12.6, 5.5], "lens", "glow"),
        box([7.4, 12.6, -1.8], [8.6, 13.2, 5.2], "metal_d"),
        box([6.8, 7.4, -6], [9.2, 9, -5], "brass"),                                   # coils
        box([6.8, 7.4, -4], [9.2, 9, -3], "brass"),
    ] + grip(5, "wood_d") + stock("wood", y0=6, y1=9.4, long=15)


def t_freeze(m):
    return [
        box([7, 6.5, -1], [9, 9.6, 7], "metal_m", "metal_l"),
        box([7.4, 7.2, -6], [8.6, 8.6, -1], "acc_m", "acc_l"),                        # nozzle
        box([7, 6.8, -7.2], [9, 9, -6], "acc_l"),
        box([7.3, 9.6, -0.5], [8.7, 12.4, 5], "lens", "glow"),                        # frost tank
        box([7.2, 12.4, 0], [8.8, 12.8, 4.5], "metal_d"),
        box([7.2, 1.5, 4.6], [8.8, 6.5, 7], "metal_d"),
    ]


def t_minigun(m):
    parts = [
        box([6, 5.5, 2], [10, 11, 10], "metal_m", "metal_l"),
        box([5.6, 5.2, -12], [10.4, 11.2, -11], "metal_d", "metal_m"),
        box([5.6, 5.2, -4], [10.4, 11.2, -3], "metal_d", "metal_m"),
        box([7.5, 11, 3], [8.5, 13.5, 4], "black"),
        box([7.5, 13, 3], [8.5, 13.6, 9], "black"),
        box([7.5, 11, 8], [8.5, 13.5, 9], "black"),
        box([10, 3, 3], [12.6, 8, 8.5], "acc_m", "acc_l"),
        box([9.6, 6.5, 4], [10.1, 8.2, 7.5], "brass"),
        box([7.2, 1.5, 7], [8.8, 5.5, 9], "grip"),
    ]
    for k in range(6):
        a = math.radians(k * 60 + 30)
        cx, cy = 8 + math.cos(a) * 1.55, 8.2 + math.sin(a) * 1.55
        parts.append(box([cx - 0.45, cy - 0.45, -16], [cx + 0.45, cy + 0.45, 2], "metal_l"))
    parts.append(box([7.55, 7.75, -16], [8.45, 8.65, 2], "black"))
    return parts


TEMPLATES = {"pistol": t_pistol, "revolver": t_revolver, "smg": t_smg, "rifle": t_rifle, "shotgun": t_shotgun,
             "lmg": t_lmg, "sniper": t_sniper, "launcher": t_launcher, "raygun": t_raygun, "raygun2": t_raygun2,
             "thundergun": t_thundergun, "wunderwaffe": t_wunderwaffe, "freeze": t_freeze, "minigun": t_minigun}


def elements(gun):
    m = SPECS[gun]["model"]
    return TEMPLATES[m["t"]](m)


# ---------------------------------------------------------------------- icons

def _slot_of(e):
    return SLOTS[[cell(s) for s in SLOTS].index(e["faces"]["east"]["uv"])]


def _outline(img):
    px = img.load()
    size = img.width
    edge = []
    for x in range(size):
        for y in range(size):
            if px[x, y][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < size and 0 <= ny < size) or px[nx, ny][3] == 0:
                    edge.append((x, y))
                    break
    for x, y in edge:
        r, g, b, a = px[x, y]
        px[x, y] = (int(r * 0.55), int(g * 0.55), int(b * 0.55), a)
    return img


def icon(gun, pap, size=32):
    """Point-sample a side view (muzzle right). Long guns lie diagonally, like vanilla weapons."""
    c = colours(gun, pap)
    els = elements(gun)
    zs = [v for e in els for v in (e["from"][2], e["to"][2])]
    ys = [v for e in els for v in (e["from"][1], e["to"][1])]
    z0, z1, y0, y1 = min(zs), max(zs), min(ys), max(ys)
    L, H = z1 - z0, y1 - y0
    diagonal = L / H > 2.0
    zc, yc = (z0 + z1) / 2, (y0 + y1) / 2
    s = (size - 2) * math.sqrt(2) / (L + H) if diagonal else (size - 3) / max(L, H)
    order = sorted(els, key=lambda e: -e["to"][0])          # nearest (+x) first
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    r2 = math.sqrt(2)
    for x in range(size):
        for y in range(size):
            dx, dy = x + 0.5 - size / 2, y + 0.5 - size / 2
            if diagonal:
                u, v = (dx - dy) / r2 / s, (-dx - dy) / r2 / s
            else:
                u, v = dx / s, -dy / s
            mz, my = zc - u, yc + v
            for e in order:
                if e["from"][2] <= mz <= e["to"][2] and e["from"][1] <= my <= e["to"][1]:
                    col = c[_slot_of(e)]
                    if e["to"][1] - my < 0.9 / s:
                        col = tuple(min(255, int(k * 1.25)) for k in col)
                    px[x, y] = col + (255,)
                    break
    return _outline(img)
