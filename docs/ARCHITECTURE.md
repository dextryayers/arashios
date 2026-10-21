# Arsitektur ArashiOS

Dokumen ini menjelaskan arsitektur teknis ArashiOS pada Fase 0 sampai Fase 3. Sumber kebenaran scope tetap [plan.md](../plan.md). Keputusan arsitektur yang mengikat dicatat di [docs/adr](adr/README.md).

## 1. Tujuan dan Batasan

ArashiOS adalah distribusi berbasis Debian 12 bookworm dengan tiga edisi desktop dan tiga arsitektur. Fase 1 membuktikan pipeline build, boot hybrid, branding dasar, dan pengujian otomatis pada amd64. Fase 2 dan Fase 3 menambahkan paket branding, tema Kage untuk GTK, Cinnamon, XFCE, Openbox, dan Kvantum, serta konfigurasi tiga desktop pada tingkat statis. Installer, repository mandiri, tool keamanan yang di-vendor, dan validasi boot belum aktif.

Batasan yang memengaruhi arsitektur:

1. Basis paket adalah Debian 12 bookworm. Komponen yang dipakai: `main`, `contrib`, `non-free`, dan `non-free-firmware`.
2. Live image memakai `live-build` dengan image `iso-hybrid`, squashfs, dan dukungan BIOS serta UEFI pada amd64.
3. Tidak ada repository pihak ketiga permanen pada sistem terpasang. Tool non-Debian akan di-vendor pada Fase 4.
4. Semua kustomisasi harus dapat dilacak ke repository. Tidak ada perubahan manual pada image jadi.
5. arm64 dan i386 disiapkan pada konfigurasi, tetapi validasi build dan boot dilakukan pada Fase 10.

## 2. Lapisan Sistem

```text
+------------------------------------------------------------------+
| Aplikasi                                                         |
| tool keamanan, tool coding, aplikasi harian, arsenal             |
+------------------------------------------------------------------+
| Desktop                                                          |
| Cinnamon / XFCE / LXQt, LightDM, tema Kage                       |
+------------------------------------------------------------------+
| Paket dan konfigurasi ArashiOS                                   |
| branding, tema, desktop, metadata, hardening, skel               |
+------------------------------------------------------------------+
| Debian 12 bookworm                                               |
| kernel 6.1 LTS, systemd, APT, firmware, security archive         |
+------------------------------------------------------------------+
| Live layer                                                       |
| live-boot, live-config, squashfs, iso-hybrid, persistence        |
+------------------------------------------------------------------+
| Firmware dan bootloader                                          |
| UEFI GRUB, BIOS syslinux, OVMF dan SeaBIOS pada pengujian        |
+------------------------------------------------------------------+
```

Setiap lapisan memiliki kontrak yang jelas. Lapisan aplikasi tidak boleh mengubah konfigurasi boot. Lapisan desktop tidak boleh menambah repository. Lapisan live tidak boleh menyimpan state permanen tanpa mekanisme persistence yang eksplisit.

## 3. Komposisi Konfigurasi Build

`build.sh` menjalankan `lb config`, lalu menyalin overlay ke direktori kerja. Urutan overlay menentukan nilai akhir. Overlay yang disalin belakangan menimpa file dengan nama yang sama.

| Urutan | Sumber | Isi |
|---:|---|---|
| 1 | Default `live-build` | Struktur config, archive, bootloader default |
| 2 | `config/common` | Paket dasar, keamanan, coding, harian, include, hook, archive |
| 3 | `config/editions/<edition>` | Paket desktop dan konfigurasi LightDM |
| 4 | `config/arches/<arch>` | Toolchain modern dan paket laboratorium khusus arsitektur |
| 5 | Hasil generate `build.sh` | Metadata versi, branding, token, dokumentasi, smoke test |

Konsekuensi:

1. File di `config/editions` dapat menimpa file di `config/common`.
2. File di `config/arches` dapat menimpa file edisi dan common.
3. Metadata di `/etc/arashios` selalu dihasilkan pada build, bukan disimpan sebagai file statis.
4. Branding dan token disalin dari sumbernya pada setiap build agar tidak ada salinan yang basi.

