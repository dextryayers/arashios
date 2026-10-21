#!/usr/bin/env python3
"""Static verification for generated ArashiOS Kage theme and assets.

The checker does not need an X server. GTK CSS parsing is attempted when
PyGObject is available; otherwise the static CSS checks still run.
"""
from __future__ import annotations

import configparser
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
THEME_ROOT = ROOT / "build" / "theme"
TOKENS_JSON = ROOT / "branding" / "tokens.json"

errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def png_size(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def ico_sizes(path: Path) -> list[int]:
    data = path.read_bytes()
    if len(data) < 6:
        return []
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    if reserved != 0 or kind != 1:
        return []
    sizes = []
    for index in range(count):
        entry = data[6 + index * 16 : 6 + (index + 1) * 16]
        if len(entry) != 16:
            return []
        width = entry[0] or 256
        height = entry[1] or 256
        if width == height:
            sizes.append(width)
    return sorted(sizes)


def strip_css_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def parse_css_rules(text: str) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", text):
        selector = " ".join(match.group(1).split())
        rules.append((selector, match.group(2)))
    return rules


def check_text_policy(path: Path, text: str) -> None:
    check("\u2014" not in text, f"{path}: contains an em dash")
    check("\u2013" not in text, f"{path}: contains an en dash")
    check("$" not in text, f"{path}: contains an unresolved $ token")
    check("{{" not in text and "}}" not in text, f"{path}: contains a template marker")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def check_png_asset(path: Path, width: int, height: int, max_bytes: int | None = None) -> None:
    size = png_size(path)
    check(size == (width, height), f"{path}: expected {width}x{height}, got {size}")
    if max_bytes is not None:
        check(path.stat().st_size <= max_bytes, f"{path}: exceeds {max_bytes} bytes")


def main() -> int:
    for tool, args in (
        ("tokens", [sys.executable, str(ROOT / "scripts" / "generate-tokens.py"), "--check"]),
        ("theme", [sys.executable, str(ROOT / "scripts" / "generate-theme.py"), "--check"]),
    ):
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
        check(result.returncode == 0, f"generated {tool} output is stale\n{result.stdout}{result.stderr}")

    tokens = json.loads(TOKENS_JSON.read_text(encoding="utf-8"))
    token_colors = {
        value.upper()
        for value in re.findall(r"#[0-9A-Fa-f]{3,8}", TOKENS_JSON.read_text(encoding="utf-8"))
    }
    check(tokens.get("meta", {}).get("version") == "0.2.0", "token version is not 0.2.0")
    check(tokens.get("radius", {}).get("md") == "4px", "radius md must remain 4px")

    manifest_path = THEME_ROOT / "manifest.json"
    check(manifest_path.is_file(), "theme manifest is missing")
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = manifest.get("files", {})
        check(len(files) >= 160, f"theme manifest contains only {len(files)} files")
        for relative, digest in files.items():
            path = THEME_ROOT / relative
            check(path.is_file(), f"manifest file missing: {relative}")
            if path.is_file():
                import hashlib

                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                check(actual == digest, f"manifest hash mismatch: {relative}")

    for variant, expected_name in (("ArashiKage", "ArashiKage"), ("ArashiKage-HC", "ArashiKage-HC")):
        theme = THEME_ROOT / "themes" / variant
        check(theme.is_dir(), f"theme directory missing: {variant}")
        required = [
            "index.theme",
            "gtk-2.0/gtkrc",
            "gtk-3.0/gtk.css",
            "gtk-4.0/gtk.css",
            "cinnamon/cinnamon.css",
            "cinnamon/metacity-theme-3.xml",
            "metacity-1/metacity-theme-3.xml",
            "cinnamon/thumbnail.png",
            "openbox-3/themerc",
            "xfwm4/themerc",
        ]
        for relative in required:
            check((theme / relative).is_file(), f"{variant}: missing {relative}")

        index = (theme / "index.theme").read_text(encoding="utf-8")
        check(f"Name={expected_name}" in index, f"{variant}: index Name is wrong")
        check("GtkTheme=" + expected_name in index, f"{variant}: index GtkTheme is wrong")
        check("MetacityTheme=" + expected_name in index, f"{variant}: index MetacityTheme is wrong")
        check("IconTheme=Papirus-Dark" in index, f"{variant}: icon theme is not Papirus-Dark")
        check("CursorTheme=Bibata-Modern-Classic" in index, f"{variant}: cursor theme is wrong")

        gtk3 = strip_css_comments((theme / "gtk-3.0" / "gtk.css").read_text(encoding="utf-8"))
        gtk4 = strip_css_comments((theme / "gtk-4.0" / "gtk.css").read_text(encoding="utf-8"))
        cinnamon = strip_css_comments((theme / "cinnamon" / "cinnamon.css").read_text(encoding="utf-8"))
        for path, text in (
            (theme / "gtk-3.0" / "gtk.css", gtk3),
            (theme / "gtk-4.0" / "gtk.css", gtk4),
            (theme / "cinnamon" / "cinnamon.css", cinnamon),
        ):
            check(text.count("{") == text.count("}"), f"{path}: unbalanced braces")
            check_text_policy(path, text)

        for label, text in (("gtk3", gtk3), ("gtk4", gtk4), ("cinnamon", cinnamon)):
            check("Adwaita-dark" not in text, f"{variant}: {label} references Adwaita-dark")
            for value in re.findall(r"#[0-9A-Fa-f]{3,8}", text):
                normalized = value.upper()
                if len(normalized) == 9:
                    normalized = normalized[:7]
                elif len(normalized) == 4:
                    normalized = "#" + "".join(character * 2 for character in normalized[1:])
                check(normalized in token_colors, f"{variant}: {label} uses non-token color {value}")

        allowed_radius_selectors = (
            "circular",
            "switch",
            "scale slider",
            "radiobutton",
            "grouped-window-list-badge",
            "sound-player .slider .slider-handle",
        )
        for label, text in (("gtk3", gtk3), ("gtk4", gtk4), ("cinnamon", cinnamon)):
            for selector, body in parse_css_rules(text):
                for value in re.findall(r"border-radius:\s*([0-9]+)px", body):
                    radius = int(value)
                    if radius <= 4:
                        continue
                    check(
                        any(marker in selector for marker in allowed_radius_selectors),
                        f"{variant}: {label} radius {radius}px on non-pill selector: {selector[:100]}",
                    )
                for duration in re.findall(r"transition:[^;]*?([0-9]+)ms", body):
                    milliseconds = int(duration)
                    check(
                        80 <= milliseconds <= 200,
                        f"{variant}: {label} transition {milliseconds}ms outside 80..200ms",
                    )

        check("height: 30px" in cinnamon, f"{variant}: Cinnamon panel is not 30px")
        check("border-bottom: 1px solid" in cinnamon, f"{variant}: Cinnamon panel lacks bottom border")
        check("accent_bg_color" in gtk4, f"{variant}: GTK4 lacks libadwaita accent color")
        check("window_bg_color" in gtk4, f"{variant}: GTK4 lacks libadwaita window color")

        for metacity_relative in ("cinnamon/metacity-theme-3.xml", "metacity-1/metacity-theme-3.xml"):
            try:
                metacity = ElementTree.parse(theme / metacity_relative).getroot()
                check(metacity.tag == "metacity_theme", f"{variant}: invalid Metacity root in {metacity_relative}")
                check(
                    any(element.tag == "frame_style_set" for element in metacity.iter()),
                    f"{variant}: Metacity has no frame_style_set in {metacity_relative}",
                )
            except ElementTree.ParseError as error:
                check(False, f"{variant}: Metacity XML does not parse in {metacity_relative}: {error}")

        xfwm = theme / "xfwm4"
        check(len(list(xfwm.glob("*.png"))) == 70, f"{variant}: expected 70 XFWM PNG assets")
        for relative in ("title-1-active.png", "title-1-inactive.png", "close-normal-active.png", "bottom-active.png"):
            size = png_size(xfwm / relative)
            check(size is not None, f"{variant}: missing XFWM image {relative}")
        check(png_size(xfwm / "title-1-active.png") == (2, 30), f"{variant}: titlebar is not 30px")
        themerc = (xfwm / "themerc").read_text(encoding="utf-8")
        for key in ("active_text_color=", "inactive_text_color=", "full_width_title=true"):
            check(key in themerc, f"{variant}: XFWM themerc missing {key}")

        accent = "#BF4432" if variant == "ArashiKage" else "#F7F4EE"
        openbox = (theme / "openbox-3" / "themerc").read_text(encoding="utf-8")
        for key in (
            f"window.active.border.color: {accent}",
            "border.width: 2",
            "menu.items.active.bg.color:",
        ):
            check(key in openbox, f"{variant}: Openbox themerc missing {key}")

        kvantum = THEME_ROOT / "Kvantum" / variant / f"{variant}.kvconfig"
        check(kvantum.is_file(), f"{variant}: Kvantum config missing")
        kvtext = kvantum.read_text(encoding="utf-8")
        check("[%General]" in kvtext, f"{variant}: Kvantum config lacks [%General]")
        check("[GeneralColors]" in kvtext, f"{variant}: Kvantum config lacks [GeneralColors]")
        check(f"highlight.color={accent}" in kvtext, f"{variant}: Kvantum accent is wrong")

        svg = THEME_ROOT / "Kvantum" / variant / f"{variant}.svg"
        check(svg.is_file(), f"{variant}: Kvantum SVG missing")
        try:
            tree = ElementTree.parse(svg)
            ids = [element.get("id") for element in tree.iter() if element.get("id")]
            check(len(ids) == len(set(ids)), f"{variant}: Kvantum SVG has duplicate element IDs")
            check(len(ids) >= 150, f"{variant}: Kvantum SVG has only {len(ids)} element IDs")
            for required_id in (
                "button-normal",
                "button-focused",
                "lineedit-normal",
                "menu-normal",
                "menuitem-normal",
                "progress-pattern-normal",
                "checkbox-normal",
                "radio-normal",
                "titlebar-normal",
            ):
                check(required_id in ids, f"{variant}: Kvantum SVG missing {required_id}")
        except ElementTree.ParseError as error:
            check(False, f"{variant}: Kvantum SVG does not parse: {error}")

    # Wallpapers are PNG deliverables even though the editable sources are SVG.
    for name in ("kage-sumi", "kage-shuriken", "kage-bamboo", "kage-washi", "kage-storm"):
        check_png_asset(ROOT / "branding" / "wallpaper" / f"{name}.png", 3840, 2160, 4 * 1024 * 1024)
        check((ROOT / "branding" / "wallpaper" / f"{name}.svg").is_file(), f"wallpaper source missing: {name}.svg")

    check_png_asset(ROOT / "branding" / "plymouth" / "logo.png", 256, 256, 32 * 1024)
    check_png_asset(ROOT / "branding" / "plymouth" / "progress_box.png", 320, 2, 4096)
    check_png_asset(ROOT / "branding" / "plymouth" / "progress_bar.png", 320, 2, 4096)
    plymouth_script = read_text(ROOT / "branding" / "plymouth" / "arashios.script")
    for value in ("progress_box.png", "progress_bar.png", "SetBootProgressFunction", "Image.Text"):
        check(value in plymouth_script, f"Plymouth script lacks {value}")
    check(plymouth_script.count("{") == plymouth_script.count("}"), "Plymouth script has unbalanced braces")
    plymouth_ini = configparser.ConfigParser(interpolation=None)
    plymouth_ini.read(ROOT / "branding" / "plymouth" / "arashios.plymouth", encoding="utf-8")
    check(plymouth_ini.get("Plymouth Theme", "ModuleName", fallback="") == "script",
          "Plymouth theme does not use the script module")
    check(plymouth_ini.get("script", "ScriptFile", fallback="").endswith("arashios.script"),
          "Plymouth ScriptFile is wrong")
    check_png_asset(ROOT / "branding" / "boot" / "splash.png", 640, 480, 200 * 1024)
    check_png_asset(ROOT / "branding" / "boot" / "splash800x600.png", 800, 600, 250 * 1024)
    check_png_asset(ROOT / "branding" / "boot" / "grub-splash.png", 1024, 768, 250 * 1024)
    check_png_asset(ROOT / "branding" / "grub" / "background.png", 1920, 1080, 500 * 1024)
    grub_theme = read_text(ROOT / "branding" / "grub" / "theme.txt")
    for value in ("ARASHIOS / KAGE", "SECURITY FIRST", 'desktop-image: "background.png"',
                  'selected_item_pixmap_style = "select_*.png"'):
        check(value in grub_theme, f"GRUB theme lacks {value}")
    check("Debian" not in grub_theme, "GRUB theme still mentions Debian")
    live_grub = read_text(
        ROOT / "config" / "common" / "bootloaders" / "grub-pc" / "live-theme" / "theme.txt"
    )
    for value in ("ARASHIOS / KAGE", "LIVE SYSTEM", 'desktop-image: "../splash.png"',
                  'selected_item_pixmap_style = "select_*.png"'):
        check(value in live_grub, f"live GRUB theme lacks {value}")
    check("Debian" not in live_grub, "live GRUB theme still mentions Debian")
    for name in ("background.png", "select_c.png", "select_e.png", "select_n.png",
                 "select_ne.png", "select_nw.png", "select_s.png", "select_se.png",
                 "select_sw.png", "select_w.png"):
        check((ROOT / "branding" / "grub" / name).is_file(), f"GRUB asset missing: {name}")
    check(ico_sizes(ROOT / "branding" / "logo" / "arashios-favicon.ico") == [16, 32, 48, 64, 128, 256],
          "favicon ICO does not contain 16, 32, 48, 64, 128, and 256px frames")

    # Parse every generated XML and SVG document.
    for path in sorted(THEME_ROOT.rglob("*")):
        if path.suffix.lower() in {".xml", ".svg"}:
            try:
                ElementTree.parse(path)
            except ElementTree.ParseError as error:
                check(False, f"{path}: XML does not parse: {error}")

    # Optional runtime parsers. Run each toolkit in a fresh interpreter because
    # GTK 3 and GTK 4 cannot share one PyGObject process reliably.
    parser_code = """
import sys
import gi
gi.require_version("Gtk", "{version}")
from gi.repository import Gtk
for path in sys.argv[1:]:
    provider = Gtk.CssProvider()
    provider.load_from_path(path)
"""
    parser_env = os.environ.copy()
    local_gir = ROOT / ".toolchain" / "girepository-1.0"
    if local_gir.is_dir():
        existing = parser_env.get("GI_TYPELIB_PATH", "")
        parser_env["GI_TYPELIB_PATH"] = str(local_gir) + (os.pathsep + existing if existing else "")
    for version, directory in (("3.0", "gtk-3.0"), ("4.0", "gtk-4.0")):
        paths = [
            str(THEME_ROOT / "themes" / variant / directory / "gtk.css")
            for variant in ("ArashiKage", "ArashiKage-HC")
        ]
        result = subprocess.run(
            [sys.executable, "-c", parser_code.format(version=version), *paths],
            capture_output=True,
            text=True,
            check=False,
            env=parser_env,
        )
        if result.returncode == 0:
            print(f"GTK{version[0]} CSS parser: PASS")
        elif "Namespace Gtk not available" in result.stderr or "No module named 'gi'" in result.stderr:
            print(f"GTK{version[0]} CSS parser: SKIP (PyGObject GTK {version} unavailable)")
        else:
            check(False, f"GTK{version[0]} CSS parser rejected generated CSS: {result.stderr.strip()}")

    if errors:
        print(f"Theme checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Theme checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
