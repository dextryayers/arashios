#!/usr/bin/env python3
"""Static verification for the ArashiOS daily use platform.

The checker validates the daily driver workflow: locale coverage, network and
power policy, printing, audio per edition, firmware handling, and the daily
application set. It never starts a service.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML tidak tersedia. Pasang paket python3-yaml.", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
COMMON = ROOT / "config" / "common"
INCLUDES = COMMON / "includes.chroot"
EDITIONS = ROOT / "config" / "editions"
BIN = INCLUDES / "usr" / "local" / "bin"
LISTS = sorted(ROOT.glob("config/**/*.list.chroot"))

REQUIRED_LOCALES = ("en_US.UTF-8", "id_ID.UTF-8", "ja_JP.UTF-8")
DAILY_APPS = (
    "firefox-esr",
    "thunderbird",
    "libreoffice",
    "vlc",
    "gimp",
    "inkscape",
    "evince",
    "file-roller",
    "flameshot",
    "keepassxc",
    "timeshift",
    "gparted",
    "gnome-disk-utility",
    "remmina",
    "filezilla",
    "qbittorrent",
)
NETWORK_PACKAGES = ("network-manager", "network-manager-gnome", "avahi-daemon", "wpasupplicant")
PRINT_PACKAGES = ("cups", "cups-filters", "system-config-printer", "sane-utils", "xsane")
AUDIO_PACKAGES = ("pavucontrol", "alsa-utils", "libasound2-plugins", "playerctl")
POWER_PACKAGES = ("tlp", "zram-tools", "earlyoom")
FIRMWARE_PACKAGES = ("fwupd", "firmware-linux-free", "firmware-iwlwifi", "firmware-realtek")

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


def read_packages(path: Path) -> list[str]:
    packages: list[str] = []
    for line in read(path).splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            packages.extend(line.split())
    return packages


def all_packages() -> list[str]:
    packages: list[str] = []
    for path in LISTS:
        packages.extend(read_packages(path))
    return packages


def check_locale() -> None:
    locale_gen = read(INCLUDES / "etc" / "locale.gen")
    for locale in REQUIRED_LOCALES:
        check(f"{locale} UTF-8" in locale_gen, f"locale.gen tidak memuat {locale}")
    packages = all_packages()
    check("fonts-noto-cjk" in packages, "font CJK tidak dipasang untuk locale ja_JP")
    check("hunspell-id" in packages, "kamus ejaan Indonesia tidak dipasang")
    check("libreoffice-l10n-id" in packages, "locale LibreOffice Indonesia tidak dipasang")
    check("libreoffice-l10n-ja" in packages, "locale LibreOffice Jepang tidak dipasang")
    check("firefox-esr-l10n-id" in packages, "locale Firefox Indonesia tidak dipasang")
    check("firefox-esr-l10n-ja" in packages, "locale Firefox Jepang tidak dipasang")


def check_network() -> None:
    for package in NETWORK_PACKAGES:
        check(package in all_packages(), f"paket jaringan {package} tidak ada di package list")
    conf = read(INCLUDES / "etc" / "NetworkManager" / "conf.d" / "99-arashios.conf")
    check(bool(conf), "konfigurasi NetworkManager ArashiOS hilang")
    for key in ("[main]", "[device]", "[connection]", "wifi.powersave", "dns = default"):
        check(key in conf, f"kunci NetworkManager {key} hilang")
    check("uri.enable = false" in conf, "pengecekan konektivitas NetworkManager harus nonaktif")
    check("no_hosts = false" not in conf, "resolusi /etc/hosts harus tetap menyertakan host lokal")


def check_power() -> None:
    for package in POWER_PACKAGES:
        check(package in all_packages(), f"paket daya {package} tidak ada di package list")
    tlp = read(INCLUDES / "etc" / "tlp.conf")
    check("START_CHARGE_THRESH=" in tlp and "STOP_CHARGE_THRESH=" in tlp, "ambang pengisian TLP hilang")
    check("PCIE_ASPM=on" in tlp, "ASPM PCIe harus aktif pada TLP")
    zram = read(INCLUDES / "etc" / "default" / "zramswap")
    check("ALGO=zstd" in zram, "algoritma zram harus zstd")
    check("PERCENT=" in zram, "ukuran zram berbasis memori belum diatur")
    earlyoom = read(INCLUDES / "etc" / "default" / "earlyoom")
    check("EARLYOOM_MEMORY_AVAILABLE=" in earlyoom, "ambang memori earlyoom belum diatur")
    hook = read(COMMON / "hooks" / "live" / "0400-platform.chroot")
    for unit in ("tlp.service", "zram-swap.service", "earlyoom.service", "fwupd.service"):
        check(unit in hook, f"unit {unit} tidak diaktifkan oleh hook platform")


def check_print() -> None:
    for package in PRINT_PACKAGES:
        check(package in all_packages(), f"paket cetak {package} tidak ada di package list")
    hook = read(COMMON / "hooks" / "live" / "0400-platform.chroot")
    check("cups.socket" in hook, "cups.socket tidak diaktifkan")
    check("disable_unit cups.service" in hook, "cups.service harus dinonaktifkan dan diganti socket")


def check_audio() -> None:
    for package in AUDIO_PACKAGES:
        check(package in all_packages(), f"paket audio {package} tidak ada di package list")
    expectations = {
        "cinnamon": ("pipewire", "pipewire-pulse", "wireplumber"),
        "lxqt": ("pipewire", "pipewire-pulse", "wireplumber"),
        "xfce": ("pulseaudio",),
    }
    for edition, packages in expectations.items():
        listing = read(EDITIONS / edition / "package-lists" / "50-desktop.list.chroot")
        for package in packages:
            check(package in listing, f"edisi {edition} tidak memakai paket audio {package}")
        for package in ("pipewire", "pulseaudio"):
            if package not in packages:
                check(package not in listing, f"edisi {edition} tidak boleh memakai {package}")


def check_firmware() -> None:
    for package in FIRMWARE_PACKAGES:
        check(package in all_packages(), f"paket firmware {package} tidak ada di package list")
    check("mokutil" in all_packages(), "mokutil tidak dipasang untuk memeriksa Secure Boot")


def check_daily_apps() -> None:
    packages = all_packages()
    for package in DAILY_APPS:
        check(package in packages, f"aplikasi harian {package} tidak ada di package list")
    check("mpv" in packages, "pemutar media mpv tidak dipasang")
    check("seahorse" in packages, "pengelola sertifikat seahorse tidak dipasang")


def check_commands() -> None:
    for name in ("arashios-daily", "arashios-hardware-report"):
        path = BIN / name
        check(path.is_file(), f"perintah {name} hilang")
        check(path.is_file() and path.stat().st_mode & 0o111, f"perintah {name} tidak executable")


def check_duplicates() -> None:
    """Duplicates are only a problem inside one supported combination."""
    versions = {}
    for line in read(ROOT / "versions.env").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            versions[key.strip()] = value.strip().strip('"')
    combinations = versions.get("SUPPORTED_COMBINATIONS", "").split()
    for combination in combinations:
        arch, _, edition = combination.partition(":")
        files = [path for path in LISTS if path.parent.parent.name == "common"]
        files += list((EDITIONS / edition / "package-lists").glob("*.list.chroot"))
        arch_dir = ROOT / "config" / "arches" / arch / "package-lists"
        if arch_dir.is_dir():
            files += list(arch_dir.glob("*.list.chroot"))
        counts: dict[str, int] = {}
        for path in files:
            for package in read_packages(path):
                counts[package] = counts.get(package, 0) + 1
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        check(not duplicates, f"paket duplikat pada {edition}/{arch}: " + ", ".join(duplicates))


def main() -> int:
    check_locale()
    check_network()
    check_power()
    check_print()
    check_audio()
    check_firmware()
    check_daily_apps()
    check_commands()
    check_duplicates()

    if errors:
        print(f"Daily use checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Daily use checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