### 3.1 Struktur Direktori

```text
config/
├── arches/
│   ├── amd64/package-lists/
│   ├── arm64/package-lists/
│   └── i386/package-lists/
├── common/
│   ├── archives/
│   ├── hooks/live/
│   ├── includes.chroot/
│   └── package-lists/
└── editions/
    ├── cinnamon/
    ├── lxqt/
    └── xfce/
```

Setiap edisi memiliki `package-lists/50-desktop.list.chroot` dan `includes.chroot/etc/lightdm/lightdm.conf.d/50-arashios.conf`. Overlay arsitektur memuat paket yang tidak tersedia di semua arsitektur. `ltrace` dan `thermald` hanya tersedia untuk amd64 dan i386, sehingga keduanya berada di `35-arch-tools.list.chroot` pada kedua overlay tersebut.

### 3.2 Daftar Paket

Daftar paket memakai awalan numerik untuk urutan baca, bukan urutan instalasi yang ketat.

| Berkas | Cakupan | Isi utama |
|---|---|---|
| `00-base.list.chroot` | Semua edisi | live-boot, live-config, APT, firmware, UFW, AppArmor, utilitas dasar |
| `10-desktop-common.list.chroot` | Semua edisi | Xorg, LightDM, font, icon theme, PulseAudio, NetworkManager |
| `20-security.list.chroot` | Semua edisi | Recon, web, password, wireless, forensics, container |
| `30-dev-core.list.chroot` | Semua edisi | GCC, Python, Git, Neovim, tmux, database client |
| `40-daily.list.chroot` | Semua edisi | Firefox ESR, LibreOffice, VLC, GIMP, KeePassXC, Timeshift |
| `50-desktop.list.chroot` | Per edisi | Cinnamon, XFCE, atau LXQt dan aplikasi khasnya |
| `31-dev-modern.list.chroot` | amd64 dan arm64 | Clang, Rust, Node.js, Java, PHP, Ruby, Go tools |
| `35-arch-tools.list.chroot` | amd64 dan i386 | ltrace, thermald |
| `60-lab.list.chroot` | amd64 | QEMU dan qemu-utils |

Jumlah paket unik pada validasi terakhir:

| Edisi | amd64 | arm64 | i386 |
|---|---:|---:|---:|
| Cinnamon | 233 | - | - |
| XFCE | 234 | 230 | 214 |
| LXQt | 242 | 238 | 222 |

Angka ini adalah irisan paket dari daftar, bukan ukuran image terpasang. Dependency resolution dapat menambah paket. Kombinasi Cinnamon arm64 dan i386 tidak didukung pada v1. arm64 tidak memuat `ltrace` dan `thermald` karena kedua paket tidak dibangun untuk arm64.

Lab virtual pada amd64 memakai QEMU dan qemu-utils. libvirt dan virt-manager ditunda ke Fase 4 sebagai paket opsional pada sistem terpasang agar image live tidak menjalankan daemon tambahan.

## 4. Alur Boot

### 4.1 UEFI amd64

```text
Firmware UEFI
  |
  +-- OVMF atau firmware perangkat
        |
        v
      EFI/BOOT/BOOTX64.EFI
        |
        v
      GRUB EFI
        |
        v
      menu GRUB ArashiOS
        |
        v
      kernel linux-image-amd64 + initramfs
        |
        v
      live-boot memasang squashfs
        |
        v
      systemd
        |
        v
      LightDM dan sesi desktop
```

ISO membawa GRUB EFI melalui `--bootloaders syslinux,grub-efi`. `xorriso` menulis El Torito UEFI dan MBR hybrid. Secure Boot tidak didukung pada v1 dan harus dimatikan pada perangkat uji.

### 4.2 BIOS amd64 dan i386

```text
Firmware BIOS
  |
  +-- MBR hybrid ISO
        |
        v
      ISOLINUX
        |
        v
      menu ArashiOS
        |
        v
      kernel dan initramfs
        |
        v
      live-boot dan systemd
```

amd64 memakai `syslinux` dan `grub-efi`. i386 memakai `syslinux` saja. UEFI i386 tidak didukung karena firmware UEFI 32-bit dan kombinasi paketnya tidak menjadi target v1.

