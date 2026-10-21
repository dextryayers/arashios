# Kebijakan Privasi

## Ringkasan

ArashiOS tidak mengumpulkan telemetry, tidak mengirim crash report otomatis, dan tidak memiliki akun pengguna. Data tetap berada di perangkat kecuali pengguna memulai koneksi jaringan.

## Data yang Tidak Dikumpulkan

1. Identitas pengguna.
2. Alamat IP.
3. Lokasi.
4. Pola penggunaan aplikasi.
5. Isi berkas atau riwayat shell.
6. Data perangkat keras yang dikirim ke server.
7. Crash dump otomatis.

## Koneksi Jaringan Default

| Layanan | Tujuan | Data | Dapat dimatikan |
|---|---|---|---|
| APT | Mirror Debian | Permintaan paket, alamat IP | Ya |
| NTP | Server waktu | Alamat IP, waktu | Ya |
| Pembaruan firmware | Vendor firmware | Bergantung vendor | Ya |
| Aplikasi pengguna | Tujuan yang dipilih pengguna | Bergantung aplikasi | Ya |

Tidak ada koneksi yang dilakukan oleh ArashiOS untuk analytics atau iklan.

## Log Lokal

1. systemd journal disimpan lokal dan dibatasi ukurannya.
2. Log apt disimpan lokal.
3. Riwayat shell disimpan di home pengguna.
4. Pengguna dapat menghapus log kapan saja.
5. Log tidak dikirim otomatis.

## Diagnostik Sukarela

Jika pengguna memilih mengirim laporan bug, pengguna mengontrol isi laporan. Jangan sertakan data sensitif. Tim dapat meminta output terbatas seperti `inxi -Fxz` atau `journalctl` dengan rentang waktu tertentu. Pengiriman bersifat opsional.

## Aplikasi Pihak Ketiga

Aplikasi yang dipasang pengguna memiliki kebijakan privasi masing-masing. ArashiOS tidak dapat menjamin perilaku aplikasi pihak ketiga. Pengguna disarankan memeriksa izin dan koneksi jaringan aplikasi.

## Anak-anak

ArashiOS tidak ditujukan untuk anak di bawah 13 tahun dan tidak mengumpulkan data pribadi.

## Perubahan

Perubahan kebijakan dicatat di changelog dan diumumkan pada rilis. Versi baru berlaku pada rilis berikutnya.

## Kontak

Kanal privasi resmi ditetapkan pada Fase 0.5. Sampai saat itu, gunakan kanal privat proyek di GitHub.
