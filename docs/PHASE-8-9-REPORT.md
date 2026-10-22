# Laporan Fase 8 dan Fase 9

Status: implementasi statis selesai. Exit gate runtime belum lulus karena ISO
belum dapat dibangun pada host ini.

Tanggal: 2026-10-22

## 1. Ringkasan

Fase 8 memindahkan seluruh kustomisasi ArashiOS ke paket Debian dan repository
APT bertanda tangan. Enam belas paket dibangun secara deterministik, repo
lokal dibuat dengan kunci GPG, integrasi image dan pinning diterapkan, dan
jalur upgrade antar rilis diuji.

Fase 9 membangun lapisan quality assurance: matriks boot, smoke suite dengan
lapisan JSON, checklist hardening, SBOM CycloneDX, penandatanganan artefak,
pemindaian kerentanan, audit kepatuhan, dan pemeriksaan reproduksibilitas.

Yang belum ada:

1. Image ISO sehingga boot, runtime, dan scan CVE belum dijalankan.
2. Repository publik karena domain final belum ditetapkan.
3. Audit jaringan pada sesi live bersih.
4. Checklist hardware tiga mesin.

## 2. Sub-fase Fase 8

### 8.1 Standar packaging

Spesifikasi paket berada di `packages/packages.yaml` dengan 16 paket. Setiap
paket memiliki control, copyright, changelog, dan md5sums. Pemeriksaan
`scripts/check-packages.py` menjalankan 304 pemeriksaan: kelengkapan spesifikasi,
field control, lokasi berkas FHS, timestamp yang seragam, dan indeks repository.

### 8.2 Build paket

`scripts/build-packages.py` membangun 15 paket dan `scripts/build-branding-package.sh`
membangun paket branding. Hasil:

| Paket | Berkas | Ukuran |
|---|---:|---:|
| arashios-branding | 214 | 724608 byte |
| arashios-theme-gtk | 7 | 7684 byte |
| arashios-theme-cinnamon | 6 | 9568 byte |
| arashios-theme-qt | 6 | 11104 byte |
| arashios-theme-xfce | 143 | 9788 byte |
| arashios-theme-openbox | 2 | 2264 byte |
| arashios-icons | 7 | 4808 byte |
| arashios-desktop-common | 23 | 15292 byte |
| arashios-desktop-cinnamon | 3 | 3352 byte |
| arashios-desktop-xfce | 8 | 4440 byte |
| arashios-desktop-lxqt | 8 | 8856 byte |
| arashios-meta-redteam | 0 | 1840 byte |
| arashios-meta-dev | 0 | 1568 byte |
| arashios-meta-daily | 0 | 1624 byte |
| arashios-arsenal | 4 | 19748 byte |
| arashios-repo-keyring | 1 | 2644 byte |

Metapaket memakai daftar paket yang diaudit, sehingga isinya selalu sama
dengan image.

### 8.3 Repository aptly

`scripts/build-repo.py` membuat struktur repository yang sama dengan keluaran
aptly: pool per huruf, indeks `Packages` untuk tiga arsitektur, `Release`
dengan checksum MD5, SHA-1, dan SHA-256, serta `InRelease` dan `Release.gpg`.

Bukti: `gpgv` memverifikasi `InRelease` dengan kunci RSA 4096 dengan fingerprint
`04D3397E795ADB94067D782D3C2CF6464F082804`. Konfigurasi aptly tersedia di
`repo/conf/distributions.yaml`.

`tests/repo-offline.sh` membuktikan jalur secara penuh: repository disalin ke
direktori sementara, `apt update` membacanya memakai keyring archive, `apt`
melihat paket `arashios-arsenal`, indeks dibangun ulang dari pool menghasilkan
daftar paket yang identik dengan indeks yang dipublikasikan, dan pool memuat 16
paket.

### 8.4 Integrasi ISO

`build.sh` membangun paket dan repository lokal pada setiap build, menyalin
seluruh `.deb` ke `config/packages.chroot` agar dipasang tanpa jaringan, dan
menulis `sources.list.d/arashios.sources` bila `REPO_ENABLED=1`. Nilai bawaan
adalah 0 karena domain belum dipublikasikan.