### 4.3 Urutan Layanan

Setelah `live-boot` memasang rootfs squashfs, systemd menjalankan unit dasar Debian. Layanan yang relevan untuk ArashiOS:

1. `systemd-sysctl` menerapkan `/etc/sysctl.d/99-arashios-hardening.conf`.
2. `apparmor.service` memuat profil.
3. `ufw.service` menerapkan kebijakan firewall.
4. `NetworkManager.service` menyalakan antarmuka jaringan.
5. `lightdm.service` menampilkan greeter atau autologin ke sesi live.
6. `arashios-wallpaper.desktop` menerapkan wallpaper setelah sesi dimulai.

`openssh-server` tidak dipasang dan unit `ssh` dimask. Remote access tidak aktif secara default.

## 5. Live Runtime

| Komponen | Nilai | Catatan |
|---|---|---|
| Boot parameter | `boot=live components quiet splash console=tty0 console=ttyS0,115200` | Ditambah `username`, `hostname`, `locales`, `keyboard-layouts`, `timezone` |
| User live | `arashi` | Tanpa password, hanya untuk sesi live |
| Hostname | `arashios` | Ditetapkan pada build dan boot |
| Autologin | Aktif | LightDM langsung masuk ke sesi live |
| Locale | `en_US.UTF-8` | Locale tambahan dapat dipasang pengguna |
| Keyboard | `us` | Dapat diubah pada installer Fase 7 |
| Timezone | `UTC` | Dapat diubah pada installer Fase 7 |
| Persistence | Belum aktif | Direncanakan pada Fase 7 |
| Shell | Zsh | Diatur oleh script live-config `9990-arashios-shell` |
| Installer | Belum ada | Calamares direncanakan pada Fase 7 |

Autologin hanya boleh berlaku pada sesi live. Pada Fase 7, Calamares harus menghapus `autologin-user` dan `autologin-session` dari konfigurasi LightDM sistem terpasang. Sampai langkah itu ada, image tidak boleh dipakai sebagai sistem produksi.

## 6. Tata Letak Berkas ArashiOS

| Path | Isi | Sumber |
|---|---|---|
| `/etc/arashios/version` | Versi rilis | `build.sh` |
| `/etc/arashios/edition` | Nama edisi | `build.sh` |
| `/etc/arashios/arch` | Arsitektur | `build.sh` |
| `/etc/arashios/build-info` | Metadata build | `build.sh` |
| `/etc/os-release` | Identitas sistem | `config/common/includes.chroot` |
| `/etc/arashios/` | Metadata runtime | Generated |
| `/usr/share/arashios/theme/` | Token CSS, QSS, JSON, manifest tema | `build/tokens`, `build/theme` |
| `/usr/share/themes/ArashiKage*` | Tema GTK, Cinnamon, XFCE, Openbox | `build/theme` |
| `/usr/share/Kvantum/ArashiKage*` | Tema Qt | `build/theme` |
| `/usr/share/arashios/branding/` | Wordmark dan aset merek | `branding/` |
| `/usr/share/backgrounds/arashios/` | Wallpaper | `branding/wallpaper` |
| `/usr/share/grub/themes/arashios/` | Tema GRUB | `branding/grub` |
| `/usr/share/plymouth/themes/arashios/` | Tema Plymouth | `branding/plymouth` |
| `/usr/share/icons/hicolor/scalable/apps/arashios.svg` | Ikon aplikasi | `branding/logo` |
| `/usr/local/bin/arashios-wallpaper` | Penerap wallpaper | `config/common/includes.chroot` |
| `/usr/local/bin/arashios-smoke` | Smoke test | `tests/smoke.sh` |
| `/usr/local/bin/bat` | Alias `batcat` | Hook `0150-cli-aliases.chroot` |
| `/usr/local/bin/fd` | Alias `fdfind` | Hook `0150-cli-aliases.chroot` |

## 7. Keamanan

### 7.1 Postur Default

