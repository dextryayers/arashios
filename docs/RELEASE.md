# Rilis ArashiOS

Dokumen ini menjelaskan alur rilis ArashiOS dari persiapan sampai publikasi.
Alur ini berlaku untuk kanal stable, edge, dan nightly.

## 1. Persiapan

1. Pastikan seluruh gate Fase 9 lulus pada image nyata.
2. Tetapkan versi rilis mengikuti pola `V<MAJOR>.<MM>.<DD>`.
3. Perbarui `CHANGELOG.md` dengan entri rilis, perubahan paket, dan risiko.
4. Buat tag Git bertanda tangan pada commit rilis.
5. Jalankan `scripts/check-release.sh` sebelum membangun artefak.

## 2. Matriks Build

Artefak yang dirilis:

| Arsitektur | Edisi | Nama berkas |
|---|---|---|
| amd64 | Cinnamon | ArashiOS-amd64-<versi>.iso |
| amd64 | XFCE | ArashiOS-amd64-<versi>-xfce.iso |
| amd64 | LXQt | ArashiOS-amd64-<versi>-lxqt.iso |
| arm64 | XFCE | ArashiOS-arm64-<versi>.iso |
| arm64 | LXQt | ArashiOS-arm64-<versi>-lxqt.iso |
| i386 | LXQt | ArashiOS-i386-<versi>.iso |
| i386 | XFCE | ArashiOS-i386-<versi>-xfce.iso |

Setiap artefak dibangun dengan `build.sh`, lalu diverifikasi dengan
`tests/verify-artifact.sh`.

## 3. Verifikasi Artefak

Setiap artefak wajib memiliki:

1. Nama sesuai skema.
2. Ukuran di bawah batas per edisi.
3. Volume ID sesuai.
4. Struktur ISO 9660, kernel, dan initrd.
5. Bootloader UEFI atau BIOS sesuai arsitektur.
6. Checksum SHA-256 dan SHA-512.
7. SBOM CycloneDX.
8. Tanda tangan minisign atau GPG.

## 4. Publikasi

1. Unggah artefak ke mirror utama.
2. Buat torrent dan berkas zsync.
3. Publikasikan checksum gabungan `SHA256SUMS` dan `SHA512SUMS`.
4. Buat GitHub Release dengan catatan rilis.
5. Perbarui halaman unduh pada situs web.

## 5. Pasca Rilis

1. Pantau mirror dan kanal update selama 7 hari.
2. Siapkan hotfix jika diperlukan.
3. Arsipkan log build, laporan smoke test, dan laporan CVE.
4. Publikasikan laporan pasca rilis.

## 6. Perintah

```bash
make build EDITION=cinnamon ARCH=amd64
./tests/verify-artifact.sh out/ArashiOS-amd64-V1.10.21.iso
./scripts/check-release.sh
./scripts/publish-mirror.sh --dry-run
```
