# ArashiOS V1.10.21 - Rencana Induk Produk dan Rekayasa

| Atribut | Nilai |
|---|---|
| Dokumen | plan.md |
| Versi dokumen | 1.0 |
| Tanggal baseline | 2026-10-21 |
| Status | Baseline eksekusi |
| Basis sistem | Debian 12 (bookworm) |
| Build system | live-build |
| Arsitektur | amd64, arm64, i386 |
| Edisi desktop | Cinnamon, XFCE, LXQt |
| Nama rilis | Shizukesa |
| Design system | Kage |
| Versi produk | V1.10.21 |
| Pemilik | ArashiOS Project |

Dokumen ini adalah sumber kebenaran untuk scope, arsitektur, desain, dan urutan rilis ArashiOS. Setiap perubahan scope harus melalui pembaruan dokumen ini dan persetujuan maintainer.

---

## 0. Ringkasan Eksekutif

ArashiOS adalah distribusi Linux berbasis Debian 12 yang ditujukan untuk operator red team, praktisi keamanan, dan developer yang membutuhkan lingkungan kerja terpadu. Prioritas produk: keamanan ofensif, kedua lingkungan coding, ketiga penggunaan harian. Ketiganya harus berjalan pada satu instalasi, bukan tiga varian terpisah.

Diferensiasi utama bukan jumlah tool. Kali, Parrot, dan BlackArch sudah memiliki ratusan hingga ribuan tool. ArashiOS bersaing pada empat hal yang terukur:

1. Kurasi. Setiap paket yang masuk ISO memiliki pemilik, kategori, lisensi, dan smoke test.
2. Stabilitas. Basis Debian stable, bukan rolling, dengan tool mutakhir yang di-vendor secara terkontrol.
3. Reproducibility. Build memakai snapshot Debian, manifest vendor, dan artefak bertanda tangan.
4. Pengalaman desktop. Design system Kage yang konsisten dari GRUB sampai terminal, sesuatu yang tidak dimiliki distro security lain.

Target v1.0 adalah paritas kemampuan pada 12 alur kerja keamanan inti, bukan paritas jumlah paket. Tujuh artefak ISO direncanakan pada matriks tiga arsitektur dan tiga edisi desktop.

Estimasi effort: 32 person-week kerja teknis, ditambah 15 persen buffer menjadi 37 person-week. Dengan dua kontributor setara penuh waktu, kalender rilis 18 sampai 20 minggu. Satu maintainer penuh waktu: 9 sampai 10 bulan. Satu maintainer paruh waktu 20 jam per minggu: 18 sampai 20 bulan.

MVP yang bisa boot dan menampilkan desktop bertema: Fase 0 sampai Fase 2, sekitar 3 minggu dengan dua kontributor.

---

## 1. Visi, Posisi, dan Pengguna

### 1.1 Visi

Menjadi distribusi security pertama yang terasa seperti produk jadi: stabil, cepat, konsisten secara visual, dan nyaman dipakai untuk bekerja delapan jam sehari.

### 1.2 Misi

1. Menyediakan tool red team inti yang siap pakai tanpa instalasi tambahan.
2. Menyediakan toolchain coding modern di atas basis Debian stable.
3. Menjaga ISO tetap di bawah batas ukuran yang ditetapkan melalui kurasi tiga tingkat.
4. Menghasilkan artefak yang dapat diverifikasi: checksum, signature, SBOM, dan build log.
5. Menjaga privasi pengguna: tanpa telemetry, tanpa akun default, tanpa panggilan jaringan otomatis.

### 1.3 Posisi terhadap distro lain

| Aspek | Kali Linux | Parrot OS | BlackArch | ArashiOS v1 |
|---|---|---|---|---|
| Basis | Debian testing | Debian testing | Arch Linux | Debian 12 stable |
| Model rilis | Rolling | Rolling | Rolling | Point release, siklus 4 minggu |
| Tool preinstall | 600+ | 500+ | 2800+ | 130 paket T0, target 40 paket T1 |
| Desktop | XFCE, GNOME, KDE | MATE, KDE, XFCE | Window manager bebas | Cinnamon, XFCE, LXQt |
| Fokus coding | Dasar | Dasar | Dasar | Setara fokus security |
| Design system | Tidak ada | Tidak ada | Tidak ada | Kage |
| Build terverifikasi | Tidak publik | Tidak publik | Tidak publik | Reproducible, signed, SBOM |
| ARM | Luas, termasuk NetHunter | Terbatas | Terbatas | arm64 untuk XFCE dan LXQt |
| 32-bit | Terbatas | Terbatas | Tidak | i386 untuk LXQt dan XFCE, tier legacy |

Klaim paritas yang dipakai: 12 alur kerja inti, yaitu reconnaissance, scanning, web testing, exploitation, password attack, Active Directory, wireless, network interception, forensics, reverse engineering, pivoting, dan reporting. Di luar 12 alur kerja tersebut, ArashiOS v1 tidak menjanjikan paritas.

### 1.4 Persona

| Persona | Kebutuhan utama | Edisi yang disarankan |
|---|---|---|
| Red team operator | Tool lengkap, pivoting, C2, reporting | Cinnamon |
| Security student dan CTF player | Ringan, cepat boot di VM, wordlist siap | XFCE |
| Developer security tooling | Toolchain modern, container, editor | Cinnamon atau XFCE |
| Pengguna harian privacy-aware | Browser, office, media, enkripsi disk | Cinnamon |
| Hardware lama atau VM 2 GB | RAM kecil, boot cepat | LXQt |

### 1.5 Non-goals v1

1. Membuat desktop environment baru dari nol.
2. Membuat package manager baru.
3. Menyaingi jumlah paket BlackArch.
4. Mendukung Secure Boot dengan kernel bertanda tangan pada rilis pertama.
5. Menyediakan installer otomatis tanpa interaksi.
6. Mendistribusikan tool proprietary seperti Burp Suite, Cobalt Strike, atau Nessus di dalam ISO.
7. Menyediakan layanan cloud, VPN, atau akun bawaan.

---

## 2. Prinsip Produk dan Rekayasa

| ID | Prinsip | Konsekuensi teknis |
|---|---|---|
| PR-01 | Kurasi di atas kuantitas | Setiap paket punya manifest YAML, lisensi, dan smoke test |
| PR-02 | Basis stabil, tool mutakhir | Debian stable, backports terbatas, vendor dengan versi terkunci |
| PR-03 | Reproducible by default | Snapshot Debian, manifest hash, SOURCE_DATE_EPOCH, diffoscope |
| PR-04 | Offline capable | Tidak ada tool yang butuh jaringan saat pertama dijalankan |
| PR-05 | Privacy first | Tanpa telemetry, tanpa remote analytics, tanpa akun default |
| PR-06 | Tiga edisi, satu codebase | Overlay konfigurasi, bukan fork |
| PR-07 | Desain dengan batasan | Palet, tipografi, dan spacing dikunci di design token |
| PR-08 | Legal clarity | Tool proprietary hanya lewat installer opt-in, bukan redistribusi |
| PR-09 | Measurable quality | Setiap klaim performa punya budget dan test |
| PR-10 | Maintainer sustainability | Otomasi build dan QA, scope dibatasi per rilis |

---

## 3. Keputusan Arsitektur

| ID | Keputusan | Alasan | Konsekuensi |
|---|---|---|---|
| ADR-001 | Basis Debian 12 bookworm | Stabil, ekosistem paket besar, dukungan LTS sampai 2028 | Tool versi baru perlu backports atau vendor |
| ADR-002 | live-build sebagai build system | Menghasilkan ISO hybrid BIOS dan UEFI, config berbasis file | Kustomisasi installer terbatas dibanding Debian installer |
| ADR-003 | Tiga edisi desktop terpisah | Ukuran ISO terkendali, QA per edisi jelas | Tiga matriks uji, tiga paket theme |
| ADR-004 | Vendor tool saat build, bukan repo Kali permanen | Menghindari konflik glibc dan dependency | Manifest vendor dan audit ABI wajib |
| ADR-005 | Calamares sebagai installer | Branding mudah, alur partisi modern | Perlu QA manual untuk skenario alongside |
| ADR-006 | Design system Kage | Identitas visual konsisten dan dapat diuji | Aset harus dipaketkan, bukan file lepas |
| ADR-007 | Versi V major.MM.DD | Mudah dilacak terhadap tanggal rilis | Perlu disiplin saat hotfix |
| ADR-008 | Tanpa telemetry | Kepercayaan pengguna security | Tidak ada crash reporting otomatis |
| ADR-009 | systemd | Standar Debian, integrasi tooling | Tidak ada dukungan init alternatif |
| ADR-010 | Podman rootless sebagai default container | Lebih aman untuk tool tidak tepercaya | Docker tetap tersedia sebagai paket opsional |
| ADR-011 | VSCodium sebagai editor default | Build open source tanpa telemetry | Ekstensi marketplace dibatasi |
| ADR-012 | i386 berstatus tier legacy | Permintaan hardware lama | Tool coverage tidak penuh, didokumentasikan |

