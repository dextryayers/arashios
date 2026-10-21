# ArashiOS V1.10.21 - Rencana Induk Produk, Desain, dan Rekayasa

| Atribut | Nilai |
|---|---|
| Dokumen | plan.md |
| Versi dokumen | 2.0 |
| Tanggal | 2026-10-21 |
| Status | Baseline eksekusi |
| Produk | ArashiOS |
| Versi produk | V1.10.21 |
| Nama rilis | Shizukesa |
| Design system | Kage |
| Basis | Debian 12 (bookworm) |
| Build system | live-build |
| Arsitektur | amd64, arm64, i386 |
| Edisi desktop | Cinnamon, XFCE, LXQt |
| Lisensi kode | GPL-3.0-or-later |
| Lisensi aset | CC-BY-SA-4.0 |
| Pemilik | ArashiOS Project |

## Riwayat Revisi

| Versi | Tanggal | Perubahan |
|---|---|---|
| 1.0 | 2026-10-21 | Baseline produk, desain, arsitektur, dan roadmap |
| 2.0 | 2026-10-21 | Deep upgrade: katalog kebutuhan, model ancaman, katalog uji, spesifikasi build, tata kelola, dan rencana rilis |

Dokumen ini adalah sumber kebenaran untuk scope, desain, arsitektur, kualitas, dan urutan rilis ArashiOS. Perubahan scope harus melalui revisi dokumen dan persetujuan maintainer.

---

# BAGIAN I - PRODUK

## 0. Ringkasan Eksekutif

ArashiOS adalah distribusi Linux berbasis Debian 12 untuk operator red team, praktisi keamanan, dan developer. Prioritas produk: keamanan ofensif, lingkungan coding, lalu penggunaan harian. Ketiganya berjalan pada satu instalasi.

Diferensiasi diukur pada empat area:

1. Kurasi. Setiap paket preinstall memiliki manifest, lisensi, pemilik, dan smoke test.
2. Stabilitas. Basis Debian stable dengan tool mutakhir yang di-vendor secara terkontrol.
3. Build assurance. Snapshot Debian, manifest hash, artefak bertanda tangan, dan SBOM.
4. Pengalaman desktop. Design system Kage yang konsisten dari GRUB sampai terminal.

Target v1.0 adalah paritas kemampuan pada 12 alur kerja keamanan inti, bukan paritas jumlah paket dengan Kali, Parrot, atau BlackArch.

Estimasi teknis: 37 person-week termasuk buffer. Dengan dua kontributor setara penuh waktu, kalender rilis 18 sampai 20 minggu. Satu maintainer penuh waktu: 9 sampai 10 bulan. Satu maintainer paruh waktu 20 jam per minggu: 18 sampai 20 bulan.

Definisi sukses v1.0:

1. Tujuh artefak ISO pada matriks rilis.
2. Boot UEFI dan BIOS pada seluruh artefak tier 1.
3. Installer lulus 30 skenario tanpa data loss.
4. Tool security T0 dan T1 lulus smoke test.
5. Toolchain enam bahasa lulus hello world.
6. Tema Kage konsisten pada tiga edisi desktop.
7. Semua artefak memiliki checksum, signature, dan SBOM.
8. Tidak ada telemetry dan tidak ada panggilan jaringan otomatis.

### 0.1 Keputusan yang Dikunci

| Area | Keputusan |
|---|---|
| Basis | Debian 12 bookworm |
| Build | live-build, ISO hybrid |
| Desktop | Cinnamon, XFCE, LXQt |
| Installer | Calamares |
| Theme | Kage, Japanese Minimal dengan aksen red team |
| Tool non-Debian | Vendor saat build, bukan repo Kali permanen |
| Container | Podman rootless default |
| Editor | Neovim dan VSCodium default |
| Telemetry | Tidak ada |
| Versi | V major.MM.DD, baseline V1.10.21 |
| Nama ISO | ArashiOS-<arch>-<versi>[-<edisi>].iso |

---

## 1. Visi, Misi, dan Posisi

### 1.1 Visi

Menjadi distribusi security yang terasa seperti produk jadi: stabil, cepat, konsisten secara visual, dan nyaman dipakai untuk bekerja delapan jam sehari.

### 1.2 Misi

1. Menyediakan tool red team inti yang siap pakai tanpa instalasi tambahan.
2. Menyediakan toolchain coding modern di atas basis Debian stable.
3. Menjaga ISO tetap terkendali melalui kurasi tiga tingkat.
4. Menghasilkan artefak yang dapat diverifikasi secara kriptografis.
5. Menjaga privasi pengguna dan tidak mengumpulkan data.
6. Mendokumentasikan setiap keputusan teknis dan risiko lisensi.

