#!/usr/bin/env bash
# Boot an ArashiOS ISO in QEMU and capture a screenshot plus serial log.
# Usage: ./tests/qemu-boot.sh <iso> [uefi|bios] [timeout_seconds] [--keep]
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISO=""
MODE="uefi"
TIMEOUT=120
KEEP=0
QEMU_PID=""
TMP=""

usage() {
    cat <<EOF
Pemakaian: $0 <iso> [uefi|bios] [timeout] [--keep]

  uefi    Boot dengan firmware OVMF. Default.
  bios    Boot dengan firmware SeaBIOS.
  timeout Detik sebelum screenshot diambil. Default: 120.
  --keep  Simpan direktori sementara untuk debugging.
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

log() {
    printf '[qemu] %s\n' "$*"
}

cleanup() {
    if [ -n "$QEMU_PID" ] && kill -0 "$QEMU_PID" 2>/dev/null; then
        kill "$QEMU_PID" 2>/dev/null || true
        wait "$QEMU_PID" 2>/dev/null || true
    fi
    if [ -n "$TMP" ] && [ -d "$TMP" ]; then
        if [ "$KEEP" -eq 1 ]; then
            printf '[qemu] Direktori sementara: %s\n' "$TMP"
        else
            rm -rf "$TMP"
        fi
    fi
}
trap cleanup EXIT INT TERM

positional=()
for arg in "$@"; do
    case "$arg" in
        --keep) KEEP=1 ;;
        -h|--help) usage; exit 0 ;;
        *) positional+=("$arg") ;;
    esac
done
[ "${#positional[@]}" -ge 1 ] || { usage; exit 2; }
ISO="${positional[0]}"
[ "${#positional[@]}" -ge 2 ] && MODE="${positional[1]}"
[ "${#positional[@]}" -ge 3 ] && TIMEOUT="${positional[2]}"

[ -f "$ISO" ] || die "ISO tidak ditemukan: $ISO"
ISO="$(readlink -f "$ISO")"
case "$MODE" in uefi|bios) ;; *) die "Mode harus uefi atau bios: $MODE" ;; esac
case "$TIMEOUT" in ''|*[!0-9]*) die "Timeout harus bilangan bulat." ;; esac
[ "$TIMEOUT" -ge 20 ] || die "Timeout minimal 20 detik."

base="$(basename "$ISO")"
case "$base" in
    ArashiOS-amd64-*) ARCH="amd64" ;;
    ArashiOS-i386-*) ARCH="i386" ;;
    ArashiOS-arm64-*) ARCH="arm64" ;;
    *) die "Nama ISO tidak dikenali: $base" ;;
esac

[ "$ARCH" != "arm64" ] || die "Boot test arm64 belum diimplementasikan pada Fase 1."

QEMU="$(command -v qemu-system-x86_64 || true)"
[ -n "$QEMU" ] || die "qemu-system-x86_64 tidak ditemukan. Jalankan scripts/check-env.sh."
command -v python3 >/dev/null 2>&1 || die "python3 tidak ditemukan."

if [ "$MODE" = "uefi" ]; then
    [ "$ARCH" != "i386" ] || die "UEFI i386 tidak didukung pada Fase 1. Gunakan mode bios."
    OVMF_CODE=""
    OVMF_VARS=""
    for pair in \
        "/usr/share/OVMF/OVMF_CODE_4M.fd:/usr/share/OVMF/OVMF_VARS_4M.fd" \
        "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd" \
        "/usr/share/edk2/ovmf/OVMF_CODE.fd:/usr/share/edk2/ovmf/OVMF_VARS.fd"; do
        code="${pair%%:*}"
        vars="${pair##*:}"
        if [ -f "$code" ] && [ -f "$vars" ]; then
            OVMF_CODE="$code"
            OVMF_VARS="$vars"
            break
        fi
    done
    [ -n "$OVMF_CODE" ] || die "Firmware OVMF tidak ditemukan. Pasang paket ovmf."
fi

mkdir -p /tmp/opencode
TMP="$(mktemp -d /tmp/opencode/arashios-qemu.XXXXXX)"
MON="$TMP/monitor.sock"
SERIAL="$TMP/serial.log"
SHOT="$TMP/boot.ppm"
VARS_COPY="$TMP/OVMF_VARS.fd"

MEMORY=4096
MACHINE="q35"
[ "$ARCH" = "i386" ] && { MEMORY=2048; MACHINE="pc"; }

QEMU_ARGS=(
    -name "ArashiOS-$ARCH-$MODE"
    -machine "$MACHINE"
    -m "$MEMORY"
    -smp 2
    -cdrom "$ISO"
    -boot d
    -vga std
    -display none
    -monitor "unix:$MON,server=on,wait=off"
    -serial "file:$SERIAL"
    -nic none
    -no-reboot
)

