# Changelog

Format mengikuti Keep a Changelog dan Semantic Versioning untuk dokumen. Versi produk memakai pola V major.MM.DD.

## [V1.10.21] - 2026-10-21

### Added

- Fondasi repository Fase 0: README, lisensi, panduan kontribusi, kebijakan keamanan, kode etik, dan changelog.
- Dua belas ADR untuk basis Debian, live-build, edisi desktop, vendoring, installer, desain, versi, telemetry, systemd, Podman, editor, dan i386.
- Design system Kage dengan token JSON, generator CSS, SCSS, QSS, laporan kontras, dan preview.
- Aset merek: mark, wordmark, wallpaper, tema GRUB, tema Plymouth, latar raster, dan nine-slice.
- Skrip pemeriksaan host, validasi konfigurasi, pemeriksaan dokumen, dan traceability.
- CI lint, config matrix live-build, dan release workflow.
- Konfigurasi common, tiga edisi desktop, dan overlay amd64, arm64, serta i386.
- Daftar paket keamanan, coding, harian, dan desktop untuk tiga edisi.
- Metadata sistem, APT pinning, sysctl hardening, UFW, AppArmor, dan Podman rootless.
- Hook locale, branding, alias CLI, layanan, dan cleanup.
- Skeletons Zsh, tmux, Neovim, Git, GTK, XFCE Terminal, QTerminal, ripgrep, dan bat, serta konfigurasi Starship.
- Build wrapper dengan dry-run, overlay arsitektur, snapshot, metadata, checksum, dan signature opsional.
- Verifikasi artefak ISO, harness boot QEMU UEFI dan BIOS, serta smoke test runtime.
- Dokumentasi build, arsitektur, desain, dan laporan Fase 0 dan 1.

### Changed

- i386 memakai syslinux saja karena UEFI i386 tidak didukung pada v1.
- BIOS memakai syslinux, bukan GRUB, mengikuti default live-build.
- Volume ID dihitung dari versi dan dibatasi 32 karakter.
- Metadata build mencatat host, kernel, arsitektur, versi live-build, dan hash konfigurasi.
- CI config matrix memakai container Debian 12 dan menguji tujuh kombinasi.
- `check-env.sh --release` mewajibkan host Debian 12 dan workflow rilis memakai mode tersebut.
- Traceability matrix merujuk seluruh 52 test case.
- Lab virtual amd64 dibatasi ke QEMU dan qemu-utils. libvirt dan virt-manager ditunda ke Fase 4.
- Plan dinaikkan ke 2.0.1 untuk menyelaraskan BIOS live, sysctl BPF, dan lab QEMU.
- Matriks build dibatasi ke tujuh kombinasi yang didukung melalui `SUPPORTED_COMBINATIONS`.
- `kernel.unprivileged_bpf_disabled` disetel ke 2 mengikuti default kernel Debian 12.

### Fixed

- Path hook pada `scripts/validate-config.sh` memakai akar repository.
- `ltrace` dan `thermald` dipindahkan ke overlay amd64 dan i386 karena tidak tersedia untuk arm64.
- Audit indeks bookworm mengonfirmasi 0 paket hilang pada tujuh kombinasi.
- Release workflow memakai path ISO eksplisit untuk setiap kombinasi arsitektur dan edisi.
- Alias `bat` dan `fd` ditambahkan untuk nama biner Debian `batcat` dan `fdfind`.
- Tujuh test case yang belum muncul langsung di traceability matrix sudah dirujuk.

### Known limitations

- ISO amd64 belum dibangun pada host ini karena toolchain build belum terpasang.
- Calamares, tool vendored, repository mandiri, dan signing produksi belum aktif.
- Tema desktop masih memakai basis Adwaita dan Papirus.
- arm64 dan i386 belum dibangun atau diuji boot.
- Autologin belum dihapus pada sistem terpasang.

## [2.0] - 2026-10-21

### Added

- Katalog kebutuhan FR, SR, PR, UX, dan CR.
- Model ancaman STRIDE.
- Katalog 52 test case dan traceability matrix.
- Spesifikasi build live-build dan mode kegagalan.
- Skema manifest tool T0 sampai T3.
- Risk register, tata kelola, SLO, dan rencana rilis.
- Design token Kage dengan kontras terukur.
- Rencana multi-arsitektur amd64, arm64, i386.

### Changed

- Struktur dokumen menjadi 9 bagian.
- Roadmap fase 0 sampai 11 diperluas menjadi 94 sub-fase.
- Penamaan ISO memiliki aturan edisi default per arsitektur.

## [1.0] - 2026-10-21

### Added

- Baseline produk, desain, arsitektur, dan roadmap.
- Matriks tiga edisi desktop.
- Kebijakan toolstack T0 sampai T3.
- Estimasi effort dan risiko awal.
