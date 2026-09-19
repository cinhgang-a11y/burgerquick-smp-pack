"""
Renders a Minecraft JSON item model (elements + texture) to a PNG from a few angles, so 3D
models can be checked without opening the game.

    python preview_model.py <model.json> <texture.png> <out.png>
"""
import json
import math
import sys

from PIL import Image, ImageDraw

SCALE = 22          # pixels per model unit
VIEWS = [(35, 25), (145, 25), (0, 89)]   # (yaw, pitch) in degrees; last one looks straight down


def rotate_y(p, origin, degrees):
    """Minecraft element rotation around +Y (right-hand rule: +x turns toward -z)."""
    a = math.radians(degrees)
    x, z = p[0] - origin[0], p[2] - origin[2]
    return (x * math.cos(a) + z * math.sin(a) + origin[0], p[1], -x * math.sin(a) + z * math.cos(a) + origin[2])


def face_corners(f, t, face):
    """Corners in texture order: top-left, top-right, bottom-right, bottom-left."""
    x0, y0, z0 = f
    x1, y1, z1 = t
    return {
        "north": [(x1, y1, z0), (x0, y1, z0), (x0, y0, z0), (x1, y0, z0)],
        "south": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        "east": [(x1, y1, z1), (x1, y1, z0), (x1, y0, z0), (x1, y0, z1)],
        "west": [(x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0)],
        "up": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
        "down": [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
    }[face]


SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.6, "west": 0.6}


def camera(p, yaw, pitch):
    x, y, z = p[0] - 8, p[1] - 8, p[2] - 8
    a = math.radians(yaw)
    x, z = x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)
    b = math.radians(-pitch)
    y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
    return x, y, z


def perspective_coeffs(dst, src):
    """Coefficients for Image.transform(PERSPECTIVE) mapping dst quad -> src quad."""
    matrix = []
    for (x, y), (u, v) in zip(dst, src):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    b = [c for pair in src for c in pair]
    n = 8
    a = [row[:] + [b[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        a[col], a[pivot] = a[pivot], a[col]
        if abs(a[col][col]) < 1e-12:
            return None
        for r in range(n):
            if r != col:
                f = a[r][col] / a[col][col]
                for c in range(col, n + 1):
                    a[r][c] -= f * a[col][c]
    return [a[i][n] / a[i][i] for i in range(n)]


def render_view(model, texture, yaw, pitch, size):
    canvas = Image.new("RGBA", (size, size), (38, 38, 44, 255))
    tw, th = texture.size
    polys = []
    for el in model["elements"]:
        rot = el.get("rotation")
        for face, spec in el["faces"].items():
            corners = face_corners(el["from"], el["to"], face)
            if rot and rot["axis"] == "y":
                corners = [rotate_y(c, rot["origin"], rot["angle"]) for c in corners]
            cam = [camera(c, yaw, pitch) for c in corners]
            # back-face culling (camera looks toward -z)
            ax, ay = cam[1][0] - cam[0][0], cam[1][1] - cam[0][1]
            bx, by = cam[3][0] - cam[0][0], cam[3][1] - cam[0][1]
            if ax * by - ay * bx <= 0:
                continue
            depth = sum(c[2] for c in cam) / 4
            pts = [(size / 2 + c[0] * SCALE, size * 0.62 - c[1] * SCALE) for c in cam]
            polys.append((depth, pts, spec["uv"], SHADE[face]))
    for depth, pts, uv, shade in sorted(polys, key=lambda p: p[0]):
        u0, v0, u1, v1 = [c * tw / 16 for c in uv]
        src = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        coeffs = perspective_coeffs(pts, src)
        if not coeffs:
            continue
        warped = texture.transform((size, size), Image.PERSPECTIVE, coeffs, Image.NEAREST)
        if shade < 1:
            r, g, b, a = warped.split()
            r, g, b = (ch.point(lambda v, s=shade: int(v * s)) for ch in (r, g, b))
            warped = Image.merge("RGBA", (r, g, b, a))
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        canvas.paste(warped, (0, 0), Image.composite(warped.split()[3], mask.point(lambda v: 0), mask))
    return canvas


def main(model_path, texture_path, out_path):
    model = json.load(open(model_path, encoding="utf-8"))
    texture = Image.open(texture_path).convert("RGBA")
    size = 560
    views = [render_view(model, texture, yaw, pitch, size) for yaw, pitch in VIEWS]
    out = Image.new("RGBA", (size * len(views), size))
    for i, v in enumerate(views):
        out.paste(v, (i * size, 0))
    out.save(out_path)
    print("saved", out_path)


if __name__ == "__main__":
    main(*sys.argv[1:4])
