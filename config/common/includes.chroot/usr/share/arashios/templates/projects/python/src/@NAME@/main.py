"""Titik masuk CLI @NAME@."""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="@NAME@", description="Alat @NAME@")
    parser.add_argument("--version", action="store_true", help="tampilkan versi")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        from @NAME@ import __version__

        print(__version__)
        return 0
    print("@NAME@ siap digunakan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