| Kontrol | Implementasi | Lokasi |
|---|---|---|
| Firewall | UFW, deny incoming, allow outgoing | `00-base.list.chroot`, hook `0200-services.chroot` |
| AppArmor | Paket `apparmor`, `apparmor-utils`, profil | `00-base.list.chroot`, hook `0200-services.chroot` |
| SSH | Tidak dipasang, unit dimask | `00-base.list.chroot`, hook `0200-services.chroot` |
| Kernel hardening | sysctl terkait pointer, dmesg, BPF, rp_filter, syncookies | `etc/sysctl.d/99-arashios-hardening.conf` |
| Update otomatis | `unattended-upgrades` | `00-base.list.chroot` |
| Container | Podman rootless, `subuid`, `subgid`, `uidmap` | `20-security.list.chroot`, include |
| Repository | Tidak ada Kali, backports dengan pinning | `archives/`, `apt/preferences.d/` |
| Telemetry | Tidak ada | Tidak ada paket atau service telemetry |

### 7.2 Batas Kepercayaan

1. Build host adalah batas kepercayaan tertinggi. Host yang disusupi dapat menghasilkan ISO yang disusupi.
2. Mirror Debian dan snapshot adalah sumber paket. HTTPS dan signature APT dipakai untuk verifikasi.
3. Tool vendored pada Fase 4 akan memiliki manifest, checksum, dan sumber yang tercatat.
4. Signing ISO belum aktif. Fase 9 menambahkan minisign dan verifikasi checksum pada pipeline rilis.
5. Repository ArashiOS belum ada. Pembaruan saat ini mengikuti Debian security melalui APT.

### 7.3 Repository dan Pinning

| Sumber | Komponen | Perilaku |
|---|---|---|
| Debian bookworm | main, contrib, non-free, non-free-firmware | Default |
| Debian bookworm-security | main, contrib, non-free, non-free-firmware | Update keamanan |
| Debian bookworm-backports | main, contrib, non-free, non-free-firmware | `NotAutomatic`, tidak untuk upgrade otomatis |

Backports dipakai hanya untuk paket yang secara eksplisit membutuhkan versi lebih baru. Tidak ada repository Kali atau repository pihak ketiga lain yang ditambahkan pada sistem terpasang.

## 8. Arsitektur dan Edisi

| Arsitektur | Kernel | Bootloader | Edisi default | Status Fase 1 |
|---|---|---|---|---|
| amd64 | `amd64` 6.1 | syslinux dan grub-efi | Cinnamon | Target build dan boot |
| arm64 | `arm64` 6.1 | grub-efi | XFCE | Konfigurasi disiapkan, build Fase 10 |
| i386 | `686-pae` | syslinux | LXQt | Konfigurasi disiapkan, build Fase 10 |

Aturan nama artefak:

```text
ArashiOS-<arch>-<version>[-<edition>].iso
```

Edisi default per arsitektur tidak memakai sufiks. Edisi non-default memakai sufiks `-cinnamon`, `-xfce`, atau `-lxqt`. Contoh:

```text
ArashiOS-amd64-V1.10.21.iso
ArashiOS-amd64-V1.10.21-xfce.iso
ArashiOS-i386-V1.10.21-xfce.iso
```

## 9. Build dan Reproducibility

Pipeline build:

```text
Validasi argumen
  |
  v
lb config
  |
  v
Salin overlay common, edisi, arsitektur
  |
  v
Generate metadata, token, branding
  |
  v
lb build
  |
  v
Rename ISO, checksum, signature opsional
```

Kontrol reproducibility yang sudah ada:

1. Versi dan codename berasal dari `versions.env`.
2. `SOURCE_DATE_EPOCH` dapat ditetapkan untuk metadata build.
3. Snapshot Debian dapat dikunci dengan `DEBIAN_SNAPSHOT`.
4. `MKSQUASHFS_OPTIONS` memakai jumlah proses yang eksplisit.
5. Token dan aset raster dihasilkan secara deterministik dari sumber JSON dan SVG.

Kontrol yang belum ada:

1. Normalisasi timestamp seluruh berkas di rootfs.
2. UUID ISO deterministik.
3. `diffoscope` antara dua build.
4. Repositori snapshot keamanan.
5. Signature dan attestation build.

Target hash identik baru berlaku pada Fase 9. Fase 1 hanya menjamin artefak dapat dibangun ulang dengan input yang sama, bukan hash yang identik.

