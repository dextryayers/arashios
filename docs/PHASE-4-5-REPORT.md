# Laporan Fase 4 dan Fase 5

Status: implementasi statis selesai. Exit gate runtime belum lulus karena ISO
belum dapat dibangun pada host ini.

Tanggal: 2026-10-22

## 1. Ringkasan

Fase 4 membangun toolstack keamanan yang dapat diaudit: katalog 215 entri,
manifest per tool, sumber upstream terkunci, Arsenal, harness smoke test,
wordlist, dan container lab dengan digest terkunci.

Fase 5 membangun lingkungan coding: toolchain user level dengan lock
checksum, template proyek untuk tujuh jenis proyek, template container
rootless, harness hello world untuk sepuluh bahasa, dan dokumentasi offline.

Yang belum ada:

1. Artefak binary tool tier 1 dan `artifact.sha256` pada manifest.
2. Image ISO dan boot UEFI serta BIOS.
3. Eksekusi smoke test toolstack pada image.
4. Login desktop dan pengujian VSCodium.
5. Penarikan image container lab.

## 2. Sub-fase Fase 4

### 4.1 Taksonomi dan manifest

| Item | Hasil |
|---|---|
| Katalog sumber | `tools/catalog.yaml`, 215 entri |
| Pin sumber | `tools/source-pins.yaml`, 41 tool tier 1 |
| Manifest | `vendor/manifests/`, 215 berkas YAML dan satu index |
| Katalog runtime | `config/common/includes.chroot/usr/share/arashios/toolstack/catalog.json` |
| Skema | tier, alur kerja, lisensi, arsitektur, build, install, test |

Tier yang dipakai:

| Tier | Jumlah | Distribusi |
|---|---:|---|
| T0 | 159 | image ISO, paket Debian bookworm |
| T1 | 41 | image ISO, binary hasil build dari commit terkunci |
| T2 | 10 | unduhan pengguna, tidak masuk image |
| T3 | 5 | container image dengan digest |

### 4.2 Instalasi T0

Daftar keamanan berada di `config/common/package-lists/20-security.list.chroot`
dengan 88 paket khusus keamanan. Paket toolchain dan harian tetap berada di
daftar miliknya masing-masing sehingga tidak ada paket duplikat.

Seluruh paket diverifikasi tersedia di bookworm untuk amd64, arm64, dan i386.
Paket `ltrace` dan `thermald` hanya ada pada amd64 dan i386 dan berada di
overlay arsitektur.

Alur kerja yang dilayani:

| Alur kerja | Tool T0 | Tool T1 |
|---|---|---|
| WF-01 Reconnaissance | 34 | 7 |
| WF-02 Web testing | 11 | 10 |
| WF-03 Exploitation | 3 | 2 |
| WF-04 Password attack | 6 | 1 |
| WF-05 Active Directory | 5 | 6 |
| WF-06 Wireless | 7 | 1 |
| WF-07 Network interception | 7 | 2 |
| WF-08 Pivoting | 4 | 2 |
| WF-09 Forensics | 13 | 1 |
| WF-10 Reverse engineering | 8 | 8 |
| WF-11 Cloud dan container | 12 | 2 |
| WF-12 Reporting | 5 | 1 |

### 4.3 Vendor T1

Sumber upstream dikunci pada tag dan commit untuk 41 tool. Contoh:

| Tool | Versi | Commit | Lisensi |
|---|---|---|---|
| nuclei | 3.11.1 | a8c88feb4a1c8e961b7902534ce3af97e9d524a4 | MIT |
| netexec | 1.5.1 | c7dc286ba65daf10402cdc470e531b84e6d3d911 | BSD-2-Clause |
| metasploit-framework | 4.11.7 | d1dde11225376661c484f394d554457c8f475974 | BSD-3-Clause |
| radare2 | 6.2.4 | 485e5e205b190fc297a2a95a6f982ff5d9f54039 | LGPL-3.0-only |
| volatility3 | 2.28.2 | 881e970121c16f0932fb9d16fbd5fb258cbcbf75 | VSL |
| kismet | 2025.09 | 7a3b5d207e6b15d7dcbb8fa916e121e51d3280e0 | GPL-3.0-only |

Pipeline build tersedia di `scripts/build-vendor-tools.sh`. Skrip mengkloning
sumber, memverifikasi commit checkout, menjalankan build sesuai manifest, lalu
mencatat hash artefak di `vendor/artifacts.lock.json`.

### 4.4 Audit glibc

`scripts/check-glibc.py` memeriksa simbol glibc pada binary hasil build dan
menolak simbol di atas 2.36. Binary statis, termasuk binary Go, lolos tanpa
pemeriksaan simbol. Audit berjalan otomatis pada akhir pipeline vendor.

### 4.5 Wordlist

