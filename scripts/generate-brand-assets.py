#!/usr/bin/env python3
"""Generate raster brand assets that cannot rely on an SVG renderer.

Outputs:
  branding/grub/background.png
  branding/grub/select_*.png
  branding/plymouth/logo.png

Only the Python standard library is used. The output is deterministic so
`--check` can verify that committed assets match the generator.
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRUB_DIR = ROOT / "branding" / "grub"
PLYMOUTH_DIR = ROOT / "branding" / "plymouth"

SUMI = (7, 7, 9)
SUMI_END = (18, 18, 22)
WASHI = (237, 232, 222)
ASH = (139, 134, 125)
VERMILION = (191, 68, 50)
EMBER = (232, 145, 122)

SELECT_NAMES = ("nw", "n", "ne", "w", "c", "e", "sw", "s", "se")


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def encode_png(width: int, height: int, rows: list[bytes], color_type: int) -> bytes:
    raw = b"".join(b"\x00" + row for row in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )


def clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))


def blend(base: tuple[int, int, int], overlay: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    return (
        clamp(base[0] * (1.0 - alpha) + overlay[0] * alpha),
        clamp(base[1] * (1.0 - alpha) + overlay[1] * alpha),
        clamp(base[2] * (1.0 - alpha) + overlay[2] * alpha),
    )


def build_background() -> bytes:
    width, height = 1920, 1080
    cx, cy = width * 0.30, height * 0.50
    radius = 300.0
    thickness = 9.0
    rows: list[bytes] = []

    for y in range(height):
        row = bytearray(width * 3)
        for x in range(width):
            t = (x / width) * 0.35 + (y / height) * 0.65
            color = (
                clamp(SUMI[0] + (SUMI_END[0] - SUMI[0]) * t),
                clamp(SUMI[1] + (SUMI_END[1] - SUMI[1]) * t),
                clamp(SUMI[2] + (SUMI_END[2] - SUMI[2]) * t),
            )

            if x % 80 == 0 or y % 80 == 0:
                color = blend(color, ASH, 0.035)

            distance = math.hypot(x - cx, y - cy)
            glow = max(0.0, 1.0 - distance / (width * 0.52))
            if glow > 0:
                color = blend(color, VERMILION, glow * glow * 0.18)

            offset = x * 3
            row[offset : offset + 3] = bytes(color)
        rows.append(bytes(row))

    # Draw the ensō ring in a second pass over its bounding box.
    left = max(0, int(cx - radius - thickness - 2))
    right = min(width, int(cx + radius + thickness + 3))
    top = max(0, int(cy - radius - thickness - 2))
    bottom = min(height, int(cy + radius + thickness + 3))
    for y in range(top, bottom):
        row = bytearray(rows[y])
        for x in range(left, right):
            dx = x - cx
            dy = y - cy
            distance = math.hypot(dx, dy)
            edge = abs(distance - radius)
            if edge > thickness / 2 + 1.5:
                continue
            angle = math.degrees(math.atan2(dy, dx))
            if -96.0 < angle < -54.0:
                continue
            if edge <= thickness / 2:
                alpha = 0.88
            else:
                alpha = 0.88 * max(0.0, 1.0 - (edge - thickness / 2) / 1.5)
            offset = x * 3
            base = (row[offset], row[offset + 1], row[offset + 2])
            row[offset : offset + 3] = bytes(blend(base, WASHI, alpha))
        rows[y] = bytes(row)

    return encode_png(width, height, rows, 2)


def build_select_pixmap() -> bytes:
    width, height = 10, 10
    row = bytes(EMBER) * width
    return encode_png(width, height, [row] * height, 2)


def build_plymouth_logo() -> bytes:
    width, height = 256, 256
    cx, cy = 128.0, 128.0
    radius = 96.0
    thickness = 9.0
    rows: list[bytes] = []

    for y in range(height):
        row = bytearray(width * 4)
        for x in range(width):
            rgba = (0, 0, 0, 0)
            distance = math.hypot(x - cx, y - cy)
            edge = abs(distance - radius)
            angle = math.degrees(math.atan2(y - cy, x - cx))
            if edge <= thickness / 2 + 1.5 and not (-100.0 < angle < -55.0):
                if edge <= thickness / 2:
                    alpha = 255
                else:
                    alpha = int(255 * max(0.0, 1.0 - (edge - thickness / 2) / 1.5))
                rgba = (*WASHI, alpha)

            dot_distance = math.hypot(x - 188, y - 68)
            if dot_distance <= 9:
                rgba = (*VERMILION, 255)
            elif dot_distance <= 10.5:
                alpha = int(255 * max(0.0, 1.0 - (dot_distance - 9) / 1.5))
                rgba = (*VERMILION, alpha)

            offset = x * 4
            row[offset : offset + 4] = bytes(rgba)
        rows.append(bytes(row))

    return encode_png(width, height, rows, 6)


def generate() -> dict[Path, bytes]:
    files: dict[Path, bytes] = {
        GRUB_DIR / "background.png": build_background(),
        PLYMOUTH_DIR / "logo.png": build_plymouth_logo(),
    }
    select = build_select_pixmap()
    for name in SELECT_NAMES:
        files[GRUB_DIR / f"select_{name}.png"] = select
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