### 1.3 Diferensiasi

| Diferensiasi | Implementasi |
|---|---|
| Kurasi terukur | 130 paket T0, target 40 paket T1, sisanya T2 dan T3 |
| Build assurance | Snapshot, hash manifest, signature, SBOM, build log |
| Desain konsisten | Kage dari bootloader sampai terminal |
| Coding first-class | Toolchain modern dan kebijakan version manager |
| Tiga edisi | Cinnamon, XFCE, LXQt dari satu codebase |
| Privasi | Tanpa telemetry, tanpa akun default, tanpa panggilan boot |

### 1.4 Perbandingan Distro

| Aspek | Kali Linux | Parrot OS | BlackArch | ArashiOS v1 |
|---|---|---|---|---|
| Basis | Debian testing | Debian testing | Arch Linux | Debian 12 stable |
| Model rilis | Rolling | Rolling | Rolling | Point release 4 minggu |
| Tool preinstall | 600+ | 500+ | 2800+ | 130 T0, target 40 T1 |
| Desktop | XFCE, GNOME, KDE | MATE, KDE, XFCE | Window manager bebas | Cinnamon, XFCE, LXQt |
| Fokus coding | Dasar | Dasar | Dasar | Setara fokus security |
| Design system | Tidak ada | Tidak ada | Tidak ada | Kage |
| Build assurance | Tidak publik | Tidak publik | Tidak publik | Reproducible, signed, SBOM |
| ARM | Luas, termasuk NetHunter | Terbatas | Terbatas | arm64 XFCE dan LXQt |
| 32-bit | Terbatas | Terbatas | Tidak | i386 LXQt dan XFCE, tier legacy |
| Dukungan | Komunitas besar | Komunitas menengah | Komunitas khusus | 12 bulan per major |

### 1.5 Definisi Paritas

Paritas diukur pada 12 alur kerja, bukan jumlah paket.

| ID | Alur kerja | Kemampuan minimum v1 |
|---|---|---|
| WF-01 | Reconnaissance | nmap, masscan, arp-scan, dnsrecon, whatweb, amass |
| WF-02 | Web testing | sqlmap, ffuf, gobuster, nuclei, nikto, wpscan |
| WF-03 | Exploitation | Metasploit, searchsploit, exploitdb |
| WF-04 | Password attack | hydra, medusa, john, hashcat, crunch, cewl |
| WF-05 | Active Directory | impacket, netexec, evil-winrm, enum4linux-ng, kerbrute |
| WF-06 | Wireless | aircrack-ng, hcxtools, hcxdumptool, reaver, wifite, kismet |
| WF-07 | Network interception | wireshark, tshark, tcpdump, bettercap, mitmproxy, ettercap |
| WF-08 | Pivoting | chisel, ligolo-ng, proxychains4, socat |
| WF-09 | Forensics | sleuthkit, testdisk, foremost, binwalk, exiftool, volatility3 |
| WF-10 | Reverse engineering | gdb, pwndbg, radare2, ghidra, jadx, apktool |
| WF-11 | Cloud dan container | awscli, azure-cli, kubectl, trivy, podman, ansible |
| WF-12 | Reporting | LibreOffice, pandoc, Obsidian opt-in, template laporan |

Status target: seluruh WF memiliki minimal satu tool yang lulus smoke test pada rilis v1.0.

### 1.6 Persona

| Persona | Kebutuhan | Edisi |
|---|---|---|
| Red team operator | Tool lengkap, pivoting, C2, reporting | Cinnamon |
| Security student dan CTF | Ringan, boot cepat di VM, wordlist siap | XFCE |
| Developer security tooling | Toolchain modern, container, editor | Cinnamon atau XFCE |
| Pengguna harian privacy-aware | Browser, office, media, enkripsi disk | Cinnamon |
| Hardware lama atau VM 2 GB | RAM kecil, boot cepat | LXQt |

### 1.7 Non-goals v1

1. Desktop environment baru dari nol.
2. Package manager baru.
3. Menyamai jumlah paket BlackArch.
4. Secure Boot dengan kernel bertanda tangan pada rilis pertama.
5. Installer tanpa interaksi.
6. Redistribusi tool proprietary.
7. Layanan cloud, VPN, atau akun bawaan.
8. Dukungan resmi untuk arsitektur di luar amd64, arm64, dan i386.
9. Wayland sebagai default.
10. Rolling release.

---

## 2. Prinsip Produk dan Rekayasa