---

## 4. Design System Kage

### 4.1 Konsep

Kage (影) berarti bayangan. Sistem visual menggabungkan estetika Jepang yang tenang dengan aksen red team yang tegas. Prinsip visual yang dipakai:

1. Ma (間): ruang kosong sebagai elemen aktif, bukan sisa layout.
2. Kanso (簡素): sederhana, tanpa ornamen yang tidak berfungsi.
3. Shibui (渋い): keindahan yang tidak mencolok.
4. Shinobi (忍び): siluet gelap, kontras rendah pada permukaan, aksen tajam pada aksi.
5. Blade: garis tipis 1 piksel, sudut hampir tegak, tanpa bayangan tebal.

Warna merah hanya dipakai untuk aksi, fokus, dan peringatan. Merah tidak dipakai sebagai dekorasi.

### 4.2 Palet warna

| Token | Hex | Peran | Porsi layar |
|---|---|---|---|
| sumi-900 | #0A0A0C | Latar utama | 55 sampai 60 persen |
| sumi-800 | #121215 | Permukaan panel dan jendela | 20 sampai 25 persen |
| sumi-700 | #1B1B20 | Permukaan naik, menu, tooltip | 8 persen |
| steel-600 | #2C2C33 | Garis, border, pemisah | 5 persen |
| ash-400 | #8B867D | Teks sekunder, placeholder | 3 persen |
| washi-100 | #EDE8DE | Teks utama | 4 persen |
| vermilion-500 | #C9382E | Aksi utama, indikator aktif | 2 persen |
| vermilion-400 | #E04B3D | Hover dan fokus | 1 persen |
| ember-300 | #F06A5A | Teks aksen di atas latar gelap | 0.5 persen |
| jade-500 | #5C8F7A | Status sukses | 0.3 persen |
| gold-500 | #B08D57 | Status peringatan | 0.3 persen |
| blood-700 | #7E1D18 | Status bahaya, latar destructive | 0.2 persen |

Aturan kontras:

1. Teks utama minimal 7:1 terhadap latar.
2. Teks sekunder minimal 4.5:1.
3. Teks aksen memakai ember-300, bukan vermilion-500, bila di atas sumi-900.
4. Setiap pasangan warna diverifikasi dengan skrip kontras pada CI Fase 2.

### 4.3 Tipografi

| Peran | Font | Berat | Ukuran | Tracking |
|---|---|---|---|---|
| Wordmark | Shippori Mincho | 600 | 32 sampai 48 px | 0.02em |
| Judul layar | Inter | 600 | 24 px | 0 |
| Judul seksi | Inter | 600 | 18 px | 0 |
| Body | Inter | 400 | 14 px | 0 |
| Label | Inter | 500 | 11 px, uppercase | 0.08em |
| Data dan kode | JetBrains Mono Nerd Font | 400 | 13 px | 0 |
| Terminal | JetBrains Mono Nerd Font | 400 | 11 sampai 13 px | 0 |
| Fallback Jepang | Noto Sans JP | 400 | mengikuti body | 0 |

Line height: 1.4 untuk body, 1.2 untuk judul, 1.5 untuk terminal. Semua font berlisensi OFL dan disimpan di repo.

### 4.4 Spacing, radius, elevasi, dan gerak

| Token | Nilai | Pemakaian |
|---|---|---|
| space-1 | 4 px | Jarak ikon dan teks |
| space-2 | 8 px | Padding kontrol kecil |
| space-3 | 12 px | Padding standar |
| space-4 | 16 px | Jarak antar grup |
| space-6 | 24 px | Jarak antar seksi |
| space-8 | 32 px | Margin layar |
| space-12 | 48 px | Pemisah besar |
| radius-sm | 2 px | Kontrol dan tombol |
| radius-md | 4 px | Dialog, maksimum |
| border | 1 px solid steel-600 | Semua pemisah |
| shadow-menu | 0 8px 24px rgba(0,0,0,0.45) | Hanya menu dan popover |

Gerak: 120 ms untuk hover, 180 ms untuk panel, 240 ms untuk dialog. Easing cubic-bezier(0.2, 0, 0, 1). Tanpa bounce, tanpa animasi lebih dari 300 ms. Mode reduced motion mematikan animasi Plymouth dan transisi panel.

### 4.5 Ikonografi dan kursor

1. Basis: Papirus-Dark, dilisensikan GPL-3.0.
2. Folder memakai warna sumi-700, bukan merah, agar tidak ramai.
3. Ikon aplikasi ArashiOS dibuat khusus: Arsenal, Control Center, Help.
4. Gaya ikon: garis 1.5 px, sudut 1 px, tanpa gradient.
5. Kursor: Bibata Modern Classic versi gelap, atau fallback Adwaita yang diwarnai ulang.
6. Ukuran ikon panel 16 px, menu 24 px, aplikasi 32 px.

### 4.6 Logo dan wordmark

1. Mark utama: karakter 嵐 dalam Shippori Mincho, dikelilingi ensō tipis 1.5 px.
2. Wordmark: ARASHIOS dalam Inter 600, uppercase, tracking 0.12em.
3. Lockup horizontal: mark di kiri, wordmark di kanan, jarak 8 px.
4. Varian: penuh warna, monokrom washi, monokrom sumi, 16 px favicon.
5. Clear space minimal setengah tinggi mark.
6. Ukuran digital minimum 24 px.
7. Logo Debian tidak dipakai sebagai identitas utama. Atribusi "based on Debian" ditampilkan di About dan dokumentasi.

### 4.7 Wallpaper

| Nama | Deskripsi | Mode |
|---|---|---|
| kage-sumi | Gradient sumi dengan ensō dan grain halus | Gelap, default |
| kage-shuriken | Pola geometri shuriken kontras 4 persen | Gelap |
| kage-bamboo | Siluet bambu rendah kontras | Gelap |
| kage-washi | Tekstur kertas washi dengan segel merah | Terang |
| kage-storm | Garis isobar dan petir tipis | Gelap |

Resolusi 3840x2160, format PNG dan SVG sumber. Lisensi CC-BY-SA-4.0. Tidak ada wallpaper pihak ketiga tanpa lisensi jelas.

### 4.8 Boot experience

| Tahap | Implementasi | Durasi target |
|---|---|---|
| GRUB | Latar sumi-900, wordmark 嵐, menu kanan, garis seleksi vermilion 2 px | Timeout 5 detik |
| Plymouth | Ensō digambar 1.5 detik, wordmark fade in, progress arc vermilion | 3 sampai 5 detik |
| LightDM | Wallpaper kage-sumi, jam tengah, kotak login border 1 px, tanpa branding bar | 1 detik |
| Desktop | Panel dan wallpaper muncul tanpa flicker | 2 detik |

GRUB menyediakan entri tambahan khusus build uji: "ArashiOS serial console" dengan parameter `console=ttyS0,115200`, dipakai CI untuk verifikasi boot tanpa framebuffer.

### 4.9 Layout desktop per edisi

Cinnamon:

1. Panel atas 30 px, latar sumi-900 opasitas 96 persen, border bawah 1 px.
2. Menu Arashi di kiri dengan kategori dan indikator aktif vermilion.
3. Window list ikon saja, tanpa label.
4. Jam tengah dalam JetBrains Mono, format `YYYY.MM.DD HH:MM`.
5. Workspace 4 buah, indikator berupa garis vertikal tipis.
6. Desktop tanpa ikon. Nemo memakai list view.
7. Notifikasi kanan atas, border 1 px, tanpa sudut membulat.

XFCE:

1. Panel atas 30 px dengan Whisker Menu, Docklike Tasklist, jam, tray, power.
2. Workspace 4 buah, indikator kotak 6 px.
3. Thunar list view, tanpa thumbnail untuk file tidak dikenal.
4. xfwm4 compositor aktif, shadow halus, tanpa blur.
5. xfce4-terminal dengan JetBrains Mono 11 px.

LXQt:

1. Panel atas 30 px, Quick Launch, Taskbar, Tray, Clock.
2. Openbox sebagai window manager, tema themerc Kage, border aktif vermilion.
3. Qt style Kvantum dengan tema ArashiKage.
4. PCManFM-Qt list view, QTerminal JetBrains Mono 11 px.
5. Tanpa desktop icon, tanpa compositor berat.

Aturan umum: tidak ada widget jam besar di desktop, tidak ada dock melayang, tidak ada animasi startup. Desktop harus terlihat tenang saat tidak ada jendela.

### 4.10 Terminal, editor, dan shell

1. Shell default zsh, dengan starship prompt bertema Kage.
2. Prompt menampilkan direktori, branch git, status exit, dan durasi perintah. Tanpa ikon emoji.
3. Palet terminal diturunkan dari Kanagawa dengan atribusi MIT di file LICENSE.
4. Neovim memakai colorscheme `arashios-kage` yang diturunkan dari Kanagawa, dengan plugin minimum.
5. Tmux memakai status bar sumi-800, indikator aktif vermilion.
6. fastfetch atau neofetch menampilkan mark 嵐 dan informasi sistem, tanpa logo ASCII besar.

