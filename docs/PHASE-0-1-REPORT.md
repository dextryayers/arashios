# Laporan Fase 0 dan Fase 1

Tanggal: 21 Oktober 2026

Status: Fase 0 selesai pada tingkat deliverable, dengan dua butir exit gate yang memerlukan tindakan di luar repository. Fase 1 selesai pada tingkat implementasi, menunggu build dan boot test pada host dengan toolchain lengkap.

## 1. Ringkasan

| Fase | Target | Status |
|---|---|---|
| 0 | Fondasi repo, kebijakan, ADR, token, CI, requirement baseline | Selesai, dua butir exit gate terbuka |
| 1 | ISO live amd64 yang boot di UEFI dan BIOS, branding dasar, harness uji | Implementasi selesai, build belum dijalankan |

Fase 1 belum dapat dinyatakan lulus sampai ISO amd64 dibangun, diverifikasi, dan diuji boot pada QEMU UEFI serta BIOS. Laporan ini membedakan antara pekerjaan yang sudah divalidasi secara statis dan pekerjaan yang masih menunggu eksekusi.

## 2. Lingkungan

| Butir | Nilai |
|---|---|
| Host pengembangan | LMDE 7, basis Debian 13 trixie |
| CPU | 16 thread |
| RAM | 18.9 GiB |
| Ruang bebas | 38 GB pada `/home` |
| Virtualisasi | `/dev/kvm` dapat diakses |
| Firmware host | UEFI, Secure Boot dimatikan |
| Swap | Tidak ada |
| Tool build hilang | `lb`, `debootstrap`, `xorriso`, `qemu-system-x86_64`, `qemu-img`, OVMF |
| Tool build tersedia | `grub-mkimage`, `mcopy`, `mkfs.vfat`, `mksquashfs` |

Host pengembangan bukan acuan rilis. Build rilis harus memakai Debian 12 bookworm yang bersih atau container Debian 12.

## 3. Fase 0

### 3.1 Deliverable

| Area | Berkas | Status |
|---|---|---|
| Identitas proyek | `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` | Selesai |
| Versi | `versions.env`, `CHANGELOG.md` | Selesai |
| Build | `build.sh`, `Makefile` | Selesai |
| Kebijakan legal | `docs/LEGAL.md`, `docs/PRIVACY.md`, `docs/TRADEMARK.md` | Selesai |
| ADR | `docs/adr/001` sampai `docs/adr/012` | Selesai |
| Design token | `branding/tokens.json`, `scripts/generate-tokens.py` | Selesai |
| Aset merek | Logo, wordmark, wallpaper, GRUB, Plymouth | Selesai |
| Generator aset | `scripts/generate-brand-assets.py` | Selesai |
| Validasi | `scripts/check-env.sh`, `scripts/validate-config.sh`, `scripts/check-docs.sh`, `scripts/check-traceability.py` | Selesai |
| CI | `.github/workflows/ci.yml` | Selesai |
| Rilis | `.github/workflows/release.yml` | Selesai |
| Template kontribusi | Issue dan pull request template | Selesai |

### 3.2 Exit Gate

| Kriteria | Status | Bukti |
|---|---|---|
| `make lint` lulus | Lulus | Dijalankan dengan ShellCheck 0.10.0 dari binary statis. Validasi konfigurasi, dokumen, traceability, sintaks shell, dan sintaks Python lulus |
| Semua ADR disetujui | Lulus | 12 ADR berstatus Accepted |
| `check-env.sh` lulus | Belum | Tool build belum terpasang |
| Nama tidak bentrok | Belum diverifikasi hukum | Pencarian merek dan domain belum dilakukan |
| Token tervalidasi | Lulus | `generate-tokens.py --check` lulus, kontras tercatat |
| Requirement memiliki ID dan kriteria uji | Lulus | 58 requirement, 52 test case, semua tertrace |

Dua butir Fase 0 masih terbuka: pemasangan toolchain build dan verifikasi nama secara hukum. Keduanya memerlukan tindakan di luar repository.

### 3.3 Requirement dan Traceability

| Metrik | Nilai |
|---|---:|
| Requirement | 58 |
| Requirement tertrace | 58 |
| Test case | 52 |
| Test case direferensikan | 52 |
| ADR | 12 |
| Fase | 12 |
| Sub-fase | 94 |
| Baris plan | 2.902 |
| Kata plan | 17.474 |
| Ukuran plan | 99.230 byte |

