# Repository APT ArashiOS

Dokumen ini menjelaskan arsitektur repository APT ArashiOS yang ditandatangani, pinning,
integrasi ke image, dan kanal rilis.

## 1. Arsitektur

```text
repo/
├── conf/distributions.yaml     konfigurasi aptly
├── keys/
│   ├── arashios-archive-keyring.gpg   kunci publik
│   ├── arashios-archive-keyring.asc   kunci publik format armor
│   ├── arashios-archive.fingerprint   sidik jari kunci
│   └── gnupg/                        kunci privat, tidak pernah masuk image
├── manifest.json                 snapshot paket dan checksum
├── pool -> public/pool           symlink ke pool yang dipublikasikan
└── public/
    ├── dists/stable/
    │   ├── InRelease
    │   ├── Release
    │   ├── Release.gpg
    │   └── main/binary-<arch>/Packages{,.gz}
    └── pool/main/<huruf>/<paket>/<file>.deb
```

## 2. Kunci

| Aspek | Nilai |
|---|---|
| Algoritma | RSA 4096 |
| Pakai | Penandatanganan repository saja |
| Masa berlaku | 3 tahun |
| Kunci privat | `repo/keys/gnupg`, tidak pernah masuk image |
| Kunci publik | Dikemas sebagai `arashios-repo-keyring` |
| Verifikasi | `gpgv` dan apt-secure |

Rotasi kunci dijelaskan di [KEY-ROTATION.md](KEY-ROTATION.md).

## 3. Build repository

```bash
# Kunci pengembangan, sekali saja
./scripts/generate-repo-key.sh

# Bangun paket lalu repository
python3 scripts/build-packages.py --all
python3 scripts/build-repo.py --packages build/packages --output repo/public --sign
```

Hasil build:

1. Pool paket disalin ke `repo/public/pool/main/<huruf>/<paket>/`.
2. Indeks `Packages` ditulis untuk amd64, arm64, dan i386.
3. `Release` memuat checksum MD5, SHA-1, dan SHA-256.
4. `InRelease` dan `Release.gpg` dibuat bila kunci tersedia.

Verifikasi:

```bash
gpgv --keyring repo/keys/arashios-archive-keyring.gpg \
    repo/public/dists/stable/InRelease
```

## 4. Integrasi ke image

`build.sh` membangun paket dan repository lokal pada setiap build, lalu
menyalin seluruh `.deb` ke `config/packages.chroot` sehingga live-build
memasangnya tanpa jaringan.

Entrypoint repository untuk sistem terpasang berasal dari
`/etc/apt/sources.list.d/arashios.sources` dan hanya diaktifkan bila
`REPO_ENABLED=1` pada `versions.env`. Nilai bawaannya 0 karena domain final
belum dipublikasikan.

```text
Types: deb
URIs: https://repo.arashios.example
Suites: stable
Components: main
Architectures: amd64 arm64 i386
Signed-By: /usr/share/keyrings/arashios-archive-keyring.gpg
```

## 5. Pinning

| Repository | Prioritas | Berkas |
|---|---|---|
| ArashiOS stable | 500 | `arashios-archive` |
| Debian bookworm | 500 | bawaan Debian |
| Debian security | 500 | bawaan Debian |
| Debian backports | 100 | `arashios-backports` |

Backports hanya boleh dipakai oleh kernel dan Go:

```text
Package: linux-image-* linux-headers-* linux-modules-* golang* golang-*
Pin: release n=bookworm-backports
Pin-Priority: 500
```

Paket lain tetap memakai priority 100 sehingga tidak menimpa stable.

## 6. Kanal rilis

| Kanal | Frekuensi | Suite | Dukungan |
|---|---|---|---|
| stable | 4 minggu | stable | 12 bulan |
| edge | 1 minggu | edge | 6 bulan |
| nightly | Harian | nightly | tanpa dukungan |

Setiap kanal memakai repository terpisah dan kunci yang sama. Paket yang
dihapus dari kanal diumumkan pada release notes.

## 7. Snapshot

```bash
python3 scripts/snapshot-manifest.py
python3 scripts/snapshot-manifest.py --check
```

Manifest mencatat versi rilis, fingerprint kunci, hash konfigurasi, dan
checksum setiap paket. Manifest menjadi acuan rebuild dan jalur upgrade.

## 8. Jalur upgrade

```bash
./tests/upgrade-path.sh
```

Pemeriksaan membang paket pada dua versi rilis, memastikan versi baru selalu
lebih tinggi, memastikan isi paket berubah, memastikan changelog memuat entri
rilis, dan memulihkan state build.

## 9. Pemeriksaan

```bash
python3 scripts/check-packages.py
python3 scripts/snapshot-manifest.py --check
./tests/upgrade-path.sh
```

## 10. Batasan saat ini

1. Repository belum diunggah ke mirror publik dan domain final belum ditetapkan.
2. `apt update` dan `apt upgrade` belum diuji pada image karena image belum
   dibangun.
3. aptly belum dipakai. Builder Python menghasilkan struktur yang sama dengan
   keluaran aptly, dan konfigurasi aptly tersedia di `repo/conf`.
4. Kunci yang dibuat di host ini adalah kunci pengembangan tanpa passphrase.