### 4.11 Aturan visual

Lakukan:

1. Gunakan satu aksen merah per layar.
2. Pertahankan jarak minimum 12 px antar kontrol.
3. Gunakan garis 1 px sebagai pemisah, bukan bayangan.
4. Gunakan teks uppercase hanya untuk label pendek.
5. Uji tampilan pada skala font 100, 125, dan 150 persen.

Hindari:

1. Gradient pada tombol atau panel.
2. Sudut membulat lebih dari 4 px.
3. Bayangan tebal atau glow.
4. Emoji di UI sistem.
5. Lebih dari dua warna aksen dalam satu layar.

### 4.12 Aksesibilitas

1. Fokus keyboard terlihat: outline 2 px vermilion-400 dengan offset 2 px.
2. Semua aksi dapat dicapai dengan keyboard.
3. Status tidak boleh dibedakan hanya dengan warna.
4. Orca tersedia di metapackage daily.
5. Mode kontras tinggi `kage-contrast` disediakan sebagai varian tema.
6. Installer dan greeter diuji dengan navigasi keyboard saja.

---

## 5. Arsitektur Teknis

### 5.1 Lapisan sistem

```
+--------------------------------------------------------------+
| Aplikasi: security tools, coding tools, daily apps           |
+--------------------------------------------------------------+
| Desktop: Cinnamon / XFCE / LXQt + tema Kage                  |
+--------------------------------------------------------------+
| ArashiOS packages: branding, theme, meta, arsenal            |
+--------------------------------------------------------------+
| Debian 12 bookworm: kernel 6.1, systemd, APT, firmware       |
+--------------------------------------------------------------+
| Live layer: live-boot, live-config, squashfs, hybrid ISO     |
+--------------------------------------------------------------+
```

### 5.2 Basis dan kebijakan kernel

1. Kernel default: `linux-image-amd64` 6.1 LTS dari bookworm.
2. Opsi hardware baru: `linux-image-amd64` dari bookworm-backports, tersedia sebagai paket terpisah, bukan default.
3. Firmware: aktifkan komponen `non-free-firmware` untuk WiFi, GPU, dan Bluetooth.
4. Tanpa patch kernel out-of-tree pada v1. Semua patch harus melalui paket dan diuji.
5. Module signing tidak diaktifkan karena kernel tidak ditandatangani untuk Secure Boot.

### 5.3 Pipeline build

```
versions.env
    |
    v
build.sh --edition <edition> --arch <arch>
    |
    +--> validasi versi, arch, edition
    +--> siapkan workdir build/<edition>-<arch>/
    +--> lb config (bookworm, iso-hybrid, syslinux + grub-efi)
    +--> overlay config/common + config/editions/<edition>
    +--> pasang repo lokal (repo/pool) dan vendor manifest
    +--> lb build
    +--> sign, checksum, SBOM
    v
out/ArashiOS-<arch>-<version>[-<edition>].iso
```

Aturan build:

1. Build tidak boleh mengakses internet selain mirror yang diizinkan dan snapshot yang dikunci.
2. Tidak ada `curl | bash` di dalam hook build.
3. Semua unduhan memiliki checksum dan versi.
4. Build dijalankan di container Debian 12 untuk reproducibility.
5. Setiap build menghasilkan log yang disimpan sebagai artefak.

### 5.4 Struktur repository

```
arashios/
├── plan.md
├── README.md
├── LICENSE
├── build.sh
├── versions.env
├── config/
│   ├── common/
│   │   ├── package-lists/
│   │   ├── includes.chroot/
│   │   ├── hooks/live/
│   │   └── archives/
│   └── editions/
│       ├── cinnamon/
│       ├── xfce/
│       └── lxqt/
├── branding/
│   ├── logo/
│   ├── wallpaper/
│   ├── grub/
│   ├── plymouth/
│   └── lightdm/
├── packages/
│   ├── arashios-branding/
│   ├── arashios-theme-gtk/
│   ├── arashios-theme-qt/
│   ├── arashios-icons/
│   ├── arashios-desktop-common/
│   ├── arashios-desktop-cinnamon/
│   ├── arashios-desktop-xfce/
│   ├── arashios-desktop-lxqt/
│   ├── arashios-meta-redteam/
│   ├── arashios-meta-dev/
│   ├── arashios-meta-daily/
│   ├── arashios-arsenal/
│   └── arashios-repo-keyring/
├── vendor/
│   ├── debs/
│   ├── binaries/
│   └── manifests/
├── repo/
│   ├── conf/
│   └── pool/
├── scripts/
├── test/
│   ├── qemu-boot.sh
│   ├── smoke/
│   └── install-matrix/
├── docs/
└── out/
```

### 5.5 Paket ArashiOS

| Paket | Isi | Arch |
|---|---|---|
| arashios-branding | os-release, issue, lsb-release, wallpaper, GRUB, Plymouth, LightDM | all |
| arashios-theme-gtk | Tema GTK3, GTK4, Cinnamon CSS, override libadwaita | all |
| arashios-theme-qt | Tema Kvantum, konfigurasi qt5ct | all |
| arashios-icons | Papirus yang diwarnai ulang, ikon aplikasi ArashiOS | all |
| arashios-desktop-common | Skel, zsh, starship, tmux, neovim, font, kursor | all |
| arashios-desktop-cinnamon | Cinnamon, Nemo, applet, layout | all |
| arashios-desktop-xfce | XFCE, Thunar, plugin, layout | all |
| arashios-desktop-lxqt | LXQt, PCManFM-Qt, Openbox, layout | all |
| arashios-meta-redteam | Daftar paket security tier T0 dan T1 | all |
| arashios-meta-dev | Toolchain dan editor | all |
| arashios-meta-daily | Browser, office, media, utilitas | all |
| arashios-arsenal | CLI installer untuk tool T2 dan T3 | all |
| arashios-repo-keyring | Kunci GPG repo ArashiOS | all |

Semua paket dibangun dengan debhelper 13, lintian bersih, dan menyertakan copyright serta changelog.

### 5.6 Mekanisme overlay edisi

live-build tidak menggabungkan direktori secara otomatis. `build.sh` melakukan:

1. Salin `config/common` ke workdir.
2. Salin `config/editions/<edition>` di atasnya.
3. Gabungkan package list tanpa duplikasi.
4. Jalankan `lb config` sebelum overlay agar file default tidak menimpa konfigurasi proyek.
5. Validasi hasil overlay dengan `scripts/validate-config.sh`.

### 5.7 Repository APT dan signing

1. Repository lokal dibangun dengan aptly.
2. Setiap rilis memakai snapshot aptly yang tidak berubah.
3. Kunci GPG repo: RSA 4096, masa berlaku 3 tahun, subkey signing terpisah.
4. Kunci publik dipaketkan sebagai `arashios-repo-keyring`.
5. File `Release` ditandatangani, `InRelease` disediakan.
6. Rotasi kunci didokumentasikan di `docs/KEY-ROTATION.md`.
7. ISO tidak memuat repo Kali. Semua paket vendor berasal dari `repo/pool` lokal.

### 5.8 CI dan otomasi

| Pekerjaan | Trigger | Runner | Output |
|---|---|---|---|
| Lint | Setiap push | GitHub hosted | shellcheck, lintian, markdownlint |
| Unit package | Setiap push | GitHub hosted | .deb arashios-* |
| ISO amd64 | Tag dan nightly | Self-hosted amd64 | 3 edisi |
| ISO arm64 | Tag | Self-hosted arm64 atau QEMU | XFCE, LXQt |
| ISO i386 | Tag | Self-hosted amd64 | LXQt, XFCE |
| Boot test | Setelah build | QEMU KVM | Log boot dan screenshot |
| Release | Tag `v*` | Self-hosted | Signature, checksum, SBOM |

Aturan CI:

1. Build gagal jika ISO melebihi budget ukuran.
2. Build gagal jika smoke test kurang dari 100 persen.
3. Build gagal jika ada paket tanpa manifest lisensi.
4. Artefak disimpan 90 hari untuk nightly, permanen untuk rilis.

### 5.9 Reproducibility

1. `SOURCE_DATE_EPOCH` diambil dari tanggal versi.
2. Waktu snapshot Debian dikunci per rilis di `versions.env`.
3. UUID ISO, volume ID, dan label dibuat deterministik.
4. `mksquashfs` memakai `-noappend`, `-all-time`, dan urutan file yang stabil.
5. Permission dan ownership dinormalisasi di hook.
6. `diffoscope` dijalankan antara dua build; selisih yang diketahui didokumentasikan.
7. Target: dua build dengan input sama menghasilkan hash identik pada Fase 9. Jika tidak tercapai, rilis tetap boleh jalan dengan laporan selisih.

### 5.10 Strategi multi-arsitektur

