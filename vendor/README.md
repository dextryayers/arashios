# Vendor ArashiOS

Direktori ini menyimpan deskripsi tool tier 1 yang dibangun dari sumber
upstream terkunci. Direktori ini tidak berisi binary hasil build.

```text
vendor/
├── manifests/     satu manifest YAML per tool, hasil generate
│   └── index.yaml  ringkasan tier, workflow, dan jumlah tool
└── artifacts.lock.json  hash artefak hasil build, diisi saat pipeline vendor
```

## Isi direktori

| Path | Isi | Dibuat oleh |
|---|---|---|
| `manifests/<tool>.yaml` | versi, sumber, commit, lisensi, arsitektur, build, install, test | `scripts/generate-toolstack.py` |
| `manifests/index.yaml` | jumlah tool per tier dan coverage alur kerja | `scripts/generate-toolstack.py` |
| `artifacts.lock.json` | SHA-256 artefak binary per tool dan arsitektur | `scripts/build-vendor-tools.sh` |

## Aturan

1. Manifest tidak diedit manual. Sumbernya ada di `tools/catalog.yaml` dan
   `tools/source-pins.yaml`.
2. Binary tidak disimpan di repository. Artefak dibangun pada host build dan
   diverifikasi lewat checksum.
3. Cache artefak lokal berada di `~/.cache/arashios/vendor`.
4. Tool yang tidak dapat dibangun dengan aman dipindahkan ke tier 2 atau 3.
5. Binary yang membutuhkan glibc di atas 2.36 ditolak oleh
   `scripts/check-glibc.py`.

## Pemeriksaan

```bash
python3 scripts/generate-toolstack.py --check
python3 scripts/check-toolstack.py
./scripts/build-vendor-tools.sh --list
```