| ID | Prinsip | Konsekuensi |
|---|---|---|
| PR-01 | Kurasi di atas kuantitas | Setiap paket punya manifest, lisensi, dan test |
| PR-02 | Basis stabil, tool mutakhir | Debian stable, backports terbatas, vendor terkunci |
| PR-03 | Reproducible by default | Snapshot, SOURCE_DATE_EPOCH, diffoscope |
| PR-04 | Offline capable | Tool berfungsi tanpa jaringan setelah instalasi |
| PR-05 | Privacy first | Tanpa telemetry, analytics, atau akun default |
| PR-06 | Tiga edisi, satu codebase | Overlay konfigurasi, bukan fork |
| PR-07 | Desain dengan batasan | Token warna, tipe, dan spacing dikunci |
| PR-08 | Legal clarity | Proprietary hanya lewat installer opt-in |
| PR-09 | Measurable quality | Setiap klaim punya budget dan test |
| PR-10 | Sustainable maintenance | Otomasi dan scope per rilis |

---

## 3. Scope, Asumsi, dan Batasan

### 3.1 In Scope v1.0

| Area | Cakupan |
|---|---|
| Sistem | Debian 12 bookworm amd64, arm64, i386 |
| Boot | UEFI dan BIOS, live dan installed |
| Desktop | Cinnamon, XFCE, LXQt |
| Installer | Calamares, erase, alongside, manual, LUKS, LVM |
| Security | T0 dan T1 untuk 12 alur kerja |
| Coding | Python, Go, Rust, Node, Java, C/C++ |
| Daily | Browser, office, media, print, Bluetooth, power |
| Update | APT repo ArashiOS, Debian security |
| Assurance | Checksum, signature, SBOM, build log |
| Dokumentasi | Instalasi, dual boot, hardening, kontribusi |

### 3.2 Out of Scope v1.0

| Area | Alasan |
|---|---|
| Secure Boot signed | Butuh shim dan MOK, dijadwalkan pasca v1 |
| Wayland default | Fokus stabilitas X11 |
| NetHunter | Khusus Android, di luar produk |
| Windows Subsystem for Linux | Dijadwalkan pasca v1 |
| Cloud images | Dijadwalkan pasca v1 |
| Rolling release | Model point release dipilih |
| Tool proprietary | Lisensi dan redistribusi |

### 3.3 Asumsi

1. Build host x86_64 dengan minimal 16 GB RAM dan 25 GB disk.
2. Mirror Debian dapat diakses saat build.
3. Pengguna target memiliki pemahaman dasar keamanan.
4. Hardware uji tersedia untuk laptop Intel, AMD, dan perangkat ARM.
5. Maintainer memiliki kunci GPG dan minisign.

### 3.4 Batasan

1. Debian 12 didukung hingga Juni 2028.
2. Kernel default 6.1 LTS.
3. i386 memiliki coverage tool terbatas.
4. arm64 membutuhkan runner native atau QEMU.
5. Secure Boot harus dimatikan pada v1.
6. Tool proprietary tidak boleh dibundel.

---

## 4. Model Rilis dan Dukungan

### 4.1 Skema Versi

`V<major>.<MM>.<DD>`

Contoh: V1.10.21 berarti major 1, bulan 10, tanggal 21. Baseline proyek memakai 2026-10-21.

| Perubahan | Dampak versi |
|---|---|
| Rebase basis atau breaking change | Major naik |
| Rilis bulanan | MM dan DD berubah |
| Hotfix | Tanggal rilis baru |
| Perubahan paket minor | Tanggal rilis baru |

### 4.2 Kanal

| Kanal | Frekuensi | Stabilitas | Pengguna |
|---|---|---|---|
| stable | 4 minggu | Tinggi | Produksi |
| edge | 1 minggu | Sedang | Pengguna awal |
| nightly | Harian | Rendah | Kontributor dan QA |

### 4.3 Siklus Dukungan

1. Setiap major didukung 12 bulan.
2. Rilis terakhir major mendapat 6 bulan tambahan.
3. Debian 12 LTS berakhir Juni 2028.
4. ArashiOS v1 mengikuti batas Debian 12.
5. Rebase ke Debian 13 direncanakan pada v2.

### 4.4 Kompatibilitas

1. Upgrade antar rilis minor didukung tanpa reinstalasi.
2. Downgrade tidak didukung.
3. Perubahan major boleh memerlukan reinstalasi.
4. Konfigurasi pengguna di `/etc` dipertahankan dengan prompt.
5. Paket yang dihapus upstream diumumkan di release notes.

---

## 5. Katalog Kebutuhan

Kebutuhan diberi ID dan diverifikasi pada fase yang disebut. Katalog lengkap dengan traceability ada di Lampiran H.

### 5.1 Functional Requirements

