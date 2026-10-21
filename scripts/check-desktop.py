#!/usr/bin/env python3
"""Static verification for ArashiOS desktop integration.

This checker validates configuration files and package lists. It never starts a
desktop session. Runtime login, panel rendering, and screenshot checks remain
separate acceptance gates that require a built ISO.
"""
from __future__ import annotations

import configparser
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
COMMON = ROOT / "config" / "common" / "includes.chroot"
EDITIONS = ROOT / "config" / "editions"
errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def read_ini(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    try:
        parser.read(path, encoding="utf-8")
    except configparser.MissingSectionHeaderError:
        # QSettings permits root-level keys such as the LXQt panel `panels=`
        # entry. ConfigParser needs an explicit group for the same data.
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        parser.read_string("[General]\n" + read(path), source=str(path))
    return parser


def require_file(path: Path, label: str | None = None) -> None:
    check(path.is_file(), f"missing file: {label or path.relative_to(ROOT)}")


def check_executable(path: Path) -> None:
    require_file(path)
    if path.is_file():
        check(path.stat().st_mode & 0o111 != 0, f"not executable: {path.relative_to(ROOT)}")


def check_shell_syntax(path: Path, shell: str = "bash") -> None:
    if not path.is_file():
        return
    result = subprocess.run([shell, "-n", str(path)], capture_output=True, text=True, check=False)
    check(result.returncode == 0, f"{path.relative_to(ROOT)}: shell syntax error: {result.stderr.strip()}")


def check_dconf_dir(path: Path) -> None:
    require_file(path)
    if not path.is_file():
        return
    text = read(path)
    check(not re.search(r"^[^#\n]*\s+=\s*", text, re.M), f"{path.relative_to(ROOT)}: whitespace around assignment")
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "local"
        result = subprocess.run(["dconf", "compile", str(output), str(path.parent)],
                                capture_output=True, text=True, check=False)
        check(result.returncode == 0, f"{path.relative_to(ROOT)}: dconf compile failed: {result.stderr.strip()}")


def desktop_ids(path: Path) -> set[str]:
    parser = read_ini(path)
    values: set[str] = set()
    for section in parser.sections():
        for key, value in parser.items(section):
            if key in {"inode/directory", "text/plain", "text/html", "x-scheme-handler/http"} or "/" in key:
                values.add(value.strip())
    return values


def check_mimeapps(path: Path, expected: dict[str, str]) -> None:
    require_file(path)
    if not path.is_file():
        return
    parser = read_ini(path)
    check(parser.has_section("Default Applications"), f"{path.relative_to(ROOT)}: no Default Applications section")
    for mime, desktop in expected.items():
        actual = parser.get("Default Applications", mime, fallback="")
        check(actual == desktop, f"{path.relative_to(ROOT)}: {mime} is '{actual}', expected '{desktop}'")
    for desktop in desktop_ids(path):
        check(desktop.endswith(".desktop"), f"{path.relative_to(ROOT)}: invalid desktop id {desktop}")


def prop_value(parent: ElementTree.Element, name: str) -> str:
    element = parent.find(f"./property[@name='{name}']")
    return element.get("value", "") if element is not None else ""


def panel_tree(path: Path) -> tuple[ElementTree.Element, ElementTree.Element] | None:
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError):
        return None
    panels = root.find("./property[@name='panels']")
    plugins = root.find("./property[@name='plugins']")
    if panels is None or plugins is None:
        return None
    return panels, plugins


