# Rotasi Kunci Repository ArashiOS

Dokumen ini menjelaskan prosedur rotasi kunci signing repository ArashiOS.

## 1. Kebijakan

| Aspek | Nilai |
|---|---|
| Algoritma | RSA 4096 |
| Masa berlaku kunci | 3 tahun |
| Peringatan | 6 bulan sebelum kedaluwarsa |
| Kunci cadangan | Dua lokasi fisik terpisah |
| Penghapusan | Memerlukan dua maintainer |
| Publikasi | Fingerprint pada release notes dan README |

## 2. Jadwal

| Waktu | Tindakan |
|---|---|
| 12 bulan sebelum kedaluwarsa | Jadwalkan rotasi, buat kunci baru |
| 6 bulan sebelum kedaluwarsa | Publikasikan fingerprint baru |
| 3 bulan sebelum kedaluwarsa | Tanda tangan repository dengan kunci baru dan lama |
| Saat kedaluwarsa | Kunci lama ditarik dari keyring paket |

## 3. Membuat kunci baru

```bash
export ARASHIOS_REPO_KEY_PASSPHRASE='passphrase-yang-kuat'
mv repo/keys/gnupg repo/keys/gnupg.lama
./scripts/generate-repo-key.sh
```

Kunci privat tidak pernah masuk image, repository publik, atau arsip rilis.
Kunci cadangan disimpan pada media offline.

## 4. Paket keyring dengan dua kunci

Selama masa transisi, paket `arashios-repo-keyring` memuat kunci lama dan
kunci baru:

```bash
gpg --export --armor OLD_FINGERPRINT > repo/keys/arashios-archive-keyring.asc
gpg --export --armor NEW_FINGERPRINT >> repo/keys/arashios-archive-keyring.asc
python3 scripts/build-packages.py --package arashios-repo-keyring
```

Sistem terpasang yang belum diperbarui tetap dapat memverifikasi repository
yang ditandatangani dengan kunci lama.

## 5. Penghapusan kunci lama

1. Pastikan seluruh kanal rilis ditandatangani dengan kunci baru.
2. Pastikan tidak ada image rilis aktif yang hanya memuat kunci lama.
3. Bangun paket keyring baru tanpa kunci lama.
4. Terbitkan rilis keyring melalui kanal stable.
5. Simpan kunci lama yang dicabut di arsip internal, bukan di publik.

## 6. Pemeriksaan

```bash
gpgv --keyring repo/keys/arashios-archive-keyring.gpg \
    repo/public/dists/stable/InRelease
cat repo/keys/arashios-archive.fingerprint
```

Fingerprint pada `docs/REPOSITORY.md` dan release notes harus sama dengan
berkas fingerprint.
