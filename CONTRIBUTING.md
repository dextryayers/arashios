# Contributing to ArashiOS

## Prinsip

1. Perubahan kecil dan terfokus lebih mudah direview.
2. Setiap perubahan harus dapat diuji.
3. Setiap klaim performa harus punya angka.
4. Tidak ada em dash atau en dash di dokumen.
5. Tidak ada telemetry atau panggilan jaringan tersembunyi.

## Alur Kontribusi

1. Buka issue atau diskusi sebelum perubahan besar.
2. Fork repository dan buat branch fitur.
3. Tulis kode, test, dan dokumentasi.
4. Jalankan `make lint` dan test terkait.
5. Buat pull request dengan deskripsi dan bukti uji.
6. Sertakan screenshot untuk perubahan visual.
7. Tunggu review minimal satu maintainer.

## Branch

| Branch | Fungsi |
|---|---|
| main | Pengembangan utama |
| release/vX.YY.ZZ | Stabilisasi rilis |
| feat/nama | Fitur |
| fix/nama | Perbaikan |
| docs/nama | Dokumentasi |

## Commit

Gunakan Conventional Commits:

```
feat(build): tambah dukungan snapshot Debian
fix(theme): perbaiki kontras tombol primer
docs(adr): catat keputusan podman rootless
test(qemu): tambah uji boot UEFI
```

Setiap commit wajib menyertakan Developer Certificate of Origin:

```
Signed-off-by: Nama <email@example.com>
```

Gunakan `git commit -s`.

## Gaya Kode

### Shell

1. `#!/usr/bin/env bash`
2. `set -Eeuo pipefail`
3. Quote variabel kecuali ada alasan.
4. Fungsi `die` dan `log` untuk pesan.
5. shellcheck bersih.

### Python

1. Python 3.11.
2. Hanya standard library untuk skrip build.
3. Format 4 spasi.
4. Tidak ada dependensi eksternal tanpa diskusi.

### Dokumen

1. Bahasa Indonesia atau Inggris.
2. Tanpa emoji.
3. Tanpa em dash dan en dash.
4. Tabel untuk spesifikasi.
5. Setiap persyaratan punya ID.

## Review

1. Satu approval untuk perubahan biasa.
2. Dua approval untuk build, paket, dan keamanan.
3. Perubahan visual menyertakan screenshot before dan after.
4. Perubahan dokumen menjalankan `scripts/check-docs.sh`.
5. Perubahan tema menjalankan `scripts/generate-tokens.py --check`.

## Lisensi

Dengan berkontribusi, Anda menyetujui lisensi berikut:

| Komponen | Lisensi |
|---|---|
| Kode | GPL-3.0-or-later |
| Aset visual | CC-BY-SA-4.0 |
| Dokumentasi | CC-BY-4.0 |