| ID | Kebutuhan | Kriteria penerimaan | Fase |
|---|---|---|---|
| FR-001 | ISO boot UEFI dan BIOS | Boot ke desktop pada QEMU kedua mode | 1 |
| FR-002 | Tiga edisi desktop | Cinnamon, XFCE, LXQt masing-masing boot | 3 |
| FR-003 | Live user | User `arashi`, autologin live, tanpa password | 1 |
| FR-004 | Installer | Calamares menyelesaikan erase, alongside, manual | 7 |
| FR-005 | LUKS dan LVM | Instalasi terenkripsi dapat dibuka kembali | 7 |
| FR-006 | Persistence | Data bertahan setelah reboot | 7 |
| FR-007 | Tool security T0 | 100 persen smoke test lulus | 4 |
| FR-008 | Tool security T1 | 100 persen smoke test lulus | 4 |
| FR-009 | Arsenal | list, info, install, remove, verify berfungsi | 4 |
| FR-010 | Coding toolchain | Enam bahasa kompilasi hello world | 5 |
| FR-011 | Container | Podman rootless menjalankan hello-world | 5 |
| FR-012 | Daily apps | Browser, office, media, print berfungsi | 6 |
| FR-013 | Update | apt update dan upgrade berhasil | 8 |
| FR-014 | Recovery | chroot dan grub repair berfungsi | 7 |
| FR-015 | Multi-arch | amd64, arm64, i386 menghasilkan ISO | 1, 10 |

### 5.2 Security Requirements

| ID | Kebutuhan | Kriteria penerimaan | Fase |
|---|---|---|---|
| SR-001 | Tanpa repo Kali runtime | sources.list hanya Debian dan repo ArashiOS | 4 |
| SR-002 | Artefak bertanda tangan | Semua ISO memiliki signature valid | 9 |
| SR-003 | Checksum | SHA256 dan SHA512 tersedia | 10 |
| SR-004 | SBOM | CycloneDX per ISO | 9 |
| SR-005 | Tanpa telemetry | Tidak ada koneksi otomatis saat boot | 9 |
| SR-006 | Tanpa kredensial default | Tidak ada password default | 7 |
| SR-007 | Hardening default | UFW, AppArmor, sysctl sesuai daftar | 9 |
| SR-008 | Tanpa SSH server | Hanya openssh-client | 9 |
| SR-009 | Vendor terverifikasi | Setiap T1 punya checksum dan manifest | 4 |
| SR-010 | glibc compatibility | Tidak ada simbol di atas GLIBC_2.36 | 4 |
| SR-011 | Supply chain | Snapshot dan build container bersih | 9 |
| SR-012 | CVE | Tidak ada critical atau high saat rilis | 9 |
| SR-013 | Disclosure | Kanal privat dan SLA 72 jam | 9 |
| SR-014 | Lisensi | Copyright lengkap untuk semua paket | 9 |
| SR-015 | Reproducibility | Hash identik atau laporan diffoscope | 9 |

### 5.3 Performance Requirements

| ID | Kebutuhan | Target | Fase |
|---|---|---|---|
| PR-001 | RAM idle Cinnamon | Maksimal 800 MB | 3 |
| PR-002 | RAM idle XFCE | Maksimal 550 MB | 3 |
| PR-003 | RAM idle LXQt | Maksimal 420 MB | 3 |
| PR-004 | Boot QEMU Cinnamon | Maksimal 35 detik | 3 |
| PR-005 | Boot QEMU XFCE | Maksimal 30 detik | 3 |
| PR-006 | Boot QEMU LXQt | Maksimal 25 detik | 3 |
| PR-007 | Ukuran ISO Cinnamon | Maksimal 4.2 GB | 4 |
| PR-008 | Ukuran ISO XFCE | Maksimal 3.9 GB | 4 |
| PR-009 | Ukuran ISO LXQt | Maksimal 3.5 GB | 4 |
| PR-010 | Shell startup | Maksimal 300 ms | 5 |

### 5.4 UX dan Accessibility Requirements

| ID | Kebutuhan | Kriteria penerimaan | Fase |
|---|---|---|---|
| UX-001 | Kage consistency | Boot, greeter, desktop, terminal memakai token sama | 2, 3 |
| UX-002 | Kontras teks | Teks utama minimal 7:1, sekunder 4.5:1 | 2 |
| UX-003 | Fokus keyboard | Outline 2 px terlihat pada semua kontrol | 3 |
| UX-004 | Navigasi keyboard | Installer dan greeter dapat diselesaikan tanpa mouse | 3, 7 |
| UX-005 | Reduced motion | Animasi dapat dimatikan | 3 |
| UX-006 | Skala font | 100, 125, 150 persen tanpa clipping | 3 |
| UX-007 | Status tidak warna saja | Ikon atau teks mendampingi warna | 3 |
| UX-008 | Locale | en_US, id_ID, ja_JP tampil benar | 6 |
| UX-009 | Screen reader | Orca tersedia dan dapat dijalankan | 6 |
| UX-010 | Dual boot clarity | Peringatan BitLocker dan Fast Startup | 7 |

