#!/usr/bin/env python3
"""Static verification for the ArashiOS installer, persistence, and recovery.

The checker validates the Calamares configuration against the schemas shipped
by Calamares 3.2, the Kage branding of the installer, the post install script,
and the recovery helpers. It never runs the installer.
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
CALAMARES = INCLUDES / "etc" / "calamares"
BRANDING = INCLUDES / "usr" / "share" / "calamares" / "branding" / "arashios"
BIN = INCLUDES / "usr" / "local" / "bin"

REQUIRED_SEQUENCE = (
    "welcome",
    "locale",
    "localecfg",
    "keyboard",
    "partition",
    "mount",
    "luksbootkeyfile",
    "users",
    "displaymanager",
    "packages",
    "fstab",
    "hwclock",
    "bootloader",
    "services-systemd",
    "removeuser",
    "finished",
    "shellprocess",
)
INSTALLER_PACKAGES = (
    "calamares",
    "calamares-settings-debian",
    "os-prober",
    "parted",
    "cryptsetup",
    "lvm2",
    "mokutil",
    "efibootmgr",
)

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


def load_yaml(path: Path) -> dict:
    text = read(path)
    if not text:
        return {}
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def read_packages(path: Path) -> list[str]:
    packages: list[str] = []
    for line in read(path).splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            packages.extend(line.split())
    return packages


def all_packages() -> list[str]:
    packages: list[str] = []
    for path in sorted(ROOT.glob("config/**/*.list.chroot")):
        packages.extend(read_packages(path))
    return packages


def check_settings() -> None:
    settings = load_yaml(CALAMARES / "settings.conf")
    check(bool(settings), "settings.conf Calamares tidak dapat dibaca")
    check(settings.get("branding") == "arashios", "branding Calamares harus arashios")
    installation = settings.get("installation", {})
    check(installation.get("product.name") == "ArashiOS", "nama produk installer harus ArashiOS")
    check(
        installation.get("bootloaderEntryName") == "ArashiOS",
        "entri bootloader harus bernama ArashiOS",
    )
    check(installation.get("autologinSession") is False, "autologin sesi installer harus mati")
    check(
        installation.get("doNotStorePassword") is False,
        "password pengguna tetap boleh disimpan di keyring",
    )
    check(
        settings.get("modules") == "/etc/calamares/modules.conf",
        "ruang modul Calamares salah",
    )


def check_sequence() -> None:
    modules = load_yaml(CALAMARES / "modules.conf")
    sequence = modules.get("sequence", [])
    check(isinstance(sequence, list), "modules.conf harus memuat daftar sequence")
    for name in REQUIRED_SEQUENCE:
        check(name in sequence, f"modul Calamares {name} tidak ada di sequence")
    check(
        sequence.index("partition") < sequence.index("fstab"),
        "modul partisi harus berjalan sebelum fstab",
    )
    check(
        sequence.index("locale") < sequence.index("localecfg"),
        "modul locale harus berjalan sebelum localecfg",
    )
    check(
        sequence.index("bootloader") < sequence.index("removeuser"),
        "modul bootloader harus berjalan sebelum penghapusan user live",
    )
    check(
        sequence[-1] == "shellprocess",
        "post install harus menjadi langkah terakhir",
    )


def check_partition() -> None:
    partition = load_yaml(CALAMARES / "modules" / "partition.conf")
    check(bool(partition), "partition.conf Calamares tidak dapat dibaca")
    check(partition.get("defaultFs") == "ext4", "filesystem default harus ext4")
    check(partition.get("efiSystemPartition") is True, "partisi EFI harus disiapkan")
    check(
        str(partition.get("efiSystemPartitionSize", "")).endswith("M"),
        "ukuran partisi EFI harus dinyatakan dalam MiB",
    )
    check(partition.get("efiMountPoint") == "/boot/efi", "mount point EFI harus /boot/efi")
    check(partition.get("luksFormatEnabled") is True, "enkripsi LUKS harus ditawarkan")
    check(partition.get("luksOption") == "luks2", "LUKS2 harus menjadi default")
    check(
        str(partition.get("minimumDiskSize", "")).endswith("G"),
        "ukuran disk minimum harus dinyatakan dalam GiB",
    )


def check_users_and_display() -> None:
    users = load_yaml(CALAMARES / "modules" / "users.conf")
    check(users.get("doAutoLogin") is False, "autologin harus mati pada sistem terpasang")
    check(not users.get("autologinUser"), "user autologin harus kosong")
    default_user = users.get("defaultUser", {})
    check(
        default_user.get("name") == "arashios",
        "user default harus berbeda dari user live arashi",
    )
    check(default_user.get("autologin") is False, "autologin user default harus mati")
    check(default_user.get("shell") == "/usr/bin/zsh", "shell default harus zsh")
    groups = users.get("defaultGroups", [])
    for group in ("sudo", "audio", "video", "network", "lpadmin", "scanner", "bluetooth"):
        check(group in groups, f"grup default {group} belum ada")
    display = load_yaml(CALAMARES / "modules" / "displaymanager.conf")
    check(display.get("displaymanagers") == ["lightdm"], "display manager harus lightdm")


def check_removeuser() -> None:
    removeuser = load_yaml(CALAMARES / "modules" / "removeuser.conf")
    check(
        removeuser.get("username") == "arashi",
        "job removeuser harus menghapus user live arashi",
    )


def check_services() -> None:
    services = load_yaml(CALAMARES / "modules" / "services-systemd.conf")
    names = [item.get("name") for item in services.get("services", [])]
    for unit in ("NetworkManager.service", "lightdm.service", "cups.socket", "fwupd.service"):
        check(unit in names, f"unit {unit} tidak diaktifkan pada sistem terpasang")
    masked = [item.get("name") for item in services.get("mask", [])]
    check("ssh.socket" in masked, "ssh.socket harus dimask")
    disabled = [item.get("name") for item in services.get("disable", [])]
    check("ssh.service" in disabled, "ssh.service harus dinonaktifkan")
    targets = [item.get("name") for item in services.get("targets", [])]
    check("graphical.target" in targets, "target graphical harus diaktifkan")


def check_fstab_and_bootloader() -> None:
    fstab = load_yaml(CALAMARES / "modules" / "fstab.conf")
    check("mountOptions" in fstab, "fstab.conf harus memuat mountOptions")
    check("tmpOptions" in fstab, "fstab.conf harus memuat tmpOptions")
    check("noatime" in str(fstab.get("mountOptions", {})), "noatime harus dipakai")
    bootloader = load_yaml(CALAMARES / "modules" / "bootloader.conf")
    check(bootloader.get("grubMkconfig") == "grub-mkconfig", "grub-mkconfig harus dipakai")
    check(bootloader.get("grubCfg") == "/boot/grub/grub.cfg", "lokasi grub.cfg salah")
    check(
        bootloader.get("bootloaderEntryName") == "ArashiOS",
        "nama entri bootloader harus ArashiOS",
    )
    check(
        str(bootloader.get("timeout", "")) == "5",
        "timeout bootloader harus 5 detik",
    )


def check_branding() -> None:
    for name in ("branding.desc", "stylesheet.qss", "show.qml"):
        check((BRANDING / name).is_file(), f"berkas branding {name} hilang")
    slides = sorted((BRANDING / "slides").glob("*.md")) if (BRANDING / "slides").is_dir() else []
    check(len(slides) >= 3, "slideshow installer harus punya minimal tiga slide")
    desc = read(BRANDING / "branding.desc")
    check("componentName: arashios" in desc, "componentName branding harus arashios")
    check("productName: \"ArashiOS\"" in desc, "nama produk pada branding tidak benar")
    check("uploadServer:" in desc, "uploadServer harus dinyatakan")
    check("type: \"none\"" in desc, "log installer tidak boleh dikirim ke server")
    check("#0A0A0C" in desc and "#BF4432" in desc, "warna branding harus memakai palet Kage")
    style = read(BRANDING / "stylesheet.qss")
    check("#sidebarApp" in style, "stylesheet installer harus menata sidebar")
    slideshow = read(BRANDING / "show.qml")
    check("Slide" in slideshow, "slideshow installer harus memakai komponen Slide")


def check_postinstall() -> None:
    script = read(BIN / "arashios-postinstall")
    check(bool(script), "skrip post install hilang")
    check("autologin-user" in script, "post install harus menonaktifkan autologin")
    check("dpkg --purge" in script and "calamares" in script, "post install harus menghapus installer")
    check("systemctl enable" in script, "post install harus mengaktifkan layanan")
    check("timeshift" in script, "post install harus membuat snapshot timeshift")
    check("userdel" in script, "post install harus memastikan user live tidak ada")
    check("graphical.target" in script, "post install harus menetapkan target graphical")
    path = BIN / "arashios-postinstall"
    check(path.is_file() and path.stat().st_mode & 0o111, "post install harus executable")


def check_helpers() -> None:
    recovery = read(BIN / "arashios-recovery")
    for needle in ("grub-install", "grub-mkconfig", "cryptsetup", "vgchange", "backup-efi"):
        check(needle in recovery, f"perintah pemulihan {needle} tidak tersedia")
    persistence = read(BIN / "arashios-persistence")
    check("union" in persistence, "helper persistensi harus menulis direktif union")
    check("persistence" in persistence, "helper persistensi harus memakai label persistence")
    dualboot = read(BIN / "arashios-dualboot-check")
    check("BitLocker" in dualboot, "pemeriksaan dual boot harus mendeteksi BitLocker")
    check("Fast Startup" in dualboot, "pemeriksaan dual boot harus mendeteksi Fast Startup")
    check("Secure Boot" in dualboot, "pemeriksaan dual boot harus memeriksa Secure Boot")
    for name in ("arashios-recovery", "arashios-persistence", "arashios-dualboot-check"):
        path = BIN / name
        check(path.is_file() and path.stat().st_mode & 0o111, f"{name} harus executable")


def check_packages() -> None:
    packages = all_packages()
    for package in INSTALLER_PACKAGES:
        check(package in packages, f"paket installer {package} tidak ada di package list")
    check("grub-pc" in packages, "grub-pc tidak ada untuk instalasi BIOS")
    check("grub-efi-amd64" in packages, "grub-efi-amd64 tidak ada untuk instalasi UEFI amd64")
    check("grub-efi-arm64" in packages, "grub-efi-arm64 tidak ada untuk instalasi UEFI arm64")
    for path in sorted(ROOT.glob("config/**/*.list.chroot")):
        text = read(path).lower()
        check("kali" not in text, f"{path.relative_to(ROOT)}: Mention repository Kali")
        check("blackarch" not in text, f"{path.relative_to(ROOT)}: mention repository BlackArch")


def check_hooks() -> None:
    hook = read(COMMON / "hooks" / "live" / "0500-installer.chroot")
    check("@VERSION@" in hook or "/etc/arashios/version" in hook, "hook installer harus memakai versi rilis")
    check("arashios-banner.png" in hook, "hook installer harus memasang banner Kage")
    check("NoDisplay=false" in hook, "hook installer harus memastikan installer dapat dijalankan")
    branding_hook = read(COMMON / "hooks" / "live" / "0100-branding.chroot")
    check("GRUB_THEME" in branding_hook, "tema GRUB harus dipasang untuk sistem terpasang")
    check("GRUB_DISABLE_OS_PROBER=false" in branding_hook, "os-prober harus aktif untuk boot ganda")


def main() -> int:
    check_settings()
    check_sequence()
    check_partition()
    check_users_and_display()
    check_removeuser()
    check_services()
    check_fstab_and_bootloader()
    check_branding()
    check_postinstall()
    check_helpers()
    check_packages()
    check_hooks()

    if errors:
        print(f"Installer checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Installer checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
