# ADR-006: Design system Kage

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

ArashiOS membutuhkan identitas visual yang konsisten di GTK, Qt, GRUB, Plymouth, LightDM, dokumentasi, dan situs web. Tema harus terasa Jepang minimal dengan aksen red team, bukan sekadar tempelan grafis.

## Keputusan

Design system bernama Kage memakai token JSON sebagai sumber kebenaran. Palet inti: sumi, washi, ash, ember, dan vermilion. Tipografi memakai Inter untuk UI dan JetBrains Mono untuk terminal. Token menghasilkan CSS, SCSS, QSS, dan laporan kontras. Semua pasangan warna teks wajib memenuhi WCAG AA.

## Konsekuensi

1. Setiap perubahan warna harus melalui token.
2. Kontras dihitung otomatis dan build gagal jika ambang dilanggar.
3. Tema GTK dan Qt diturunkan dari token yang sama.
4. Aset visual berlisensi CC-BY-SA-4.0.
5. Motif ninja dipakai secara halus, tanpa emoji dan tanpa ornamen berlebihan.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Tema upstream tanpa kustomisasi | Tidak konsisten antar edisi |
| Estetika cyberpunk berat | Kontras dan keterbacaan buruk |
| Warna acak per edisi | Merusak identitas dan aksesibilitas |
