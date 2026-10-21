# Vendoring Tool ArashiOS

Dokumen ini menjelaskan bagaimana tool tier 1 masuk ke ArashiOS, bagaimana
integritasnya dijaga, dan bagaimana pembaruannya dilakukan.

## 1. Keputusan

Tool yang tidak tersedia di Debian bookworm diambil dari sumber upstream pada
saat build, diverifikasi checksum dan commit, lalu dipasang ke lokasi
terpisah. Repository pihak ketiga tidak pernah ditambahkan ke sistem
terpasang. Keputusan ini selaras dengan ADR-004.

## 2. Kebutuhan sumber

Setiap tool T1 harus punya:

1. Tag rilis dan commit yang dapat diverifikasi.
2. Lisensi yang mengizinkan distribusi ulang.
3. Perintah build yang dapat direproduksi.
4. Smoke test yang berjalan tanpa jaringan.
5. Status dukungan untuk amd64, arm64, dan i386.

## 3. Alur kerja

```text
scripts/refresh-source-pins.py     perbarui tag dan commit upstream
        |
        v
tools/source-pins.yaml             pin sumber yang diaudit
        |
        v
scripts/generate-toolstack.py      hasilkan manifest dan katalog runtime
        |
        v
vendor/manifests/<tool>.yaml       manifest per tool
        |
        v
scripts/build-vendor-tools.sh       bangun dari commit terkunci
        |
        v
scripts/check-glibc.py              audit glibc terhadap batas 2.36
        |
        v
vendor/artifacts.lock.json         hash artefak hasil build
        |
        v
arashios-arsenal verify            verifikasi checksum di cache lokal
```

## 4. Aturan build

| Aturan | Nilai |
|---|---|
| Go | `CGO_ENABLED=0`, `-trimpath`, `-ldflags "-s -w"` |
| Python | virtualenv terisolasi, tanpa `pip install` global |
| Ruby | gem dibangun dari sumber terkunci |
| Java | OpenJDK 17, JAR di direktori tetap |
| C dan C++ | build dari sumber, cek glibc wajib |
| glibc maksimum | 2.36 |
| Binary Go | statis, lolos audit glibc tanpa pemeriksaan simbol |

## 5. Audit glibc

```bash
scripts/check-glibc.py ./nuclei --max-glibc 2.36
```

Binary yang membutuhkan simbol glibc di atas 2.36 tidak dapat berjalan pada
Debian 12. Binary tersebut harus dibangun ulang terhadap glibc yang lebih
lama atau dipindahkan ke tier 3.

## 6. Status integritas

| Aspek | Status |
|---|---|
| Commit sumber | terkunci untuk 41 tool T1 |
| Checksum artefak | belum ada karena artefak belum dibangun |
| Checksum toolchain | terkunci untuk 9 komponen pada 3 arsitektur |
| Lisensi | diaudit dan tercatat di `docs/LICENSES.md` |
| Atribusi | tercatat di `NOTICE` |

## 7. Pembaruan

1. Pembaruan commit dilakukan pada siklus rilis, tidak pada build harian.
2. Setiap pembaruan melewati build, audit glibc, smoke test, dan audit lisensi.
3. CVE critical pada tool T1 menjadi blokir rilis.
4. Perubahan lisensi upstream tercatat di CHANGELOG.
5. Tool yang tidak dapat dibangun dengan aman dipindahkan ke tier 2 atau 3.

## 8. Pemeriksaan

```bash
python3 scripts/check-toolstack.py
python3 scripts/check-licenses.py
scripts/build-vendor-tools.sh --list
```
