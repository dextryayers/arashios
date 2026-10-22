# Katalog Tool ArashiOS

Direktori ini adalah sumber kebenaran untuk tool yang boleh masuk ke image
ArashiOS.

```text
tools/
├── catalog.yaml       metadata tool: tier, alur kerja, paket, lisensi, arsitektur
└── source-pins.yaml   pin sumber upstream untuk tool tier 1
```

## Alur kerja

1. Tambah atau ubah entri di `tools/catalog.yaml`.
2. Untuk tool tier 1, tambah pin di `tools/source-pins.yaml` dengan tag dan
   commit upstream.
3. Jalankan `python3 scripts/generate-toolstack.py` untuk memperbarui manifest
   di `vendor/manifests` dan katalog runtime di
   `config/common/includes.chroot/usr/share/arashios/toolstack/catalog.json`.
4. Jalankan `python3 scripts/check-toolstack.py` dan
   `python3 scripts/check-licenses.py --update`.

## Aturan entri

| Field | Aturan |
|---|---|
| `name` | huruf kecil, angka, titik, garis |
| `tier` | T0 sampai T3 |
| `workflow` | satu ID alur kerja atau daftar ID |
| `package` | hanya untuk T0, harus ada di package list |
| `binary` | biner yang dipakai smoke test |
| `license` | `debian` untuk T0, SPDX untuk T1, `proprietary` untuk T2 dan T3 |
| `arch` | arsitektur yang didukung, default semua |
| `source` | kunci pin untuk T1, string bebas untuk T0, T2, dan T3 |
| `build` | `go`, `python`, `ruby`, `java`, `source`, `data`, atau `binary` |
| `install_path` | lokasi install absolut untuk T1 |

Tujuan jumlah tool:

| Tier | Minimum | Maksimum |
|---|---:|---:|
| T0 | 130 | tidak dibatasi |
| T1 | 40 | tidak dibatasi |
| T2 | 8 | 12 |
| T3 | 3 | tidak dibatasi |

Setiap alur kerja wajib punya minimal satu tool T0 dan satu tool T1.