### 5.5 Compliance Requirements

| ID | Kebutuhan | Kriteria penerimaan | Fase |
|---|---|---|---|
| CR-001 | Lisensi kode | GPL-3.0-or-later konsisten | 0 |
| CR-002 | Lisensi aset | CC-BY-SA-4.0 dan atribusi | 2 |
| CR-003 | Trademark Debian | Tidak memakai logo Debian sebagai identitas | 2 |
| CR-004 | Trademark ArashiOS | Pencarian merek dan domain | 0 |
| CR-005 | Export notice | Disclaimer dual-use | 0 |
| CR-006 | GPL compliance | Source atau tawaran source untuk paket GPL | 9 |
| CR-007 | Privacy policy | Tanpa data collection | 9 |
| CR-008 | Code of conduct | Contributor Covenant 2.1 | 0 |

---

# BAGIAN II - DESAIN

## 6. Design System Kage

### 6.1 Konsep

Kage (影) berarti bayangan. Sistem visual menggabungkan estetika Jepang yang tenang dengan aksen red team yang tegas.

| Prinsip | Implementasi |
|---|---|
| Ma (間) | Ruang kosong sebagai elemen aktif |
| Kanso (簡素) | Tanpa ornamen yang tidak berfungsi |
| Shibui (渋い) | Warna tenang, aksen tajam |
| Shinobi (忍び) | Siluet gelap, kontras rendah pada permukaan |
| Blade | Garis 1 px, sudut 2 px, tanpa bayangan tebal |

Warna merah hanya untuk aksi, fokus, dan peringatan. Merah tidak dipakai sebagai dekorasi.

### 6.2 Token Warna

| Token | Hex | Peran | Porsi layar |
|---|---|---|---|
| sumi-900 | #0A0A0C | Latar utama | 55 sampai 60 persen |
| sumi-800 | #121215 | Panel dan jendela | 20 sampai 25 persen |
| sumi-700 | #1B1B20 | Menu, tooltip, permukaan naik | 8 persen |
| steel-600 | #2C2C33 | Border dan pemisah | 5 persen |
| ash-400 | #8B867D | Teks sekunder | 3 persen |
| washi-100 | #EDE8DE | Teks utama | 4 persen |
| vermilion-500 | #C9382E | Aksi, indikator aktif | 2 persen |
| vermilion-400 | #E04B3D | Hover dan fokus | 1 persen |
| ember-300 | #F06A5A | Teks aksen di latar gelap | 0.5 persen |
| jade-500 | #5C8F7A | Sukses | 0.3 persen |
| gold-500 | #B08D57 | Peringatan | 0.3 persen |
| blood-700 | #7E1D18 | Latar destructive | 0.2 persen |

Kontras terukur:

| Pasangan | Rasio | Aturan |
|---|---|---|
| washi-100 pada sumi-900 | 16.20:1 | Teks utama, lulus AAA |
| washi-100 pada sumi-800 | 15.31:1 | Teks utama di panel, lulus AAA |
| ash-400 pada sumi-900 | 5.47:1 | Teks sekunder, lulus AA |
| ember-300 pada sumi-900 | 6.51:1 | Teks aksen, lulus AA |
| vermilion-400 pada sumi-900 | 4.94:1 | Teks aksen kecil, lulus AA |
| vermilion-500 pada sumi-900 | 3.85:1 | Hanya komponen UI dan teks besar |
| vermilion-500 pada washi-100 | 4.21:1 | Hanya komponen UI dan teks besar |
| jade-500 pada sumi-900 | 5.34:1 | Status sukses |
| gold-500 pada sumi-900 | 6.40:1 | Status peringatan |
| blood-700 pada sumi-900 | 1.96:1 | Hanya latar, tidak untuk teks |

Aturan tambahan:

1. Teks aksen di atas sumi-900 memakai ember-300, bukan vermilion-500.
2. Vermilion-500 hanya untuk border fokus, indikator aktif, dan teks 18 px ke atas.
3. Status tidak boleh dibedakan hanya dengan warna.
4. Setiap token diverifikasi ulang pada Fase 2 dengan skrip kontras di CI.

### 6.3 Tipografi