| Berkas | Entri | Bytes |
|---|---:|---:|
| common-paths.txt | 129 | 961 |
| common-subdomains.txt | 129 | 872 |
| common-passwords.txt | 84 | 819 |
| common-parameters.txt | 68 | 544 |
| common-usernames.txt | 60 | 515 |
| detection-payloads.txt | 29 | 552 |

Total 4263 byte, jauh di bawah batas 10 MiB. Lisensi CC-BY-SA-4.0, checksum
dicatat di `manifest.json`, dan tiap berkas memiliki komentar sumber.

### 4.6 Arsenal

`arashios-arsenal` menyediakan `list`, `info`, `workflows`, `verify`,
`install`, `remove`, `doctor`, dan `smoke`. Perilaku per tier sudah diuji pada
lingkungan sandbox. Tool T2 tidak pernah dipasang otomatis. Tool T3 diarahkan
ke `arashios-lab`. `remove` hanya menghapus berkas yang tercatat pada state
Arsenal.

### 4.7 Container T3

Empat lab terdaftar dengan digest terkunci: dvwa, debian-base, kali-rolling,
dan juice-shop. Image tanpa digest ditolak. Semua container berjalan tanpa
mode privileged dan tanpa akses jaringan host.

### 4.8 Smoke test

`arashios-tool-smoke` menjalankan smoke test per tool tanpa jaringan dan
menulis laporan JSON. Harness memakai katalog yang dapat diarahkan sehingga
perilaku dapat diuji pada host build.

### 4.9 Audit lisensi

`docs/LICENSES.md` mencatat 41 tool tier 1 beserta lisensi dan sumbernya.
`scripts/check-licenses.py` memeriksa bahwa tool proprietary tidak pernah
masuk image, bahwa NOTICE mencantumkan atribusi pihak ketiga, dan bahwa
dokumentasi lisensi selalu sinkron dengan katalog.

### 4.10 Kebijakan update

Dokumen `docs/TOOLSTACK.md` mencatat sumber, SLA, dan aturan pembaruan untuk
setiap tier beserta konsekuensi CVE.

## 3. Sub-fase Fase 5

### 5.1 Toolchain bahasa

Sembilan komponen toolchain user level dikunci pada versi dan checksum:

| Komponen | Versi | Peran | Checksum sumber |
|---|---|---|---|
| uv | 0.13.4 | python | upstream |
| fnm | 1.39.0 | node | dihitung lokal |
| node | 22 | node | dikelola fnm |
| rustup | 1.28.2 | rust | upstream |
| rust | stable | rust | dikelola rustup |
| go | 1.27.3 | go | indeks resmi Go |
| starship | 1.27.0 | shell | upstream |
| eza | 0.23.5 | shell | dihitung lokal |
| vscodium | 1.140.06880 | editor | upstream |

Checksum tersedia untuk amd64, arm64, dan i386 pada komponen yang mendukung
ketiganya. Installer memverifikasi checksum, menolak arsip yang mencoba keluar
dari direktori target, dan tidak menimpa berkas lain di `~/.local/bin`.

### 5.2 Editor

Konfigurasi Neovim tetap dipakai sebagai editor bawaan dan tidak membutuhkan
plugin manager. VSCodium disediakan sebagai toolchain user level dengan
pengaturan telemetry dimatikan.

### 5.3 Container

Template `base`, `python`, `go`, `rust`, `node`, dan `security` memakai image
dasar dengan digest terkunci. Perintah `arashios-container` membangun image,
menjalankannya secara rootless, dan memeriksa kesiapan container.

### 5.4 CLI

Konfigurasi Zsh, tmux, ripgrep, bat, dan Neovim dipertahankan. Prompt
Starship memakai palet Kage dan aktif bila Starship terpasang.

### 5.5 Dotfiles

Skeleton di `/etc/skel` diperluas dengan preferensi container dan validasi
startup shell. Rata-rata startup shell Zsh pada host pengembangan 10 ms
dengan batas pemeriksaan 1200 ms dan target rilis 300 ms.

### 5.6 Version manager

`uv`, `fnm`, dan `rustup` dipasang sebagai toolchain user level. Semua
dapat dilepas tanpa sudo.

### 5.7 Template proyek

Tujuh template tersedia: python, go, rust, node, c, java, dan security-report.
Template dirender tanpa placeholder tersisa dan tidak menimpa direktori yang
sudah berisi berkas.

### 5.8 Dokumentasi offline

`arashios-help` menyediakan sepuluh topik dari dokumen yang dibundel di
`/usr/share/doc/arashios`.

### 5.9 Smoke test

`arashios-coding-smoke` menguji sepuluh bahasa. Pada host pengembangan enam
bahasa lulus dan empat dilewati karena kompilatornya tidak terpasang:

