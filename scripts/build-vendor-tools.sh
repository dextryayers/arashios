#!/usr/bin/env bash
# Build ArashiOS tier 1 vendor tools from pinned upstream sources.
#
# The script clones the pinned commit, verifies the commit hash, runs the build
# command from the tool manifest, and records the SHA-256 of the produced
# artifact in vendor/artifacts.lock.json.
#
# Usage:
#   scripts/build-vendor-tools.sh --tool nuclei --arch amd64
#   scripts/build-vendor-tools.sh --all --arch amd64
#   scripts/build-vendor-tools.sh --list
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="$ROOT/vendor/cache"
BUILD_ROOT="$ROOT/vendor/build"
LOCK="$ROOT/vendor/artifacts.lock.json"

TOOL=""
ALL=0
ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m)"
LIST=0
DRY_RUN=0

usage() {
    cat <<EOF
Pemakaian: $0 [opsi]

Opsi:
  --tool NAME  Bangun satu tool tier 1.
  --all        Bangun semua tool tier 1 yang punya build command.
  --arch ARCH  Arsitektur target. Default: arsitektur host.
  --list       Tampilkan tool tier 1 yang tersedia.
  --dry-run    Tampilkan rencana tanpa menjalankan build.
  -h, --help   Tampilkan bantuan ini.
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

log() {
    printf '[vendor] %s\n' "$*"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --tool) TOOL="${2:-}"; shift 2 ;;
        --all) ALL=1; shift ;;
        --arch) ARCH="${2:-}"; shift 2 ;;
        --list) LIST=1; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) die "Argumen tidak dikenal: $1" ;;
    esac
done

manifest_field() {
    local file="$1" key="$2"
    python3 - "$file" "$key" <<'PY'
import sys
import yaml
path, key = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as handle:
    data = yaml.safe_load(handle)
value = data.get(key, "")
if isinstance(value, (dict, list)):
    import json
    print(json.dumps(value))
else:
    print(value)
PY
}

if [ "$LIST" -eq 1 ]; then
    for file in "$ROOT"/vendor/manifests/*.yaml; do
        name="$(basename "$file" .yaml)"
        [ "$name" = "index" ] && continue
        tier="$(manifest_field "$file" tier)"
        [ "$tier" = "T1" ] || continue
        version="$(manifest_field "$file" version)"
        printf '%-22s %s\n' "$name" "$version"
    done
    exit 0
fi

[ -n "$TOOL" ] || [ "$ALL" -eq 1 ] || die "Pilih --tool NAME atau --all."

if [ "$ALL" -eq 1 ]; then
    TOOLS=()
    for file in "$ROOT"/vendor/manifests/*.yaml; do
        name="$(basename "$file" .yaml)"
        [ "$name" = "index" ] && continue
        tier="$(manifest_field "$file" tier)"
        [ "$tier" = "T1" ] || continue
        TOOLS+=("$name")
    done
else
    TOOLS=("$TOOL")
fi

command -v python3 >/dev/null 2>&1 || die "python3 tidak ditemukan."
command -v git >/dev/null 2>&1 || die "git tidak ditemukan."

mkdir -p "$CACHE" "$BUILD_ROOT"

lock_update() {
    local name="$1" arch="$2" path="$3" digest="$4"
    python3 - "$LOCK" "$name" "$arch" "$path" "$digest" <<'PY'
import json
import os
import sys
lock_path, name, arch, path, digest = sys.argv[1:6]
data = {"schema_version": 1, "artifacts": {}}
if os.path.isfile(lock_path):
    with open(lock_path, encoding="utf-8") as handle:
        data = json.load(handle)
data.setdefault("artifacts", {}).setdefault(name, {})[arch] = {
    "path": path,
    "sha256": digest,
}
with open(lock_path, "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2, sort_keys=True)
    handle.write("\n")
PY
}

for name in "${TOOLS[@]}"; do
    manifest="$ROOT/vendor/manifests/$name.yaml"
    [ -f "$manifest" ] || die "Manifest tidak ditemukan: $name"

    source_url="$(manifest_field "$manifest" source)"
    source_ref="$(manifest_field "$manifest" source_ref)"
    source_commit="$(manifest_field "$manifest" source_commit)"
    build_kind="$(python3 -c "
import sys, yaml
with open('$manifest', encoding='utf-8') as handle:
    print(yaml.safe_load(handle).get('build', {}).get('kind', ''))
")"
    build_command="$(python3 -c "
import sys, yaml
with open('$manifest', encoding='utf-8') as handle:
    print(yaml.safe_load(handle).get('build', {}).get('command', ''))
")"
    install_path="$(python3 -c "
import sys, yaml
with open('$manifest', encoding='utf-8') as handle:
    print(yaml.safe_load(handle).get('install', {}).get('path', ''))
")"

    if [ -z "$build_command" ]; then
        log "$name dilewati, tidak ada perintah build"
        continue
    fi

    workdir="$BUILD_ROOT/$name-$ARCH"
    log "$name: sumber $source_url ref $source_ref"

    if [ "$DRY_RUN" -eq 1 ]; then
        printf '  clone %s @ %s\n' "$source_url" "$source_commit"
        printf '  build %s\n' "$build_command"
        printf '  install %s\n' "$install_path"
        continue
    fi

    rm -rf "$workdir"
    mkdir -p "$workdir"
    git clone --filter=blob:none --no-checkout "$source_url" "$workdir" >/dev/null
    git -C "$workdir" checkout --detach "$source_commit" >/dev/null
    actual_commit="$(git -C "$workdir" rev-parse HEAD)"
    if [ "$actual_commit" != "$source_commit" ]; then
        die "$name: commit checkout $actual_commit tidak cocok dengan pin $source_commit"
    fi

    case "$build_kind" in
        go)
            command -v go >/dev/null 2>&1 || die "$name: go tidak tersedia di host build"
            CGO_ENABLED=0 GOOS=linux GOARCH="$ARCH" \
                sh -c "cd '$workdir' && $build_command" >/dev/null
            ;;
        python)
            command -v python3 >/dev/null 2>&1 || die "$name: python3 tidak tersedia di host build"
            python3 -m venv "$workdir/venv"
            "$workdir/venv/bin/pip" install --no-deps "$workdir" >/dev/null
            ;;
        ruby)
            command -v gem >/dev/null 2>&1 || die "$name: gem tidak tersedia di host build"
            gem build "$workdir" >/dev/null
            ;;
        java|source|data)
            log "$name: build manual diperlukan, lihat manifest"
            continue
            ;;
        *)
            log "$name: build kind $build_kind belum didukung"
            continue
            ;;
    esac

    artifact="$workdir/${name}"
    if [ ! -f "$artifact" ]; then
        artifact="$(find "$workdir" -maxdepth 2 -type f -name "$name" -print -quit || true)"
    fi
    [ -n "$artifact" ] && [ -f "$artifact" ] || die "$name: artefak tidak ditemukan setelah build"

    digest="$(sha256sum "$artifact" | cut -d' ' -f1)"
    log "$name: artefak $artifact sha256 $digest"
    lock_update "$name" "$ARCH" "$artifact" "$digest"

    python3 "$ROOT/scripts/check-glibc.py" "$artifact" --max-glibc "2.36" || true
done

log "Selesai. Lock artefak: $LOCK"