Tujuh test case yang sebelumnya belum muncul langsung di matriks sudah ditambahkan ke requirement yang sesuai:

| Test | Requirement |
|---|---|
| `T-BOOT-05` sampai `T-BOOT-08` | `FR-001` |
| `T-DESK-04` | `FR-002` |
| `T-INST-07` dan `T-INST-08` | `FR-004` |

## 4. Fase 1

### 4.1 Deliverable

| Area | Berkas | Status |
|---|---|---|
| Build wrapper | `build.sh` | Selesai |
| Target build | `Makefile` | Selesai |
| Konfigurasi common | `config/common/` | Selesai |
| Edisi Cinnamon | `config/editions/cinnamon/` | Selesai |
| Edisi XFCE | `config/editions/xfce/` | Selesai |
| Edisi LXQt | `config/editions/lxqt/` | Selesai |
| Overlay amd64 | `config/arches/amd64/` | Selesai |
| Overlay arm64 | `config/arches/arm64/` | Selesai |
| Metadata sistem | `os-release`, `lsb-release`, `issue`, `build-info` | Selesai |
| Hardening | sysctl, UFW, AppArmor, SSH mask | Selesai |
| Branding boot | GRUB, Plymouth, LightDM, wallpaper | Selesai |
| Dotfile | Zsh, konfigurasi Starship, tmux, Neovim, Git, GTK, terminal | Selesai |
| Verifikasi artefak | `tests/verify-artifact.sh` | Selesai |
| Boot harness | `tests/qemu-boot.sh` | Selesai |
| Smoke test | `tests/smoke.sh` | Selesai |
| Dokumentasi build | `docs/BUILD.md` | Selesai |
| Dokumentasi arsitektur | `docs/ARCHITECTURE.md` | Selesai |
| Dokumentasi desain | `docs/DESIGN.md` | Selesai |

### 4.2 Konfigurasi Build

| Butir | Nilai |
|---|---|
| Distribusi | Debian 12 bookworm |
| Komponen APT | main, contrib, non-free, non-free-firmware |
| Format ISO | iso-hybrid |
| Boot amd64 | syslinux dan grub-efi |
| Boot i386 | syslinux |
| Boot arm64 | grub-efi |
| Kernel amd64 | `amd64` |
| Kernel i386 | `686-pae` |
| Kernel arm64 | `arm64` |
| User live | `arashi` |
| Hostname | `arashios` |
| Locale | `en_US.UTF-8` |
| Timezone | `UTC` |
| Keyboard | `us` |
| Backports | Tersedia, `NotAutomatic` |
| Repository Kali | Tidak ada |
| Telemetry | Tidak ada |

### 4.3 Edisi dan Paket

| Edisi | amd64 | arm64 | i386 |
|---|---:|---:|---:|
| Cinnamon | 233 | 231 | 213 |
| XFCE | 234 | 232 | 214 |
| LXQt | 242 | 240 | 222 |

Angka adalah paket unik dari irisan daftar paket. Dependency resolution dapat menambah paket pada image akhir.

### 4.4 Branding

| Aset | Berkas | Status |
|---|---|---|
| Mark | `branding/logo/arashios-mark.svg` | Selesai |
| Wordmark | `branding/logo/arashios-wordmark.svg` | Selesai |
| Wallpaper | `branding/wallpaper/kage-sumi.svg` | Selesai |
| Tema GRUB | `branding/grub/theme.txt` | Selesai |
| Latar GRUB | `branding/grub/background.png` | Selesai |
| Nine-slice | `branding/grub/select_*.png` | Selesai |
| Tema Plymouth | `branding/plymouth/arashios.plymouth` | Selesai |
| Skrip Plymouth | `branding/plymouth/arashios.script` | Selesai |
| Logo Plymouth | `branding/plymouth/logo.png` | Selesai |
| Token CSS | `build/tokens/tokens.css` | Selesai |
| QSS Qt | `build/tokens/kage.qss` | Selesai |
| Laporan kontras | `build/tokens/contrast.md` | Selesai |
| Preview | `build/tokens/preview.html` | Selesai |

Kontras utama:

