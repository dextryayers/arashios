# Security Policy

## Scope

Kanal ini menerima laporan untuk:

1. ISO ArashiOS.
2. Paket ArashiOS.
3. Repository APT.
4. Build pipeline dan CI.
5. Website resmi.
6. Konfigurasi default yang melemahkan keamanan.
7. SBOM, tanda tangan artefak, dan checksum rilis.
8. Kunci signing repository dan rotasi kunci.

Artefak rilis yang dilindungi adalah berkas `.iso`, `.sha256`, `.sha512`,
`.sig`, dan `.sbom.json`. Laporan disertai perintah verifikasi akan membantu reproduksi.

## Kanal

Kanal privat ditetapkan pada Fase 0.5. Sampai kanal resmi tersedia, gunakan fitur private security advisory di GitHub.

Jangan membuka issue publik untuk kerentanan yang belum diperbaiki.

## SLA

| Tingkat | Respons awal | Perbaikan |
|---|---|---|
| Critical | 24 jam | 7 hari |
| High | 72 jam | 30 hari |
| Medium | 7 hari | 90 hari |
| Low | 14 hari | Rilis berikutnya |

## Yang Disertakan dalam Laporan

1. Versi ArashiOS dan edisi.
2. Arsitektur dan firmware.
3. Langkah reproduksi.
4. Dampak dan bukti konsep.
5. Saran mitigasi jika ada.
6. Apakah laporan boleh dipublikasikan.

## Safe Harbor

Riset yang dilakukan dengan niat baik, tanpa merusak data, dan tanpa mengakses data pengguna lain dianggap aktivitas yang diizinkan. Proyek tidak akan menempuh tindakan hukum terhadap peneliti yang mengikuti kebijakan ini.

## Disclosure

1. Detail tidak dipublikasikan sebelum perbaikan tersedia.
2. Kredit peneliti jika diizinkan.
3. Advisory dipublikasikan di website dan GitHub Security.
4. CVE diminta jika dampak mencukupi.

## Verifikasi Rilis

Setiap rilis menyertakan checksum SHA-256 dan SHA-512, SBOM CycloneDX, dan
tanda tangan. Verifikasi dilakukan sebagai berikut:

```bash
sha256sum -c ArashiOS-amd64-V1.10.21.iso.sha256
./scripts/sign-artifact.sh --verify ArashiOS-amd64-V1.10.21.iso.sig
python3 ./scripts/check-sbom.py ArashiOS-amd64-V1.10.21.iso.sbom.json
```

Fingerprint kunci repository ada di `repo/keys/arashios-archive.fingerprint`
dan dipublikasikan bersama release notes. Kunci privat tidak pernah ada di
image maupun repository publik.

## Rotasi Kunci

Kunci repository dan kunci tanda tangan artefak mengikuti jadwal rotasi yang
tercantum pada [docs/KEY-ROTATION.md](docs/KEY-ROTATION.md). Penghapusan kunci
memerlukan dua maintainer.

## Dukungan Versi

| Versi | Dukungan |
|---|---|
| Rilis major terbaru | Penuh |
| Rilis major sebelumnya | Security fix 6 bulan |
| Nightly | Tidak ada jaminan |
