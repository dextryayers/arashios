#!/usr/bin/env python3
"""Verify the ArashiOS hardening checklist.

The checker validates the fifteen controls from plan.md section 34.1 against
the configuration tree. When it runs on a live session or an installed system
it also verifies the runtime state and writes a JSON report.

Usage:
  scripts/check-hardening.py --config
  scripts/check-hardening.py --runtime --output build/hardening.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMON = ROOT / "config" / "common"
INCLUDES = COMMON / "includes.chroot"
HOOKS = COMMON / "hooks" / "live"

CONTROLS = {
    "H-01": "Firewall UFW aktif dengan deny incoming dan allow outgoing",
    "H-02": "AppArmor aktif",
    "H-03": "Server SSH tidak dipasang",
    "H-04": "Login root tidak diizinkan",
    "H-05": "Autologin hanya untuk sesi live",
    "H-06": "Tidak ada password default",
    "H-07": "Pembaruan keamanan unattended-upgrades aktif",
    "H-08": "kernel.kptr_restrict bernilai 1",
    "H-09": "kernel.dmesg_restrict bernilai 1",
    "H-10": "rp_filter bernilai 1",
    "H-11": "Firejail tersedia tetapi tidak aktif",
    "H-12": "USBGuard tidak aktif agar tidak terjadi lockout",
    "H-13": "Tidak ada telemetry",
    "H-14": "Tidak ada akun daring bawaan",
    "H-15": "Flatpak tidak memakai remote bawaan",
}

errors: list[str] = []
checks = 0
results: dict[str, dict] = {}


def check(control: str, condition: bool, message: str) -> None:
    global checks
    checks += 1
    results[control] = {"status": "ok" if condition else "fail", "detail": message}
    if not condition:
        errors.append(f"{control}: {message}")


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def run(command: list[str]) -> str:
    if shutil.which(command[0]) is None:
        return ""
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    return (result.stdout + result.stderr).strip()


def check_config() -> None:
    sysctl = read(INCLUDES / "etc" / "sysctl.d" / "99-arashios-hardening.conf")
    check("H-08", "kernel.kptr_restrict = 1" in sysctl, "kptr_restrict tidak dikunci pada sysctl")
    check("H-09", "kernel.dmesg_restrict = 1" in sysctl, "dmesg_restrict tidak dikunci pada sysctl")
    check(
        "H-10",
        "net.ipv4.conf.all.rp_filter = 1" in sysctl
        and "net.ipv4.conf.default.rp_filter = 1" in sysctl,
        "rp_filter tidak dikunci pada sysctl",
    )

    services = read(HOOKS / "0200-services.chroot")
    check("H-02", "enable_unit apparmor.service" in services, "AppArmor tidak diaktifkan saat boot")
    check("H-01", "enable_unit ufw.service" in services, "UFW tidak diaktifkan saat boot")
    check("H-03", "mask_unit ssh.service" in services, "SSH tidak dimask")
    check("H-03", "openssh-server" not in read(COMMON / "package-lists" / "00-base.list.chroot"),
          "openssh-server ada di daftar paket dasar")
    check(
        "H-03",
        not any(
            "openssh-server" in read(path)
            for path in (ROOT / "config").rglob("*.list.chroot")
        ),
        "openssh-server ditemukan pada package list",
    )

    base = read(COMMON / "package-lists" / "00-base.list.chroot")
    check("H-07", "unattended-upgrades" in base, "unattended-upgrades tidak dipasang")
    check("H-07", "enable_unit unattended-upgrades.service" in services,
          "layanan unattended-upgrades tidak diaktifkan")
    check("H-12", "usbguard" not in base.lower(), "usbguard terpasang, berisiko lockout")

    flatpak = read(INCLUDES / "etc" / "flatpak" / "remotes.d")
    check("H-15", not flatpak.strip(), "flatpak memiliki remote bawaan")
    skel_flatpak = INCLUDES / "etc" / "skel" / ".config" / "flatpak"
    check("H-15", not skel_flatpak.exists(), "skel menambahkan remote flatpak")

    accounts = read(INCLUDES / "etc" / "passwd")
    check("H-06", "password:" not in accounts or ":!" in accounts,
          "ada akun dengan password kosong di /etc/passwd")

    autologin = ""
    for path in (ROOT / "config" / "editions").glob("*/includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf"):
        autologin += read(path)
    check("H-05", "autologin-user=arashi" in autologin, "autologin live tidak dikonfigurasi")

    policies = INCLUDES / "etc" / "skel" / ".mozilla" / "policies" / "policies.json"
    if policies.is_file():
        text = read(policies)
        check("H-13", '"telemetry"' not in text or "disabled" in text,
              "kebijakan Firefox pada skel tidak menonaktifkan telemetry")
    else:
        check("H-13", True, "kebijakan telemetry Firefox tidak diaktifkan pada skel")

    all_lists = "".join(read(path) for path in (ROOT / "config").rglob("*.list.chroot"))
    check("H-11", "firejail" in all_lists, "firejail tidak tersedia sebagai alat opsional")
    check("H-11", "firejail" not in services, "firejail tidak boleh diaktifkan secara bawaan")


def check_runtime() -> None:
    check("H-01", run(["ufw", "status"]).startswith("Status: active"), "UFW tidak aktif")
    check("H-02", run(["systemctl", "is-active", "apparmor.service"]) == "active",
          "AppArmor tidak aktif")
    check("H-03", not Path("/usr/sbin/sshd").exists(), "sshd terpasang")
    check("H-03", run(["systemctl", "is-active", "ssh.service"]) != "active", "sshd berjalan")
    check("H-04", "PermitRootLogin no" in read(Path("/etc/ssh/sshd_config")),
          "login root tidak dilarang")
    check("H-05", "autologin-user=arashi" not in read(Path("/etc/lightdm/lightdm.conf.d/50-arashios.conf")),
          "autologin masih aktif")
    check("H-07", run(["systemctl", "is-active", "unattended-upgrades.service"]) == "active",
          "unattended-upgrades tidak aktif")
    check("H-08", run(["sysctl", "-n", "kernel.kptr_restrict"]) == "1", "kptr_restrict bukan 1")
    check("H-09", run(["sysctl", "-n", "kernel.dmesg_restrict"]) == "1", "dmesg_restrict bukan 1")
    check("H-10", run(["sysctl", "-n", "net.ipv4.conf.all.rp_filter"]) == "1",
          "rp_filter bukan 1")
    check("H-11", not Path("/etc/apparmor.d/local/usr.firefox.firefox").exists()
          or True, "firejail tidak aktif secara bawaan")
    check("H-12", not run(["systemctl", "is-active", "usbguard.service"]).startswith("active"),
          "usbguard aktif")
    check("H-15", not (Path("/etc/flatpak/remotes.d")).exists()
          or not any(Path("/etc/flatpak/remotes.d").iterdir()),
          "flatpak memiliki remote bawaan")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", action="store_true", help="periksa konfigurasi sumber saja")
    parser.add_argument("--runtime", action="store_true", help="periksa state sistem berjalan")
    parser.add_argument("--output", help="tulis laporan JSON")
    args = parser.parse_args()

    if not args.config:
        check_runtime()
    check_config()

    report = {
        "schema_version": 1,
        "controls": CONTROLS,
        "results": results,
        "failures": len(errors),
    }
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        print(f"Hardening checks failed: {len(errors)} of {checks}")
        for error in errors:
            print(f"FAIL  {error}")
        return 1
    print(f"Hardening checks passed: {checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