| Pasangan | Rasio | Status |
|---|---:|---|
| Washi pada Sumi | 16.20:1 | Lulus AAA |
| Ash pada Sumi | 5.47:1 | Lulus AA |
| Ember pada Sumi | 6.51:1 | Lulus AA |
| Vermilion pada Sumi | 3.85:1 | Lulus untuk teks besar |
| Label tombol | 6.62:1 | Lulus AA |
| Sukses | 7.03:1 | Lulus AA |
| Peringatan | 9.90:1 | Lulus AA |
| Danger | 4.77:1 | Lulus AA |

### 4.5 Keamanan

| Kontrol | Implementasi | Status |
|---|---|---|
| SSH | Tidak dipasang, unit dimask | Selesai |
| UFW | Deny incoming, allow outgoing | Selesai |
| AppArmor | Paket dan profil, service aktif | Selesai |
| sysctl | kptr, dmesg, BPF, rp_filter, syncookies, IPv6 RA | Selesai |
| Rootless Podman | `uidmap`, `fuse-overlayfs`, `slirp4netns`, `subuid`, `subgid` | Selesai |
| Update | `unattended-upgrades` | Selesai |
| Repository | Tanpa Kali, backports dipin | Selesai |
| Telemetry | Tidak ada | Selesai |
| Autologin installed system | Belum dihapus | Fase 7 |

### 4.6 Pengujian

| Pemeriksaan | Perintah | Hasil |
|---|---|---|
| Sintaks shell | `bash -n` pada `build.sh`, `scripts/*.sh`, `tests/*.sh`, hook | Lulus |
| Sintaks Python | `python3 -m py_compile scripts/*.py` | Lulus |
| Validasi konfigurasi | `./scripts/validate-config.sh` | Lulus |
| Dokumen | `./scripts/check-docs.sh` | Lulus, 84 berkas |
| Traceability | `./scripts/check-traceability.py` | Lulus, 58 requirement dan 52 test |
| Token | `./scripts/generate-tokens.py --check` | Lulus |
| Aset raster | `./scripts/generate-brand-assets.py --check` | Lulus |
| ShellCheck | `shellcheck -x` | Lulus, ShellCheck 0.10.0 |
| Lint terpadu | `make lint` | Lulus dengan ShellCheck dari PATH sementara |
| Build ISO | `make build` | Belum dijalankan, toolchain belum lengkap |
| Verifikasi ISO | `make verify` | Belum dijalankan, ISO belum ada |
| Boot QEMU | `make test` | Belum dijalankan, ISO dan QEMU belum ada |
| Smoke test | `arashios-smoke` | Belum dijalankan, sesi live belum ada |

## 5. Audit Paket

### 5.1 Ketersediaan

| Butir | Jumlah |
|---|---:|
| Paket kandidat tersedia di bookworm | 130 |
| Paket kandidat tidak tersedia | 39 |
| Alias yang dikonfirmasi | 6 |

Alias yang dipakai:

| Nama kandidat | Paket Debian |
|---|---|
| `exiftool` | `libimage-exiftool-perl` |
| `impacket` | `python3-impacket` |
| `kubectl` | `kubernetes-client` |
| `pwntools` | `python3-pwntools` |
| `scapy` | `python3-scapy` |
| `ddrescue` | `gddrescue` |

### 5.2 Paket yang Tidak Tersedia

Paket berikut tidak dimasukkan ke daftar Fase 1 dan akan ditangani pada Fase 4 melalui vendoring atau penggantian:

```text
impacket-scripts
crackmapexec
enum4linux
enum4linux-ng
sslyze
burpsuite
rizin
cutter
bulk-extractor
wordlists
exploitdb
theharvester
```

Kebijakan:

1. Tidak menambahkan repository Kali permanen.
2. Tool yang tidak tersedia di Debian akan di-vendor dengan manifest dan checksum.
3. Setiap tool vendored harus lulus cek kompatibilitas glibc.
4. Tool yang tidak dapat di-vendor dengan aman akan diganti atau dihapus dari scope.

## 6. Perubahan Penting Selama Implementasi

