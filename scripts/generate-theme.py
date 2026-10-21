#!/usr/bin/env python3
"""Generate the Kage desktop theme from branding/tokens.json.

Outputs:
  build/theme/themes/ArashiKage
  build/theme/themes/ArashiKage-HC
  build/theme/Kvantum/ArashiKage
  build/theme/Kvantum/ArashiKage-HC
  build/theme/manifest.json

The generator uses templates under branding/theme/templates and only the
Python standard library. It is deterministic, so `--check` can reject stale
theme output before a build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "branding" / "tokens.json"
RESOLVED = ROOT / "build" / "tokens" / "tokens.resolved.json"
TEMPLATES = ROOT / "branding" / "theme" / "templates"
OUT = ROOT / "build" / "theme"

Color = tuple[int, int, int]
RGBA = tuple[int, int, int, int]


class ThemeError(Exception):
    """Raised when theme generation cannot continue."""


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


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


def rgba_rows(width: int, height: int, background: RGBA) -> list[bytearray]:
    return [bytearray(bytes(background) * width) for _ in range(height)]


def set_rgba(rows: list[bytearray], x: int, y: int, color: RGBA) -> None:
    if y < 0 or y >= len(rows):
        return
    width = len(rows[0]) // 4
    if x < 0 or x >= width:
        return
    offset = x * 4
    rows[y][offset : offset + 4] = bytes(color)


def fill_rect(
    rows: list[bytearray],
    x: int,
    y: int,
    width: int,
    height: int,
    color: RGBA,
) -> None:
    height = min(height, len(rows))
    width_px = len(rows[0]) // 4
    for py in range(max(0, y), min(len(rows), y + height)):
        row = rows[py]
        left = max(0, x)
        right = min(width_px, x + width)
        if left >= right:
            continue
        row[left * 4 : right * 4] = bytes(color) * (right - left)


def line(
    rows: list[bytearray],
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: RGBA,
) -> None:
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    while True:
        set_rgba(rows, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        twice = 2 * error
        if twice >= dy:
            error += dy
            x0 += sx
        if twice <= dx:
            error += dx
            y0 += sy


def circle(rows: list[bytearray], cx: float, cy: float, radius: float, color: RGBA) -> None:
    left = int(math.floor(cx - radius)) - 1
    right = int(math.ceil(cx + radius)) + 1
    top = int(math.floor(cy - radius)) - 1
    bottom = int(math.ceil(cy + radius)) + 1
    width_px = len(rows[0]) // 4
    for y in range(max(0, top), min(len(rows), bottom)):
        for x in range(max(0, left), min(width_px, right)):
            if math.hypot(x - cx, y - cy) <= radius:
                set_rgba(rows, x, y, color)


def build_xfwm_assets(colors: dict[str, Color]) -> dict[str, bytes]:
    surface = colors["surface"]
    bg = colors["bg"]
    bg_alt = colors["bg_alt"]
    border = colors["border"]
    border_strong = colors["border_strong"]
    text = colors["text"]
    text_muted = colors["text_muted"]
    accent = colors["accent"]
    accent_strong = colors["accent_strong"]
    danger = colors["danger_strong"]
    washi = colors["washi_50"]

    def rgba(color: Color, alpha: int = 255) -> RGBA:
        return (color[0], color[1], color[2], alpha)

    def title_piece(active: bool) -> bytes:
        width, height = 2, 30
        rows = rgba_rows(width, height, rgba(surface if active else bg))
        edge = accent_strong if active else border
        fill_rect(rows, 0, 0, width, 1, rgba(edge))
        return encode_png(width, height, rows, 6)

    def side_piece(active: bool) -> bytes:
        width, height = 2, 30
        rows = rgba_rows(width, height, rgba(accent_strong if active else border))
        return encode_png(width, height, rows, 6)

    def corner_piece(active: bool, right: bool, bottom: bool = False) -> bytes:
        width = 8 if not bottom else 8
        height = 30 if not bottom else 2
        rows = rgba_rows(width, height, (0, 0, 0, 0))
        fill = surface if active else bg
        edge = accent_strong if active else border
        fill_rect(rows, 0, 0, width, height, rgba(fill))
        if bottom:
            fill_rect(rows, 0, 0, width, height, rgba(edge))
            return encode_png(width, height, rows, 6)
        fill_rect(rows, 0, 0, width, 1, rgba(edge))
        if right:
            fill_rect(rows, width - 1, 0, 1, height, rgba(edge))
        else:
            fill_rect(rows, 0, 0, 1, height, rgba(edge))
        # Cut a small transparent notch so the outer corner reads as a radius.
        for y in range(2):
            for x in range(2 - y):
                set_rgba(rows, (width - 1 - x) if right else x, y, (0, 0, 0, 0))
        return encode_png(width, height, rows, 6)

    def bottom_piece(active: bool) -> bytes:
        width, height = 16, 2
        rows = rgba_rows(width, height, rgba(accent_strong if active else border))
        return encode_png(width, height, rows, 6)

    def button_piece(
        kind: str,
        active: bool,
        state: str,
        toggled: bool = False,
    ) -> bytes:
        width, height = 28, 30
        base = surface if active else bg
        icon = text if active else text_muted
        if state == "prelight":
            base = colors["surface_raised"]
            icon = text
        if state == "pressed":
            base = accent_strong
            icon = washi
        if toggled and state == "normal":
            base = colors["surface_raised"]
            icon = accent
        rows = rgba_rows(width, height, rgba(base))
        stroke = rgba(border_strong if active else border)
        fill_rect(rows, 0, 0, width, 1, stroke)
        # Button separators make the three controls scan as distinct targets.
        fill_rect(rows, 0, 0, 1, height, stroke)
        icon_color = rgba(icon)
        if kind == "close":
            if state == "prelight":
                rows = rgba_rows(width, height, rgba(danger))
                icon_color = rgba(washi)
            line(rows, 9, 8, width - 10, height - 9, icon_color)
            line(rows, width - 10, 8, 9, height - 9, icon_color)
        elif kind == "hide":
            line(rows, 9, height // 2, width - 10, height // 2, icon_color)
        elif kind == "maximize":
            fill_rect(rows, 9, 8, width - 19, 1, icon_color)
            fill_rect(rows, 9, height - 9, width - 19, 1, icon_color)
            fill_rect(rows, 9, 8, 1, height - 17, icon_color)
            fill_rect(rows, width - 10, 8, 1, height - 17, icon_color)
            if toggled:
                fill_rect(rows, 12, 5, width - 22, 1, icon_color)
                fill_rect(rows, width - 10, 5, 1, height - 17, icon_color)
        elif kind == "menu":
            for y in (9, 14, 19):
                fill_rect(rows, 9, y, width - 19, 1, icon_color)
        elif kind == "shade":
            line(rows, 9, 16, width // 2, 10, icon_color)
            line(rows, width // 2, 10, width - 10, 16, icon_color)
            if toggled:
                line(rows, 9, 13, width // 2, 19, icon_color)
                line(rows, width // 2, 19, width - 10, 13, icon_color)
        elif kind == "stick":
            circle(rows, width / 2, height / 2, 4, icon_color)
            fill_rect(rows, width // 2, 7, 1, 16, icon_color)
        return encode_png(width, height, rows, 6)

    files: dict[str, bytes] = {}
    for active, suffix in ((True, "active"), (False, "inactive")):
        files[f"title-1-{suffix}.png"] = title_piece(active)
        files[f"left-{suffix}.png"] = side_piece(active)
        files[f"right-{suffix}.png"] = side_piece(active)
        files[f"top-left-{suffix}.png"] = corner_piece(active, right=False)
        files[f"top-right-{suffix}.png"] = corner_piece(active, right=True)
        files[f"bottom-{suffix}.png"] = bottom_piece(active)
        files[f"bottom-left-{suffix}.png"] = corner_piece(active, right=False, bottom=True)
        files[f"bottom-right-{suffix}.png"] = corner_piece(active, right=True, bottom=True)
        for kind in ("close", "hide", "maximize", "menu", "shade", "stick"):
            for state in ("normal", "prelight", "pressed"):
                files[f"{kind}-{state}-{suffix}.png"] = button_piece(kind, active, state)
            if kind in ("maximize", "shade", "stick"):
                files[f"{kind}-toggled-{suffix}.png"] = button_piece(kind, active, "normal", toggled=True)
                files[f"{kind}-toggled-prelight-{suffix}.png"] = button_piece(kind, active, "prelight", toggled=True)
                files[f"{kind}-toggled-pressed-{suffix}.png"] = button_piece(kind, active, "pressed", toggled=True)
    return files


def build_thumbnail(colors: dict[str, Color]) -> bytes:
    width, height = 256, 256
    bg = colors["bg"]
    surface = colors["surface"]
    washi = colors["washi_100"]
    accent = colors["accent_strong"]
    rows = rgba_rows(width, height, (bg[0], bg[1], bg[2], 255))
    for y in range(height):
        t = y / (height - 1)
        color = blend(bg, surface, t)
        fill_rect(rows, 0, y, width, 1, (color[0], color[1], color[2], 255))
    fill_rect(rows, 0, 0, width, 30, (surface[0], surface[1], surface[2], 255))
    fill_rect(rows, 0, 30, width, 1, (accent[0], accent[1], accent[2], 255))
    # Three abstract window cards and a mark.
    for index, (x, y, w, h) in enumerate(((18, 52, 106, 70), (138, 52, 100, 70), (18, 136, 220, 96))):
        fill_rect(rows, x, y, w, h, (surface[0], surface[1], surface[2], 255))
        fill_rect(rows, x, y, w, 1, (accent[0], accent[1], accent[2], 255) if index == 0 else (washi[0], washi[1], washi[2], 80))
        fill_rect(rows, x + 8, y + 10, max(18, w // 3), 2, (washi[0], washi[1], washi[2], 110))
        fill_rect(rows, x + 8, y + 18, max(28, w // 2), 2, (washi[0], washi[1], washi[2], 55))
    for radius in range(44, 48):
        circle(rows, 198, 188, radius, (washi[0], washi[1], washi[2], 150))
    circle(rows, 198, 188, 34, (bg[0], bg[1], bg[2], 255))
    fill_rect(rows, 202, 194, 18, 18, (accent[0], accent[1], accent[2], 255))
    line(rows, 206, 207, 216, 197, (washi[0], washi[1], washi[2], 255))
    return encode_png(width, height, rows, 6)


def kvantum_svg(colors: dict[str, Color]) -> bytes:
    surface = colors["surface"]
    surface_raised = colors["surface_raised"]
    bg_alt = colors["bg_alt"]
    border = colors["border"]
    border_strong = colors["border_strong"]
    accent = colors["accent"]
    accent_strong = colors["accent_strong"]
    washi = colors["washi_50"]
    text = colors["text"]
    text_muted = colors["text_muted"]
    success = colors["success"]

    def hx(color: Color, alpha: str = "") -> str:
        return "#%02X%02X%02X%s" % (color[0], color[1], color[2], alpha)

    parts: list[str] = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" '
        'viewBox="0 0 512 512">'
    )
    parts.append('<g id="kage-kvantum">')

    def frame(element: str, state: str, fill: Color, stroke: Color, border_width: int = 1) -> None:
        uid = f"{element}-{state}"
        x = y = 8
        size = 32
        radius = 2
        parts.append(f'<g id="{uid}">')
        parts.append(
            f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{radius}" '
            f'fill="{hx(fill)}" stroke="{hx(stroke)}" stroke-width="{border_width}"/>'
        )
        parts.append("</g>")
        # Nine-slice edges and corners. Kvantum uses these when frame.top/left
        # are greater than zero; the colors stay flat and token-derived.
        edge = max(1, border_width)
        parts.append(f'<g id="{uid}-top"><rect x="{x}" y="{y}" width="{size}" height="{edge}" fill="{hx(stroke)}"/></g>')
        parts.append(f'<g id="{uid}-bottom"><rect x="{x}" y="{y + size - edge}" width="{size}" height="{edge}" fill="{hx(stroke)}"/></g>')
        parts.append(f'<g id="{uid}-left"><rect x="{x}" y="{y}" width="{edge}" height="{size}" fill="{hx(stroke)}"/></g>')
        parts.append(f'<g id="{uid}-right"><rect x="{x + size - edge}" y="{y}" width="{edge}" height="{size}" fill="{hx(stroke)}"/></g>')
        parts.append(f'<g id="{uid}-topleft"><rect x="{x}" y="{y}" width="{edge}" height="{edge}" fill="{hx(stroke)}"/></g>')
        parts.append(f'<g id="{uid}-topright"><rect x="{x + size - edge}" y="{y}" width="{edge}" height="{edge}" fill="{hx(stroke)}"/></g>')
        parts.append(f'<g id="{uid}-bottomleft"><rect x="{x}" y="{y + size - edge}" width="{edge}" height="{edge}" fill="{hx(stroke)}"/></g>')
        parts.append(f'<g id="{uid}-bottomright"><rect x="{x + size - edge}" y="{y + size - edge}" width="{edge}" height="{edge}" fill="{hx(stroke)}"/></g>')

    frame_map = {
        "button": (surface_raised, border),
        "tbutton": (surface_raised, border),
        "lineedit": (bg_alt, border),
        "spinbox": (bg_alt, border),
        "spin": (surface_raised, border),
        "tab": (surface_raised, border),
        "tabframe": (surface, border),
        "menuitem": (surface_raised, surface_raised),
        "menubaritem": (surface_raised, border),
        "menu": (surface_raised, border_strong),
        "common": (surface, border),
        "group": (surface, border),
        "header": (surface_raised, border),
        "progress": (surface, border),
        "progress-pattern": (accent_strong, accent_strong),
        "itemview": (surface, border),
        "slider": (border_strong, border_strong),
        "slidercursor": (accent, accent_strong),
        "scrollbarslider": (border_strong, border_strong),
        "scrollbargroove": (surface, surface),
        "ss": (surface_raised, surface_raised),
        "tooltip": (surface_raised, border_strong),
        "toolbar": (surface, surface),
        "splitter": (border, border),
        "titlebar": (surface, surface),
        "focus": (surface_raised, accent),
    }
    for element, (fill, stroke) in frame_map.items():
        for state, (state_fill, state_stroke) in (
            ("normal", (fill, stroke)),
            ("focused", (fill, accent)),
            ("pressed", (bg_alt, accent_strong)),
            ("toggled", (accent_strong, accent_strong)),
            ("disabled", (bg_alt, border)),
        ):
            frame(element, state, state_fill, state_stroke, 2 if state == "focused" else 1)

    # Indicator elements.
    def triangle(uid: str, points: str, color: Color) -> None:
        parts.append(f'<g id="{uid}"><polygon points="{points}" fill="{hx(color)}"/></g>')

    for direction, points in {
        "down": "8,12 24,12 16,22",
        "up": "8,20 24,20 16,10",
        "left": "12,8 12,24 2,16",
        "right": "20,8 20,24 30,16",
    }.items():
        for state, color in (("normal", text), ("focused", accent), ("pressed", washi), ("disabled", text_muted)):
            triangle(f"arrow-{direction}-{state}", points, color)
            if direction == "down":
                triangle(f"arrow-{state}", points, color)

    for state, stroke in (("normal", border_strong), ("focused", accent), ("disabled", border)):
        parts.append(
            f'<g id="checkbox-{state}"><rect x="8" y="8" width="20" height="20" rx="2" '
            f'fill="{hx(bg_alt)}" stroke="{hx(stroke)}" stroke-width="2"/></g>'
        )
        parts.append(
            f'<g id="checkbox-checked-{state}"><rect x="8" y="8" width="20" height="20" rx="2" '
            f'fill="{hx(accent_strong)}" stroke="{hx(accent_strong)}" stroke-width="2"/>'
            f'<polyline points="12,18 16,22 24,12" fill="none" stroke="{hx(washi)}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>'
        )
        parts.append(
            f'<g id="checkbox-tristate-{state}"><rect x="8" y="8" width="20" height="20" rx="2" '
            f'fill="{hx(accent_strong)}" stroke="{hx(accent_strong)}" stroke-width="2"/>'
            f'<rect x="12" y="17" width="12" height="3" fill="{hx(washi)}"/></g>'
        )
        parts.append(
            f'<g id="radio-{state}"><circle cx="18" cy="18" r="10" fill="{hx(bg_alt)}" '
            f'stroke="{hx(stroke)}" stroke-width="2"/></g>'
        )
        parts.append(
            f'<g id="radio-checked-{state}"><circle cx="18" cy="18" r="10" fill="{hx(accent_strong)}" '
            f'stroke="{hx(accent_strong)}" stroke-width="2"/><circle cx="18" cy="18" r="4" fill="{hx(washi)}"/></g>'
        )

    # Grip and window control indicators.
    for state, color in (("normal", text_muted), ("focused", text), ("pressed", accent)):
        grip_parts: list[str] = []
        splitter_parts: list[str] = []
        for index in range(3):
            offset = index * 5
            grip_parts.append(
                f'<circle cx="{10 + offset}" cy="20" r="1.5" fill="{hx(color)}"/>'
                f'<circle cx="{10 + offset}" cy="14" r="1.5" fill="{hx(color)}"/>'
                f'<circle cx="{10 + offset}" cy="8" r="1.5" fill="{hx(color)}"/>'
            )
            splitter_parts.append(
                f'<circle cx="{10 + offset}" cy="18" r="1.5" fill="{hx(color)}"/>'
            )
        parts.append(f'<g id="grip-{state}">{"".join(grip_parts)}</g>')
        parts.append(f'<g id="splitter-grip-{state}">{"".join(splitter_parts)}</g>')
        parts.append(
            f'<g id="resize-grip-{state}"><path d="M 8 28 L 28 8 M 14 28 L 28 14 M 20 28 L 28 20" '
            f'stroke="{hx(color)}" stroke-width="2" fill="none"/></g>'
        )
        parts.append(
            f'<g id="mdi-{state}"><rect x="7" y="8" width="22" height="2" fill="{hx(color)}"/>'
            f'<rect x="7" y="14" width="22" height="2" fill="{hx(color)}"/>'
            f'<rect x="7" y="20" width="22" height="2" fill="{hx(color)}"/></g>'
        )

    parts.append("</g></svg>")
    return ("\n".join(parts) + "\n").encode("utf-8")


def xfwm_assets(colors: dict[str, Color]) -> dict[str, bytes]:
    return build_xfwm_assets(colors)


@dataclass(frozen=True)
class Variant:
    name: str
    comment: str
    colors: dict[str, Color]
    variables: dict[str, str]


def load_resolved() -> dict[str, Any]:
    if not RESOLVED.exists():
        fail(
            "build/tokens/tokens.resolved.json belum ada. "
            "Jalankan ./scripts/generate-tokens.py terlebih dahulu."
        )
    try:
        return json.loads(RESOLVED.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"token hasil resolusi tidak valid: {exc}")


def base_colors(resolved: dict[str, Any]) -> dict[str, Color]:
    colors = {snake(key): hex_color(value) for key, value in resolved["resolvedSemantic"].items()}
    for group, shades in resolved["color"].items():
        for shade, value in shades.items():
            colors[f"{snake(group)}_{shade}"] = hex_color(value)
    return colors


def base_variables(resolved: dict[str, Any], colors: dict[str, Color]) -> dict[str, str]:
    values: dict[str, str] = {}
    for key, value in resolved["resolvedSemantic"].items():
        values[snake(key)] = value
    values["gtk_font_family"] = resolved["typography"]["fontFamily"]["sans"]
    values["cinnamon_font_family"] = resolved["typography"]["fontFamily"]["sans"]
    values["mono_font_family"] = resolved["typography"]["fontFamily"]["mono"]
    for key, value in resolved["radius"].items():
        values[f"radius_{snake(key)}"] = value
    for group, shades in resolved["color"].items():
        for shade, value in shades.items():
            values[f"{snake(group)}_{shade}"] = value
    values["accent_alpha"] = resolved["resolvedSemantic"]["accentStrong"] + "80"
    values["theme_comment"] = "Japanese minimal theme with restrained vermilion accents."
    values["theme_name"] = "ArashiKage"
    return values


def contrast_palette(resolved: dict[str, Any]) -> dict[str, Color]:
    colors = {snake(key): hex_color(value) for key, value in resolved["resolvedSemantic"].items()}
    for group, shades in resolved["color"].items():
        for shade, value in shades.items():
            colors[f"{snake(group)}_{shade}"] = hex_color(value)
    return colors


def high_contrast_colors(base: dict[str, Color]) -> dict[str, Color]:
    colors = dict(base)
    colors.update(
        {
            "bg": base["sumi_900"],
            "bg_alt": base["sumi_900"],
            "surface": base["sumi_800"],
            "surface_raised": base["sumi_700"],
            "surface_sunken": base["sumi_900"],
            "text": base["washi_50"],
            "text_muted": base["washi_200"],
            "text_subtle": base["ash_300"],
            "text_inverse": base["sumi_900"],
            "accent": base["washi_50"],
            "accent_hover": base["washi_100"],
            "accent_pressed": base["washi_200"],
            "accent_strong": base["washi_50"],
            "accent_strong_hover": base["washi_100"],
            "on_accent": base["sumi_900"],
            "danger": base["ember_400"],
            "danger_strong": base["vermilion_500"],
            "border": base["ash_400"],
            "border_strong": base["washi_100"],
            "focus": base["washi_50"],
        }
    )
    return colors


def make_variant(
    resolved: dict[str, Any],
    name: str,
    comment: str,
    colors: dict[str, Color],
) -> Variant:
    variables = base_variables(resolved, colors)
    for key, color in colors.items():
        variables[key] = "#%02X%02X%02X" % color
    variables["theme_name"] = name
    variables["theme_comment"] = comment
    variables["accent_alpha"] = "#%02X%02X%02X80" % colors["accent_strong"]
    return Variant(name=name, comment=comment, colors=colors, variables=variables)


def render_template(relative: str, variables: dict[str, str]) -> str:
    path = TEMPLATES / relative
    if not path.exists():
        fail(f"template hilang: {path.relative_to(ROOT)}")
    try:
        return Template(path.read_text(encoding="utf-8")).substitute(variables)
    except KeyError as exc:
        fail(f"variabel template tidak dikenal di {path.name}: {exc}")


def theme_files(variant: Variant, resolved: dict[str, Any]) -> dict[str, bytes]:
    files: dict[str, bytes] = {
        "index.theme": render_template("index.theme.in", variant.variables).encode(),
        "gtk-2.0/gtkrc": render_template("gtk-2.0/gtkrc.in", variant.variables).encode(),
        "gtk-3.0/gtk.css": render_template("gtk-3.0/gtk.css.in", variant.variables).encode(),
        "gtk-4.0/gtk.css": render_template("gtk-4.0/gtk.css.in", variant.variables).encode(),
        "cinnamon/cinnamon.css": render_template("cinnamon/cinnamon.css.in", variant.variables).encode(),
        "cinnamon/metacity-theme-3.xml": render_template(
            "cinnamon/metacity-theme-3.xml.in", variant.variables
        ).encode(),
        "metacity-1/metacity-theme-3.xml": render_template(
            "cinnamon/metacity-theme-3.xml.in", variant.variables
        ).encode(),
        "cinnamon/thumbnail.png": build_thumbnail(variant.colors),
        "xfwm4/themerc": render_template("xfwm4/themerc.in", variant.variables).encode(),
        "openbox-3/themerc": render_template("openbox-3/themerc.in", variant.variables).encode(),
    }
    for filename, data in xfwm_assets(variant.colors).items():
        files[f"xfwm4/{filename}"] = data
    return files


def kvantum_files(variant: Variant) -> dict[str, bytes]:
    config = render_template("kvantum/ArashiKage.kvconfig.in", variant.variables)
    return {
        f"{variant.name}.kvconfig": config.encode(),
        f"{variant.name}.svg": kvantum_svg(variant.colors),
    }


def generate() -> dict[Path, bytes]:
    resolved = load_resolved()
    colors = base_colors(resolved)
    variants = [
        make_variant(
            resolved,
            "ArashiKage",
            "Japanese minimal theme with restrained vermilion accents.",
            colors,
        ),
        make_variant(
            resolved,
            "ArashiKage-HC",
            "High contrast variant of the Kage theme.",
            high_contrast_colors(colors),
        ),
    ]
    files: dict[Path, bytes] = {}
    for variant in variants:
        for relative, data in theme_files(variant, resolved).items():
            files[OUT / "themes" / variant.name / relative] = data
        for relative, data in kvantum_files(variant).items():
            files[OUT / "Kvantum" / variant.name / relative] = data

    manifest: dict[str, Any] = {
        "name": "ArashiOS Kage theme",
        "tokensVersion": resolved["meta"]["version"],
        "themes": [variant.name for variant in variants],
        "files": {},
    }
    for path, data in sorted(files.items()):
        manifest["files"][str(path.relative_to(OUT))] = hashlib.sha256(data).hexdigest()
    files[OUT / "manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the ArashiOS Kage desktop theme.")
    parser.add_argument("--check", action="store_true", help="Fail if generated theme files are stale")
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
            print("ERROR: tema tidak sinkron:", file=sys.stderr)
            for problem in problems:
                print(f"  {problem}", file=sys.stderr)
            print("Jalankan: ./scripts/generate-theme.py", file=sys.stderr)
            return 1
        print(f"OK: {len(files)} berkas tema sinkron")
        return 0

    if OUT.exists():
        shutil.rmtree(OUT)
    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"ArashiOS: {len(files)} berkas tema ditulis ke {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