def main() -> int:
    common_gtk3 = read_ini(COMMON / "etc/gtk-3.0/settings.ini")
    check(common_gtk3.get("Settings", "gtk-theme-name", fallback="") == "ArashiKage", "system GTK3 theme is not ArashiKage")
    check(common_gtk3.get("Settings", "gtk-icon-theme-name", fallback="") == "Papirus-Dark", "system icon theme is not Papirus-Dark")
    check(common_gtk3.get("Settings", "gtk-cursor-theme-name", fallback="") == "Bibata-Modern-Classic", "system cursor theme is wrong")
    check(common_gtk3.get("Settings", "gtk-font-name", fallback="") == "Inter 10", "system UI font is not Inter 10")

    common_gtk4 = read_ini(COMMON / "etc/gtk-4.0/settings.ini")
    check(common_gtk4.get("Settings", "gtk-theme-name", fallback="") == "ArashiKage", "system GTK4 theme is not ArashiKage")
    check("gtk-4.0/gtk.css" in read(COMMON / "etc/gtk-4.0/gtk.css"), "system GTK4 CSS does not import Kage")
    check("gtk-4.0/gtk.css" in read(COMMON / "etc/xdg/gtk-4.0/gtk.css"), "XDG GTK4 CSS does not import Kage")
    gtk2 = read(COMMON / "etc/gtk-2.0/gtkrc")
    for value in ("ArashiKage", "Papirus-Dark", "Inter 10", "Bibata-Modern-Classic"):
        check(value in gtk2, f"system GTK2 config lacks {value}")

    for prefix in ("etc", "etc/skel/.config"):
        gtk3 = read_ini(COMMON / prefix / "gtk-3.0/settings.ini")
        check(gtk3.get("Settings", "gtk-theme-name", fallback="") == "ArashiKage", f"{prefix}: skel GTK3 theme is wrong")
        gtk4 = read_ini(COMMON / prefix / "gtk-4.0/settings.ini")
        check(gtk4.get("Settings", "gtk-theme-name", fallback="") == "ArashiKage", f"{prefix}: skel GTK4 theme is wrong")

    environment = read(COMMON / "etc/environment")
    for value in ("QT_QPA_PLATFORMTHEME=qt5ct", "QT_STYLE_OVERRIDE=kvantum"):
        check(value in environment, f"/etc/environment lacks {value}")

    qt5ct = read_ini(COMMON / "etc/xdg/qt5ct/qt5ct.conf")
    check(qt5ct.get("Appearance", "style", fallback="") == "kvantum", "qt5ct style is not Kvantum")
    check(qt5ct.get("Appearance", "icon_theme", fallback="") == "Papirus-Dark", "qt5ct icon theme is wrong")
    kvantum = read_ini(COMMON / "etc/xdg/Kvantum/kvantum.kvconfig")
    check(kvantum.get("General", "theme", fallback="") == "ArashiKage", "system Kvantum theme is wrong")

    for path in (
        COMMON / "usr/local/bin/arashios-accessibility",
        COMMON / "usr/local/bin/kage-contrast",
        COMMON / "usr/local/bin/arashios-wallpaper",
    ):
        check_executable(path)
        check_shell_syntax(path)
    token_colors = {
        value.upper()
        for value in re.findall(r"#[0-9A-Fa-f]{6}", (ROOT / "branding/tokens.json").read_text(encoding="utf-8"))
    }
    for path in (
        COMMON / "etc/skel/.config/xfce4/terminal/terminalrc",
        COMMON / "etc/skel/.config/qterminal.org/qterminal.ini",
    ):
        for value in re.findall(r"#[0-9A-Fa-f]{6}", read(path)):
            check(value.upper() in token_colors, f"{path.relative_to(ROOT)}: terminal color {value} is not a Kage token")

    accessibility = read(COMMON / "usr/local/bin/arashios-accessibility")
    for value in (
        "contrast",
        "motion",
        "ArashiKage-HC",
        "enable-animations",
        "Bibata-Modern-Classic",
        "org.cinnamon.desktop.wm.preferences theme",
    ):
        check(value in accessibility, f"accessibility helper lacks {value}")
    wallpaper = read(COMMON / "usr/local/bin/arashios-wallpaper")
    check("kage-sumi.png" in wallpaper, "wallpaper helper does not default to a PNG wallpaper")
    for desktop in ("set_xfce", "set_cinnamon", "set_lxqt"):
        check(desktop in wallpaper, f"wallpaper helper lacks {desktop}")

    greeter = read_ini(COMMON / "etc/lightdm/lightdm-gtk-greeter.conf.d/50-arashios.conf")
    check(greeter.get("greeter", "theme-name", fallback="") == "ArashiKage", "LightDM theme is not ArashiKage")
    check(greeter.get("greeter", "icon-theme-name", fallback="") == "Papirus-Dark", "LightDM icon theme is wrong")
    check(greeter.get("greeter", "background", fallback="").endswith(".png"), "LightDM wallpaper is not PNG")
    check(greeter.get("greeter", "panel-position", fallback="") == "top", "LightDM panel is not on top")
    check(greeter.get("greeter", "font-name", fallback="") == "Inter 10", "LightDM font is wrong")

    hook = ROOT / "config/common/hooks/live/0100-branding.chroot"
    require_file(hook)
    check_shell_syntax(hook, "sh")
    hook_text = read(hook)
    for value in ("dconf update", "calendar@cinnamon.org", "menu@cinnamon.org", "arashios-accessibility"):
        check(value in hook_text, f"branding hook lacks {value}")

    require_file(COMMON / "etc/dconf/profile/user")
    check(read(COMMON / "etc/dconf/profile/user").strip() == "user-db:user\nsystem-db:local", "dconf profile is wrong")

    common_packages = read(ROOT / "config/common/package-lists/10-desktop-common.list.chroot")
    for package in (
        "lightdm",
        "lightdm-gtk-greeter",
        "dconf-cli",
        "qt5-style-kvantum",
        "qt5ct",
        "gtk2-engines-murrine",
        "libadwaita-1-0",
        "bibata-cursor-theme",
        "papirus-icon-theme",
        "fonts-inter",
        "fonts-jetbrains-mono",
    ):
        check(re.search(rf"^{re.escape(package)}$", common_packages, re.M) is not None,
              f"common package list lacks {package}")

    # Cinnamon
    cinnamon = EDITIONS / "cinnamon"
    cinnamon_dconf = cinnamon / "includes.chroot/etc/dconf/db/local.d/00-arashios"
    check_dconf_dir(cinnamon_dconf)
    dconf = read(cinnamon_dconf)
    for value in (
        "[org/cinnamon]",
        "panels-enabled=['1:0:top']",
        "panels-height=['1:30']",
        "name='ArashiKage'",
        "theme='ArashiKage'",
        "gtk-theme='ArashiKage'",
        "icon-theme='Papirus-Dark'",
        "cursor-theme='Bibata-Modern-Classic'",
        "picture-uri='file:///usr/share/backgrounds/arashios/kage-sumi.png'",
        "show-desktop-icons=false",
        "num-workspaces=4",
        "automount=false",
    ):
        check(value in dconf, f"Cinnamon dconf lacks {value}")
    check("Adwaita-dark" not in dconf, "Cinnamon dconf still references Adwaita-dark")
    for value in (
        "[org/gnome/terminal/legacy/profiles:]",
        "use-theme-colors=false",
        "font='JetBrains Mono 11'",
        "cursor-background-color='#DD785B'",
        "default-size-columns=120",
    ):
        check(value in dconf, f"Cinnamon terminal profile lacks {value}")
    check_mimeapps(cinnamon / "includes.chroot/etc/xdg/mimeapps.list", {
        "inode/directory": "nemo.desktop",
        "text/plain": "org.gnome.gedit.desktop",
        "image/png": "org.gnome.eog.desktop",
    })
    cinnamon_packages = read(cinnamon / "package-lists/50-desktop.list.chroot")
    for package in ("cinnamon", "cinnamon-core", "nemo", "gnome-terminal", "gedit", "eog", "pipewire"):
        check(re.search(rf"^{re.escape(package)}$", cinnamon_packages, re.M) is not None,
              f"Cinnamon package list lacks {package}")
    cinnamon_lightdm = read_ini(cinnamon / "includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf")
    check(cinnamon_lightdm.get("Seat:*", "user-session", fallback="") == "cinnamon", "Cinnamon LightDM session is wrong")

    # XFCE
    xfce = EDITIONS / "xfce"
    xfce_conf = xfce / "includes.chroot/etc/xdg/xfce4/xfconf/xfce-perchannel-xml"
    for name in ("xsettings.xml", "xfwm4.xml", "xfce4-panel.xml", "xfce4-desktop.xml", "xfce4-session.xml", "thunar.xml"):
        require_file(xfce_conf / name)
        if (xfce_conf / name).is_file():
            try:
                ElementTree.parse(xfce_conf / name)
            except ElementTree.ParseError as error:
                check(False, f"XFCE {name} does not parse: {error}")
    xsettings = read(xfce_conf / "xsettings.xml")
    for value in ("ArashiKage", "Papirus-Dark", "Bibata-Modern-Classic", "Inter 10", "JetBrains Mono 10"):
        check(value in xsettings, f"XFCE xsettings lacks {value}")
    xfwm4 = read(xfce_conf / "xfwm4.xml")
    for value in ("value=\"ArashiKage\"", "value=\"|HMC\"", "workspace_count\" type=\"int\" value=\"4\""):
        check(value in xfwm4, f"XFCE xfwm4 lacks {value}")
    panel = panel_tree(xfce_conf / "xfce4-panel.xml")
    check(panel is not None, "XFCE panel XML structure is invalid")
    if panel is not None:
        panels, plugins = panel
        panel1 = panels.find("./property[@name='panel-1']")
        check(panel1 is not None, "XFCE panel-1 is missing")
        if panel1 is not None:
            check(prop_value(panel1, "size") == "30", "XFCE panel is not 30px")
            check(prop_value(panel1, "position").startswith("p=6"), "XFCE panel is not at the top")
            ids = [value.get("value", "") for value in panel1.findall("./property[@name='plugin-ids']/value")]
            check(len(ids) == 11, f"XFCE panel has {len(ids)} plugin IDs")
            definitions = {
                element.get("name")
                for element in plugins
                if element.get("name", "").startswith("plugin-")
            }
            check({f"plugin-{value}" for value in ids} == definitions, "XFCE panel plugin IDs do not match plugin definitions")
            check(prop_value(plugins, "plugin-1") == "whiskermenu", "XFCE panel lacks Whisker Menu")
            check(prop_value(plugins, "plugin-3") == "tasklist", "XFCE panel lacks tasklist")
            check(prop_value(plugins, "plugin-11") == "pager", "XFCE panel lacks workspace switcher")
    desktop_xml = read(xfce_conf / "xfce4-desktop.xml")
    check("kage-sumi.png" in desktop_xml, "XFCE wallpaper is not Kage PNG")
    for value in ("show-filesystem\" type=\"bool\" value=\"false\"", "show-home\" type=\"bool\" value=\"false\"",
                  "show-trash\" type=\"bool\" value=\"false\""):
        check(value in desktop_xml, f"XFCE desktop icons are not disabled: {value}")
    check_mimeapps(xfce / "includes.chroot/etc/xdg/mimeapps.list", {
        "inode/directory": "thunar.desktop",
        "text/plain": "mousepad.desktop",
        "image/png": "ristretto.desktop",
    })
    xfce_packages = read(xfce / "package-lists/50-desktop.list.chroot")
    for package in ("xfce4", "xfce4-goodies", "xfce4-whiskermenu-plugin", "thunar", "mousepad", "ristretto", "pulseaudio"):
        check(re.search(rf"^{re.escape(package)}$", xfce_packages, re.M) is not None,
              f"XFCE package list lacks {package}")
    xfce_lightdm = read_ini(xfce / "includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf")
    check(xfce_lightdm.get("Seat:*", "user-session", fallback="") == "xfce", "XFCE LightDM session is wrong")

    # LXQt
    lxqt = EDITIONS / "lxqt"
    lxqt_ini = read_ini(lxqt / "includes.chroot/etc/xdg/lxqt/lxqt.conf")
    check(lxqt_ini.get("General", "theme", fallback="") == "ArashiKage", "LXQt theme is not ArashiKage")
    check(lxqt_ini.get("General", "icon_theme", fallback="") == "Papirus-Dark", "LXQt icon theme is wrong")
    check(lxqt_ini.get("Qt", "style", fallback="") == "kvantum", "LXQt Qt style is not Kvantum")
    session_ini = read_ini(lxqt / "includes.chroot/etc/xdg/lxqt/session.conf")
    check(session_ini.get("Mouse", "cursor_theme", fallback="") == "Bibata-Modern-Classic", "LXQt cursor theme is wrong")
    check(session_ini.get("Mouse", "cursor_size", fallback="") == "24", "LXQt cursor size is wrong")
    panel_ini = read_ini(lxqt / "includes.chroot/etc/xdg/lxqt/panel.conf")
    check(panel_ini.get("panel1", "position", fallback="") == "Top", "LXQt panel is not on top")
    check(panel_ini.get("panel1", "panelSize", fallback="") == "30", "LXQt panel is not 30px")
    plugins = panel_ini.get("panel1", "plugins", fallback="")
    for plugin in ("mainmenu", "quicklaunch", "taskbar", "statusnotifier", "tray", "worldclock", "volume"):
        check(plugin in plugins, f"LXQt panel lacks {plugin}")
    check(panel_ini.get("quicklaunch", "apps\\size", fallback="") == "3", "LXQt quick launch has no entries")
    check(panel_ini.get("worldclock", "timeFormat", fallback="") == "HH:mm", "LXQt clock format is wrong")
    pcmanfm = read_ini(lxqt / "includes.chroot/etc/xdg/pcmanfm-qt/lxqt/settings.conf")
    check(pcmanfm.get("Desktop", "Wallpaper", fallback="").endswith("kage-sumi.png"), "LXQt wallpaper is not Kage PNG")
    check(pcmanfm.get("Desktop", "DesktopShortcuts", fallback="x") == "", "LXQt desktop shortcuts are not empty")
    check(pcmanfm.get("FolderView", "Mode", fallback="") == "detail", "PCManFM-Qt is not in list view")
    check(pcmanfm.get("Volume", "AutoRun", fallback="") == "false", "PCManFM-Qt autorun is enabled")
    openbox = read(lxqt / "includes.chroot/etc/xdg/openbox/rc.xml")
    check("<name>ArashiKage</name>" in openbox, "Openbox theme is not ArashiKage")
    check("<titleLayout>IMC</titleLayout>" in openbox, "Openbox button layout is wrong")
    check("<number>4</number>" in openbox, "Openbox does not have four workspaces")
    check("debian-menu.xml" not in openbox, "Openbox exposes the Debian menu tree")
    try:
        ElementTree.parse(lxqt / "includes.chroot/etc/xdg/openbox/rc.xml")
        ElementTree.parse(lxqt / "includes.chroot/etc/xdg/openbox/menu.xml")
    except ElementTree.ParseError as error:
        check(False, f"Openbox XML does not parse: {error}")
    check_mimeapps(lxqt / "includes.chroot/etc/xdg/mimeapps.list", {
        "inode/directory": "pcmanfm-qt.desktop",
        "text/plain": "featherpad.desktop",
        "image/png": "lximage-qt.desktop",
        "application/zip": "lxqt-archiver.desktop",
    })
    lxqt_packages = read(lxqt / "package-lists/50-desktop.list.chroot")
    for package in ("lxqt-core", "lxqt-panel", "pcmanfm-qt", "qterminal", "openbox", "obconf", "lxqt-archiver", "pipewire"):
        check(re.search(rf"^{re.escape(package)}$", lxqt_packages, re.M) is not None,
              f"LXQt package list lacks {package}")
    lxqt_lightdm = read_ini(lxqt / "includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf")
    check(lxqt_lightdm.get("Seat:*", "user-session", fallback="") == "lxqt", "LXQt LightDM session is wrong")

    # The source tree must not fall back to the old undeclared theme or SVG wallpaper.
    for path in (ROOT / "config").rglob("*"):
        if path.is_file() and path.suffix in {".ini", ".conf", ".xml", ".list.chroot", "settings.ini", "themerc"}:
            text = read(path)
            check("Adwaita-dark" not in text, f"{path.relative_to(ROOT)}: old Adwaita-dark reference")
            if path.name in {"lxqt.conf", "settings.ini", "xfce4-desktop.xml", "00-arashios", "50-arashios.conf"}:
                check("kage-sumi.svg" not in text, f"{path.relative_to(ROOT)}: SVG wallpaper reference")

    if errors:
        print(f"Desktop checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Desktop checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
