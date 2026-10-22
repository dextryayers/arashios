# Toolstack ArashiOS

Dokumen ini menjelaskan tool keamanan dan toolchain yang disediakan ArashiOS,
kebijakan tier, alur kerja yang dilayani, serta batas implementasi pada
Fase 4 dan Fase 5. Sumber kebenaran data ada di `tools/catalog.yaml`,
`tools/source-pins.yaml`, `toolchains/catalog.yaml`, dan `toolchains/lock.yaml`.

## 1. Prinsip

1. Tool T0 dari Debian bookworm selalu diutamakan.
2. Tool T1 dibangun dari sumber upstream yang terkunci pada commit tertentu.
3. Tool T2 diunduh pengguna sendiri dan tidak pernah masuk image.
4. Tool T3 berjalan sebagai container dengan digest terkunci.
5. Tidak ada repository pihak ketiga yang ditambahkan ke sistem terpasang.
6. Setiap tool memiliki manifest, smoke test, lisensi, dan status arsitektur.
7. Setiap tool yang dipasang tanpa sudo harus dapat dilepas tanpa sudo.

## 2. Tier dan-distribusi

| Tier | Sumber | Jumlah | Distribusi | Contoh |
|---|---|---:|---|---|
| T0 | Debian bookworm | 159 paket | image ISO | nmap, sqlmap, hashcat |
| T1 | Vendor upstream terkunci | 41 tool | image ISO | nuclei, netexec, radare2 |
| T2 | Unduhan pengguna | 10 tool | tidak didistribusikan | burpsuite, sliver |
| T3 | Container image | 5 image | tidak didistribusikan | dvwa, kali-rolling |

Total katalog 215 entri. Katalog tersedia sebagai JSON runtime di
`/usr/share/arashios/toolstack/catalog.json` dan sebagai YAML per tool di
`vendor/manifests`.

## 3. Alur kerja

Setiap alur kerja wajib punya minimal satu tool T0 dan satu tool T1.

| ID | Alur kerja | Tool T0 utama | Tool T1 utama |
|---|---|---|---|
| WF-01 | Reconnaissance | nmap, masscan, arp-scan, dnsrecon, whatweb | amass, subfinder, httpx |
| WF-02 | Web testing | sqlmap, ffuf, gobuster, nikto, dirsearch | nuclei, wpscan, feroxbuster |
| WF-03 | Exploitation | gdb, strace, python3-pwntools | metasploit-framework, exploitdb |
| WF-04 | Password attack | hydra, medusa, john, hashcat, cewl | seclists-core |
| WF-05 | Active Directory | python3-impacket, ldap-utils, smbmap | netexec, evil-winrm, certipy |
| WF-06 | Wireless | aircrack-ng, wifite, hcxtools | kismet |
| WF-07 | Network interception | wireshark, tshark, tcpdump, bettercap | responder, termshark |
| WF-08 | Pivoting | proxychains4, socat, openssh-client | chisel, ligolo-ng |
| WF-09 | Forensics | sleuthkit, testdisk, foremost, binwalk | volatility3 |
| WF-10 | Reverse engineering | gdb, apktool, python3-pwntools, patchelf | radare2, rizin, jadx |
| WF-11 | Cloud dan container | podman, awscli, azure-cli, kubectl | trivy, helm |
| WF-12 | Reporting | pandoc, libreoffice, jq, yq | fastfetch |

## 4. Tool T0

Daftar paket berada di `config/common/package-lists/20-security.list.chroot`.
Semua paket diverifikasi tersedia di bookworm untuk amd64, arm64, dan i386.
Paket yang hanya tersedia pada sebagian arsitektur, seperti `ltrace` dan
`thermald`, berada di overlay arsitektur.

Pemeriksaan:

```bash
python3 scripts/check-toolstack.py
```

Pemeriksaan memverifikasi nama paket, duplikasi, kelengkapan alur kerja,
konsistensi manifest, dan kebijakan lisensi.

## 5. Tool T1

### 5.1 Manifest

Setiap tool T1 memiliki manifest di `vendor/manifests/<tool>.yaml` dengan
versi, sumber, commit, lisensi, dukungan arsitektur, perintah build, lokasi
install, dan smoke test.

```yaml
name: nuclei
version: 3.11.1
tier: T1
source: https://github.com/projectdiscovery/nuclei.git
source_ref: v3.11.1
source_commit: a8c88feb4a1c8e961b7902534ce3af97e9d524a4
license: MIT
arch:
  amd64: supported
  arm64: supported
  i386: supported
build:
  kind: go
  go_version: "1.23"
  command: CGO_ENABLED=0 GOOS=linux GOARCH=$TARGETARCH go build ...
artifact:
  status: source-locked
  sha256: ""
install:
  path: /usr/local/bin/nuclei
test:
  kind: version
  command: [nuclei]
```

### 5.2 Siklus hidup

