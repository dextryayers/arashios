#!/usr/bin/env python3
"""Generate raster brand assets that cannot rely on an SVG renderer.

Outputs:
  branding/grub/background.png
  branding/grub/select_*.png
  branding/plymouth/logo.png
  branding/plymouth/progress_box.png
  branding/plymouth/progress_bar.png
  branding/logo/arashios-favicon.ico
  branding/logo/hicolor/<size>x<size>/apps/arashios.png
  branding/wallpaper/*.png
  branding/boot/splash.png
  branding/boot/splash800x600.png
  branding/boot/grub-splash.png

The generator uses only the Python standard library. Every composition is
derived from branding/tokens.json so raster assets, CSS, and Qt styles share
one palette. Output is deterministic so `--check` can reject stale assets.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import zlib
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parent.parent
TOKENS_PATH = ROOT / "branding" / "tokens.json"
GRUB_DIR = ROOT / "branding" / "grub"
PLYMOUTH_DIR = ROOT / "branding" / "plymouth"
LOGO_DIR = ROOT / "branding" / "logo"
WALLPAPER_DIR = ROOT / "branding" / "wallpaper"
BOOT_DIR = ROOT / "branding" / "boot"

SELECT_NAMES = ("nw", "n", "ne", "w", "c", "e", "sw", "s", "se")
FAVICON_SIZES = (16, 24, 32, 48, 64, 128, 256)
WALLPAPERS = ("kage-sumi", "kage-shuriken", "kage-bamboo", "kage-washi", "kage-storm")

Color = tuple[int, int, int]
RGBA = tuple[int, int, int, int]


def load_palette() -> dict[str, Color]:
    data = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    palette: dict[str, Color] = {}
    for group, shades in data["color"].items():
        for shade, value in shades.items():
            palette[f"{group}.{shade}"] = hex_color(value)
    return palette


def hex_color(value: str) -> Color:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))


def blend(base: Color, overlay: Color, alpha: float) -> Color:
    if alpha <= 0:
        return base
    if alpha >= 1:
        return overlay
    return (
        clamp(base[0] * (1.0 - alpha) + overlay[0] * alpha),
        clamp(base[1] * (1.0 - alpha) + overlay[1] * alpha),
        clamp(base[2] * (1.0 - alpha) + overlay[2] * alpha),
    )


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def encode_png(width: int, height: int, rows: Sequence[bytes], color_type: int) -> bytes:
    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )


def encode_ico(images: Sequence[tuple[int, bytes]]) -> bytes:
    count = len(images)
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + 16 * count
    entries = bytearray()
    payload = bytearray()
    for size, data in images:
        width = 0 if size >= 256 else size
        entries += struct.pack(
            "<BBBBHHII",
            width,
            width,
            0,
            0,
            1,
            32,
            len(data),
            offset,
        )
        payload += data
        offset += len(data)
    return header + bytes(entries) + bytes(payload)


def gradient_rows(
    width: int,
    height: int,
    start: Color,
    end: Color,
    horizontal: float = 0.0,
) -> list[bytearray]:
    rows: list[bytearray] = []
    for y in range(height):
        t = y / max(height - 1, 1)
        row_color = blend(start, end, t)
        if horizontal <= 0:
            rows.append(bytearray(bytes(row_color) * width))
            continue
        row = bytearray(width * 3)
        for x in range(width):
            u = x / max(width - 1, 1)
            color = blend(row_color, end, u * horizontal)
            offset = x * 3
            row[offset : offset + 3] = bytes(color)
        rows.append(row)
    return rows


def set_pixel(rows: list[bytearray], x: int, y: int, color: Color, alpha: float = 1.0) -> None:
    if y < 0 or y >= len(rows):
        return
    width = len(rows[0]) // 3
    if x < 0 or x >= width:
        return
    offset = x * 3
    base = (rows[y][offset], rows[y][offset + 1], rows[y][offset + 2])
    rows[y][offset : offset + 3] = bytes(blend(base, color, alpha))


def draw_rect(
    rows: list[bytearray],
    x: float,
    y: float,
    width: float,
    height: float,
    color: Color,
    alpha: float = 1.0,
) -> None:
    left = max(0, int(math.floor(x)))
    top = max(0, int(math.floor(y)))
    right = min(len(rows[0]) // 3, int(math.ceil(x + width)))
    bottom = min(len(rows), int(math.ceil(y + height)))
    for py in range(top, bottom):
        row = rows[py]
        for px in range(left, right):
            offset = px * 3
            base = (row[offset], row[offset + 1], row[offset + 2])
            row[offset : offset + 3] = bytes(blend(base, color, alpha))


def draw_line(
    rows: list[bytearray],
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    thickness: float,
    color: Color,
    alpha: float = 1.0,
) -> None:
    half = max(thickness, 1.0) / 2.0
    left = max(0, int(math.floor(min(x0, x1) - half - 1)))
    right = min(len(rows[0]) // 3, int(math.ceil(max(x0, x1) + half + 1)))
    top = max(0, int(math.floor(min(y0, y1) - half - 1)))
    bottom = min(len(rows), int(math.ceil(max(y0, y1) + half + 1)))
    dx = x1 - x0
    dy = y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return
    for py in range(top, bottom):
        row = rows[py]
        for px in range(left, right):
            if length_sq == 0:
                distance = math.hypot(px - x0, py - y0)
            else:
                t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / length_sq))
                distance = math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))
            if distance > half + 1.0:
                continue
            if distance <= half:
                pixel_alpha = alpha
            else:
                pixel_alpha = alpha * max(0.0, 1.0 - (distance - half))
            offset = px * 3
            base = (row[offset], row[offset + 1], row[offset + 2])
            row[offset : offset + 3] = bytes(blend(base, color, pixel_alpha))


def draw_ring(
    rows: list[bytearray],
    cx: float,
    cy: float,
    radius: float,
    thickness: float,
    color: Color,
    alpha: float = 1.0,
    gap: tuple[float, float] | None = None,
) -> None:
    half = thickness / 2.0
    left = max(0, int(math.floor(cx - radius - half - 2)))
    right = min(len(rows[0]) // 3, int(math.ceil(cx + radius + half + 2)))
    top = max(0, int(math.floor(cy - radius - half - 2)))
    bottom = min(len(rows), int(math.ceil(cy + radius + half + 2)))
    for py in range(top, bottom):
        row = rows[py]
        dy = py - cy
        for px in range(left, right):
            dx = px - cx
            distance = math.hypot(dx, dy)
            edge = abs(distance - radius)
            if edge > half + 1.5:
                continue
            if gap is not None:
                angle = math.degrees(math.atan2(dy, dx))
                if gap[0] < angle < gap[1]:
                    continue
            if edge <= half:
                pixel_alpha = alpha
            else:
                pixel_alpha = alpha * max(0.0, 1.0 - (edge - half) / 1.5)
            offset = px * 3
            base = (row[offset], row[offset + 1], row[offset + 2])
            row[offset : offset + 3] = bytes(blend(base, color, pixel_alpha))


def draw_disc(
    rows: list[bytearray],
    cx: float,
    cy: float,
    radius: float,
    color: Color,
    alpha: float = 1.0,
) -> None:
    left = max(0, int(math.floor(cx - radius - 2)))
    right = min(len(rows[0]) // 3, int(math.ceil(cx + radius + 2)))
    top = max(0, int(math.floor(cy - radius - 2)))
    bottom = min(len(rows), int(math.ceil(cy + radius + 2)))
    for py in range(top, bottom):
        row = rows[py]
        for px in range(left, right):
            distance = math.hypot(px - cx, py - cy)
            if distance > radius + 1:
                continue
            pixel_alpha = alpha if distance <= radius else alpha * max(0.0, 1.0 - (distance - radius))
            offset = px * 3
            base = (row[offset], row[offset + 1], row[offset + 2])
            row[offset : offset + 3] = bytes(blend(base, color, pixel_alpha))


def draw_polygon(
    rows: list[bytearray],
    points: Sequence[tuple[float, float]],
    color: Color,
    alpha: float = 1.0,
) -> None:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    left = max(0, int(math.floor(min(xs))))
    right = min(len(rows[0]) // 3, int(math.ceil(max(xs))))
    top = max(0, int(math.floor(min(ys))))
    bottom = min(len(rows), int(math.ceil(max(ys))))
    for py in range(top, bottom):
        row = rows[py]
        for px in range(left, right):
            inside = False
            j = len(points) - 1
            for i, point in enumerate(points):
                xi, yi = point
                xj, yj = points[j]
                if ((yi > py) != (yj > py)) and (
                    px < (xj - xi) * (py - yi) / ((yj - yi) or 1e-9) + xi
                ):
                    inside = not inside
                j = i
            if inside:
                offset = px * 3
                base = (row[offset], row[offset + 1], row[offset + 2])
                row[offset : offset + 3] = bytes(blend(base, color, alpha))


def draw_grid(
    rows: list[bytearray],
    step: int,
    color: Color,
    alpha: float,
) -> None:
    height = len(rows)
    width = len(rows[0]) // 3
    for y in range(0, height, step):
        row = rows[y]
        for x in range(0, width, step * 2):
            offset = x * 3
            for span in range(0, min(step, width - x)):
                index = offset + span * 3
                base = (row[index], row[index + 1], row[index + 2])
                row[index : index + 3] = bytes(blend(base, color, alpha))
    for x in range(0, width, step):
        for y in range(0, height, step * 2):
            for span in range(0, min(step, height - y)):
                target = rows[y + span]
                offset = x * 3
                base = (target[offset], target[offset + 1], target[offset + 2])
                target[offset : offset + 3] = bytes(blend(base, color, alpha))


def add_grain(rows: list[bytearray], color: Color, seed: int = 7) -> None:
    """Add deterministic sparse grain without importing random state."""
    height = len(rows)
    width = len(rows[0]) // 3
    state = seed
    for _ in range((width * height) // 14000):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        x = state % width
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        y = state % height
        set_pixel(rows, x, y, color, 0.035)


def build_background(palette: dict[str, Color]) -> bytes:
    width, height = 1920, 1080
    sumi900 = palette["sumi.900"]
    sumi700 = palette["sumi.700"]
    washi = palette["washi.100"]
    ash = palette["ash.400"]
    vermilion = palette["vermilion.500"]
    ember = palette["ember.400"]
    rows = gradient_rows(width, height, sumi900, sumi700)
    draw_grid(rows, 120, ash, 0.028)
    cx, cy = width * 0.30, height * 0.50
    draw_ring(rows, cx, cy, 300, 9, washi, 0.88, gap=(-125.0, -48.0))
    draw_ring(rows, cx, cy, 306, 2, vermilion, 0.18)
    draw_disc(rows, cx + 262, cy - 248, 11, ember, 0.92)

    left = max(0, int(cx - 320))
    right = min(width, int(cx + 320))
    top = max(0, int(cy - 320))
    bottom = min(height, int(cy + 320))
    for y in range(top, bottom):
        row = rows[y]
        for x in range(left, right):
            distance = math.hypot(x - cx, y - cy)
            glow = max(0.0, 1.0 - distance / (width * 0.55))
            if glow <= 0:
                continue
            offset = x * 3
            base = (row[offset], row[offset + 1], row[offset + 2])
            row[offset : offset + 3] = bytes(blend(base, vermilion, glow * glow * 0.12))

    return encode_png(width, height, rows, 2)


def build_select_pixmap(palette: dict[str, Color]) -> bytes:
    width, height = 10, 10
    color = palette["ember.400"]
    return encode_png(width, height, [bytes(color) * width] * height, 2)


def build_plymouth_logo(palette: dict[str, Color]) -> bytes:
    width, height = 256, 256
    washi = palette["washi.100"]
    vermilion = palette["vermilion.500"]
    rows: list[bytearray] = [bytearray(width * 4) for _ in range(height)]
    for y in range(height):
        row = rows[y]
        for x in range(width):
            dx = x - width / 2
            dy = y - height / 2
            distance = math.hypot(dx, dy)
            edge = abs(distance - 96.0)
            angle = math.degrees(math.atan2(dy, dx))
            alpha = 0
            if edge <= 6.0 and not (-130.0 < angle < -50.0):
                alpha = 255 if edge <= 4.5 else int(255 * max(0.0, 1.0 - (edge - 4.5) / 1.5))
            dot_distance = math.hypot(x - 188, y - 68)
            if dot_distance <= 9:
                red = (*vermilion, 255)
            elif dot_distance <= 10.5:
                red = (*vermilion, int(255 * max(0.0, 1.0 - (dot_distance - 9) / 1.5)))
            else:
                red = (0, 0, 0, 0)
            rgba: RGBA
            if red[3]:
                rgba = red
            else:
                rgba = (*washi, alpha)
            offset = x * 4
            row[offset : offset + 4] = bytes(rgba)
    return encode_png(width, height, rows, 6)


def build_plymouth_progress_bar(palette: dict[str, Color], color_name: str) -> bytes:
    width, height = 320, 2
    color = palette[color_name]
    return encode_png(width, height, [bytes(color) * width] * height, 2)


def build_wallpaper(name: str, palette: dict[str, Color]) -> bytes:
    width, height = 3840, 2160
    sumi900 = palette["sumi.900"]
    sumi800 = palette["sumi.800"]
    sumi700 = palette["sumi.700"]
    washi50 = palette["washi.50"]
    washi100 = palette["washi.100"]
    washi200 = palette["washi.200"]
    ash300 = palette["ash.300"]
    ash400 = palette["ash.400"]
    ember400 = palette["ember.400"]
    vermilion = palette["vermilion.500"]
    vermilion400 = palette["vermilion.400"]
    jade = palette["jade.500"]
    gold = palette["gold.500"]

    if name == "kage-washi":
        rows = gradient_rows(width, height, washi50, washi200)
        for y in range(0, height, 5):
            draw_line(rows, 0, y, width, y + 2, 1, ash400, 0.035)
        draw_ring(rows, width * 0.26, height * 0.50, 720, 26, sumi700, 0.09, gap=(-135, -55))
        draw_rect(rows, width * 0.75, height * 0.63, 150, 150, vermilion, 0.92)
        draw_line(rows, width * 0.75 + 35, height * 0.63 + 112, width * 0.75 + 115, height * 0.63 + 32, 9, washi50, 0.92)
        draw_line(rows, 150, 180, 150, 520, 8, vermilion, 0.55)
        add_grain(rows, sumi700, seed=11)
        return encode_png(width, height, rows, 2)

    if name == "kage-bamboo":
        rows = gradient_rows(width, height, sumi900, sumi700)
        stalks = ((2350, 70), (2580, 42), (2760, 96), (3040, 54), (3260, 34))
        for x, stalk_width in stalks:
            draw_rect(rows, x, 0, stalk_width, height, jade, 0.14)
            draw_line(rows, x + 3, 0, x + 3, height, 3, ash300, 0.13)
            for y in range(160, height, 320):
                draw_rect(rows, x - 8, y, stalk_width + 16, 9, ash300, 0.18)
                draw_line(rows, x - 8, y + 4, x + stalk_width + 8, y + 4, 2, washi100, 0.10)
        draw_ring(rows, 780, height * 0.42, 330, 12, washi100, 0.30, gap=(-120, -54))
        draw_rect(rows, 520, 1520, 120, 120, vermilion, 0.88)
        draw_line(rows, 550, 1608, 610, 1548, 7, washi50, 0.9)
        draw_line(rows, 170, 1900, 700, 1900, 3, ash400, 0.26)
        add_grain(rows, washi100, seed=17)
        return encode_png(width, height, rows, 2)

    if name == "kage-storm":
        rows = gradient_rows(width, height, sumi900, sumi800)
        for radius in (280, 420, 560, 700, 840, 980, 1120):
            draw_ring(rows, width * 0.68, height * 0.5, radius, 3, ash300, 0.18, gap=(-40, 20))
        draw_ring(rows, width * 0.68, height * 0.5, 280, 6, ember400, 0.72, gap=(-32, 12))
        draw_line(rows, 2760, 300, 2620, 760, 7, washi100, 0.58)
        draw_line(rows, 2620, 760, 2790, 760, 7, washi100, 0.58)
        draw_line(rows, 2790, 760, 2570, 1320, 7, washi100, 0.58)
        draw_line(rows, 2570, 1320, 2730, 1320, 7, ember400, 0.74)
        draw_line(rows, 2730, 1320, 2520, 1880, 7, washi100, 0.58)
        draw_line(rows, 220, 260, 620, 260, 4, vermilion, 0.72)
        draw_line(rows, 220, 260, 220, 920, 4, vermilion, 0.38)
        add_grain(rows, washi100, seed=23)
        return encode_png(width, height, rows, 2)

    if name == "kage-shuriken":
        rows = gradient_rows(width, height, sumi900, sumi800)
        cx, cy = width * 0.67, height * 0.50
        outer = 860
        inner = 250
        points = [
            (cx, cy - outer),
            (cx + inner, cy - inner),
            (cx + outer, cy),
            (cx + inner, cy + inner),
            (cx, cy + outer),
            (cx - inner, cy + inner),
            (cx - outer, cy),
            (cx - inner, cy - inner),
        ]
        draw_polygon(rows, points, ash300, 0.045)
        for index in range(0, len(points), 2):
            draw_line(rows, cx, cy, points[index][0], points[index][1], 4, ash300, 0.22)
        for index in range(1, len(points), 2):
            draw_line(rows, points[index][0], points[index][1], points[(index + 1) % 8][0], points[(index + 1) % 8][1], 3, washi100, 0.15)
        draw_ring(rows, cx, cy, 160, 8, vermilion, 0.86, gap=(-100, -40))
        draw_disc(rows, cx, cy, 34, vermilion, 0.9)
        draw_ring(rows, cx, cy, 1180, 2, ash400, 0.14)
        draw_line(rows, 260, 330, 900, 330, 4, vermilion, 0.60)
        draw_line(rows, 260, 330, 260, 1560, 3, ember400, 0.28)
        add_grain(rows, washi100, seed=29)
        return encode_png(width, height, rows, 2)

    # kage-sumi, the default.
    rows = gradient_rows(width, height, sumi900, sumi700)
    draw_grid(rows, 160, ash400, 0.030)
    draw_ring(rows, width * 0.70, height * 0.50, 830, 30, washi100, 0.55, gap=(-128, -47))
    draw_ring(rows, width * 0.70, height * 0.50, 845, 4, vermilion, 0.18)
    draw_line(rows, 220, 260, 220, 1560, 9, vermilion, 0.36)
    draw_line(rows, 220, 260, 360, 260, 9, vermilion, 0.62)
    draw_rect(rows, 3200, 1680, 110, 110, vermilion, 0.9)
    draw_line(rows, 3228, 1760, 3282, 1706, 6, washi50, 0.9)
    draw_line(rows, 300, 1920, 860, 1920, 3, ash400, 0.28)
    draw_disc(rows, 900, 1920, 7, vermilion400, 0.85)
    add_grain(rows, washi100, seed=31)
    return encode_png(width, height, rows, 2)


def build_splash(palette: dict[str, Color], width: int, height: int) -> bytes:
    rows = gradient_rows(width, height, palette["sumi.900"], palette["sumi.700"], horizontal=0.10)
    draw_grid(rows, max(32, width // 20), palette["ash.400"], 0.025)
    draw_ring(
        rows,
        width * 0.23,
        height * 0.50,
        min(width, height) * 0.25,
        max(5, width // 180),
        palette["washi.100"],
        0.55,
        gap=(-128, -48),
    )
    draw_ring(
        rows,
        width * 0.23,
        height * 0.50,
        min(width, height) * 0.255,
        max(2, width // 500),
        palette["vermilion.500"],
        0.35,
    )
    draw_disc(
        rows,
        width * 0.23 + min(width, height) * 0.20,
        height * 0.50 - min(width, height) * 0.20,
        max(5, width // 140),
        palette["ember.400"],
        0.9,
    )
    draw_line(rows, width * 0.48, height * 0.34, width * 0.48, height * 0.66, max(2, width // 500), palette["vermilion.500"], 0.7)
    draw_line(rows, width * 0.52, height * 0.68, width * 0.80, height * 0.68, max(2, width // 500), palette["ash.400"], 0.35)
    draw_disc(rows, width * 0.82, height * 0.68, max(4, width // 200), palette["vermilion.500"], 0.8)
    return encode_png(width, height, rows, 2)


def build_favicon_raster(size: int, palette: dict[str, Color]) -> bytes:
    rows: list[bytearray] = [bytearray(size * 4) for _ in range(size)]
    center = (size - 1) / 2
    radius = size * 0.36
    ring_width = max(1.6, size * 0.07)
    seal_size = max(3, size * 0.22)
    for y in range(size):
        row = rows[y]
        for x in range(size):
            # Opaque sumi tile with a tiny corner radius.
            edge = min(x, y, size - 1 - x, size - 1 - y)
            if edge < 1:
                alpha = 0
            elif edge < 2:
                alpha = int(255 * (edge - 0.0))
            else:
                alpha = 255
            rgba: RGBA = (*palette["sumi.900"], alpha)
            dx = x - center
            dy = y - center
            distance = math.hypot(dx, dy)
            ring_edge = abs(distance - radius)
            angle = math.degrees(math.atan2(dy, dx))
            if ring_edge <= ring_width / 2 and not (-140 < angle < -50):
                rgba = (*palette["washi.100"], 255)
            sx = x - (size - seal_size - size * 0.08)
            sy = y - (size - seal_size - size * 0.08)
            if 0 <= sx < seal_size and 0 <= sy < seal_size:
                rgba = (*palette["vermilion.500"], 255)
                if abs(sx - sy) < max(1, seal_size * 0.12) or abs(sx + sy - seal_size) < max(1, seal_size * 0.12):
                    rgba = (*palette["washi.50"], 255)
            offset = x * 4
            row[offset : offset + 4] = bytes(rgba)
    return encode_png(size, size, rows, 6)


def build_banner(palette: dict[str, Color], width: int = 1024, height: int = 128) -> bytes:
    """Installer banner: enso mark, hairline, and seal. No text, no renderer."""
    rows = [bytearray(width * 4) for _ in range(height)]
    for y in range(height):
        row = rows[y]
        for x in range(width):
            offset = x * 4
            row[offset : offset + 4] = bytes((*palette["sumi.900"], 255))
    center_x = height * 0.5
    center_y = height * 0.5
    radius = height * 0.32
    ring_width = max(1.5, height * 0.055)
    for y in range(height):
        row = rows[y]
        for x in range(int(center_x - radius - ring_width), int(center_x + radius + ring_width) + 1):
            if not 0 <= x < width:
                continue
            dx = x - center_x
            dy = y - center_y
            distance = math.hypot(dx, dy)
            angle = math.degrees(math.atan2(dy, dx))
            if abs(distance - radius) <= ring_width / 2 and not (-140 < angle < -50):
                offset = x * 4
                row[offset : offset + 4] = bytes((*palette["washi.100"], 255))
    seal = max(3, int(height * 0.16))
    seal_x = int(center_x + radius * 0.62)
    seal_y = int(center_y + radius * 0.62)
    for y in range(seal_y, min(seal_y + seal, height)):
        for x in range(seal_x, min(seal_x + seal, width)):
            offset = x * 4
            rows[y][offset : offset + 4] = bytes((*palette["vermilion.500"], 255))
    line_y = int(height * 0.72)
    line_start = int(height * 1.25)
    line_end = int(width * 0.62)
    for y in range(line_y - 1, line_y + 2):
        if not 0 <= y < height:
            continue
        row = rows[y]
        for x in range(line_start, min(line_end, width)):
            offset = x * 4
            row[offset : offset + 4] = bytes((*palette["ash.500"], 255))
    return encode_png(width, height, rows, 6)


def build_welcome(palette: dict[str, Color], width: int = 480, height: int = 240) -> bytes:
    """Installer welcome image: centered enso mark on a sumi field."""
    rows = [bytearray(width * 4) for _ in range(height)]
    for y in range(height):
        row = rows[y]
        for x in range(width):
            offset = x * 4
            row[offset : offset + 4] = bytes((*palette["sumi.800"], 255))
    center_x = width / 2
    center_y = height / 2
    radius = min(width, height) * 0.3
    ring_width = max(1.5, min(width, height) * 0.03)
    for y in range(height):
        row = rows[y]
        for x in range(width):
            dx = x - center_x
            dy = y - center_y
            distance = math.hypot(dx, dy)
            angle = math.degrees(math.atan2(dy, dx))
            if abs(distance - radius) <= ring_width / 2 and not (-140 < angle < -50):
                offset = x * 4
                row[offset : offset + 4] = bytes((*palette["washi.100"], 255))
    seal = max(4, int(min(width, height) * 0.07))
    seal_x = int(center_x + radius * 0.6)
    seal_y = int(center_y + radius * 0.6)
    for y in range(seal_y, min(seal_y + seal, height)):
        for x in range(seal_x, min(seal_x + seal, width)):
            offset = x * 4
            rows[y][offset : offset + 4] = bytes((*palette["vermilion.500"], 255))
    return encode_png(width, height, rows, 6)


def build_boot_assets(palette: dict[str, Color]) -> dict[Path, bytes]:
    return {
        BOOT_DIR / "splash.png": build_splash(palette, 640, 480),
        BOOT_DIR / "splash800x600.png": build_splash(palette, 800, 600),
        BOOT_DIR / "grub-splash.png": build_splash(palette, 1024, 768),
    }


def generate() -> dict[Path, bytes]:
    palette = load_palette()
    files: dict[Path, bytes] = {
        GRUB_DIR / "background.png": build_background(palette),
        PLYMOUTH_DIR / "logo.png": build_plymouth_logo(palette),
        PLYMOUTH_DIR / "progress_box.png": build_plymouth_progress_bar(palette, "sumi.500"),
        PLYMOUTH_DIR / "progress_bar.png": build_plymouth_progress_bar(palette, "vermilion.500"),
    }
    select = build_select_pixmap(palette)
    for name in SELECT_NAMES:
        files[GRUB_DIR / f"select_{name}.png"] = select
    for name in WALLPAPERS:
        files[WALLPAPER_DIR / f"{name}.png"] = build_wallpaper(name, palette)
    for size in FAVICON_SIZES:
        files[LOGO_DIR / "hicolor" / f"{size}x{size}" / "apps" / "arashios.png"] = build_favicon_raster(size, palette)
    ico_images = [
        (size, build_favicon_raster(size, palette))
        for size in (16, 32, 48, 64, 128, 256)
    ]
    files[LOGO_DIR / "arashios-favicon.ico"] = encode_ico(ico_images)
    files[LOGO_DIR / "arashios-banner.png"] = build_banner(palette)
    files[LOGO_DIR / "arashios-welcome.png"] = build_welcome(palette)
    files.update(build_boot_assets(palette))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ArashiOS raster brand assets.")
    parser.add_argument("--check", action="store_true", help="Fail if assets are stale")
    args = parser.parse_args()

    files = generate()
    if args.check:
        problems: list[str] = []
        for path, data in files.items():
            if not path.exists():
                problems.append(f"hilang: {path.relative_to(ROOT)}")
            elif path.read_bytes() != data:
                problems.append(f"kedaluwarsa: {path.relative_to(ROOT)}")
        if problems:
            print("ERROR: aset raster tidak sinkron:", file=sys.stderr)
            for problem in problems:
                print(f"  {problem}", file=sys.stderr)
            print("Jalankan: ./scripts/generate-brand-assets.py", file=sys.stderr)
            return 1
        print(f"OK: {len(files)} aset raster sinkron")
        return 0

    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print(f"  {path.relative_to(ROOT)}  {len(data)} bytes")
    print(f"ArashiOS: {len(files)} aset raster ditulis")
    return 0


if __name__ == "__main__":
    sys.exit(main())