### 8.5 Snapshot dan pinning

`scripts/snapshot-manifest.py` menulis `repo/manifest.json` berisi versi,
fingerprint kunci, hash konfigurasi, dan checksum setiap paket. Pinning
memprioritaskan archive ArashiOS setara stable Debian dan membatasi backports
hanya untuk kernel dan Go.

### 8.6 Upgrade path

`tests/upgrade-path.sh` membangun paket pada dua versi rilis, memastikan versi
baru selalu lebih tinggi, memastikan isi paket berubah, memastikan changelog
memuat entri rilis, dan memulihkan state build. Hasil lulus.

### 8.7 Backports policy

`etc/apt/preferences.d/arashios-backports` memberi priority 500 hanya untuk
`linux-image-*`, `linux-headers-*`, `linux-modules-*`, `golang*`, dan
`golang-*`. Paket lain tetap pada priority 100.

### 8.8 Dokumentasi

`docs/PACKAGING.md`, `docs/REPOSITORY.md`, dan `docs/KEY-ROTATION.md`.

## 3. Sub-fase Fase 9

### 9.1 Test plan

`docs/QA-PLAN.md` memuat dua belas lapisan pengujian, matriks boot, pembagian
empat puluh pemeriksaan runtime, kriteria kelulusan, dan prosedur per rilis.

### 9.2 Boot test otomatis

`tests/boot-matrix.sh` menguji tujuh kombinasi pada mode firmware yang
berlaku, memverifikasi artefak lebih dulu, dan menandai kombinasi tanpa ISO
sebagai dilewati. arm64 dicatat sebagai dilewati karena memerlukan runner arm64.

### 9.3 Smoke suite

`tests/smoke-suite.sh` menggabungkan smoke test runtime, checklist hardening,
dan diagnosis harian menjadi satu laporan JSON. Pemeriksaan dikelompokkan
menjadi enam kelompok totaling empat puluh pemeriksaan.

### 9.4 Hardening

`scripts/check-hardening.py` memverifikasi 15 kontrol H-01 sampai H-15 dalam
dua mode: konfigurasi sumber dan runtime sistem. Mode konfigurasi lulus 18
pemeriksaan. `docs/HARDENING.md` menjelaskan nilai bawaan dan cara
verifikasinya.

### 9.5 Vulnerability scan

`scripts/scan-vulnerabilities.sh` menjalankan debsecan, trivy, dan grype yang
tersedia, lalu menggabungkan hasilnya menjadi satu laporan JSON dengan
status tiap pemindai, jumlah temuan per severity, dan daftar temuan. Pemindai
yang tidak ada dilaporkan sebagai skipped. `docs/VULNERABILITIES.md` mengatur
ambang dan jalur perbaikan.

### 9.6 SBOM

`scripts/generate-sbom.py` menghasilkan SBOM CycloneDX 1.6 dengan 361
komponen: setiap paket Debian yang dipilih konfigurasi beserta versinya dari
indeks bookworm, ditambah 16 paket ArashiOS dengan checksum SHA-256. Nomor
serial diturunkan dari hash komponen sehingga deterministik.
`scripts/check-sbom.py` memvalidasinya.

### 9.7 Artifact signing

`scripts/sign-artifact.sh` menandatangani dan memverifikasi artefak memakai
minisign atau GPG. `build.sh` menandatangani ISO dan SBOM bila kunci
tersedia, dan `tests/verify-artifact.sh` memeriksa keberadaan serta validitas
SBOM dan tanda tangan.

### 9.8 Audit kepatuhan

`scripts/check-compliance.py` menjalankan 133 pemeriksaan lisensi, atribusi,
dual use, ekspor, privasi, merek dagang, safe harbor, dan ketiadaan
akses jaringan pada skrip pemelihara. `docs/COMPLIANCE.md` merangkum hasilnya.

### 9.9 Disclosure policy

`SECURITY.md` sudah mencakup cakupan, kanal privat, SLA 24 jam untuk critical
dan 72 jam untuk high, safe harbor, dan dukungan versi.

### 9.10 Reproducibility

