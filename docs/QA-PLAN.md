# Rencana QA ArashiOS

Dokumen ini adalah rencana pengujian untuk rilis ArashiOS. Setiap fase punya
lapisan pengujian yang berbeda, dan setiap lapis menghasilkan bukti yang dapat
diarsipkan.

## 1. Lapisan Pengujian

| Lapis | Alat | Cakupan | Kapan |
|---|---|---|---|
| Statis | shellcheck, py_compile, check-docs, check-traceability | Gaya, sintaks, kebijakan | Setiap push |
| Konfigurasi | validate-config, check-toolstack, check-daily, check-installer, check-packages | Tree build, paket, installer | Setiap push |
| Paket | check-packages, branding-package | Kualitas paket dan reproduksibilitas | Setiap push |
| Tema | tests/theme.sh, tests/desktop-matrix.sh | CSS GTK3 dan GTK4, layout desktop | Setiap push |
| Toolchain | tests/toolstack.sh, tests/coding.sh | Katalog, lock, template, bahasa | Setiap push |
| Config matrix | tests/config-matrix.sh | Tujuh kombinasi live-build | Setiap push |
| Artefak | tests/verify-artifact.sh | Nama, ukuran, struktur ISO, checksum, tanda tangan | Setelah build |
| Boot | tests/boot-matrix.sh | UEFI dan BIOS pada tiga edisi | Setelah build |
| Runtime | tests/smoke-suite.sh, tests/smoke.sh | Empat puluh pemeriksaan pada image | Setelah boot |
| Kerentanan | scripts/scan-vulnerabilities.sh | debsecan, trivy, grype | Sebelum rilis |
| Kepatuhan | scripts/check-compliance.py | Lisensi, privasi, ekspor | Sebelum rilis |
| Reproduksibilitas | scripts/check-reproducibility.sh | Build dua kali | Sebelum rilis |

## 2. Matriks Boot

| Kombinasi | UEFI | BIOS | Runner |
|---|---|---|---|
| amd64 cinnamon | ya | ya | amd64 |
| amd64 xfce | ya | ya | amd64 |
| amd64 lxqt | ya | ya | amd64 |
| arm64 xfce | ya | tidak | arm64 |
| arm64 lxqt | ya | tidak | arm64 |
| i386 lxqt | tidak | ya | amd64 |
| i386 xfce | tidak | ya | amd64 |

Setiap boot menghasilkan screenshot PPM dan log serial di `out/`. Ringkasan
matriks disimpan di `build/boot-matrix/`.

## 3. Empat Puluh Pemeriksaan Runtime

Pemeriksaan runtime dibagi menjadi lima kelompok.

| Kelompok | Jumlah | Pemeriksaan |
|---|---:|---|
| Identitas dan build | 6 | versi, edisi, arsitektur, build-info, logo, issue |
| Layanan dan keamanan | 8 | NetworkManager, LightDM, UFW, AppArmor, SSH, sysctl, autologin, unattended-upgrades |
| Tool keamanan | 8 | nmap, sqlmap, hydra, hashcat, aircrack, wireshark, tshark, podman |
| Tool coding | 8 | gcc, python3, go, rustc, node, java, php, ruby |
| Aplikasi dan desktop | 6 | firefox, thunderbird, libreoffice, vlc, keepassxc, panel |
| Platform dan installer | 4 | locale, printer, container rootless, katalog arsenal |

Laporan JSON ditulis oleh `tests/smoke-suite.sh`.

## 4. Kriteria Kelulusan

| Area | Kriteria |
|---|---|
| Build | Tujuh kombinasi konfigurasi valid, semua paket tersedia |
| Paket | Semua paket lolos pemeriksaan standar, build reproducible |
| Boot | UEFI dan BIOS mencapai desktop tanpa error |
| Runtime | Empat puluh pemeriksaan lulus, hardening 100 persen |
| Keamanan | Tidak ada CVE critical atau high terbuka |
| Kepatuhan | Seluruh pemeriksaan kepatuhan lulus |
| Releas | Checklist RC-01 sampai RC-20 lengkap |

## 5. Prosedur Per Rilis

```bash
make lint
make config-matrix
make build EDITION=cinnamon ARCH=amd64
./tests/verify-artifact.sh out/ArashiOS-amd64-V1.10.21.iso
./tests/boot-matrix.sh
./tests/smoke-suite.sh --output build/smoke-report.json
python3 scripts/generate-sbom.py --index-dir <indeks> --output out/ArashiOS-amd64-V1.10.21.sbom.json
./scripts/scan-vulnerabilities.sh --output build/vulnerability-report.json
python3 scripts/check-compliance.py --output build/compliance-report.json
./scripts/check-reproducibility.sh
```

## 6. Klasifikasi Temuan

| Tingkat | Dampak | Tindakan |
|---|---|---|
| Blocker | ISO tidak boot, data hilang, CVE critical | Build gagal, rilis ditunda |
| Tinggi | Fitur inti gagal, hardening tidak berlaku | Build gagal |
| Sedang | Fitur pendukung gagal, tampilan tidak konsisten | Perbaiki sebelum rilis |
| Rendah | Kosmetik dan teks | Perbaiki pada rilis berikutnya |

## 7. Bukti yang Diarsipkan

| Bukti | Lokasi |
|---|---|
| Log build | `build/<edition>-<arch>/build.log` |
| Log boot | `build/boot-matrix/` |
| Laporan smoke | `build/smoke-report.json` |
| Laporan hardening | `build/hardening.json` |
| Laporan kerentanan | `build/vulnerability-report.json` |
| Laporan kepatuhan | `build/compliance-report.json` |
| Laporan reproduksibilitas | `build/reproducibility-report.json` |
| SBOM | `out/<iso>.sbom.json` |
| Checksum dan tanda tangan | `out/<iso>.sha256`, `out/<iso>.sha512`, `out/<iso>.sig` |

## 8. Batasan saat ini

1. Belum ada image ISO sehingga lapis boot dan runtime belum dijalankan.
2. Pemindai kerentanan belum terpasang pada host pengembangan.
3. Checklist hardware tiga mesin belum dijalankan.