| Arsitektur | Build host | Metode | Status |
|---|---|---|---|
| amd64 | x86_64 | Native | Tier 1 |
| arm64 | arm64 atau x86_64 | Native runner atau qemu-user-static + binfmt | Tier 1 untuk XFCE, tier 2 untuk LXQt |
| i386 | x86_64 | debootstrap i386, eksekusi native via multiarch | Tier 3, legacy |

Catatan i386:

1. Debian 12 masih menyediakan i386, tetapi tidak semua paket tersedia.
2. Tool Go dan Rust modern mungkin tidak mendukung 386.
3. i386 hanya dirilis dengan LXQt dan XFCE.
4. Jika coverage tool T0 turun di bawah 85 persen, i386 diturunkan menjadi build komunitas tanpa dukungan resmi.

---

## 6. Edisi, Matriks Dukungan, dan Penamaan ISO

### 6.1 Matriks edisi

| Edisi | Desktop | RAM idle target | Ukuran ISO target | Arsitektur tier 1 | Penggunaan |
|---|---|---|---|---|---|
| Cinnamon | Cinnamon 5.6 | maksimal 800 MB | maksimal 4.2 GB | amd64 | Flagship, daily driver |
| XFCE | XFCE 4.18 | maksimal 550 MB | maksimal 3.9 GB | amd64, arm64 | Red team di VM, laptop lama |
| LXQt | LXQt 1.2 | maksimal 420 MB | maksimal 3.5 GB | amd64 (tier 1), i386 (tier 3) | Hardware lama, VM 2 GB |

### 6.2 Matriks artefak rilis

| Artefak | Edisi | Arch | Tier | Nama file |
|---|---|---|---|---|
| A1 | Cinnamon | amd64 | 1 | ArashiOS-amd64-V1.10.21.iso |
| A2 | XFCE | amd64 | 1 | ArashiOS-amd64-V1.10.21-xfce.iso |
| A3 | LXQt | amd64 | 1 | ArashiOS-amd64-V1.10.21-lxqt.iso |
| A4 | XFCE | arm64 | 1 | ArashiOS-arm64-V1.10.21.iso |
| A5 | LXQt | arm64 | 2 | ArashiOS-arm64-V1.10.21-lxqt.iso |
| A6 | XFCE | i386 | 3 | ArashiOS-i386-V1.10.21-xfce.iso |
| A7 | LXQt | i386 | 3 | ArashiOS-i386-V1.10.21.iso |

Aturan penamaan:

1. Pola dasar: `ArashiOS-<arch>-<versi>[-<edisi>].iso`.
2. Edisi default per arch tidak memakai sufiks: amd64 Cinnamon, arm64 XFCE, i386 LXQt.
3. Edisi non-default memakai sufiks `-xfce` atau `-lxqt`.
4. Arch yang dipakai: `amd64` untuk 64-bit x86, `arm64` untuk 64-bit ARM, `i386` untuk 32-bit x86.
5. Setiap ISO disertai `.sha256`, `.sha512`, `.sig`, `.sbom.json`, dan `.torrent`.
6. Nama file tidak boleh memuat spasi, tanda kurung, atau karakter non-ASCII.

### 6.3 Dukungan

| Tier | Definisi | Komitmen |
|---|---|---|
| 1 | Rilis penuh | Boot, installer, smoke test, signature, dukungan 12 bulan |
| 2 | Rilis terbatas | Boot dan smoke test, dukungan komunitas 6 bulan |
| 3 | Legacy | Artefak diproduksi CI, dukungan komunitas, tanpa jaminan tool lengkap, evaluasi setiap rilis |

---

## 7. Toolstack

### 7.1 Kebijakan tiga tingkat

| Tier | Sumber | Redistribusi | Jumlah target | Contoh |
|---|---|---|---|---|
| T0 | Repo Debian bookworm | Ya, sesuai lisensi Debian | 100 sampai 130 paket | nmap, sqlmap, hashcat, wireshark |
| T1 | Vendor .deb atau build dari source, versi terkunci | Ya, dengan copyright | 35 sampai 50 paket | metasploit, netexec, nuclei, chisel |
| T2 | Unduhan saat pengguna memilih | Tidak, hanya skrip installer | 8 sampai 12 paket | Burp CE, Nessus, IDA Free |
| T3 | Container image atau distrobox | Tidak, image ditarik pengguna | Tidak dibatasi | kali-rolling, lab vulnerable |

Aturan T1:

1. Klasifikasikan tool berdasarkan bahasa: Ruby, Python, Go, Java, C.
2. Tool Go dibangun dari source dengan versi tag terkunci dan `GOARCH` sesuai arsitektur. Binari statis tidak bergantung glibc.
3. Tool Ruby dan Python dipasang sebagai paket atau pipx dengan versi terkunci.
4. Tool C hanya diambil dari vendor jika simbol GLIBC maksimum tidak melebihi glibc 2.36 milik bookworm. Verifikasi dengan `objdump -T` dan `grep GLIBC_`.
5. Jika syarat glibc gagal, tool dipindahkan ke T3 container.
6. Setiap paket T1 menyertakan file copyright dan sumber upstream.

### 7.2 Katalog keamanan T0 (terverifikasi di bookworm amd64)

| Kategori | Paket |
|---|---|
| Recon | nmap, masscan, arp-scan, dnsrecon, dnsutils, whois, ldap-utils, whatweb, wafw00f, nikto, dirb, gobuster, ffuf, dirsearch, recon-ng |
| Web testing | sqlmap, nikto, whatweb, wafw00f, ffuf, gobuster, dirb, dirsearch, mitmproxy |
| Network | wireshark, tshark, tcpdump, ettercap-text-only, bettercap, socat, netcat-openbsd, proxychains4, tor, torsocks |
| Wireless | aircrack-ng, hcxtools, hcxdumptool, reaver, wifite |
| Credential | hydra, medusa, john, hashcat, crunch, cewl |
| Active Directory | python3-impacket, ldap-utils, python3-pwntools |
| Forensics | sleuthkit, autopsy, testdisk, foremost, binwalk, steghide, libimage-exiftool-perl |
| Reverse engineering | gdb, strace, ltrace, apktool, python3-pwntools, python3-scapy, binwalk |
| Cloud dan container | awscli, azure-cli, kubernetes-client, ansible, docker.io, podman, buildah, skopeo, docker-compose |
| Reporting | libreoffice, keepassxc |

### 7.3 Katalog keamanan T1 (vendor, versi terkunci)

| Kategori | Tool | Strategi |
|---|---|---|
| Exploitation | metasploit-framework | .deb vendor, gem ter-bundle, cek dependensi Ruby |
| Exploitation | exploitdb, searchsploit | arsip upstream, update bulanan |
| Active Directory | netexec, evil-winrm, enum4linux-ng, kerbrute, certipy, ldapdomaindump | Go statis atau Python pipx |
| Web | nuclei, subfinder, httpx, feroxbuster, wpscan, zaproxy, dalfox, commix | Go statis, Ruby, Java |
| Recon | amass, naabu | Go statis |
| Pivoting | chisel, ligolo-ng | Go statis |
| Wireless | kismet | .deb vendor, cek glibc |
| Reverse engineering | radare2, rizin, cutter, ghidra, jadx, upx-ucl, pwndbg, frida-tools | Source build, Java, pipx |
| Forensics | volatility3 | pipx dengan versi terkunci |
| Cloud | trivy, helm | Binari upstream dengan checksum |
| Wordlist | seclists-core | Subset MIT, full via arsenal |

Catatan: `impacket` sudah tersedia di Debian sebagai `python3-impacket`, sehingga tidak perlu vendor. `exiftool` tersedia sebagai `libimage-exiftool-perl`. `kubectl` tersedia sebagai `kubernetes-client`.

### 7.4 Katalog T2 (opt-in, tanpa redistribusi)

1. Burp Suite Community Edition.
2. Nessus Essentials.
3. IDA Free.
4. Cobalt Strike, hanya dokumentasi pembelian, tanpa unduhan otomatis.
5. Maltego Community.
6. JetBrains Toolbox.
7. Obsidian.
8. Ghidra versi upstream terbaru, jika paket T1 tertinggal.

`arashios-arsenal` menampilkan lisensi, ukuran unduhan, checksum, dan sumber resmi sebelum instalasi. Perintah yang tersedia: `list`, `info`, `install`, `remove`, `update`, `verify`.

### 7.5 Stack coding

| Komponen | Versi bookworm | Strategi ArashiOS |
|---|---|---|
| Python | 3.11 | Sistem 3.11, uv untuk proyek, pipx untuk CLI |
| Go | 1.19 | Backports golang-1.23, atau tarball resmi 1.23 |
| Rust | 1.63 | rustup stable, target default |
| Node.js | 18 | fnm dengan Node 22 LTS, npm hanya di dalam proyek |
| Java | OpenJDK 17 | Default, dipakai Ghidra dan Burp |
| C dan C++ | gcc 12, clang 14 | build-essential, cmake, ninja, meson |
| PHP | 8.2 | php-cli, composer via installer |
| Ruby | 3.1 | ruby-full, bundler |
| Lua | 5.4 | lua5.4, luarocks opsional |
| Container | podman rootless | Docker CE opsional via arsenal |
| Editor | Neovim, VSCodium | Neovim dibangun dari source, VSCodium dari upstream |
| CLI | zsh, starship, tmux, rg, fd, fzf, bat, exa, zoxide, direnv, jq, yq, httpie, gh, git | Paket Debian dan vendor terkunci |

