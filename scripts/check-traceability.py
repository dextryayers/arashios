#!/usr/bin/env python3
"""Validate requirement and test traceability in plan.md."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "plan.md"

REQUIREMENT_RE = re.compile(
    r"^\| ((?:FR|SR|PR|UX|CR)-\d{3}) \| (.+?) \| (.+?) \| (.+?) \|$"
)
TRACE_RE = re.compile(
    r"^\| ((?:FR|SR|PR|UX|CR)-\d{3}(?:\.\.\d{3})?) \| (.*?) \| (.*?) \|$"
)
TEST_DEF_RE = re.compile(r"^\| (T-[A-Z]+-\d{2}) \|")
TEST_REF_RE = re.compile(r"(T-[A-Z]+-)(\d{2})(?:\.\.(\d{2}))?")


def expand_range(value: str) -> list[str]:
    if ".." not in value:
        return [value]
    prefix, numbers = value.split("..", 1)
    base, start = prefix.rsplit("-", 1)
    end = numbers
    width = len(start)
    return [f"{base}-{number:0{width}d}" for number in range(int(start), int(end) + 1)]


def expand_test_refs(value: str) -> list[str]:
    refs: list[str] = []
    for match in TEST_REF_RE.finditer(value):
        prefix, start, end = match.groups()
        if end is None:
            refs.append(f"{prefix}{start}")
        else:
            refs.extend(f"{prefix}{number:02d}" for number in range(int(start), int(end) + 1))
    return refs


def main() -> int:
    if not PLAN.is_file():
        print(f"ERROR: {PLAN} tidak ditemukan", file=sys.stderr)
        return 1

    text = PLAN.read_text(encoding="utf-8")
    requirements: dict[str, tuple[str, str, str]] = {}
    tests: set[str] = set()
    trace_rows: list[tuple[str, str, str]] = []

    for line in text.splitlines():
        requirement_match = REQUIREMENT_RE.match(line)
        if requirement_match:
            req_id, need, acceptance, phase = requirement_match.groups()
            if req_id in requirements:
                print(f"ERROR: requirement duplikat: {req_id}", file=sys.stderr)
                return 1
            requirements[req_id] = (need.strip(), acceptance.strip(), phase.strip())
            continue

        test_match = TEST_DEF_RE.match(line)
        if test_match:
            tests.add(test_match.group(1))
            continue

        trace_match = TRACE_RE.match(line)
        if trace_match:
            trace_rows.append(trace_match.groups())

    if not requirements:
        print("ERROR: tidak ada requirement yang ditemukan di plan.md", file=sys.stderr)
        return 1
    if not tests:
        print("ERROR: tidak ada test case yang ditemukan di plan.md", file=sys.stderr)
        return 1
    if not trace_rows:
        print("ERROR: tidak ada traceability row yang ditemukan", file=sys.stderr)
        return 1

    errors: list[str] = []
    traced: set[str] = set()
    referenced_tests: set[str] = set()

    for req_range, phase, test_cell in trace_rows:
        req_ids = expand_range(req_range)
        if not phase.strip():
            errors.append(f"{req_range}: kolom fase kosong")
        if not test_cell.strip():
            errors.append(f"{req_range}: kolom test kosong")
        for req_id in req_ids:
            if req_id not in requirements:
                errors.append(f"{req_range}: requirement tidak dikenal: {req_id}")
                continue
            if req_id in traced:
                errors.append(f"{req_id}: traceability duplikat")
            traced.add(req_id)
        for test_id in expand_test_refs(test_cell):
            referenced_tests.add(test_id)
            if test_id not in tests:
                errors.append(f"{req_range}: test tidak dikenal: {test_id}")

    missing = sorted(set(requirements) - traced)
    if missing:
        errors.append("requirement belum ditrace: " + ", ".join(missing))

    if errors:
        print("ERROR: traceability gagal:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    unreferenced = sorted(tests - referenced_tests)
    print(
        f"OK: {len(requirements)} requirement, {len(traced)} traced, "
        f"{len(tests)} test case, {len(referenced_tests)} direferensikan."
    )
    if unreferenced:
        print(f"INFO: {len(unreferenced)} test belum muncul langsung di matriks: "
              f"{', '.join(unreferenced)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
