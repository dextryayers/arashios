# ADR-001: Debian 12 bookworm sebagai basis

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

ArashiOS membutuhkan basis yang stabil, memiliki pembaruan keamanan terjadwal, mendukung amd64, arm64, dan i386, serta menyediakan ekosistem paket yang luas untuk desktop, pengembangan, dan alat keamanan.

## Keputusan

Basis resmi adalah Debian 12 bookworm dengan area `main`, `contrib`, `non-free`, dan `non-free-firmware`. Arsip keamanan Debian wajib aktif. bookworm-backports hanya dipakai untuk paket yang dipilih secara eksplisit dan tidak menjadi sumber default seluruh sistem.

## Konsekuensi

1. Siklus pembaruan mengikuti Debian stable.
2. Kernel dan beberapa tool dapat dinaikkan dari backports dengan pinning.
3. Repository pihak ketiga permanen tidak ditambahkan ke sistem terpasang.
4. Dukungan hingga akhir siklus keamanan Debian 12.
5. Beberapa paket pengembangan lebih lama dari rilis upstream terbaru.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Ubuntu LTS | Snap, telemetry, dan lapisan paket tambahan memperbesar permukaan serangan |
| Arch Linux | Rolling release tidak cocok untuk ISO keamanan yang harus dapat direproduksi |
| Kali Linux | Fokus offensive dan rolling, bukan basis distro mandiri |
| Debian testing | Perubahan paket tidak dapat dijamin antar build |
