# Legal dan Kepatuhan

Dokumen ini merangkum lisensi, kewajiban distribusi, merek dagang, ekspor, dan privasi. Dokumen ini bukan nasihat hukum. Sebelum rilis publik, lakukan review oleh penasihat hukum yang kompeten.

## Matriks Lisensi

| Komponen | Lisensi | Pemegang hak |
|---|---|---|
| Skrip build, hook, konfigurasi | GPL-3.0-or-later | Kontributor ArashiOS |
| Aset visual dan tema | CC-BY-SA-4.0 | Kontributor ArashiOS |
| Dokumentasi | CC-BY-4.0 | Kontributor ArashiOS |
| Paket Debian | Lisensi masing-masing paket | Pemegang hak masing-masing |
| Tool vendored | Lisensi upstream | Pemegang hak upstream |
| Firmware non-free | Lisensi masing-masing | Pemegang hak masing-masing |
| Inspirasi palet terminal | MIT | Kanagawa.nvim dan kontributor |

Palet terminal ArashiOS terinspirasi Kanagawa.nvim. Notice dan teks lisensi
MIT pihak ketiga disertakan di `NOTICE`, paket `arashios-branding`, dan image.

## Kewajiban Distribusi

1. Sertakan teks lisensi lengkap untuk kode ArashiOS.
2. Sertakan atau tawarkan source code yang sesuai untuk komponen GPL.
3. Pertahankan notice hak cipta dan lisensi pihak ketiga.
4. Cantumkan daftar paket dan lisensi di dalam ISO.
5. Jangan menghapus metadata lisensi dari tool vendored.
6. Distribusikan aset visual di bawah CC-BY-SA-4.0 dengan atribusi.
7. Sediakan berkas `COPYING` dan `NOTICE` pada image.

## Merek Dagang

1. Nama ArashiOS dan logo adalah merek proyek.
2. Distribusi modifikasi wajib mengganti nama dan logo jika tidak disetujui.
3. Penggunaan nominatif untuk merujuk proyek asli diperbolehkan.
4. Debian adalah merek dagang Software in the Public Interest, Inc.
5. ArashiOS tidak diklaim sebagai proyek resmi Debian.
6. Status pendaftaran merek: belum diajukan.
7. Pencarian nama dan domain dilakukan pada Fase 0.5 dan diulang sebelum rilis publik.

## Ekspor dan Dual Use

1. ArashiOS memuat alat keamanan dan kriptografi.
2. Pengguna bertanggung jawab mematuhi hukum ekspor dan impor di yurisdiksinya.
3. Alat offensive hanya boleh dipakai pada sistem yang diizinkan.
4. Distribusi ke negara yang dikenai sanksi memerlukan review hukum.
5. Klasifikasi ekspor dan nomor ECCN dicatat pada manifest rilis.

## Paten

1. Lisensi GPL-3.0 memberikan paten grant untuk kontribusi kode.
2. Aset visual tidak memberikan paten grant.
3. Tool pihak ketiga tunduk pada lisensi masing-masing.
4. Kontributor tidak boleh memasukkan kode yang melanggar paten pihak lain.

## Kontribusi

1. Kontribusi memakai Developer Certificate of Origin.
2. Tidak ada copyright assignment.
3. Kontributor menyatakan berhak atas kontribusinya.
4. Kontribusi kode tunduk pada GPL-3.0-or-later.
5. Kontribusi aset tunduk pada CC-BY-SA-4.0.

## Checklist Rilis

| Item | Bukti |
|---|---|
| Teks lisensi lengkap | `LICENSE`, `COPYING`, `NOTICE` |
| Daftar paket dan lisensi | `/usr/share/doc/arashios/` |
| Source offer | URL dan commit hash |
| Manifest tool | `manifests/tools.json` |
| Review merek dagang | Catatan review |
| Review ekspor | Catatan review |
| Kebijakan privasi | `docs/PRIVACY.md` |
