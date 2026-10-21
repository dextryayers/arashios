#!/usr/bin/env python3
"""Check ArashiOS documentation and text files for project policy violations.

Checks:
  - no em dash or en dash
  - no emoji
  - no banned filler words outside plan.md
  - no TODO, TBD, or FIXME markers
  - every text file ends with a newline
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "build", "out", ".toolchain", "node_modules", "__pycache__", ".venv"}
TEXT_SUFFIXES = {
    ".md",
    ".sh",
    ".py",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".conf",
    ".txt",
    ".svg",
    ".chroot",
    ".desktop",
    ".plymouth",
    ".script",
    ".env",
    ".list",
}
TEXT_NAMES = {"Makefile", "LICENSE", ".gitignore", ".editorconfig", ".gitattributes"}

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\uFE0F\u200D]"
)
SLOP_RE = re.compile(
    r"\b(revolutionary|game[- ]changing|cutting[- ]edge|seamless|unleash|"
    r"empower|robust|leverage|synergy|best[- ]in[- ]class|world[- ]class|"
    r"next[- ]generation|state[- ]of[- ]the[- ]art|effortless|holistic|"
    r"paradigm shift|disruptive|innovative|AI[- ]powered)\b",
    re.IGNORECASE,
)
MARKER_RE = re.compile(r"\b(TODO|TBD|FIXME)\b")


def is_text_file(path: Path) -> bool:
    if path.name in TEXT_NAMES:
        return True
    for suffix in TEXT_SUFFIXES:
        if path.name.endswith(suffix):
            return True
    return False


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if is_text_file(path):
            files.append(path)
    return sorted(files)


def main() -> int:
    errors: list[str] = []
    scanned = 0

    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1
        relative = path.relative_to(ROOT)
        policy_file = relative == Path("scripts/check-docs.py")

        if "\u2014" in text:
            errors.append(f"{relative}: mengandung em dash")
        if "\u2013" in text:
            errors.append(f"{relative}: mengandung en dash")
        if EMOJI_RE.search(text):
            errors.append(f"{relative}: mengandung emoji")
        if not policy_file and MARKER_RE.search(text):
            errors.append(f"{relative}: mengandung TODO, TBD, atau FIXME")
        if not text.endswith("\n"):
            errors.append(f"{relative}: tidak diakhiri newline")
        if not policy_file and relative != Path("plan.md") and SLOP_RE.search(text):
            match = SLOP_RE.search(text)
            errors.append(f"{relative}: kata terlarang '{match.group(0)}'")

    required = [ROOT / "README.md", ROOT / "LICENSE", ROOT / "plan.md"]
    for path in required:
        if not path.is_file():
            errors.append(f"{path.relative_to(ROOT)}: berkas wajib hilang")

    if errors:
        print("ERROR: pemeriksaan dokumen gagal:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(f"OK: {scanned} berkas teks sesuai kebijakan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