`scripts/check-reproducibility.sh` membangun paket dua kali dengan
`SOURCE_DATE_EPOCH` yang sama dan membandingkan checksum. Hasil: seluruh
paket identik. Laporan ditulis di `build/reproducibility-report.json`.

## 4. Hasil Verifikasi

### 4.1 Pemeriksaan Statis

| Pemeriksaan | Hasil |
|---|---|
| Standar packaging | 310 pemeriksaan lulus |
| Checklist hardening konfigurasi | 18 pemeriksaan lulus |
| Audit kepatuhan | 133 pemeriksaan lulus |
| SBOM CycloneDX | 361 komponen valid |
| Katalog toolstack | 6732 pemeriksaan lulus |
| Manifest snapshot | sinkron, 16 paket, hash konfigurasi tercatat |
| Repository | InRelease terverifikasi dengan kunci repo |
| Repository offline | apt membaca repo bertanda tangan dan pool membangun ulang indeks yang identik |
| Reproduksibilitas | paket identik antar dua build |
| Repository offline | apt membaca repo bertanda tangan, pool membangun indeks identik |
| Dokumen | 458 berkas lulus |
| Traceability | 58 requirement, 52 test case |

### 4.2 Perintah

```bash
make packages
make repo
make repo-check
make sbom
make hardening-check
make compliance-check
make reproducibility
make upgrade-check
python3 scripts/scan-vulnerabilities.sh --output build/vulnerability-report.json
./tests/boot-matrix.sh
./tests/smoke-suite.sh --output build/smoke-report.json
```

## 5. Penyimpangan dan Risiko

1. ISO belum dibangun sehingga verifikasi artefak, boot, dan runtime belum
   dijalankan pada artefak nyata.
2. Pemindai kerentanan tidak terpasang pada host, laporan hanya menyatakan
   status skipped.
3. Repository belum dipublikasikan karena domain final belum ditetapkan.
4. Kunci repository yang ada di host ini adalah kunci pengembangan tanpa
   passphrase. Kunci rilis harus dibuat dengan passphrase pada media offline.
5. Kunci privat sempat berada di dalam pohon repository pada build awal.
   Kunci sudah dipindahkan ke luar repository, aturan ignore dan pemeriksaan
   `check-packages.py` mencegah kunci privat masuk kembali. Kunci pengembangan ini
   tidak dipakai untuk rilis dan sebaiknya dicabut.
5. Audit ekspor formal dan pemeriksaan merek dagang belum diulang sebelum
   rilis publik.
6. Laporan kepatuhan otomatis belum menggantikan review hukum.
7. SBOM memakai nama paket Debian tanpa informasi lisensi per paket, lisensi
   diambil dari berkas copyright pada sistem terpasang.
8. Diffoscope belum dipakai karena image belum dibangun.

## 6. Exit Gate Runtime

Fase 8 dan Fase 9 belum dapat ditutup sampai:

1. `apt update` dan `apt upgrade` berhasil pada image dengan repo lokal.
2. Rebuild offline dari `repo/pool` berhasil.
3. Upgrade dari rilis lama berjalan tanpa reinstalasi.
4. Semua paket lolos pemeriksaan standar pada image nyata.
5. Boot UEFI dan BIOS lulus pada tiga edisi.
6. Empat puluh pemeriksaan runtime lulus.
7. Checklist hardening 100 persen pada image.
8. Tidak ada CVE critical atau high pada image.
9. SBOM tersedia dan valid untuk setiap artefak.
10. Tanda tangan artefak dan SBOM valid.
11. Laporan reproduksibilitas untuk dua build ISO tersedia.
12. Laporan kepatuhan dan sadari kerentanan terarsipkan.

## 7. Langkah Berikutnya

1. Pasang toolchain ISO lengkap dan tool pemindaian pada host build.
2. Bangun tujuh artefak ISO.
3. Jalankan matriks boot, smoke suite, dan pemindaian kerentanan.
4. Terapkan repository lokal pada image dan uji `apt update` serta upgrade.
5. Siapkan kunci rilis dan publikasikan repository ke mirror.
6. Lanjutkan ke Fase 10 untuk distribusi dan rilis.