| Bahasa | Status host | Toolchain ISO |
|---|---|---|
| Python | lulus | 3.11 |
| Go | lulus | 1.19 sistem, 1.27.3 user level |
| Rust | lulus | 1.63 sistem, stabil user level |
| C | lulus | GCC 12 |
| C++ | lulus | GCC 12 |
| Node.js | lulus | 18 sistem, 22 user level |
| Java | dilewati | OpenJDK 17 |
| PHP | dilewati | php-cli 8.2 |
| Ruby | dilewati | ruby-full 3.1 |
| Lua | dilewati | lua5.4 |

## 4. Hasil Verifikasi

### 4.1 Pemeriksaan Statis

| Pemeriksaan | Hasil |
|---|---|
| Katalog toolstack dan manifest | 6705 pemeriksaan lulus |
| Wordlist dan checksum | 31 pemeriksaan lulus |
| Metadata lisensi | 156 pemeriksaan lulus |
| Katalog runtime toolstack | sinkron |
| Katalog runtime toolchain | sinkron |
| Lock checksum toolchain | lengkap untuk 9 komponen dan 3 arsitektur |
| Validasi konfigurasi live-build | lulus |
| Toolstack dan Arsenal | lulus |
| Lingkungan coding | lulus |
| ShellCheck, bash -n, py_compile | lulus |

### 4.2 Ketersediaan Paket Bookworm

Audit nama paket terhadap indeks bookworm amd64, arm64, dan i386 pada
main, contrib, non-free, dan non-free-firmware:

| Arsitektur | Paket unik | Hilang |
|---|---:|---:|
| amd64 | 313 | 0 |
| arm64 | 313 | 0 |
| i386 | 313 | 0 |

`ltrace` dan `thermald` hanya tersedia di amd64 dan i386 dan berada di overlay
arsitektur.

### 4.3 Dry Run Live-Build

Dry run ulang dijalankan untuk tujuh kombinasi setelah penambahan toolstack
dan toolchain. Hasil akhir tercatat pada [PHASE-2-3-REPORT.md](PHASE-2-3-REPORT.md)
dan appendix matriks.

### 4.4 Perintah

```bash
./scripts/check-toolstack.py
./scripts/check-wordlists.py
./scripts/check-licenses.py
./scripts/generate-toolstack.py --check
./scripts/generate-toolchain.py --check
./scripts/refresh-toolchain-lock.py --check
./tests/toolstack.sh
./tests/coding.sh
make lint
```

## 5. Penyimpangan dan Risiko

1. Artefak binary tier 1 belum dibangun sehingga `artifact.sha256` pada
   manifest masih kosong dan statusnya `source-locked`.
2. Smoke test tool只能在 image yang sudah dibangun dijalankan.
3. Image lab juice-shop belum memiliki digest terkunci dan ditolak sampai
   digest tersedia.
4. Host pengembangan tidak memasang Podman sehingga diagnosis container
   menandai masalah yang belum dapat diuji.
5. Empat bahasa dilewati pada smoke test karena kompilatornya tidak tersedia
   pada host.
6. Benchmark startup shell dijalankan pada host LMDE, bukan pada image
   bookworm.
7. Toolchain user level belum pernah dipasang dari jaringan pada host ini
   karena build image belum tersedia.
8. README dan CHANGELOG memakai nama tool yang berbeda dari nama paket Debian
   untuk beberapa paket, misalnya `fd-find` dan `bat`.

## 6. Exit Gate Runtime

Fase 4 dan Fase 5 belum dapat ditutup sampai:

1. ISO amd64 dibangun dan checksum diverifikasi.
2. Boot UEFI dan BIOS berhasil pada QEMU.
3. `arashios-arsenal list` dan `arashios-tool-smoke --tier T0` lulus di image.
4. `arashios-coding-smoke` lulus untuk enam bahasa di image.
5. `arashios-container doctor` melaporkan rootless aktif.
6. `arashios-toolchain install uv` selesai tanpa sudo dan checksum cocok.
7. `arashios-new-project create` menghasilkan proyek yang bisa dikompilasi.
8. VSCodium berjalan pada sesi desktop nyata.
9. Artefak tier 1 dibangun dan `artifact.sha256` terisi.
10. Audit glibc lulus untuk seluruh artefak tier 1.
11. Image lab ditarik dengan digest terkunci dan berjalan.
12. Waktu boot, RAM, dan ukuran ISO diukur.

## 7. Langkah Berikutnya

1. Pasang toolchain ISO lengkap pada host Debian 12.
2. Bangun ISO amd64 Cinnamon.
3. Jalankan smoke test runtime termasuk bagian toolstack dan coding.
4. Bangun artefak tier 1 pada host build dan isi `artifact.sha256`.
5. Jalankan audit glibc pada artefak baru.
6. Uji toolchain user level dari dalam image.
7. Ambil screenshot desktop dan arsipkan laporan smoke test.
8. Lanjutkan ke Fase 6 setelah exit gate runtime Fase 4 dan Fase 5 lulus.
