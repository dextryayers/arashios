# Arsenal ArashiOS

Arsenal adalah antarmuka baris perintah untuk katalog tool ArashiOS. Arsenal
tidak menambah repository pihak ketiga, tidak memasang paket tanpa verifikasi,
dan tidak meninggalkan berkas yang tidak dapat dilepas.

## 1. Perintah

| Perintah | Fungsi |
|---|---|
| `list` | Daftar tool dengan filter tier, alur kerja, dan peran |
| `info <tool>` | Detail tool, sumber, versi, lisensi, dan lokasi install |
| `workflows` | Coverage tool pada 12 alur kerja keamanan |
| `verify [tool]` | Verifikasi keberadaan biner dan checksum artefak |
| `install <tool>` | Pasang tool sesuai tiernya |
| `remove <tool>` | Hapus tool yang dipasang Arsenal |
| `doctor` | Ringkasan kesiapan toolstack |
| `smoke [tool]` | Jalankan smoke test tool |

Opsi umum:

| Opsi | Fungsi |
|---|---|
| `--json` | Keluaran JSON untuk pemrosesan lanjutan |
| `--catalog PATH` | Lintak katalog toolstack lain |

## 2. Contoh

```bash
# Tool T0 untuk alur kerja Active Directory
arashios-arsenal list --tier T0 --workflow WF-05

# Rincian tool T1
arashios-arsenal info netexec

# Rencana pemasangan tanpa mengubah sistem
arashios-arsenal install nuclei --dry-run

# Verifikasi ketat untuk tool T1
arashios-arsenal verify --tier T1 --strict

# Ringkasan kesiapan
arashios-arsenal doctor --json
```

## 3. Perilaku per tier

### Tier 0

Tool T0 berasal dari Debian. `install` menjalankan `apt-get install` dan
menolak berjalan tanpa hak root. `remove` menolak menghapus paket Debian
karena itu keputusan administrator sistem.

### Tier 1

Tool T1 dibangun dari sumber terkunci. `install` hanya berjalan bila artefak
ada di cache lokal dan checksum cocok dengan `artifact.sha256`. Biner
dipasang ke `~/.local/bin` dan dicatat di state Arsenal.

```bash
arashios-arsenal install nuclei --from ./nuclei-3.11.1-amd64.tar.gz
```

Cache artefak memakai lokasi berikut:

| Lokasi | Kegunaan |
|---|---|
| `$ARASHIOS_VENDOR_CACHE` | overrides cache untuk pengujian |
| `~/.cache/arashios/vendor` | cache default pengguna |
| `/var/cache/arashios/vendor` | cache sistem untuk image |

### Tier 2

Tool T2 proprietary atau berukuran besar. Arsenal tidak mengunduh dan tidak
memasangnya. Perintah hanya menampilkan arah unduhan dari upstream.

### Tier 3

Tool T3 berjalan sebagai container. Arsenal mengarahkan pengguna ke
`arashios-lab`, yang menolak image tanpa digest.

## 4. State dan pelepasan

Arsenal menyimpan daftar instalasi miliknya di
`~/.local/share/arashios/arsenal-state.json`. Hanya tool yang tercatat di
berkas tersebut yang dapat dilepas dengan `remove`. Tool sistem, tool T2, dan
tool T3 tidak pernah disentuh.

## 5. Keluar JSON

Semua perintah mendukung `--json` sehingga hasil dapat dipakai oleh skrip
audit, dan laporan rilis.

```bash
arashios-arsenal list --json | python3 -c "import json,sys;print(len(json.load(sys.stdin)['tools']))"
```

## 6. Integrasi dengan CI

```bash
arashios-arsenal verify --tier T0 --strict
arashios-tool-smoke --tier T0 --output build/toolstack-smoke.json
```
