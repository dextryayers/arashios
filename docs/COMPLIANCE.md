# Kepatuhan ArashiOS

Dokumen ini merangkum pemeriksaan kepatuhan yang dijalankan sebelum rilis.

## 1. Pemeriksaan

```bash
python3 scripts/check-compliance.py --output build/compliance-report.json
```

Pemeriksaan mencakup:

| ID | Pemeriksaan |
|---|---|
| C-01 | Lisensi kode GPL-3.0-or-later tercatat |
| C-02 | Lisensi aset visual CC-BY-SA-4.0 tercatat |
| C-03 | Kebijakan ekspor tercatat |
| C-04 | Tawaran source tercatat |
| C-05 | Atribusi Kanagawa pada NOTICE |
| C-06 | Atribusi wordlist ArashiOS pada NOTICE |
| C-07 | Kebijakan tanpa telemetry |
| C-08 | Kebijakan tanpa akun bawaan |
| C-09 | Kebijakan merek dagang |
| C-10 | SLA respons minimal 72 jam |
| C-11 | Safe harbor ada |
| C-12 | Kode etik memakai Contributor Covenant |
| C-13 | Disclaimer dual use ada |
| C-14 | Atribusi Debian ada |
| C-15 | Pernyataan bukan proyek resmi Debian |
| C-16 | Semua tool tier 1 ada di matriks lisensi |
| C-17 | Tool proprietary tidak pernah masuk image |
| C-18 | Skrip pemelihara tidak mengakses jaringan |
| C-19 | Paket ArashiOS tidak bergantung pada pengunduh |
| C-20 | Aset merek adalah SVG yang valid |
| C-21 | Manifest tema mencatat daftar berkas |

## 2. Lisensi

| Komponen | Lisensi | Sumber kebenaran |
|---|---|---|
| Kode ArashiOS | GPL-3.0-or-later | LICENSE |
| Aset visual | CC-BY-SA-4.0 | LICENSE dan NOTICE |
| Dokumentasi | CC-BY-4.0 | LICENSE |
| Tool tier 1 | Lisensi upstream | docs/LICENSES.md |
| Paket Debian | Lisensi masing-masing | /usr/share/doc/<paket>/copyright |
| Wordlist ArashiOS | CC-BY-SA-4.0 | /usr/share/wordlists/arashios/LICENSE |

## 3. Ekspor dan Responsible Use

ArashiOS menyertakan tool keamanan dual use. Pengguna bertanggung jawab
mematuhi hukum yang berlaku. Tool tidak boleh dipakai untuk mengakses sistem
tanpa izin. Kepatuhan ekspor menjadi tanggung jawab pengguna dan distributor.

## 4. Privasi

Tidak ada telemetry, analytics, atau crash reporting otomatis. Tidak ada akun
daring bawaan. Tidak ada panggilan jaringan saat boot. Laporan lengkap ada di
[PRIVACY.md](PRIVACY.md).

## 5. Atribusi

1. Debian adalah merek dagang Software in the Public Interest, Inc.
2. ArashiOS tidak diklaim sebagai proyek resmi Debian.
3. Palet terminal terinspirasi Kanagawa.nvim dengan lisensi MIT.
4. Wordlist ArashiOS adalah kurasi internal berlisensi CC-BY-SA-4.0.
5. Installer memakai Calamares berlisensi GPL-3.0-or-later.

## 6. Bukti Rilis

| Bukti | Perintah |
|---|---|
| Laporan kepatuhan | `python3 scripts/check-compliance.py --output build/compliance-report.json` |
| Matriks lisensi | `docs/LICENSES.md` |
| Notice | `NOTICE` |
| SBOM | `out/<iso>.sbom.json` |

## 7. Batasan saat ini

1. Audit ekspor formal belum dilakukan oleh penasihat hukum.
2. Pemeriksaan nama merek dagang belum diulang sebelum rilis publik.
3. Laporan kepatuhan otomatis belum menggantikan review hukum.