1. `scripts/refresh-source-pins.py` memperbarui tag dan commit upstream.
2. `scripts/build-vendor-tools.sh` membangun tool dari commit terkunci.
3. `scripts/check-glibc.py` memastikan binary tidak membutuhkan glibc di atas
   2.36. Binary yang gagal audit dipindahkan ke tier 3.
4. Hash artefak dicatat di `vendor/artifacts.lock.json`.
5. `arashios-arsenal verify` memeriksa checksum artefak di cache lokal.

### 5.3 Status saat ini

Status sumber sudah terkunci untuk 41 tool. Artefak nuclei 3.11.1 dan
subfinder 2.17.0 sudah dibangun dari commit yang dipin, lolos audit glibc
sebagai binary statis, dan hash-nya tercatat di `vendor/artifacts.lock.json`
serta di manifest masing-masing. Sembilan puluh satu tool lain masih
berstatus `source-locked` karena artefaknya belum dibangun.

## 6. Smoke test

`arashios-tool-smoke` menjalankan smoke test setiap tool tanpa jaringan.
Tool T0 diuji dengan keberadaan biner dan probe versi. Tool T1 diuji dengan
perintah versi dan pencocokan keluaran.

```bash
arashios-tool-smoke --tier T0
arashios-tool-smoke --workflow WF-02 --output /tmp/report.json
```

Hasil disimpan sebagai JSON dan dapat dipakai sebagai bukti rilis.

## 7. Arsenal

Arsenal adalah antarmuka tunggal untuk melihat, memasang, memasang ulang, dan
memverifikasi tool. Dokumentasi lengkap ada di [ARSENAL.md](ARSENAL.md).

```bash
arashios-arsenal list --workflow WF-05
arashios-arsenal info nuclei
arashios-arsenal install nuclei --dry-run
arashios-arsenal verify --tier T1 --strict
arashios-arsenal doctor
```

Aturan keamanan Arsenal:

1. Tool T0 dipasang lewat apt dan ditolak tanpa hak root.
2. Tool T1 dipasang dari cache lokal setelah checksum cocok.
3. Tool T2 hanya menampilkan instruksi unduhan upstream.
4. Tool T3 hanya berjalan melalui `arashios-lab` dengan digest terkunci.
5. `remove` hanya menghapus berkas yang dicatat Arsenal.

## 8. Wordlist

Wordlist ArashiOS berada di `/usr/share/wordlists/arashios` dengan lisensi
CC-BY-SA-4.0. Isinya adalah kurasi internal, bukan salinan dataset pihak
ketiga. Setiap berkas memiliki checksum di `manifest.json`.

| Berkas | Entri | Kegunaan |
|---|---:|---|
| common-paths.txt | 129 | brute force direktori |
| common-subdomains.txt | 129 | enumerasi subdomain |
| common-parameters.txt | 68 | fuzzing parameter |
| common-passwords.txt | 84 | audit kredensial |
| common-usernames.txt | 60 | enumerasi pengguna |
| detection-payloads.txt | 29 | deteksi kelas kerentanan |

Dataset pihak ketiga seperti SecLists adalah tool T1 dan rockyou adalah tool
T2, keduanya tidak masuk image sebagai data mentah.

## 9. Container

Container memakai Podman rootless. Image lab dikunci dengan digest dan
dijalankan tanpa mode privileged serta tanpa akses jaringan host. Detail
kebijakan ada di [CONTAINERS.md](CONTAINERS.md).

## 10. Kebijakan pembaruan

| Komponen | Sumber | SLA critical | SLA high |
|---|---|---|---|
| Debian security | Debian | 24 jam | 7 hari |
| Tool T0 | Debian | mengikuti Debian | mengikuti Debian |
| Tool T1 | Upstream terkunci | 7 hari | 30 hari |
| Tool T2 | Upstream | pengguna | pengguna |
| Tool T3 | Image upstream | 30 hari | 60 hari |

1. CVE critical yang belum dimitigasi memblokir rilis.
2. CVE high wajib dimitigasi atau didokumentasikan.
3. Versi T1 baru selalu menyertai pembaruan manifest dan pengujian ulang.
4. Pemeriksaan lisensi dijalankan pada setiap rilis.

## 11. Pemeriksaan yang dijalankan

```bash
python3 scripts/check-toolstack.py
python3 scripts/check-wordlists.py
python3 scripts/check-licenses.py
python3 scripts/generate-toolstack.py --check
./tests/toolstack.sh
```

## 12. Batasan saat ini

1. Artefak T1 belum dibangun sehingga `artifact.sha256` masih kosong.
2. Smoke test runtime hanya bisa dijalankan pada image yang sudah dibangun.
3. Image lab juice-shop belum memiliki digest terkunci dan ditolak sampai
   digest tersedia.
4. Audit lisensi paket Debian dilakukan lewat metadata paket pada sistem
   terpasang, bukan lewat pembacaan berkas copyright per paket.
5. Container T3 belum diuji pada host tanpa Podman.