| Peran | Font | Berat | Ukuran | Line height | Tracking |
|---|---|---|---|---|---|
| Wordmark | Shippori Mincho | 600 | 32 sampai 48 px | 1.1 | 0.02em |
| Judul layar | Inter | 600 | 24 px | 1.2 | 0 |
| Judul seksi | Inter | 600 | 18 px | 1.2 | 0 |
| Body | Inter | 400 | 14 px | 1.4 | 0 |
| Label | Inter | 500 | 11 px uppercase | 1.2 | 0.08em |
| Data | JetBrains Mono | 400 | 13 px | 1.4 | 0 |
| Terminal | JetBrains Mono | 400 | 11 sampai 13 px | 1.5 | 0 |
| Fallback Jepang | Noto Sans JP | 400 | mengikuti body | 1.4 | 0 |

Aturan:

1. Maksimal dua keluarga font per layar.
2. Tidak memakai font weight di bawah 400 untuk teks kecil.
3. Tidak memakai uppercase untuk kalimat panjang.
4. Font UI minimal 11 px.
5. Font terminal minimal 11 px.

### 6.4 Spacing, Radius, Elevasi, dan Gerak

| Token | Nilai | Pemakaian |
|---|---|---|
| space-1 | 4 px | Jarak ikon dan teks |
| space-2 | 8 px | Padding kontrol kecil |
| space-3 | 12 px | Padding standar |
| space-4 | 16 px | Jarak antar grup |
| space-6 | 24 px | Jarak antar seksi |
| space-8 | 32 px | Margin layar |
| space-12 | 48 px | Pemisah besar |
| radius-sm | 2 px | Tombol dan input |
| radius-md | 4 px | Dialog, maksimum |
| border | 1 px solid steel-600 | Semua pemisah |
| shadow-menu | 0 8px 24px rgba(0,0,0,0.45) | Hanya menu dan popover |

Gerak:

| Aksi | Durasi | Easing |
|---|---|---|
| Hover | 120 ms | cubic-bezier(0.2, 0, 0, 1) |
| Panel | 180 ms | cubic-bezier(0.2, 0, 0, 1) |
| Dialog | 240 ms | cubic-bezier(0.2, 0, 0, 1) |
| Boot | 1500 ms | linear |

Tanpa bounce, tanpa animasi lebih dari 300 ms, tanpa parallax. Reduced motion mematikan animasi Plymouth dan transisi panel.

### 6.5 Logo dan Wordmark

1. Mark utama: karakter 嵐 dalam Shippori Mincho, dikelilingi ensō 1.5 px.
2. Wordmark: ARASHIOS dalam Inter 600, uppercase, tracking 0.12em.
3. Lockup horizontal: mark kiri, wordmark kanan, jarak 8 px.
4. Varian: penuh warna, monokrom washi, monokrom sumi, 16 px favicon.
5. Clear space minimal setengah tinggi mark.
6. Ukuran digital minimum 24 px.
7. Logo Debian tidak dipakai sebagai identitas utama.
8. Atribusi "based on Debian" ada di About dan dokumentasi.

### 6.6 Wallpaper

| Nama | Deskripsi | Mode |
|---|---|---|
| kage-sumi | Gradient sumi, ensō, grain halus | Gelap, default |
| kage-shuriken | Pola geometri shuriken kontras 4 persen | Gelap |
| kage-bamboo | Siluet bambu rendah kontras | Gelap |
| kage-washi | Tekstur washi dengan segel merah | Terang |
| kage-storm | Garis isobar dan petir tipis | Gelap |

Spesifikasi:

1. Resolusi 3840x2160.
2. Format PNG untuk distribusi, SVG untuk sumber.
3. Ukuran PNG maksimal 4 MB per file.
4. Lisensi CC-BY-SA-4.0.
5. Tanpa wallpaper pihak ketiga tanpa lisensi.

### 6.7 Ikonografi dan Kursor

1. Basis Papirus-Dark, GPL-3.0.
2. Folder memakai sumi-700, bukan merah.
3. Ikon khusus: Arsenal, Control Center, Help.
4. Gaya: garis 1.5 px, sudut 1 px, tanpa gradient.
5. Ukuran panel 16 px, menu 24 px, aplikasi 32 px.
6. Kursor Bibata Modern Classic gelap, fallback Adwaita yang diwarnai ulang.
7. Ikon status memakai bentuk sederhana, bukan emoji.

### 6.8 Spesifikasi Komponen

