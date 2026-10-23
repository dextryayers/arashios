# Pemantauan Rilis

Pemantauan dilakukan tanpa telemetry pada sistem pengguna. Semua data
dikumpulkan dari infrastruktur proyek.

## 1. Cakupan

1. Ketersediaan mirror.
2. Kecepatan unduh.
3. Status kanal update.
4. Jumlah unduh agregat.
5. Laporan error dari forum.

## 2. Hotfix Window

Selama 7 hari setelah rilis, tim siap menerbitkan hotfix. Hotfix hanya
memperbaiki masalah boot, instalasi, keamanan, atau kehilangan data.

## 3. Rollback

1. Kernel lama dipertahankan.
2. Snapshot Timeshift dibuat sebelum upgrade.
3. Artefak rilis sebelumnya tetap tersedia.

## 4. Komunikasi

1. Pengumuman di forum dan Matrix.
2. Catatan rilis diperbarui.
3. Issue pelacak hotfix dibuat.

## 5. Skrip

`scripts/monitor-release.sh` memeriksa ketersediaan mirror dan checksum.
`scripts/rc-check.sh` menjalankan seluruh gate sebelum rilis.
