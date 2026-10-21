# ADR-011: Neovim dan VSCodium

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

Pengguna membutuhkan editor terminal yang cepat dan IDE grafis yang ringan. Visual Studio Code resmi memuat telemetry dan lisensi proprietary yang tidak sesuai dengan prinsip ArashiOS.

## Keputusan

Neovim menjadi editor terminal default. VSCodium menjadi editor grafis default. Ekstensi diambil dari Open VSX. Konfigurasi awal Neovim memakai Lua dan tidak memuat plugin berat secara default.

## Konsekuensi

1. Sebagian ekstensi eksklusif Microsoft tidak tersedia.
2. VSCodium harus diverifikasi checksum dan sumbernya.
3. Konfigurasi Neovim dapat diaudit dan diperluas pengguna.
4. Terminal memakai JetBrains Mono.
5. Lisensi dan privasi editor dijelaskan di dokumentasi.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| VS Code resmi | Telemetry dan lisensi tidak sesuai |
| Code OSS build sendiri | Beban build dan distribusi tinggi |
| Hanya Neovim | Tidak ramah pengguna GUI pemula |
| JetBrains IDE | Berat dan berlisensi proprietary |
