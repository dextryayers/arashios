# ADR-007: Skema versi dan nama ISO

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

Rilis ArashiOS perlu mudah dikenali, diurutkan, dan dipetakan ke tanggal build tanpa bergantung pada semver yang tidak cocok untuk distribusi berbasis snapshot.

## Keputusan

Versi produk memakai pola `V<major>.<MM>.<DD>`, dengan baseline `V1.10.21`. Nama ISO:

```
ArashiOS-<arch>-<version>[-<edition>].iso
```

Edisi default per arsitektur tidak memakai sufiks. Edisi non-default memakai `-xfce` atau `-lxqt`. Skema dokumen dan API internal tetap memakai semver.

## Konsekuensi

1. Versi menunjukkan tanggal rilis.
2. Dua rilis pada hari yang sama memerlukan sufiks build internal.
3. Nama ISO dapat diprediksi oleh skrip unduhan.
4. Metadata build menyimpan commit, timestamp, dan versi Debian.
5. Semver produk tidak dipakai.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Semver produk | Tidak mencerminkan snapshot Debian dan tanggal build |
| CalVer YYYY.MM.DD | Lebih panjang dan tidak konsisten dengan baseline |
| Nomor build monotonic | Tidak informatif bagi pengguna |
