# ADR-013: Pipeline tema Kage

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

ArashiOS harus memakai identitas Kage pada GTK2, GTK3, GTK4 dan libadwaita,
Cinnamon, Muffin dan Metacity, XFCE, Openbox, Kvantum, LightDM, GRUB, dan
Plymouth. Menulis setiap tema secara manual membuat warna, radius, dan ukuran
panel mudah menyimpang. Tema juga harus dapat diverifikasi tanpa membuka sesi
desktop.

## Keputusan

1. `branding/tokens.json` menjadi satu-satunya sumber warna, tipografi,
   radius, gerak, dan token terminal.
2. `scripts/generate-theme.py` menghasilkan dua tema, `ArashiKage` dan
   `ArashiKage-HC`, dari template di `branding/theme/templates/`.
3. Output ditulis ke `build/theme` dan dicatat dalam
   `build/theme/manifest.json` dengan hash SHA-256.
4. `scripts/generate-theme.py --check` menolak output yang hilang,
   kedaluwarsa, atau tidak cocok dengan manifest.
5. Semua tema dan aset boot dikemas dalam satu paket lokal,
   `arashios-branding`, yang dibangun oleh `scripts/build-branding-package.sh`.
6. Paket lokal dipasang melalui `config/packages.chroot` pada setiap build ISO.
7. Pemeriksaan statis dijalankan oleh `tests/theme.sh`,
   `tests/desktop-matrix.sh`, dan `tests/branding-package.sh`.

## Konsekuensi

1. Perubahan visual harus dimulai dari token atau template, bukan dari file
   hasil generate.
2. Build menghasilkan ulang tema sebelum paket branding dibuat.
3. Manifest dan paket dapat diaudit tanpa X server.
4. Radius di atas 4px hanya diizinkan untuk pill dan kontrol melingkar.
5. GTK3 dan GTK4 dapat diverifikasi dengan parser toolkit bila PyGObject
   tersedia.
6. Paket branding bersifat `Architecture: all` dan reproducible dengan
   `SOURCE_DATE_EPOCH`.
7. Pemeriksaan runtime LightDM, panel, Openbox, dan Kvantum tetap memerlukan
   ISO dan sesi nyata.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Tema manual per toolkit | Mudah menyimpang dan sulit diaudit |
| Satu paket Debian per toolkit | Menambah dependensi dan urutan pemasangan |
| Tema pihak ketiga tanpa token | Tidak memenuhi identitas Kage dan lisensi |
| Renderer SVG eksternal saat build | Menambah dependensi host dan hasil tidak deterministik |
| Menyimpan hanya file hasil generate | Sulit dirawat dan tidak dapat diregenerasi |
| Manifest tanpa hash | Tidak dapat mendeteksi output kedaluwarsa |