Aturan lingkungan coding:

1. Tidak ada `pip install` atau `npm install -g` ke sistem. Gunakan venv, uv, pipx, atau fnm.
2. Semua toolchain user-level dapat dipasang tanpa sudo.
3. Shell startup maksimal 300 ms pada mesin uji.
4. VSCodium menjadi default. VS Code proprietary tersedia via arsenal.
5. Docker tidak dijalankan otomatis. Podman rootless menjadi default.

### 7.6 Stack daily

1. Browser: Firefox ESR default, Chromium sekunder.
2. Email: Thunderbird.
3. Office: LibreOffice, Evince, File Roller, pandoc.
4. Media: VLC, GIMP, Inkscape.
5. Utilitas: Flameshot, KeePassXC, Timeshift, GParted, GNOME Disks, Remmina, FileZilla, qBittorrent.
6. Audio: PipeWire untuk Cinnamon dan LXQt, PulseAudio untuk XFCE sesuai default Debian.
7. Power: TLP, thermald, zram-tools, earlyoom.
8. Firmware: fwupd, non-free-firmware.
9. Flatpak tersedia tanpa remote default. Flathub hanya ditambahkan oleh pengguna.

### 7.7 Wordlist dan data

1. `seclists-core` berisi 10 daftar paling sering dipakai, lisensi MIT, ukuran terkompresi di bawah 80 MB.
2. SecLists lengkap tersedia melalui `arashios-arsenal install seclists-full`.
3. rockyou.txt tidak didistribusikan di ISO karena status hukum data asal tidak jelas. Arsenal menyediakan unduhan dengan peringatan.
4. Wordlist kustom ArashiOS disimpan di `/usr/share/wordlists/arashios/`.
5. Setiap wordlist memiliki checksum dan sumber.

### 7.8 Kebijakan update dan CVE

| Komponen | Sumber update | SLA |
|---|---|---|
| Paket Debian | Debian security dan point release | 24 jam setelah publikasi |
| Paket vendor T1 | Rebuild dengan versi baru | 7 hari untuk critical, 30 hari untuk high |
| Tool T2 | Installer memeriksa versi terbaru | Pengguna memutuskan |
| Container T3 | Image tag immutable | 30 hari |
| Kernel | Debian security dan backports | 7 hari |

Setiap rilis mencatat CVE yang diketahui dan status mitigasi di `docs/SECURITY-NOTES.md`.

### 7.9 Matriks lisensi

| Komponen | Lisensi | Redistribusi | Catatan |
|---|---|---|---|
| Metasploit Framework | BSD-3-Clause | Boleh | Sertakan NOTICE |
| NetExec | BSD-2-Clause | Boleh, verifikasi | Cek file LICENSE upstream |
| Nuclei, Subfinder, Httpx | MIT | Boleh | Sertakan copyright |
| Ghidra | Apache-2.0 | Boleh | Ukuran besar, pertimbangkan T2 |
| Radare2 | LGPL-3.0 | Boleh | Sertakan source atau tawaran source |
| SecLists | MIT | Boleh | Subset saja |
| Burp Suite CE | Proprietary | Tidak | Hanya installer |
| Cobalt Strike | Commercial | Tidak | Hanya dokumentasi |
| Nessus | Proprietary | Tidak | Hanya installer |
| Papirus | GPL-3.0 | Boleh | Sertakan lisensi |
| Materia atau Arc | GPL-3.0 | Boleh | Tema turunan wajib GPL-3.0 |
| Font Inter, JetBrains Mono, Shippori Mincho | OFL-1.1 | Boleh | Sertakan lisensi |
| Kanagawa | MIT | Boleh | Atribusi di tema terminal |

---

## 8. Roadmap Fase dan Sub-fase

### Fase 0: Fondasi Proyek