| Perubahan | Alasan |
|---|---|
| i386 memakai `syslinux` saja | UEFI i386 tidak didukung pada v1 |
| Tiga edisi dikonfigurasi pada Fase 1 | Struktur common sudah stabil dan menghemat rework |
| BIOS memakai syslinux, bukan GRUB | Mengikuti default `live-build` dan mengurangi kompleksitas |
| Hook `0150-cli-aliases.chroot` ditambahkan | Debian mengganti nama `bat` menjadi `batcat` dan `fd` menjadi `fdfind` |
| `apparmor-utils` ditambahkan | Menyediakan alat audit profil |
| `60-lab` dibatasi ke QEMU | libvirt dan virt-manager ditunda ke Fase 4 agar image live ramping |
| Volume ID dihitung dari versi | Mencegah volume ID statis yang tidak cocok dengan versi |
| Metadata build diperluas | Mencatat host, versi live-build, dan hash konfigurasi |
| Traceability diperbaiki | Tujuh test case belum muncul langsung di matriks |
| Release workflow memakai path ISO eksplisit | Glob dapat mencocokkan lebih dari satu ISO untuk amd64 |
| CI dry-run memakai container Debian 12 | Menyamakan versi live-build dengan target rilis |

## 7. Risiko dan Batasan

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Toolchain host belum lengkap | Build dan boot belum dapat dibuktikan | Pasang paket host, jalankan `check-env.sh --strict` |
| Perbedaan versi live-build | Artefak berbeda dari target rilis | Build rilis pada Debian 12 bersih |
| ISO melebihi batas | Distribusi dan mirror terganggu | Audit paket, pindahkan tool ke Fase 4 |
| Plymouth tidak kompatibel | Boot logo tidak tampil | Verifikasi pada boot pertama, fallback ke teks |
| Autologin installed system | Risiko akses fisik | Hapus pada Calamares Fase 7 |
| arm64 dan i386 belum diuji | Paket dapat hilang | Validasi paket dan boot pada Fase 10 |
| Tema desktop belum penuh | Pengalaman visual belum final | Fase 2 dan Fase 3 |
| Signing belum aktif | Artefak belum dapat diverifikasi | Fase 9 |

## 8. Langkah Berikutnya

1. Pasang toolchain host:

```bash
sudo apt update
sudo apt install -y \
  live-build debootstrap xorriso squashfs-tools \
  isolinux syslinux-common syslinux-utils syslinux-efi \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools \
  qemu-system-x86 qemu-utils ovmf apt-cacher-ng shellcheck
```

2. Verifikasi host:

```bash
./scripts/check-env.sh --strict
```

3. Jalankan lint lengkap:

```bash
make lint
```

4. Build ISO amd64:

```bash
make build EDITION=cinnamon ARCH=amd64 JOBS=8
```

5. Verifikasi artefak:

```bash
make verify ISO=out/ArashiOS-amd64-V1.10.21.iso
```

6. Uji boot UEFI dan BIOS:

```bash
make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=uefi
make test ISO=out/ArashiOS-amd64-V1.10.21.iso BOOT_MODE=bios
```

7. Jalankan smoke test di sesi live sebagai user `arashi`:

```bash
arashios-smoke 2>&1 | tee ~/arashios-smoke.log
```

8. Perbaiki temuan build dan boot, lalu ulangi sampai exit gate Fase 1 lulus.

9. Commit seluruh pekerjaan dengan `git -c safe.directory=/home/aniipid/Project/arashios`.

## 9. Exit Gate Fase 1

| Kriteria | Status |
|---|---|
| ISO boot ke desktop di UEFI | Menunggu build |
| ISO boot ke desktop di BIOS | Menunggu build |
| Build dingin maksimal 60 menit | Menunggu pengukuran |
| Build hangat maksimal 20 menit | Menunggu pengukuran |
| Nama artefak sesuai pola | Lulus validasi statis |
| Checksum tersedia | Diimplementasikan, menunggu ISO |
| Tidak ada dependency error | Menunggu log build |
| Boot log serial tersedia | Diimplementasikan, menunggu ISO |

Fase 1 belum lulus. Implementasi sudah siap diuji, tetapi bukti build dan boot belum ada.

## 10. Fase 2

Fase 2 berfokus pada penyelesaian identitas Kage di seluruh boot chain dan desktop:

1. Finalisasi mark, wordmark, dan favicon.
2. Lima wallpaper 4K.
3. Tema GRUB final dan entri serial.
4. Animasi Plymouth dan verifikasi kompatibilitas.
5. Greeter LightDM final.
6. Tema GTK, Qt, kursor, dan ikon.
7. QA visual dan pengukuran waktu boot.
8. Dokumentasi desain final.

Fase 2 tidak boleh dimulai sebelum ISO Fase 1 dapat boot dan smoke test dasar berjalan.