if [ "$MODE" = "uefi" ]; then
    cp "$OVMF_VARS" "$VARS_COPY"
    QEMU_ARGS+=(
        -drive "if=pflash,format=raw,readonly=on,file=$OVMF_CODE"
        -drive "if=pflash,format=raw,file=$VARS_COPY"
    )
fi

if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
    QEMU_ARGS+=(-enable-kvm -cpu host)
    log "Akselerasi KVM aktif"
else
    QEMU_ARGS+=(-cpu max)
    log "KVM tidak tersedia, memakai TCG"
fi

log "Boot $base"
log "  mode    : $MODE"
log "  arch    : $ARCH"
log "  timeout : ${TIMEOUT}s"
log "  memory  : ${MEMORY} MiB"

"$QEMU" "${QEMU_ARGS[@]}" >"$TMP/qemu.out" 2>"$TMP/qemu.err" &
QEMU_PID=$!

elapsed=0
while kill -0 "$QEMU_PID" 2>/dev/null && [ "$elapsed" -lt "$TIMEOUT" ]; do
    sleep 2
    elapsed=$((elapsed + 2))
done

if ! kill -0 "$QEMU_PID" 2>/dev/null; then
    wait "$QEMU_PID" || true
    printf '%s\n' '--- qemu.err ---' >&2
    tail -40 "$TMP/qemu.err" >&2 || true
    die "QEMU keluar sebelum timeout."
fi

log "Mengambil screenshot melalui monitor QEMU"
if [ -S "$MON" ]; then
    python3 - "$MON" "$SHOT" <<'PY'
import socket
import sys
import time

monitor, screenshot = sys.argv[1], sys.argv[2]
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect(monitor)
time.sleep(0.5)
sock.sendall(f"screendump {screenshot}\n".encode())
time.sleep(2)
sock.sendall(b"quit\n")
time.sleep(0.5)
sock.close()
PY
else
    kill "$QEMU_PID" 2>/dev/null || true
    die "Socket monitor QEMU tidak tersedia."
fi

for _ in $(seq 1 10); do
    kill -0 "$QEMU_PID" 2>/dev/null || break
    sleep 1
done
if kill -0 "$QEMU_PID" 2>/dev/null; then
    kill "$QEMU_PID" 2>/dev/null || true
fi
wait "$QEMU_PID" 2>/dev/null || true
QEMU_PID=""

[ -s "$SHOT" ] || die "Screenshot tidak dihasilkan."

if grep -Eiq 'Kernel panic|No bootable device|Failed to load image|not a valid ISO' "$SERIAL" 2>/dev/null; then
    printf '%s\n' '--- serial.log ---' >&2
    tail -60 "$SERIAL" >&2 || true
    die "Log serial menunjukkan kegagalan boot."
fi

python3 - "$SHOT" <<'PY'
import sys

path = sys.argv[1]
data = open(path, "rb").read()
if not data.startswith(b"P6"):
    raise SystemExit("screenshot bukan PPM P6")

index = 2
tokens = []
while len(tokens) < 3:
    while index < len(data) and data[index : index + 1].isspace():
        index += 1
    if data[index : index + 1] == b"#":
        while index < len(data) and data[index : index + 1] != b"\n":
            index += 1
        continue
    start = index
    while index < len(data) and not data[index : index + 1].isspace():
        index += 1
    tokens.append(int(data[start:index]))
index += 1
width, height, maxval = tokens
pixels = data[index:]
if len(pixels) < width * height * 3:
    raise SystemExit("data PPM tidak lengkap")
bright = 0
total = 0
maximum = 0
for offset in range(0, len(pixels) - 2, 21):
    value = max(pixels[offset], pixels[offset + 1], pixels[offset + 2])
    total += 1
    if value > 40:
        bright += 1
    maximum = max(maximum, value)
ratio = bright / max(total, 1)
print(f"[qemu] screenshot {width}x{height}, rasio terang {ratio:.3f}, nilai maksimum {maximum}")
if maximum < 80:
    raise SystemExit("layar tampak gelap total")
if ratio < 0.001:
    raise SystemExit("layar tampak kosong")
PY

mkdir -p "$ROOT/out"
cp "$SHOT" "$ROOT/out/qemu-${ARCH}-${MODE}.ppm"
[ -f "$SERIAL" ] && cp "$SERIAL" "$ROOT/out/qemu-${ARCH}-${MODE}.log"

log "Screenshot: $ROOT/out/qemu-${ARCH}-${MODE}.ppm"
log "Serial    : $ROOT/out/qemu-${ARCH}-${MODE}.log"
log "Boot test lulus."