Durasi: 1 minggu. Effort: 1 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 0.1 | Inisialisasi repo, branch model, commit convention | Repo git, README, LICENSE | 0.5 hari |
| 0.2 | ADR-001 sampai ADR-012 | docs/adr/*.md | 0.5 hari |
| 0.3 | Provision build host | Skrip instalasi live-build, debootstrap, xorriso, qemu, apt-cacher-ng | 0.5 hari |
| 0.4 | CI skeleton | Lint shellcheck, markdownlint, build dry-run | 1 hari |
| 0.5 | Pemeriksaan legal dan trademark | Hasil pencarian nama, domain, lisensi | 0.5 hari |
| 0.6 | Design token v0 | `branding/tokens.json` dan ekspor CSS/SCSS | 1 hari |

Exit gate:

1. Repo dapat di-clone dan `make lint` lulus.
2. Semua ADR disetujui.
3. Build host lolos `scripts/check-env.sh`.
4. Nama ArashiOS tidak bentrok dengan merek terdaftar di yurisdiksi target.
5. Design token tervalidasi dan terdokumentasi.

### Fase 1: ISO Basis

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 1.1 | Konfigurasi live-build | config/common, config/editions/xfce | 1 hari |
| 1.2 | Bootstrap bookworm amd64 | Rootfs minimal, live-boot, live-config | 0.5 hari |
| 1.3 | Boot hybrid BIOS dan UEFI | ISO boot di QEMU kedua mode | 1 hari |
| 1.4 | Harness QEMU | test/qemu-boot.sh, screenshot, log serial | 1 hari |
| 1.5 | Baseline paket | Paket sistem, firmware, NetworkManager | 1 hari |
| 1.6 | Cache dan snapshot | apt-cacher-ng, snapshot.debian.org terkunci | 1 hari |
| 1.7 | Build script dan versi | build.sh, versions.env, artefak pertama | 1 hari |

Exit gate:

1. ISO boot ke shell atau desktop di QEMU UEFI dan BIOS.
2. Build dingin maksimal 60 menit, build hangat maksimal 20 menit.
3. Nama artefak sesuai pola dan checksum tersedia.
4. Tidak ada error dependency di log build.
5. Boot log tersedia melalui entri serial console.

### Fase 2: Branding dan Boot Experience

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 2.1 | Finalisasi logo dan varian | SVG mark, wordmark, favicon | 1 hari |
| 2.2 | Wallpaper set | 5 wallpaper 4K, sumber SVG | 2 hari |
| 2.3 | Tema GRUB | Tema terpasang, menu teruji | 1 hari |
| 2.4 | Tema Plymouth | Animasi ensō, progress arc | 2 hari |
| 2.5 | LightDM greeter | Layout, wallpaper, autologin live | 1 hari |
| 2.6 | Identitas sistem | os-release, issue, lsb-release, neofetch | 0.5 hari |
| 2.7 | Paket branding | arashios-branding .deb | 1 hari |
| 2.8 | QA boot | Screenshot, timing, kontras | 1 hari |

Exit gate:

1. Boot chain konsisten dari GRUB sampai desktop.
2. Tidak ada logo Debian di layar boot atau greeter.
3. Atribusi Debian tersedia di About dan dokumentasi.
4. Waktu boot memenuhi budget.
5. Semua aset memiliki lisensi dan sumber.

### Fase 3: Desktop dan Tema

Durasi: 4 minggu. Effort: 5 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 3.1 | Desktop common | Font, ikon, kursor, audio, network applet | 2 hari |
| 3.2 | Tema GTK3 dan GTK4 | ArashiKage, override libadwaita | 4 hari |
| 3.3 | Tema Qt | Kvantum ArashiKage, qt5ct | 3 hari |
| 3.4 | Edisi Cinnamon | Tema cinnamon.css, panel, menu, Nemo | 3 hari |
| 3.5 | Edisi XFCE | xfconf layout, Whisker, Thunar, terminal | 3 hari |
| 3.6 | Edisi LXQt | Openbox themerc, Kvantum, panel | 3 hari |
| 3.7 | Skel dan dotfiles | zsh, starship, tmux, neovim, git | 2 hari |
| 3.8 | Default aplikasi | Terminal, browser, file manager, editor | 1 hari |
| 3.9 | Aksesibilitas | Fokus, kontras, keyboard, reduced motion | 2 hari |
| 3.10 | QA edisi | 3 DE x 2 firmware | 3 hari |

Exit gate:

1. Ketiga edisi boot ke desktop tanpa error tema.
2. Budget RAM dan waktu boot terpenuhi.
3. Semua aplikasi default konsisten dengan design token.
4. Navigasi keyboard lulus untuk installer dan greeter.
5. Tidak ada aset tema yang hilang atau fallback ke tema Debian.

### Fase 4: Toolstack Keamanan

Durasi: 4 minggu. Effort: 5 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 4.1 | Taksonomi dan manifest | vendor/manifests/*.yaml per tool | 2 hari |
| 4.2 | Instalasi T0 | Paket Debian dan konfigurasi | 2 hari |
| 4.3 | Vendor T1 | .deb, binari Go, pipx, cek glibc | 6 hari |
| 4.4 | Wordlist | seclists-core, wordlist kustom | 1 hari |
| 4.5 | Arsenal installer | CLI list, info, install, verify | 4 hari |
| 4.6 | Container T3 | Kali rootless, lab image | 2 hari |
| 4.7 | Smoke test | Skrip versi dan eksekusi dasar | 3 hari |
| 4.8 | Audit lisensi | docs/LICENSES.md, copyright | 2 hari |
| 4.9 | Kebijakan update | Pin versi, jadwal review | 1 hari |

Exit gate:

1. Semua tool T0 dan T1 lulus smoke test.
2. Tidak ada dependency yang belum terpenuhi.
3. File lisensi lengkap untuk setiap paket vendor.
4. Ukuran ISO masih dalam budget.
5. Tidak ada repo Kali di sources.list ISO.
6. Arsenal dapat memasang dan menghapus tool tanpa merusak sistem.

### Fase 5: Lingkungan Coding

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 5.1 | Toolchain bahasa | Python, Go, Rust, Node, Java, C/C++ | 2 hari |
| 5.2 | Editor | Neovim, VSCodium, konfigurasi dasar | 2 hari |
| 5.3 | Container | Podman rootless, Docker opsional | 1 hari |
| 5.4 | CLI environment | zsh, starship, tmux, utilitas | 1 hari |
| 5.5 | Dotfiles | /etc/skel, first-run tidak memaksa | 1 hari |
| 5.6 | Kebijakan version manager | uv, fnm, rustup, pipx | 1 hari |
| 5.7 | Dokumentasi offline | Man page, arashios-help | 1 hari |
| 5.8 | Smoke test | Hello world 6 bahasa, container run | 1 hari |

Exit gate:

1. Enam bahasa dapat mengompilasi hello world.
2. Tidak ada instalasi global ke sistem tanpa sudo.
3. Shell startup maksimal 300 ms.
4. Podman rootless berjalan tanpa konfigurasi tambahan.
5. VSCodium berjalan dan dapat memasang ekstensi dari sumber yang diizinkan.

### Fase 6: Daily Driver dan Hardware

Durasi: 3 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 6.1 | Aplikasi harian | Browser, office, media, utilitas | 2 hari |
| 6.2 | Jaringan | NetworkManager, WiFi, Bluetooth, VPN | 2 hari |
| 6.3 | Audio | PipeWire atau PulseAudio per edisi | 2 hari |
| 6.4 | Power management | TLP, thermald, zram, earlyoom | 1 hari |
| 6.5 | Printing dan scanning | CUPS, sane | 1 hari |
| 6.6 | Locale dan font | en_US, id_ID, ja_JP, timezone | 1 hari |
| 6.7 | Firmware | non-free-firmware, fwupd, kernel backports | 1 hari |
| 6.8 | QA hardware | 3 mesin uji, suspend, WiFi, audio | 3 hari |

Exit gate:

1. Tugas harian lulus: browsing, email, office, media, print.
2. Suspend dan resume 10 dari 10 percobaan.
3. WiFi, Bluetooth, dan audio berfungsi di tiga mesin uji.
4. Tidak ada regression dibanding Debian pada hardware yang sama.
5. Locale Indonesia dan Jepang tampil benar.

### Fase 7: Installer, Persistence, dan Recovery

Durasi: 5 minggu. Effort: 5 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 7.1 | Calamares dan branding | Installer bertema Kage | 3 hari |
| 7.2 | Profil partisi | Erase, alongside, manual | 3 hari |
| 7.3 | LUKS dan LVM | Enkripsi disk, volume manager | 4 hari |
| 7.4 | Dual boot Windows | Shrink, ESP, os-prober, BitLocker warning | 4 hari |
| 7.5 | Persistence | Partisi persistence, opsi terenkripsi | 2 hari |
| 7.6 | Recovery | chroot tool, grub repair, timeshift | 3 hari |
| 7.7 | Secure Boot | Dokumentasi, deteksi status | 1 hari |
| 7.8 | QA instalasi | 10 skenario x 3 edisi | 5 hari |

Exit gate:

1. 30 dari 30 instalasi lulus tanpa data loss.
2. Triple boot Windows, Debian, ArashiOS berhasil di hardware nyata.
3. LUKS dan LVM berfungsi dan dapat dibuka kembali.
4. GRUB mendeteksi sistem operasi lain.
5. Dokumentasi peringatan BitLocker dan Fast Startup tersedia.
6. Persistence bertahan setelah reboot.

### Fase 8: Paket dan Repository

Durasi: 3 minggu. Effort: 3 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 8.1 | Standar packaging | debhelper, lintian, copyright | 2 hari |
| 8.2 | Build semua paket ArashiOS | 13 paket .deb | 3 hari |
| 8.3 | Repo aptly dan GPG | Repo lokal, InRelease, keyring | 3 hari |
| 8.4 | Integrasi ISO | ISO memakai repo lokal saja | 2 hari |
| 8.5 | Snapshot dan pinning | versions.env, manifest hash | 2 hari |
| 8.6 | Upgrade path | V1.10.21 ke V1.10.28 | 2 hari |
| 8.7 | Kebijakan backports | Hanya kernel dan Go | 1 hari |

Exit gate:

1. Rebuild offline dari `repo/pool` berhasil.
2. `apt update` dan `apt upgrade` di sistem terpasang berhasil.
3. Semua paket lintian clean.
4. Kunci GPG terverifikasi dan didokumentasikan.
5. Upgrade antar rilis tidak memerlukan reinstalasi.

### Fase 9: QA, Hardening, dan Kepatuhan

Durasi: 4 minggu. Effort: 3 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 9.1 | Test plan | docs/QA-PLAN.md, test case | 2 hari |
| 9.2 | Boot test otomatis | BIOS, UEFI, 3 edisi, 3 arch | 4 hari |
| 9.3 | Smoke suite | 40 test, hasil JSON | 3 hari |
| 9.4 | Hardening | sysctl, AppArmor, UFW, tanpa sshd | 2 hari |
| 9.5 | Vulnerability scan | debsecan, trivy, grype | 3 hari |
| 9.6 | SBOM | CycloneDX per ISO | 2 hari |
| 9.7 | Artifact signing | minisign atau cosign | 2 hari |
| 9.8 | Audit kepatuhan | Lisensi, export notice, privacy | 2 hari |
| 9.9 | Disclosure policy | SECURITY.md, kontak privat | 1 hari |

Exit gate:

1. Tidak ada CVE critical atau high yang belum dimitigasi.
2. SBOM tersedia untuk setiap ISO.
3. Signature dan checksum terverifikasi.
4. Hardening checklist 100 persen.
5. Kebijakan disclosure dipublikasikan.

### Fase 10: Rilis dan Distribusi

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 10.1 | Versi dan changelog | CHANGELOG.md, release notes | 1 hari |
| 10.2 | Build matrix final | 7 artefak ISO | 2 hari |
| 10.3 | Mirror dan torrent | Mirror HTTP, torrent, zsync | 2 hari |
| 10.4 | Website dan dokumentasi | Install, dual boot, hardening, FAQ | 3 hari |
| 10.5 | Kanal rilis | stable, edge, nightly | 1 hari |
| 10.6 | Komunitas | Forum atau Matrix, GitHub Discussions | 1 hari |
| 10.7 | Monitoring pasca rilis | Hotfix window 7 hari | 1 hari |

Exit gate:

1. Semua artefak tier 1 tersedia dan terverifikasi.
2. Checksum dan signature dapat diverifikasi pengguna.
3. Dokumentasi instalasi dan dual boot lengkap.
4. Kanal update berfungsi.
5. Tim siap untuk hotfix 7 hari.

### Fase 11: Pasca v1

Durasi: berkelanjutan.

| ID | Sub-fase | Target |
|---|---|---|
| 11.1 | Image ARM SBC | Raspberry Pi 4 dan 5, Pine64 |
| 11.2 | Secure Boot | Shim, MOK, kernel bertanda tangan |
| 11.3 | Edisi Wayland | Hyprland atau Sway, eksperimental |
| 11.4 | Arsenal GUI | Control Center berbasis GTK4 |
| 11.5 | Cloud dan WSL | Image cloud, rootfs WSL |
| 11.6 | Kebijakan i386 | Evaluasi lanjut atau deprecation |
| 11.7 | Rebase Debian 13 | ArashiOS v2 di trixie |

---

## 9. Rilis, Versi, dan Artefak

### 9.1 Skema versi

`V<major>.<MM>.<DD>`

Contoh: V1.10.21 berarti major 1, bulan 10, tanggal 21. Baseline proyek memakai 2026-10-21.

Aturan:

1. Perubahan breaking atau rebase basis menaikkan major.
2. Rilis bulanan menaikkan MM dan DD.
3. Hotfix memakai tanggal rilis, bukan sufiks alfabet.
4. Setiap artefak menyimpan versi di `/etc/arashios-release`.

### 9.2 Kanal rilis

| Kanal | Frekuensi | Stabilitas | Pengguna |
|---|---|---|---|
| stable | 4 minggu | Tinggi | Produksi |
| edge | 1 minggu | Sedang | Pengguna awal |
| nightly | Harian | Rendah | Kontributor dan QA |

### 9.3 Artefak per rilis

1. ISO.
2. SHA256SUMS dan SHA512SUMS.
3. Signature minisign atau cosign.
4. SBOM CycloneDX.
5. Build log.
6. Package manifest.
7. Release notes.
8. Torrent dan zsync.

### 9.4 Siklus dukungan

1. Setiap major didukung 12 bulan.
2. Rilis terakhir major mendapat dukungan 6 bulan tambahan.
3. Debian 12 LTS berakhir Juni 2028. ArashiOS v1 mengikuti batas tersebut.
4. Rebase ke Debian 13 direncanakan pada v2, bukan backport jangka panjang.

---

## 10. QA dan Kriteria Penerimaan

### 10.1 Matriks uji

| Dimensi | Nilai |
|---|---|
| Firmware | UEFI, BIOS |
| Arsitektur | amd64, arm64, i386 |
| Edisi | Cinnamon, XFCE, LXQt |
| Boot | Live, installer, installed system |
| Storage | SSD NVMe, SATA, USB, virtio |
| Enkripsi | Tanpa LUKS, LUKS, LUKS+LVM |
| Jaringan | Ethernet, WiFi 2.4, WiFi 5, WiFi 6 |
| GPU | Intel, AMD, NVIDIA |
| Lokasi | en_US, id_ID, ja_JP |

### 10.2 Budget performa

| Metrik | Cinnamon | XFCE | LXQt |
|---|---|---|---|
| RAM idle | 800 MB | 550 MB | 420 MB |
| Boot QEMU KVM | 35 detik | 30 detik | 25 detik |
| Boot hardware SSD | 45 detik | 40 detik | 35 detik |
| Ukuran ISO | 4.2 GB | 3.9 GB | 3.5 GB |
| Install SSD | 15 menit | 13 menit | 12 menit |
| Shell startup | 300 ms | 300 ms | 300 ms |

### 10.3 Smoke test wajib

1. `nmap --version` dan scan localhost.
2. `sqlmap --version`.
3. `msfconsole -v`.
4. `netexec --version`.
5. `nuclei -version`.
6. `hashcat -I`.
7. `aircrack-ng --help`.
8. `wireshark --version`.
9. `python3 -c "import impacket"`.
10. `gcc hello.c` dan eksekusi.
11. `go version` dan build hello.
12. `rustc --version` dan build hello.
13. `node --version` dan jalankan skrip.
14. `podman run hello-world`.
15. `neovim --version`.
16. `codium --version`.
17. `firefox-esr --version`.
18. `libreoffice --version`.
19. `timeshift --version`.
20. `sudo ufw status`.

### 10.4 Release gate

Rilis dinyatakan lulus jika:

1. Semua artefak tier 1 lulus boot UEFI dan BIOS.
2. Installer lulus 30 dari 30 skenario.
3. Smoke test lulus 100 persen.
4. Tidak ada CVE critical atau high terbuka.
5. SBOM dan signature tersedia.
6. Ukuran ISO dalam budget.
7. Dokumentasi instalasi dan dual boot selesai.
8. Tidak ada telemetry atau panggilan jaringan otomatis.

---

## 11. Keamanan, Privasi, dan Kepatuhan

### 11.1 Hardening default

1. UFW aktif, deny incoming, allow outgoing.
2. AppArmor aktif.
3. Tanpa SSH server. Hanya `openssh-client`.
4. `unattended-upgrades` untuk Debian security.
5. sysctl: `kernel.kptr_restrict=1`, `kernel.dmesg_restrict=1`, `net.ipv4.conf.all.rp_filter=1`.
6. Tanpa login root. `sudo` untuk user installer.
7. Autologin hanya pada live session, tidak pada sistem terpasang.
8. Firejail tersedia tetapi tidak aktif default.
9. USBGuard tidak aktif default untuk menghindari lockout keyboard.

### 11.2 Supply chain

1. Snapshot Debian dikunci per rilis.
2. Semua binari vendor memiliki checksum dan manifest.
3. Repo lokal ditandatangani dan di-snapshot.
4. Build di container bersih.
5. SBOM per artefak.
6. Tidak ada `curl | bash` di build atau installer default.
7. Dependency scan otomatis pada CI.

### 11.3 Privasi

1. Tanpa telemetry, analytics, atau crash reporting otomatis.
2. Tanpa akun atau kredensial default.
3. Tanpa panggilan jaringan saat boot.
4. Firefox ESR memakai pengaturan privasi yang wajar, tanpa mengunci konfigurasi pengguna.
5. DNS default mengikuti NetworkManager, bukan penyedia pihak ketiga.

### 11.4 Legal

1. Kode ArashiOS: GPL-3.0-or-later.
2. Aset visual: CC-BY-SA-4.0.
3. Dokumentasi: CC-BY-4.0.
4. Merek Debian dipakai secara faktual. Logo Debian tidak dipakai sebagai identitas.
5. Tool proprietary tidak didistribusikan. Installer hanya menautkan ke sumber resmi.
6. Pencarian merek ArashiOS dilakukan sebelum rilis publik.
7. Disclaimer dual-use disertakan di installer dan website.
8. Kepatuhan ekspor: tool kriptografi dan jaringan tunduk pada hukum lokal. Dokumen tidak menggantikan nasihat hukum.

### 11.5 Responsible disclosure

1. Kanal privat ditetapkan pada Fase 0.5.
2. SLA respons awal 72 jam.
3. Perbaikan critical dalam 7 hari.
4. Kredit peneliti jika diizinkan.
5. Kebijakan lengkap di `SECURITY.md`.

---

## 12. Risiko dan Mitigasi

| ID | Risiko | Probabilitas | Dampak | Mitigasi | Pemicu |
|---|---|---|---|---|---|
| R-01 | Konflik ABI paket Kali dengan bookworm | Sedang | Tinggi | Klasifikasi bahasa, binari statis, cek glibc, container | Build gagal dependency |
| R-02 | Coverage tool i386 rendah | Tinggi | Tinggi | LXQt saja, dokumentasi, evaluasi 85 persen | Tool T0 gagal build |
| R-03 | Build arm64 lambat | Tinggi | Sedang | Native runner, cache, build nightly | Build lebih dari 4 jam |
| R-04 | Scope creep desain | Sedang | Sedang | Design token dikunci, tanpa DE baru | Permintaan fitur di luar plan |
| R-05 | Masalah lisensi tool | Sedang | Tinggi | Audit per paket, T2 opt-in | Paket tanpa copyright |
| R-06 | Kapasitas maintainer | Tinggi | Tinggi | Otomasi, scope per rilis, minimal 2 maintainer | Miss jadwal 2 sprint |
| R-07 | ISO membengkak | Sedang | Sedang | Budget ukuran, seclists-core, T2 opt-in | ISO lebih dari budget |
| R-08 | Supply chain compromise | Rendah | Tinggi | Snapshot, signature, SBOM, checksum | Hash vendor berubah |
| R-09 | Secure Boot tidak didukung | Tinggi | Rendah | Dokumentasi jelas, roadmap MOK | Keluhan pengguna |
| R-10 | Hardware tidak kompatibel | Sedang | Sedang | non-free-firmware, backports kernel, 3 mesin uji | WiFi atau GPU gagal |
| R-11 | Konflik merek ArashiOS | Rendah | Tinggi | Pencarian merek dan domain di Fase 0.5 | Nama sudah terdaftar |
| R-12 | Debian 12 EOL 2028 | Pasti | Sedang | Rebase v2 ke Debian 13, siklus 12 bulan | Mendekati Juni 2028 |

---

## 13. Tim, Peran, dan Estimasi

### 13.1 Peran minimum

| Peran | Tanggung jawab | FTE minimum |
|---|---|---|
| Maintainer dan build engineer | Repo, build, CI, rilis | 1.0 |
| Design dan desktop | Tema, aset, layout, aksesibilitas | 0.5 |
| Security dan QA | Toolstack, hardening, test matrix | 0.5 |
| Dokumentasi dan komunitas | Docs, website, dukungan | 0.25 |

Total minimum: 2.25 FTE. Dengan 2 orang, satu orang merangkap design dan QA.

### 13.2 Effort per fase

| Fase | Person-week |
|---|---|
| 0 | 1 |
| 1 | 2 |
| 2 | 2 |
| 3 | 5 |
| 4 | 5 |
| 5 | 2 |
| 6 | 2 |
| 7 | 5 |
| 8 | 3 |
| 9 | 3 |
| 10 | 2 |
| Total | 32 |
| Buffer 15 persen | 5 |
| Total dengan buffer | 37 |

### 13.3 Kalender

```
Minggu   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
P0      ##
P1         ####
P2               ####
P3                     ########
P4                       ########
P5                           ####
P6                             ######
P7                               ##########
P8                                 ######
P9                                   ########
P10                                        ####
```

Catatan: fase 3 dan 4 dapat berjalan paralel jika ada dua kontributor. Fase 7 bergantung pada Fase 1 dan 3. Fase 9 bergantung pada semua fase sebelumnya.

---

## 14. Metrik Keberhasilan

| ID | Metrik | Target |
|---|---|---|
| M-01 | Boot sukses pada matriks tier 1 | 100 persen |
| M-02 | Installer sukses | 30 dari 30 |
| M-03 | Smoke test | 100 persen |
| M-04 | Ukuran ISO | Dalam budget |
| M-05 | RAM idle | Dalam budget |
| M-06 | Cold boot hardware | Dalam budget |
| M-07 | CVE critical terbuka saat rilis | 0 |
| M-08 | Artefak bertanda tangan | 100 persen |
| M-09 | Paket dengan manifest lisensi | 100 persen |
| M-10 | Build reproducible | Hash identik atau laporan diffoscope |
| M-11 | Waktu respons disclosure | 72 jam |
| M-12 | Downtime kanal update | 0 pada hari rilis |

---

## 15. Dokumentasi dan Komunitas

### 15.1 Dokumen wajib

1. README.md: ringkasan, screenshot, cara build.
2. INSTALL.md: instalasi, dual boot, LUKS, troubleshooting.
3. HARDENING.md: hardening setelah instalasi.
4. CONTRIBUTING.md: alur kontribusi dan standar kode.
5. CODE_OF_CONDUCT.md.
6. SECURITY.md: disclosure policy.
7. CHANGELOG.md.
8. docs/ARCHITECTURE.md.
9. docs/DESIGN.md.
10. docs/QA-PLAN.md.
11. docs/LICENSES.md.
12. docs/KEY-ROTATION.md.

### 15.2 Website

1. Halaman unduh dengan checksum dan signature.
2. Dokumentasi instalasi dan dual boot.
3. Halaman perbandingan edisi.
4. Halaman rilis dan changelog.
5. Halaman kontribusi.
6. Tanpa analytics pihak ketiga.

### 15.3 Kanal komunitas

1. GitHub Discussions untuk pertanyaan dan bug.
2. Matrix atau forum untuk diskusi real-time.
3. Kanal security privat untuk disclosure.
4. Tidak ada kanal resmi yang meminta kredensial pengguna.

---

## 16. Definisi Selesai v1.0

v1.0 dinyatakan selesai jika seluruh poin berikut terpenuhi:

1. Tujuh artefak ISO pada matriks rilis berhasil dibangun.
2. Semua artefak tier 1 boot di UEFI dan BIOS.
3. Installer lulus 30 skenario tanpa data loss.
4. Triple boot Windows, Debian, ArashiOS teruji di hardware nyata.
5. Ketiga edisi memenuhi budget RAM, boot, dan ukuran ISO.
6. Semua tool T0 dan T1 lulus smoke test.
7. Toolchain enam bahasa lulus hello world.
8. Tugas harian lulus di tiga mesin uji.
9. Tidak ada CVE critical atau high terbuka.
10. SBOM, checksum, dan signature tersedia untuk semua artefak.
11. Dokumentasi instalasi, dual boot, dan hardening selesai.
12. Repo APT lokal berfungsi dan upgrade antar rilis teruji.
13. Design system Kage diterapkan konsisten dari boot sampai terminal.
14. Tidak ada telemetry atau panggilan jaringan otomatis.
15. Audit lisensi selesai dan semua copyright tersedia.

---

## 17. Lampiran

### Lampiran A: Perintah build dan uji

```
./build.sh --edition cinnamon --arch amd64 --version V1.10.21
./build.sh --edition xfce --arch amd64 --version V1.10.21
./build.sh --edition lxqt --arch i386 --version V1.10.21

./test/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso uefi
./test/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso bios
./test/smoke/run.sh --image out/ArashiOS-amd64-V1.10.21.iso
./test/verify-artifact.sh out/ArashiOS-amd64-V1.10.21.iso
```

### Lampiran B: Status paket terverifikasi

Verifikasi dilakukan pada 2026-10-21 terhadap indeks `bookworm` amd64, komponen main, contrib, non-free, dan non-free-firmware.

| Kelompok | Jumlah | Keterangan |
|---|---|---|
| Tersedia di Debian | 130 | Kandidat T0 |
| Tidak tersedia | 39 | Masuk T1, T2, atau T3 |
| Backports tersedia | linux-image-amd64, linux-headers-amd64, golang-1.22, golang-1.23 | Dipakai terbatas |
| Alias paket | libimage-exiftool-perl, python3-impacket, kubernetes-client, python3-pwntools, python3-scapy | Nama berbeda dari upstream |

Paket yang tidak tersedia dan strateginya:

| Paket | Strategi |
|---|---|
| metasploit-framework | T1 vendor .deb |
| netexec | T1 Go build |
| evil-winrm | T1 Ruby gem |
| responder | T1 Python paket |
| wpscan | T1 Ruby gem |
| feroxbuster | T1 Go build |
| nuclei | T1 Go build |
| subfinder | T1 Go build |
| httpx | T1 Go build |
| amass | T1 Go build |
| chisel | T1 Go build |
| ligolo-ng | T1 Go build |
| seclists | T1 subset core |
| exploitdb | T1 arsip upstream |
| kismet | T1 .deb vendor atau T3 |
| zaproxy | T1 .deb vendor atau T2 |
| jadx | T1 Java build |
| ghidra | T1 atau T2, ukuran besar |
| radare2 | T1 source build |
| rizin | T1 source build |
| cutter | T1 source build |
| upx-ucl | T1 source build |
| pwndbg | T1 git tag terkunci |
| volatility3 | T1 pipx |
| frida-tools | T1 pipx |
| trivy | T1 binari upstream |
| helm | T1 binari upstream |
| starship | T1 binari upstream |
| uv | T1 binari upstream |
| eza | T1 cargo build |
| fastfetch | T1 source build atau neofetch |
| code | T2 atau VSCodium default |
| codium | T1 binari upstream |

### Lampiran C: Struktur paket dan direktori

```
packages/arashios-branding/
├── debian/
│   ├── control
│   ├── changelog
│   ├── copyright
│   └── install
└── usr/
    └── share/
        ├── backgrounds/arashios/
        ├── grub/themes/arashios/
        ├── plymouth/themes/arashios/
        └── arashios/branding/

packages/arashios-theme-gtk/
├── debian/
└── usr/share/themes/ArashiKage/
    ├── gtk-2.0/
    ├── gtk-3.0/
    ├── gtk-4.0/
    └── cinnamon/

packages/arashios-arsenal/
├── debian/
└── usr/
    ├── bin/arashios-arsenal
    └── share/arashios/arsenal/
        ├── index.yaml
        └── manifests/
```

### Lampiran D: Aturan penulisan dokumen

Aturan ini berlaku untuk semua dokumen ArashiOS:

1. Dilarang memakai em dash dan en dash. Gunakan hyphen, koma, titik dua, atau susun ulang kalimat.
2. Dilarang memakai emoji di dokumen teknis.
3. Dilarang memakai tanda seru.
4. Setiap klaim performa harus disertai angka dan metode ukur.
5. Setiap persyaratan harus dapat diuji.
6. Gunakan kalimat aktif dan present tense.
7. Hindari kata pengisi: seamless, robust, powerful, cutting-edge, next-generation, revolution, unleash, elevate, empower, holistic, synergy, game-changer, effortless, world-class, best-in-class, state-of-the-art, delve, leverage, utilize.
8. Gunakan istilah teknis Inggris jika istilah Indonesia tidak baku.
9. Tabel dipakai untuk spesifikasi, bukan paragraf panjang.
10. Setiap fase memiliki exit gate yang eksplisit.

### Lampiran E: Glosarium

| Istilah | Definisi |
|---|---|
| T0 | Paket yang tersedia langsung di repo Debian |
| T1 | Paket yang di-vendor atau dibangun dengan versi terkunci |
| T2 | Tool proprietary yang dipasang lewat installer opt-in |
| T3 | Tool yang dijalankan di container |
| Hybrid ISO | ISO yang dapat boot pada BIOS dan UEFI |
| ESP | EFI System Partition |
| LUKS | Linux Unified Key Setup |
| SBOM | Software Bill of Materials |
| MOK | Machine Owner Key |
| Kage | Design system ArashiOS |
| Shizukesa | Nama rilis V1.10.21 |
| Exit gate | Kriteria minimum untuk menyelesaikan fase |

---

Dokumen ini menjadi acuan eksekusi Fase 0. Perubahan scope, arsitektur, atau jadwal wajib dicatat sebagai revisi dokumen dengan tanggal dan alasan.