## 10. Pengujian

| Lapisan | Alat | Cakupan |
|---|---|---|
| Statis | `scripts/validate-config.sh` | Struktur, paket, hook, metadata, token, SVG |
| Dokumentasi | `scripts/check-docs.sh` | Gaya bahasa dan tautan |
| Traceability | `scripts/check-traceability.py` | Requirement dan test case |
| Artefak | `tests/verify-artifact.sh` | Nama, ukuran, ISO 9660, bootloader, checksum |
| Boot | `tests/qemu-boot.sh` | UEFI dan BIOS, screenshot, log serial |
| Runtime | `tests/smoke.sh` | Identitas, layanan, sysctl, tool, desktop, Podman |

Batas pengujian:

1. QEMU tidak membuktikan kompatibilitas perangkat keras nyata.
2. Screenshot membuktikan sesi grafis tercapai, bukan setiap aplikasi berjalan.
3. Smoke test dijalankan manual di dalam sesi live.
4. arm64 dan i386 belum memiliki harness boot.

## 11. Rencana Evolusi

| Fase | Perubahan arsitektur |
|---|---|
| 2 | Tema Kage, GRUB dan Plymouth final, QA boot. Implementasi statis selesai, QA boot menunggu ISO |
| 3 | Tiga edisi desktop dengan tema dan layout. Implementasi statis selesai, QA sesi menunggu ISO |
| 4 | Arsenal tool keamanan, manifest vendored, verifikasi checksum |
| 5 | Toolchain coding lengkap dan profil container |
| 6 | Aplikasi harian, printer, dan integrasi desktop |
| 7 | Calamares, partisi, enkripsi, persistence, recovery |
| 8 | Repository ArashiOS, mirror, dan mekanisme update |
| 9 | Hardening rilis, signing, SBOM, reproducibility |
| 10 | arm64, i386, dan aksesibilitas |
| 11 | Dokumentasi publik dan situs |
| 12 | RC, rilis, dan pemeliharaan |

## 12. Keputusan Terkait

| ADR | Topik |
|---|---|
| [ADR-001](adr/001-debian-bookworm.md) | Debian 12 bookworm sebagai basis |
| [ADR-002](adr/002-live-build-hybrid.md) | live-build dan ISO hybrid |
| [ADR-003](adr/003-three-editions.md) | Tiga edisi desktop |
| [ADR-004](adr/004-vendoring-tools.md) | Vendoring tool non-Debian |
| [ADR-005](adr/005-calamares.md) | Calamares sebagai installer |
| [ADR-006](adr/006-kage-design.md) | Design system Kage |
| [ADR-007](adr/007-versioning.md) | Skema versi dan nama ISO |
| [ADR-008](adr/008-no-telemetry.md) | Tanpa telemetry secara default |
| [ADR-009](adr/009-systemd.md) | systemd sebagai init |
| [ADR-010](adr/010-podman-rootless.md) | Podman rootless sebagai default |
| [ADR-011](adr/011-editors.md) | Neovim dan VSCodium |
| [ADR-012](adr/012-i386-scope.md) | Cakupan legacy i386 |
| [ADR-013](adr/013-theme-pipeline.md) | Pipeline tema Kage |

## 13. Penyimpangan dan Risiko

| Butir | Status | Tindakan |
|---|---|---|
| i386 UEFI | Tidak didukung | Boot BIOS saja, ditegaskan pada ADR-012 |
| Calamares | Belum ada | Fase 7 |
| Tema Kage penuh | Selesai statis, runtime belum diuji | Validasi ISO Fase 2 |
| Paket branding | Selesai dan reproducible | Validasi instalasi pada ISO |
| Tool vendored | Belum ada | Fase 4 |
| Signing | Belum ada | Fase 9 |
| arm64 dan i386 | Belum dibangun | Fase 10 |
| Autologin installed system | Belum dihapus | Fase 7 |

Risiko utama Fase 1 adalah perbedaan versi `live-build` antara host pengembangan dan host rilis. Build rilis harus memakai Debian 12 yang bersih atau container Debian 12 dengan versi paket yang dicatat pada log build.
