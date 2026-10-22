# Changelog

Format mengikuti Keep a Changelog dan Semantic Versioning untuk dokumen. Versi produk memakai pola V major.MM.DD.

## [V1.10.21] - 2026-10-22

### Added

- Fondasi repository Fase 0: README, lisensi, panduan kontribusi, kebijakan keamanan, kode etik, dan changelog.
- Tiga belas ADR untuk basis Debian, live-build, edisi desktop, vendoring, installer, desain, versi, telemetry, systemd, Podman, editor, i386, dan pipeline tema.
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
- Dokumentasi build, arsitektur, desain, integrasi desktop, laporan Fase 0 dan 1, serta laporan Fase 2 dan 3.
- Tema ArashiKage dan ArashiKage-HC untuk GTK2, GTK3, GTK4 dan libadwaita, Cinnamon, Muffin dan Metacity, XFCE, Openbox, dan Kvantum.
- Pipeline tema deterministik dengan manifest SHA-256 dan pemeriksaan output kedaluwarsa.
- Paket lokal arashios-branding berisi tema, lima wallpaper PNG, ikon, aset GRUB, dan aset Plymouth.
- Konfigurasi desktop Cinnamon, XFCE, dan LXQt dengan panel atas 30px, wallpaper Kage, dan ikon desktop nonaktif.
- Profil terminal Kage untuk GNOME Terminal, XFCE Terminal, dan QTerminal.
- Perintah arashios-accessibility untuk kontras tinggi, reduced motion, dan status.
- Pemeriksaan statis tema, desktop, dan paket branding di CI dan Makefile.
- Katalog tool ArashiOS dengan 215 entri, 159 paket tier 0, 41 tool tier 1, 10 tool tier 2, dan 5 image tier 3.
- Manifest YAML per tool di vendor/manifests dengan versi, sumber, commit, lisensi, arsitektur, build, install, dan smoke test.
- Pin sumber upstream untuk 41 tool tier 1 pada tag dan commit yang dapat diverifikasi.
- Pipeline vendor tool tier 1 dengan verifikasi commit, audit glibc 2.36, dan penguncian hash artefak.
- Artefak tier 1 nuclei 3.11.1 dan subfinder 2.17.0 yang dibangun dari commit terkunci dan lolos audit glibc.
- Arsenal dengan perintah list, info, workflows, verify, install, remove, doctor, dan smoke.
- Harness smoke test toolstack tanpa jaringan dengan laporan JSON.
- Wordlist ArashiOS dengan enam berkas kurasi internal berlisensi CC-BY-SA-4.0 dan manifest checksum.
- Konfigurasi container rootless Podman dengan policy, registry, dan template Containerfile ber-digest.
- Perintah arashios-lab untuk lab container dengan digest terkunci dan tanpa mode privileged.
- Toolchain user level untuk uv, fnm, node, rustup, rust, go, starship, eza, dan vscodium dengan lock checksum.
- Installer toolchain tanpa sudo yang memverifikasi checksum, menolak arsip keluar direktori, dan melepas diri dengan bersih.
- Tujuh template proyek: Python, Go, Rust, Node, C, Java, dan template laporan keamanan.
- Harness hello world untuk sepuluh bahasa dengan status lulus, dilewati, dan gagal yang terpisah.
- Perintah arashios-doctor untuk pemeriksaan kesehatan sistem dan arashios-help untuk dokumentasi offline.
- Dokumentasi toolstack, arsenal, coding, container, vendoring, lisensi, dan laporan Fase 4 dan Fase 5.

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

- Artefak binary tool tier 1 belum dibangun sehingga hash artefak pada manifest masih kosong.
- Image lab juice-shop belum memiliki digest terkunci dan ditolak sampai digest tersedia.
- Host pengembangan tidak memasang Podman sehingga diagnosis container menandai masalah.
- Empat bahasa dilewati pada smoke test karena kompilatornya tidak terpasang pada host.
- ISO amd64 belum dibangun pada host ini karena toolchain build belum terpasang.
- Calamares, tool vendored, repository mandiri, dan signing produksi belum aktif.
- Tema Kage sudah dihasilkan dan dikemas, tetapi rendering GTK4, Cinnamon, XFCE, Openbox, Kvantum, LightDM, dan Plymouth belum diuji pada sesi nyata.
- arm64 dan i386 belum dibangun atau diuji boot. Validasi runtime ketiga arsitektur menunggu toolchain dan ISO.
- Autologin belum dihapus pada sistem terpasang.
- Parser CSS GTK4 memerlukan GIR GTK4. Di host ini parser dijalankan dari typelib lokal di `.toolchain`.
- Cinnamon applet defaults dipatch di hook dan dapat tertimpa pembaruan paket.

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
