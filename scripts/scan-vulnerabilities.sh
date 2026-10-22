#!/usr/bin/env bash
# Scan the ArashiOS release for known vulnerabilities.
#
# The scan runs every tool that is available on the build host and merges the
# results into one JSON report. Missing tools are reported as skipped so the
# report always states which scanner produced the evidence.
#
# Usage:
#   scripts/scan-vulnerabilities.sh --output build/vulnerability-report.json
#   scripts/scan-vulnerabilities.sh --root build/squashfs-root
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT=""
TARGET=""
THRESHOLD="high"

usage() {
    cat <<'EOF'
Pemakaian: scripts/scan-vulnerabilities.sh [opsi]

Opsi:
  --output FILE   Tulis laporan JSON ke berkas.
  --root DIR      Akar sistem yang dipindai untuk trivy dan grype.
  --threshold N   Severity minimal yang dianggap gagal. Default: high.
  -h, --help      Tampilkan bantuan ini.
EOF
}

log() {
    printf '[vuln] %s\n' "$*"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --output) OUTPUT="${2:-}"; shift 2 ;;
        --root) TARGET="${2:-}"; shift 2 ;;
        --threshold) THRESHOLD="${2:-}"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'ERROR: argumen tidak dikenal: %s\n' "$1" >&2; exit 2 ;;
    esac
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

SCANNERS="[]"
DEBSECAN_STATUS="skipped"
TRIVY_STATUS="skipped"
GRYPE_STATUS="skipped"

if command -v debsecan >/dev/null 2>&1; then
    log "menjalankan debsecan"
    if debsecan --suite bookworm --format json "$TMP/debsecan.json" >/dev/null 2>&1; then
        DEBSECAN_STATUS="ok"
    else
        DEBSECAN_STATUS="failed"
    fi
else
    log "debsecan tidak tersedia"
fi

if command -v trivy >/dev/null 2>&1; then
    log "menjalankan trivy"
    if trivy -q --format json --scanners vuln --output "$TMP/trivy.json" "${TARGET:-rootfs}" >/dev/null 2>&1; then
        TRIVY_STATUS="ok"
    else
        TRIVY_STATUS="failed"
    fi
else
    log "trivy tidak tersedia"
fi

if command -v grype >/dev/null 2>&1; then
    log "menjalankan grype"
    if grype -o json --output "$TMP/grype.json" "${TARGET:-rootfs}" >/dev/null 2>&1; then
        GRYPE_STATUS="ok"
    else
        GRYPE_STATUS="failed"
    fi
else
    log "grype tidak tersedia"
fi

python3 - "$TMP" "$OUTPUT" "$THRESHOLD" "$DEBSECAN_STATUS" "$TRIVY_STATUS" "$GRYPE_STATUS" <<'PY'
import json
import sys
from pathlib import Path

tmp = Path(sys.argv[1])
output = sys.argv[2]
threshold = sys.argv[3]
statuses = {
    "debsecan": sys.argv[4],
    "trivy": sys.argv[5],
    "grype": sys.argv[6],
}

severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
findings = []


def add(source, identifier, severity, package, version, fixed):
    findings.append(
        {
            "source": source,
            "id": identifier,
            "severity": severity.lower(),
            "package": package,
            "version": version,
            "fixed_version": fixed,
        }
    )


debsecan = tmp / "debsecan.json"
if debsecan.is_file():
    try:
        data = json.loads(debsecan.read_text(encoding="utf-8"))
        for key, entries in (data.get("Debian") or {}).items():
            for entry in entries or []:
                add("debsecan", entry.get("CVE", "unknown"), entry.get("urgency", "unknown"),
                    key, entry.get("version", ""), entry.get("fixed_version", ""))
    except (OSError, json.JSONDecodeError):
        pass

trivy = tmp / "trivy.json"
if trivy.is_file():
    try:
        data = json.loads(trivy.read_text(encoding="utf-8"))
        for result in data.get("Results", []):
            for vuln in result.get("Vulnerabilities", []):
                add("trivy", vuln.get("VulnerabilityID", "unknown"),
                    vuln.get("Severity", "unknown"),
                    vuln.get("PkgName", ""), vuln.get("InstalledVersion", ""),
                    vuln.get("FixedVersion", ""))
    except (OSError, json.JSONDecodeError):
        pass

grype = tmp / "grype.json"
if grype.is_file():
    try:
        data = json.loads(grype.read_text(encoding="utf-8"))
        for match in data.get("matches", []):
            vuln = match.get("vulnerability", {})
            art = match.get("artifact", {})
            add("grype", vuln.get("id", "unknown"), vuln.get("severity", "unknown"),
                art.get("name", ""), art.get("version", ""),
                (vuln.get("fix") or {}).get("versions", [""])[0])
    except (OSError, json.JSONDecodeError):
        pass

limit = severity_order.get(threshold, 3)
blocking = [f for f in findings if severity_order.get(f["severity"], 0) >= limit]
counts = {}
for finding in findings:
    counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1

report = {
    "schema_version": 1,
    "threshold": threshold,
    "scanners": statuses,
    "counts": counts,
    "findings": sorted(findings, key=lambda f: (-severity_order.get(f["severity"], 0), f["id"])),
    "blocking": len(blocking),
}
content = json.dumps(report, indent=2, sort_keys=True) + "\n"
if output:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"laporan kerentanan ditulis ke {path}")
else:
    print(content, end="")
print(f"temuan: {len(findings)}, melewati ambang {threshold}: {len(blocking)}")
raise SystemExit(1 if blocking else 0)
PY
