# Situs Web dan Dokumentasi Publik

## 1. Tujuan

Situs web menyediakan halaman unduh, dokumentasi, dan FAQ. Situs dibangun
sebagai statis agar mudah dicerminkan.

## 2. Struktur

```text
site/
├── index.html
├── download.html
├── docs.html
├── faq.html
└── assets/
    └── style.css
```

## 3. Konten

1. Halaman utama dengan ringkasan produk.
2. Halaman unduh dengan tautan mirror.
3. Halaman dokumentasi.
4. FAQ.

## 4. Pembaruan

Situs diperbarui setiap rilis. Versi dan tautan unduh disinkronkan
dengan `versions.env`.
