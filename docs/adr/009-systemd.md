# ADR-009: systemd sebagai init

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

Debian 12 dan desktop Cinnamon, XFCE, serta LXQt terintegrasi dengan systemd. live-config juga menyediakan integrasi systemd untuk sesi live.

## Keputusan

systemd adalah init system default. Unit kustom ArashiOS diletakkan di `/etc/systemd/system` dan diaktifkan melalui hook. Init alternatif tidak didukung pada v1.

## Konsekuensi

1. Integrasi logind, networkd opsional, dan sesi desktop lebih sederhana.
2. Unit kustom harus lolos `systemd-analyze verify`.
3. Boot time dapat dianalisis dengan `systemd-analyze`.
4. Pengguna yang membutuhkan init lain harus menunggu dukungan komunitas.
5. Hook build harus idempoten.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| OpenRC | Integrasi desktop Debian tidak lengkap |
| runit | Dukungan paket dan desktop terbatas |
| s6 | Kompleks dan tidak sesuai target pengguna |
