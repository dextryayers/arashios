# ADR-008: Tanpa telemetry secara default

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

Pengguna ArashiOS bekerja pada data sensitif, riset keamanan, dan lingkungan yang mungkin terisolasi. Panggilan jaringan tersembunyi dapat membocorkan keberadaan, alamat IP, dan pola penggunaan.

## Keputusan

ArashiOS tidak mengirim telemetry, crash report, atau usage analytics secara default. Tidak ada kanal jaringan yang aktif tanpa tindakan pengguna. Pembaruan keamanan tetap dapat dilakukan melalui apt. Diagnostik hanya dikumpulkan atas permintaan eksplisit dan disimpan lokal.

## Konsekuensi

1. Tim tidak mendapat data penggunaan otomatis.
2. Perbaikan bug bergantung pada laporan pengguna.
3. Semua komponen pihak ketiga harus diaudit untuk panggilan jaringan.
4. Firewall default menolak koneksi masuk.
5. Dokumentasi menjelaskan cara menonaktifkan pembaruan otomatis jika diperlukan.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Opt-in telemetry | Tetap menambah permukaan dan risiko salah konfigurasi |
| Crash report otomatis | Dapat memuat data sensitif |
| Tanpa kebijakan tertulis | Tidak dapat diaudit |
