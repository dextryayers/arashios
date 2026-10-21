# Lingkungan Coding ArashiOS

Dokumen ini menjelaskan toolchain, editor, container, template proyek, dan
dokumentasi offline yang disediakan ArashiOS pada Fase 5.

## 1. Prinsip

1. Toolchain user level dipasang tanpa sudo dan tidak merusak paket sistem.
2. Setiap unduhan diverifikasi dengan checksum yang dikunci di
   `toolchains/lock.yaml`.
3. Versi toolchain mengikuti rilis upstream yang tercatat, bukan `latest`.
4. Toolchain sistem Debian tetap tersedia untuk builds offline dan chroot.
5. Container development berjalan rootless tanpa mode privileged.

## 2. Toolchain sistem dan user level

| Komponen | Paket Debian | Versi sistem | Versi user level |
|---|---|---|---|
| Python | python3, python3-pip, pipx | 3.11 | uv 0.13.4 |
| Go | golang | 1.19 | 1.27.3 |
| Rust | rustc, cargo | 1.63 | stabil lewat rustup 1.28.2 |
| Node.js | nodejs, npm | 18 | 22 LTS lewat fnm 1.39.0 |
| Java | openjdk-17-jdk | 17 | 17 |
| C dan C++ | build-essential, clang, cmake, ninja, meson | GCC 12, Clang 14 | sistem |
| PHP | php-cli | 8.2 | sistem |
| Ruby | ruby-full | 3.1 | sistem |
| Lua | lua5.4 | 5.4 | sistem |

Toolchain sistem dipakai untuk Image ISO agar image tetap ramping dan dapat
dibangun tanpa jaringan. Toolchain user level dipasang saat dibutuhkan
pengguna.

## 3. Perintah toolchain

```bash
arashios-toolchain list
arashios-toolchain status --json
arashios-toolchain install uv
arashios-toolchain install node
arashios-toolchain install rust
arashios-toolchain remove uv
arashios-toolchain doctor --json
arashios-toolchain env
```

Aturan:

1. Komponen tanpa checksum terkunci ditolak.
2. Checksum yang tidak cocok menghapus artefak cache dan menghentikan proses.
3. Arsip yang mencoba menulis di luar direktori target ditolak.
4. Tautan absolut di dalam arsip ditolak.
5. Komponen dipasang ke `~/.local/share/arashios/toolchains/<nama>/<versi>`.
6. Biner ditautkan ke `~/.local/bin` tanpa menimpa berkas lain.

## 4. Katalog dan lock

| Berkas | Isi |
|---|---|
| `toolchains/catalog.yaml` | Komponen, peran, URL rilis, dan lisensi |
| `toolchains/lock.yaml` | SHA-256 per komponen dan arsitektur |
| `config/common/includes.chroot/usr/share/arashios/toolchain/catalog.json` | Katalog runtime |

Checksum berasal dari dua sumber. Sumber pertama adalah berkas checksum
yang dipublikasikan upstream, misalnya `uv`, `starship`, `vscodium`, `rustup`,
dan indeks rilis Go. Sumber kedua adalah hitungan lokal atas arsip yang tidak
mempublikasikan checksum, misalnya `fnm` dan `eza`. Lock mencatat asal setiap
nilai pada kolom `origin`.

```bash
python3 scripts/refresh-toolchain-lock.py --cache ~/.cache/arashios/vendor
python3 scripts/refresh-toolchain-lock.py --check
```

## 5. Editor

### Neovim

Konfigurasi bawaan berada di `/etc/skel/.config/nvim/init.lua`. Konfigurasi
memakai palet Kage, leader pada spasi, dan tidak membutuhkan plugin manager
sehingga tetap berfungsi tanpa jaringan.

### VSCodium

VSCodium dipasang sebagai toolchain user level dan tidak memakai telemetry
bawaan. Editor memakai pengaturan privasi berikut:

```json
{
  "telemetry.telemetryLevel": "off",
  "update.mode": "manual"
}
```

## 6. Container

```bash
arashios-container list
arashios-container build python
arashios-container run python --project ~/proyek
arashios-container doctor --json
```

Template yang tersedia:

| Template | Dasar | Kegunaan |
|---|---|---|
| base | debian 12 slim | pengujian umum |
| python | python 3.11 slim | pengembangan Python |
| go | golang 1.23 bookworm | pengembangan Go |
| rust | rust 1.83 bookworm | pengembangan Rust |
| node | node 22 bookworm slim | pengembangan Node.js |
| security | debian 12 slim | audit keamanan |

Semua image dasar dikunci dengan digest. Container dijalankan dengan
`--userns keep-id`, jaringan bridge, dan `no-new-privileges`.

## 7. Template proyek

```bash
arashios-new-project list
arashios-new-project create python ~/proyek/analisis
arashios-new-project create security-report ~/proyek/laporan --name audit-2026
```

| Template | Isi |
|---|---|
| python | pyproject, paket, uji pytest, Makefile |
| go | go.mod, uji bawaan, Makefile |
| rust | Cargo.toml, rust-toolchain, Makefile |
| node | package.json, uji node:test, Makefile |
| c | Makefile, header, uji shell |
| java | Makefile, sumber Java, uji kompilasi |
| security-report | kerangka laporan, Makefile pandoc, CSS |

Semua placeholder seperti `@NAME@` dan `@DATE@` diganti saat pembuatan.
Direktori yang sudah berisi berkas tidak ditimpa tanpa `--force`.

## 8. Smoke test bahasa

```bash
arashios-coding-smoke
arashios-coding-smoke --json --output /tmp/coding.json
```

Bahasa yang diuji adalah Python, Go, Rust, C, C++, Node.js, Java, PHP, Ruby,
dan Lua. Toolchain yang tidak ada dilaporkan sebagai dilewati, bukan gagal.
Exit gate Fase 5 mensyaratkan enam bahasa lulus.

## 9. Dotfiles dan skeleton

Skeleton pengguna berada di `config/common/includes.chroot/etc/skel` dan berisi
konfigurasi Zsh, tmux, Neovim, Git, ripgrep, bat, GTK, Kvantum, terminal, dan
Starship. Prompt memakai palet Kage dan Starship dipakai bila tersedia.

Startup shell diukur pada tiap rilis dengan `time zsh -i -c exit` dan targetnya
300 ms.

## 10. Dokumentasi offline

```bash
arashios-help --list
arashios-help toolstack
arashios-help coding
```

Dokumen yang dibundel: `TOOLSTACK.md`, `CODING.md`, `ARSENAL.md`,
`CONTAINERS.md`, `VENDORING.md`, `LICENSES.md`, `DESKTOP.md`, `LEGAL.md`,
`PRIVACY.md`, `SECURITY.md`, dan `INSTALL.md`.

## 11. Pemeriksaan yang dijalankan

```bash
python3 scripts/generate-toolchain.py --check
python3 scripts/refresh-toolchain-lock.py --check
./tests/coding.sh
```

## 12. Batasan saat ini

1. Toolchain user level belum diuji pada image ISO karena ISO belum dibangun.
2. Java, PHP, Ruby, dan Lua tidak tersedia pada host pengembangan sehingga
   smoke test melompatinya.
3. VSCodium belum diuji pada sesi desktop nyata.
4. Benchmark startup shell dijalankan pada host LMDE, bukan pada image bookworm.