| Komponen | Spesifikasi |
|---|---|
| Panel | Tinggi 30 px, sumi-900 96 persen, border bawah 1 px steel |
| Menu | Lebar 360 px, padding 8 px, item 32 px, indikator aktif 2 px vermilion |
| Tombol | Tinggi 32 px, padding 12 px, radius 2 px, border 1 px steel |
| Tombol primer | Latar vermilion-500, teks washi-100, hover vermilion-400 |
| Input | Tinggi 32 px, border 1 px steel, fokus border vermilion-400 2 px |
| Notifikasi | Lebar 320 px, kanan atas, border 1 px, tanpa radius |
| Dialog | Lebar maksimal 560 px, padding 24 px, radius 4 px |
| Tooltip | Latar sumi-700, teks washi-100, padding 6 px 8 px |
| Progress | Tinggi 2 px, track steel-600, isi vermilion-500 |
| Terminal | Latar sumi-900, teks washi-100, kursor vermilion-400 |

### 6.9 Boot Experience

| Tahap | Implementasi | Durasi target |
|---|---|---|
| GRUB | Latar sumi-900, wordmark 嵐, menu kanan, garis seleksi vermilion 2 px | Timeout 5 detik |
| Plymouth | Latar sumi-900, teks ARASHIOS, progress arc vermilion | 3 sampai 5 detik |
| LightDM | Wallpaper kage-sumi, jam tengah, kotak login border 1 px | 1 detik |
| Desktop | Panel dan wallpaper tanpa flicker | 2 detik |

Ketentuan:

1. GRUB menyediakan entri uji "ArashiOS serial console" dengan `console=ttyS0,115200`.
2. Plymouth memakai font DejaVu Sans agar aman di initramfs.
3. LightDM memakai wallpaper yang sama dengan desktop default.
4. Tidak ada logo Debian pada layar boot.
5. Boot log dapat diakses dengan tombol Esc.

### 6.10 Layout per Desktop

#### Cinnamon

1. Panel atas 30 px, sumi-900 96 persen, border bawah 1 px.
2. Menu Arashi di kiri dengan kategori dan indikator aktif vermilion.
3. Window list ikon saja, tanpa label.
4. Jam tengah, JetBrains Mono, format `YYYY.MM.DD HH:MM`.
5. Empat workspace dengan indikator garis vertikal.
6. Desktop tanpa ikon.
7. Nemo list view, tanpa thumbnail untuk file tidak dikenal.
8. Notifikasi kanan atas, border 1 px, tanpa radius.

#### XFCE

1. Panel atas 30 px dengan Whisker Menu, tasklist, jam, tray, power.
2. Empat workspace dengan indikator kotak 6 px.
3. Thunar list view.
4. xfwm4 compositor dengan shadow halus, tanpa blur.
5. xfce4-terminal dengan JetBrains Mono 11 px.
6. Tanpa desktop icon.

#### LXQt

1. Panel atas 30 px dengan Quick Launch, Taskbar, Tray, Clock.
2. Openbox sebagai window manager, border aktif vermilion 2 px.
3. Kvantum ArashiKage untuk Qt.
4. PCManFM-Qt list view.
5. QTerminal JetBrains Mono 11 px.
6. Tanpa desktop icon dan tanpa compositor berat.

Aturan umum:

1. Tidak ada dock melayang.
2. Tidak ada widget jam besar di desktop.
3. Tidak ada animasi startup.
4. Desktop terlihat tenang saat tidak ada jendela.

### 6.11 Terminal dan Editor

1. Shell default zsh.
2. Prompt starship bertema Kage jika tersedia, fallback prompt zsh minimal.
3. Prompt menampilkan direktori, branch git, status exit, dan durasi perintah.
4. Tanpa emoji di prompt.
5. Palet terminal diturunkan dari Kanagawa, atribusi MIT.
6. Neovim memakai colorscheme `arashios-kage`, plugin minimum.
7. Tmux status bar sumi-800, indikator aktif vermilion.
8. Neofetch menampilkan mark 嵐 dan informasi sistem tanpa ASCII besar.

### 6.12 Aksesibilitas

1. Fokus keyboard: outline 2 px vermilion-400, offset 2 px.
2. Semua aksi dapat dicapai dengan keyboard.
3. Status memakai ikon atau teks, bukan warna saja.
4. Orca tersedia di metapackage daily.
5. Mode kontras tinggi `kage-contrast` disediakan.
6. Installer dan greeter diuji tanpa mouse.
7. Skala font 100, 125, 150 persen diuji.
8. Reduced motion dihormati.
9. Target ukuran klik minimal 32x32 px.
10. Teks tidak lebih kecil dari 11 px.

### 6.13 Checklist Visual

