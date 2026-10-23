# Proses Kandidat Rilis

## 1. Tujuan

Kandidat rilis digunakan untuk validasi akhir sebelum publikasi.

## 2. Alur

1. Bangun seluruh artefak dengan versi RC.
2. Jalankan `scripts/rc-check.sh`.
3. Jalankan matriks boot dan smoke suite.
4. Lakukan pengujian hardware pada tiga mesin.
5. Perbaiki temuan critical dan high.
6. Tandai commit final sebagai rilis.

## 3. Kriteria Kelulusan

1. Semua artefak lulus verifikasi.
2. Semua smoke test lulus.
3. Tidak ada CVE critical atau high.
4. Dokumentasi lengkap.
5. Checklist aksesibilitas lulus.

## 4. Artefak RC

Artefak RC tidak dipublikasikan ke mirror utama. Artefak RC disimpan
pada kanal edge atau nightly.
