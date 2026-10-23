# Mirror dan Distribusi

ArashiOS mendistribusikan artefak melalui mirror HTTP, torrent, dan zsync.
Mirror utama ditetapkan pada Fase 10.5. Cermin komunitas dapat ditambahkan
melalui permintaan pull.

## 1. Struktur Mirror

```text
mirror/
├── stable/
│   ├── V1.10.21/
│   │   ├── ArashiOS-*.iso
│   │   ├── *.sha256
│   │   ├── *.sha512
│   │   ├── *.sbom.json
│   │   ├── *.sig
│   │   ├── SHA256SUMS
│   │   └── SHA512SUMS
│   └── current -> V1.10.21
├── edge/
└── nightly/
```

## 2. Sinkronisasi

1. Bangun artefak pada host rilis.
2. Jalankan `scripts/publish-mirror.sh`.
3. Verifikasi checksum pada mirror.
4. Perbarui symlink `current`.

## 3. Torrent

1. Satu torrent per artefak.
2. Tracker utama dan tracker cadangan.
3. Berkas checksum disertakan.

## 4. zsync

zsync dipakai untuk pembaruan parsial. Setiap ISO disertai berkas `.zsync`
yang dibuat dari ISO final.

## 5. Verifikasi

`tests/mirror-check.sh` memeriksa:

1. Struktur direktori.
2. Keberadaan checksum.
3. Kesesuaian nama artefak.
4. Ketersediaan symlink current.
