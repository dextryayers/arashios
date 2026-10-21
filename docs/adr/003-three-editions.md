# ADR-003: Tiga edisi desktop

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

Pengguna ArashiOS memiliki kebutuhan berbeda: mesin kerja utama, VM dengan sumber daya terbatas, dan perangkat lama dengan RAM kecil. Satu edisi tidak dapat mengoptimalkan ketiganya tanpa kompromi.

## Keputusan

Tersedia tiga edisi:

| Edisi | Posisi | Default pada |
|---|---|---|
| Cinnamon | Flagship, pengalaman lengkap | amd64 |
| XFCE | Ringan dan stabil untuk VM | arm64 |
| LXQt | Paling ringan untuk perangkat lama | i386 |

Lapisan `config/common` memuat paket dan konfigurasi bersama. Setiap edisi memiliki overlay paket desktop, sesi LightDM, dan tema yang sesuai. Tujuh artefak ISO dihasilkan per rilis.

## Konsekuensi

1. Matriks QA mencakup tujuh artefak.
2. Tema harus memiliki paritas GTK dan Qt.
3. Paket desktop tidak boleh saling bertabrakan.
4. Ukuran ISO dan waktu build berbeda per edisi.
5. Dokumentasi harus menyatakan edisi default per arsitektur.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Satu edisi dengan tasksel | Pengalaman awal tidak optimal dan ukuran tidak terkendali |
| Dua edisi | Menghilangkan segmen perangkat lama atau VM ringan |
| Edisi KDE Plasma | Konsumsi sumber daya tinggi untuk target i386 |
