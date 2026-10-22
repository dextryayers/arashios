#!/usr/bin/env python3
"""Build the local ArashiOS APT repository.

The builder lays out the pool, writes the Packages index for every
architecture, produces the Release file with checksums, and signs the
repository when a GPG key is available. The output is deterministic apart
from the release timestamp, which follows SOURCE_DATE_EPOCH when set.

Usage:
  scripts/build-repo.py --packages build/packages --output repo/public
  scripts/build-repo.py --packages build/packages --output repo/public --sign
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POOL_LINK = ROOT / "repo" / "pool"
KEY_DIR = ROOT / "repo" / "keys"
SUITE = "stable"
COMPONENT = "main"
ARCHES = ("amd64", "arm64", "i386")
CONTROL_FIELDS = (
    "Package",
    "Version",
    "Architecture",
    "Maintainer",
    "Installed-Size",
    "Depends",
    "Recommends",
    "Suggests",
    "Conflicts",
    "Breaks",
    "Provides",
    "Replaces",
    "Section",
    "Priority",
    "Homepage",
    "Bugs",
    "Source",
    "Description",
)


def log(message: str) -> None:
    print(f"[repo] {message}", file=sys.stderr)


def read_control(deb: Path) -> dict:
    result = subprocess.run(
        ["dpkg-deb", "-f", str(deb)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"ERROR: control paket tidak terbaca: {deb}")
    fields: dict[str, str] = {}
    key = ""
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        if line[0] in " \t" and key:
            fields[key] += "\n" + line.strip()
            continue
        name, _, value = line.partition(":")
        key = name.strip()
        fields[key] = value.strip()
    return fields


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def package_entry(deb: Path, pool_path: str) -> str:
    control = read_control(deb)
    lines = []
    for field in CONTROL_FIELDS:
        if field == "Description":
            continue
        if field in control and control[field]:
            lines.append(f"{field}: {control[field]}")
    lines.append(f"Filename: {pool_path}")
    lines.append(f"Size: {deb.stat().st_size}")
    lines.append(f"MD5sum: {digest(deb, 'md5')}")
    lines.append(f"SHA1: {digest(deb, 'sha1')}")
    lines.append(f"SHA256: {digest(deb, 'sha256')}")
    description = control.get("Description", "")
    lines.append(f"Description: {description}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packages", default="build/packages")
    parser.add_argument("--output", default="repo/public")
    parser.add_argument("--sign", action="store_true", help="tandatangani repository dengan kunci GPG")
    parser.add_argument("--dist", default=SUITE)
    parser.add_argument("--component", default=COMPONENT)
    args = parser.parse_args()

    packages_dir = (ROOT / args.packages).resolve()
    output = (ROOT / args.output).resolve()
    if not packages_dir.is_dir():
        raise SystemExit(f"ERROR: direktori paket tidak ditemukan: {packages_dir}")

    debs = sorted(packages_dir.glob("*.deb"))
    if not debs:
        raise SystemExit(f"ERROR: tidak ada paket .deb di {packages_dir}")

    pool_root = output / "pool" / COMPONENT
    entries: dict[str, list[tuple[Path, str]]] = {arch: [] for arch in ARCHES}

    for deb in debs:
        control = read_control(deb)
        name = control.get("Package", deb.name)
        arch = control.get("Architecture", "all")
        target_dir = pool_root / name[0] / name
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / deb.name
        shutil.copy2(deb, target)
        pool_path = str(target.relative_to(output))
        for candidate in ARCHES:
            if arch in (candidate, "all"):
                entries[candidate].append((target, pool_path))

    if POOL_LINK.exists() or POOL_LINK.is_symlink():
        if POOL_LINK.is_symlink():
            POOL_LINK.unlink()
        else:
            shutil.rmtree(POOL_LINK)
    POOL_LINK.parent.mkdir(parents=True, exist_ok=True)
    POOL_LINK.symlink_to(Path("public") / "pool", target_is_directory=True)

    dists = output / "dists" / args.dist
    for arch, items in entries.items():
        if not items:
            continue
        target_dir = dists / args.component / f"binary-{arch}"
        target_dir.mkdir(parents=True, exist_ok=True)
        content = ""
        for deb, pool_path in sorted(items, key=lambda pair: pair[0].name):
            content += package_entry(deb, pool_path) + "\n"
        (target_dir / "Packages").write_text(content, encoding="utf-8")
        import gzip

        with gzip.GzipFile(filename="", mode="wb", fileobj=(target_dir / "Packages.gz").open("wb"), mtime=0) as handle:
            handle.write(content.encode("utf-8"))

    architectures = [arch for arch, items in entries.items() if items]
    release_lines = [
        f"Origin: ArashiOS Project",
        f"Label: ArashiOS",
        f"Suite: {args.dist}",
        f"Codename: {args.dist}",
        f"Version: 1.0",
        f"Architectures: {' '.join(architectures)}",
        f"Components: {args.component}",
        f"Description: ArashiOS package repository",
    ]
    stamp = os.environ.get("SOURCE_DATE_EPOCH")
    date = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime(int(stamp) if stamp else time.time()))
    release_lines.append(f"Date: {date}")
    release_lines.append("Acquire-By-Hash: no")

    checksums = []
    for path in sorted(dists.rglob("*")):
        if not path.is_file() or path.name in {"Release", "Release.gpg", "InRelease"}:
            continue
        relative = path.relative_to(dists)
        checksums.append((relative, path))
    for algorithm, label in (("md5", "MD5Sum"), ("sha1", "SHA1"), ("sha256", "SHA256")):
        release_lines.append(f"{label}:")
        for relative, path in checksums:
            release_lines.append(f" {digest(path, algorithm)} {len(path.read_bytes())} {relative}")

    release_text = "\n".join(release_lines) + "\n"
    (dists / "Release").write_text(release_text, encoding="utf-8")

    signed = False
    if args.sign:
        fingerprint_file = KEY_DIR / "arashios-archive.fingerprint"
        if not fingerprint_file.is_file():
            log("PERINGATAN: kunci repository belum ada, repository tidak ditandatangani")
        else:
            fingerprint = fingerprint_file.read_text(encoding="utf-8").strip()
            env = dict(os.environ)
            env["GNUPGHOME"] = str(KEY_DIR / "gnupg")
            passphrase = os.environ.get("ARASHIOS_REPO_KEY_PASSPHRASE", "")
            for command, target in (
                (["gpg", "--batch", "--yes", "--armor", "--detach-sign", "--output", str(dists / "Release.gpg")], None),
                (["gpg", "--batch", "--yes", "--clearsign", "--output", str(dists / "InRelease")], None),
            ):
                args_list = list(command)
                if passphrase:
                    args_list[1:1] = ["--pinentry-mode", "loopback", "--passphrase", passphrase]
                result = subprocess.run(args_list, env=env, capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    log(f"PERINGATAN: penandatanganan gagal: {result.stderr.strip()[:200]}")
            if (dists / "InRelease").is_file() and (dists / "Release.gpg").is_file():
                signed = True
                log(f"repository ditandatangani dengan kunci {fingerprint}")

    log(f"{len(debs)} paket, {len(architectures)} arsitektur, output {output}")
    log(f"signature: {'ada' if signed else 'tidak ada'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