| ID | Pemeriksaan | Lulus jika |
|---|---|---|
| VQ-01 | Palet | Tidak ada warna di luar token |
| VQ-02 | Kontras | Semua teks lulus AA |
| VQ-03 | Tipografi | Maksimal dua keluarga font per layar |
| VQ-04 | Spacing | Semua jarak kelipatan 4 px |
| VQ-05 | Radius | Tidak ada radius di atas 4 px |
| VQ-06 | Shadow | Hanya menu dan popover |
| VQ-07 | Aksen | Maksimal satu aksen merah per layar |
| VQ-08 | Ikon | Tidak ada emoji di UI sistem |
| VQ-09 | Motion | Tidak ada animasi di atas 300 ms |
| VQ-10 | Empty state | Setiap layar kosong punya pesan jelas |

---

## 7. Implementasi Desain

### 7.1 Pipeline Token

```
branding/tokens.json
        |
        +--> scss/_tokens.scss
        +--> gtk-3.0/gtk.css
        +--> gtk-4.0/gtk.css
        +--> cinnamon/cinnamon.css
        +--> qt/ArashiKage.kvconfig
        +--> xfce/xfconf.xml
        +--> openbox/themerc
        +--> plymouth/arashios.script
```

Aturan:

1. `tokens.json` adalah satu-satunya sumber warna, font, spacing, dan radius.
2. File turunan dihasilkan oleh `scripts/generate-theme.sh`.
3. Perubahan manual pada file turunan ditolak di code review.
4. Setiap build tema menjalankan validasi kontras.
5. Token diberi versi dan changelog.

### 7.2 Paket Tema

| Paket | Isi | Dependensi |
|---|---|---|
| arashios-theme-gtk | GTK3, GTK4, libadwaita override | gtk2-engines, gtk3 |
| arashios-theme-cinnamon | cinnamon.css, thumbnail | cinnamon |
| arashios-theme-qt | Kvantum, qt5ct | qt5-style-kvantum |
| arashios-theme-xfce | xfwm4, xfce4-terminal | xfce4 |
| arashios-theme-openbox | themerc, menu.xml | openbox |
| arashios-icons | Papirus turunan, ikon khusus | papirus-icon-theme |
| arashios-branding | Wallpaper, logo, GRUB, Plymouth, LightDM | plymouth, grub-common |

### 7.3 Detail per Toolkit

GTK3:

1. Tema di `/usr/share/themes/ArashiKage/gtk-3.0/`.
2. Warna memakai `@define-color`.
3. Uji dengan Nemo, Thunar, PCManFM-Qt, LightDM greeter.
4. Tidak memakai CSS yang tidak didukung GTK 3.24.

GTK4 dan libadwaita:

1. Tema di `/usr/share/themes/ArashiKage/gtk-4.0/`.
2. libadwaita tidak sepenuhnya mengikuti tema GTK.
3. Override memakai `~/.config/gtk-4.0/gtk.css` dan `/etc/gtk-4.0/gtk.css`.
4. Aplikasi libadwaita diuji: Nautilus jika ada, GNOME Disks, Evince.
5. Jika override tidak stabil, aplikasi memakai Adwaita dengan wallpaper Kage.

Cinnamon:

1. `cinnamon.css` di `/usr/share/themes/ArashiKage/cinnamon/`.
2. Panel, menu, popup, dan workspace diuji.
3. Thumbnail tema 256x256.
4. Tidak memakai gambar raster untuk elemen yang bisa CSS.

Qt dan LXQt:

1. Kvantum SVG di `/usr/share/Kvantum/ArashiKage/`.
2. `qt5ct` mengatur font dan palette.
3. `QT_STYLE_OVERRIDE=kvantum` di `/etc/environment`.
4. Openbox `themerc` untuk border dan titlebar.
5. Uji QTerminal, PCManFM-Qt, LXQt panel, dan dialog Qt.

XFCE:

1. `xfwm4/themerc` untuk border.
2. `xfce4-terminal` color palette di `terminalrc`.
3. Panel layout di `xfconf/xfce-perchannel-xml/xfce4-panel.xml`.
4. Wallpaper di `xfce4-desktop.xml`.
5. Uji Whisker Menu dan tasklist.

LightDM:

1. `lightdm-gtk-greeter` dengan tema GTK.
2. Background `/usr/share/backgrounds/arashios/kage-sumi.png`.
3. Clock format `%H:%M`, tanggal `%Y.%m.%d`.
4. Autologin live user `arashi`.
5. Setelah instalasi, autologin dinonaktifkan.

### 7.4 Tata Kelola Desain

1. Setiap aset baru harus memiliki sumber SVG dan lisensi.
2. Perubahan visual melewati review desain.
3. Screenshot before dan after disertakan di pull request.
4. Checklist VQ-01 sampai VQ-10 wajib lulus.
5. Design token tidak boleh diubah tanpa ADR.
6. Aset raster tidak disimpan jika SVG memungkinkan.
7. Ukuran repository aset dijaga di bawah 25 MB.
