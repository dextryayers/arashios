# ADR-004: Vendoring tool non-Debian

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

Sebagian alat red team tidak tersedia di Debian bookworm atau versinya tertinggal. Menambahkan repository pihak ketiga secara permanen meningkatkan risiko rantai pasok dan menyulitkan audit.

## Keputusan

Tool yang tidak tersedia di Debian diambil pada saat build, diverifikasi checksum dan tanda tangan upstream, lalu dipasang ke `/opt/arashios/tools/<tool>`. Setiap tool memiliki manifest dengan versi, URL sumber, hash, lisensi, dan tingkat kepercayaan T0 sampai T3. Repository pihak ketiga tidak ditambahkan ke sistem terpasang. Pembaruan tool dilakukan melalui rilis ArashiOS.

## Konsekuensi

1. Versi tool dapat direproduksi dan diaudit.
2. Ukuran ISO bertambah.
3. Proses rilis memerlukan pembaruan manifest dan uji ulang.
4. Lisensi dan kebijakan ekspor wajib diperiksa.
5. Tool yang membutuhkan kernel module atau repository khusus ditandai T3 dan tidak masuk default.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Menambah repository Kali permanen | Mencampur kebijakan paket dan meningkatkan risiko |
| Flatpak untuk semua tool | Sandbox menghambat raw socket dan akses perangkat |
| Instalasi manual oleh pengguna | Tidak konsisten dan tidak dapat diuji |
| blackarch repository | Tidak kompatibel dengan basis Debian dan berisiko konflik |
