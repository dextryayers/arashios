# ADR-005: Calamares sebagai installer

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

ArashiOS membutuhkan installer grafis yang dapat dikustomisasi, mendukung UEFI dan BIOS, serta bekerja dengan skema partisi yang kompleks termasuk dual boot.

## Keputusan

Installer default adalah Calamares dengan branding ArashiOS, modul partisi yang diperketat, deteksi firmware, dan ringkasan keamanan sebelum instalasi. Mode expert tetap tersedia, tetapi penghapusan disk memerlukan konfirmasi eksplisit.

## Konsekuensi

1. Calamares perlu dikemas dan diuji pada setiap edisi.
2. Branding installer mengikuti design token Kage.
3. Partisi manual dan enkripsi LUKS harus diuji.
4. Pesan kesalahan harus dapat ditindaklanjuti.
5. Instalasi otomatis belum menjadi target v1.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Debian installer | Branding dan alur pengguna terbatas |
| Installer kustom | Biaya engineering dan QA terlalu tinggi |
| Tanpa installer | Tidak memenuhi target distro mandiri |
