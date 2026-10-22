# Kebijakan Kerentanan ArashiOS

Dokumen ini menjelaskan bagaimana ArashiOS memindai, menilai, dan menangani
kerentanan pada image, paket, dan tool vendor.

## 1. Pemindai

| Pemindai | Cakupan | Keterangan |
|---|---|---|
| debsecan | Paket Debian terhadap CVE yang sudah dipublikasikan | Memakai database Debian dan paket usn |
| trivy | Image filesystem dan image container | CVE paket dan image |
| grype | Image filesystem dan image container | Cocokkan dengan basis data Nichols Advisory |
| CVE yang belum dipublikasikan | Diterima lewat kanal privat | Tidak dipindai, ditangani lewat advisori |

## 2. Menjalankan Pemindaian

```bash
./scripts/scan-vulnerabilities.sh --output build/vulnerability-report.json
```

Pemindai yang tidak tersedia dilaporkan sebagai `skipped` sehingga laporan
selalu menyatakan sumber buktinya. Laporan JSON berisi:

| Field | Arti |
|---|---|
| `scanners` | Status tiap pemindai |
| `counts` | Jumlah temuan per severity |
| `findings` | Daftar temuan lengkap dengan paket dan versi |
| `blocking` | Jumlah temuan yang melewati ambang |
| `threshold` | Ambang severity yang dianggap memblokir rilis |

## 3. Ambang

| Severity | Tindakan |
|---|---|
| Critical | Blokir rilis, diperbaiki dalam 24 jam |
| High | Blokir rilis, diperbaiki dalam 7 hari |
| Medium | Perbaiki pada rilis berikutnya atau documented |
| Low | Catat dan tinjau |

Exit gate Fase 9 mensyaratkan tidak adanya CVE critical atau high yang
terbuka pada artefak rilis.

## 4. Jalur Perbaikan

1. Base Debian menerima patch keamanan melalui `unattended-upgrades`.
2. Tool tier 1 dibangun ulang dari sumber yang sudah dipin dengan versi baru.
3. Tool tier 2 diberi tahu pengguna untuk memperbarui sendiri.
4. Image rebuilt dan seluruh lapis QA diulang.
5. Advisory keamanan diterbitkan beserta nomor CVE bila impactful.

## 5. Pemindaian Image

```bash
# Ekstrak image untuk dipindai
mkdir -p build/rootfs
sudo unsquashfs -d build/rootfs out/ArashiOS-amd64-V1.10.21.iso live/filesystem.squashfs

# Pindai
./scripts/scan-vulnerabilities.sh --root build/rootfs \
    --output build/vulnerability-report.json
```

## 6. Pelaporan

Kerentanan pada ArashiOS dilaporkan lewat kanal privat pada [SECURITY.md](../SECURITY.md).
Kerentanan pada tool pihak ketiga dilaporkan ke upstream masing-masing.

## 7. Batasan saat ini

1. Pemindai belum terpasang pada host pengembangan.
2. Pemindaian image nyata belum dilakukan karena image belum dibangun.
3. Basis data CVE tidak dapat dipakai tanpa jaringan.
