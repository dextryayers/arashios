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

---

# BAGIAN III - ARSITEKTUR DAN BUILD

## 8. Arsitektur Sistem

### 8.1 Lapisan

```
+------------------------------------------------------------------+
| Aplikasi                                                         |
| security tools, coding tools, daily apps, arsenal                 |
+------------------------------------------------------------------+
| Desktop                                                          |
| Cinnamon / XFCE / LXQt + tema Kage + LightDM                     |
+------------------------------------------------------------------+
| Paket ArashiOS                                                   |
| branding, theme, desktop, meta, arsenal, keyring                 |
+------------------------------------------------------------------+
| Debian 12 bookworm                                               |
| kernel 6.1 LTS, systemd, APT, firmware, security repo            |
+------------------------------------------------------------------+
| Live layer                                                       |
| live-boot, live-config, squashfs, hybrid ISO, persistence        |
+------------------------------------------------------------------+
| Firmware                                                         |
| UEFI, BIOS, GRUB, shim (pasca v1)                                |
+------------------------------------------------------------------+
```

### 8.2 Alur Boot

```
Firmware
  |
  +-- UEFI: ESP/EFI/arashios/grubx64.efi
  |     atau EFI/BOOT/BOOTX64.EFI
  |
  +-- BIOS: MBR -> GRUB stage 1.5 -> stage 2
        |
        v
      GRUB menu
        |
        v
      kernel + initramfs
        |
        v
      live-boot (squashfs) atau rootfs terpasang
        |
        v
      systemd
        |
        v
      LightDM -> sesi desktop
```

### 8.3 Prinsip Arsitektur

1. Satu codebase untuk tiga edisi.
2. Semua kustomisasi masuk paket, bukan file lepas.
3. Tidak ada repository pihak ketiga pada sistem terpasang selain repo ArashiOS yang ditandatangani.
4. Live dan installed system memakai paket yang sama.
5. Installer tidak menghapus data tanpa konfirmasi eksplisit.
6. Semua layanan default dapat diaudit.

---

## 9. Basis Debian dan Kernel

### 9.1 Basis

| Komponen | Nilai |
|---|---|
| Distribusi | Debian 12 bookworm |
| Komponen APT | main, contrib, non-free, non-free-firmware |
| Init | systemd |
| Kernel default | linux-image-amd64 6.1 LTS |
| Kernel alternatif | bookworm-backports 6.12, opt-in |
| Firmware | non-free-firmware |
| glibc | 2.36 |
| Python sistem | 3.11 |
| GCC | 12 |
| OpenSSL | 3.0 |

### 9.2 Kebijakan Kernel

1. Kernel default dari bookworm, tanpa patch out-of-tree.
2. Kernel backports tersedia sebagai paket `linux-image-amd64` dari backports, tidak default.
3. Module signing tidak diaktifkan pada v1.
4. Secure Boot harus dimatikan pada v1.
5. Kernel command line default: `quiet splash`.
6. Parameter debugging tersedia melalui entri GRUB terpisah.
7. Update kernel mengikuti Debian security.
8. Kernel lama dipertahankan minimal satu versi untuk rollback.

### 9.3 Firmware

1. Firmware WiFi: iwlwifi, realtek, atheros, brcm80211.
2. Firmware GPU: amdgpu, intel-sound.
3. Firmware misc: `firmware-misc-nonfree`.
4. Firmware NVIDIA proprietary tidak dibundel pada v1.
5. `fwupd` tersedia untuk update firmware perangkat yang mendukung.

---

## 10. Build System

### 10.1 Kontrak build.sh

| Aspek | Kontrak |
|---|---|
| Input | `--edition`, `--arch`, `--version`, `--jobs` |
| Environment | `versions.env`, `APT_PROXY`, `MINISIGN_KEY` |
| Output | ISO, sha256, sha512, optional signature |
| Exit code | 0 sukses, non-zero gagal |
| Log | `build/<edition>-<arch>/build.log` |
| Workdir | `build/<edition>-<arch>/` |
| Artefak | `out/ArashiOS-<arch>-<versi>[-<edisi>].iso` |

Aturan:

1. Build gagal cepat jika perintah wajib tidak ada.
2. Build gagal jika versi tidak sesuai pola.
3. Build gagal jika edisi atau arsitektur tidak didukung.
4. Build tidak menghapus artefak lama di `out/` kecuali nama sama.
5. Build menolak berjalan sebagai root tanpa peringatan.
6. Build mencatat versi host, waktu, dan hash konfigurasi.

### 10.2 Pipeline live-build

| Tahap | Perintah atau aksi | Output |
|---|---|---|
| 1 | Validasi argumen dan environment | Log |
| 2 | `lb config` dengan opsi proyek | config default |
| 3 | Overlay `config/common` | konfigurasi dasar |
| 4 | Overlay `config/editions/<edition>` | konfigurasi edisi |
| 5 | Tulis metadata edisi, versi, arch | `/etc/arashios/*` |
| 6 | `lb build` | rootfs, squashfs, ISO |
| 7 | Rename dan checksum | artefak final |
| 8 | Signature jika kunci tersedia | `.sig` |

### 10.3 Opsi live-build

```bash
lb config \
  --distribution bookworm \
  --architectures amd64 \
  --binary-images iso-hybrid \
  --bootloaders "syslinux,grub-efi" \
  --debian-installer none \
  --archive-areas "main contrib non-free non-free-firmware" \
  --linux-flavours amd64 \
  --iso-application "ArashiOS" \
  --iso-publisher "ArashiOS Project" \
  --iso-volume "ARASHIOS_V1_10_21" \
  --hostname arashios \
  --bootappend-live "boot=live components quiet splash username=arashi hostname=arashios" \
  --apt-indices false \
  --memtest none \
  --zsync false
```

Catatan:

1. arm64 memakai `--bootloaders grub-efi`.
2. i386 memakai `--linux-flavours 686-pae`.
3. Volume ID maksimal 32 karakter, uppercase, tanpa spasi.
4. `--apt-indices false` menghemat ukuran ISO.
5. `--zsync false` menghindari dependensi tambahan pada build host.

### 10.4 Lingkungan Build

| Komponen | Versi atau konfigurasi |
|---|---|
| Host | Debian 12 container |
| live-build | Versi bookworm |
| debootstrap | Versi bookworm |
| xorriso | Versi bookworm |
| squashfs-tools | Versi bookworm |
| QEMU | Untuk uji boot |
| OVMF | Untuk uji UEFI |
| apt-cacher-ng | Cache paket |
| Disk | Minimal 25 GB |
| RAM | Minimal 8 GB, disarankan 16 GB |
| CPU | 4 core minimum, 8 core disarankan |

### 10.5 Mode Kegagalan

| Gejala | Penyebab umum | Tindakan |
|---|---|---|
| Paket tidak ditemukan | Nama paket salah atau arsip tidak aktif | Periksa package list dan komponen APT |
| Dependency conflict | Versi vendor tidak cocok | Turunkan ke T3 atau pin versi |
| ISO tidak boot UEFI | GRUB EFI tidak terpasang | Periksa `grub-efi-amd64-bin` dan ESP image |
| ISO tidak boot BIOS | syslinux tidak terpasang | Periksa `isolinux` dan `syslinux-common` |
| Build kehabisan disk | Cache dan workdir menumpuk | Bersihkan `build/`, cek `df` |
| Build lambat | Tidak ada cache APT | Aktifkan apt-cacher-ng |
| Ukuran ISO melebihi budget | Terlalu banyak paket | Pindahkan tool ke T2 atau T3 |
| Boot hang | Firmware atau driver | Uji dengan `nomodeset` dan serial console |

### 10.6 Cache

1. apt-cacher-ng berjalan di `127.0.0.1:3142`.
2. Build memakai `APT_PROXY=http://127.0.0.1:3142`.
3. Cache tidak boleh menyimpan paket dari repo tidak tepercaya.
4. Cache dibersihkan setiap 30 hari.
5. Build nightly memakai cache terpisah.

### 10.7 Reproducibility

1. `SOURCE_DATE_EPOCH` diambil dari tanggal versi.
2. Snapshot Debian dikunci di `versions.env`.
3. UUID ISO, volume ID, dan label deterministik.
4. `mksquashfs` memakai `-noappend` dan `-all-time`.
5. Permission dan ownership dinormalisasi di hook.
6. Urutan file dalam arsip distabilkan.
7. `diffoscope` dijalankan antara dua build.
8. Selisih yang diketahui didokumentasikan di `docs/REPRODUCIBILITY.md`.
9. Target: hash identik pada Fase 9.

---

## 11. Struktur Repository dan Paket

### 11.1 Struktur

```
arashios/
├── plan.md
├── README.md
├── LICENSE
├── build.sh
├── Makefile
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
│   ├── tokens.json
│   ├── logo/
│   ├── wallpaper/
│   ├── grub/
│   ├── plymouth/
│   └── lightdm/
├── packages/
│   ├── arashios-branding/
│   ├── arashios-theme-gtk/
│   ├── arashios-theme-cinnamon/
│   ├── arashios-theme-qt/
│   ├── arashios-theme-xfce/
│   ├── arashios-theme-openbox/
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
├── tests/
├── docs/
└── out/
```

### 11.2 Paket Inti

| Paket | Isi | Arch |
|---|---|---|
| arashios-branding | os-release, issue, wallpaper, GRUB, Plymouth, LightDM | all |
| arashios-theme-gtk | GTK3, GTK4, libadwaita override | all |
| arashios-theme-cinnamon | cinnamon.css, thumbnail | all |
| arashios-theme-qt | Kvantum, qt5ct | all |
| arashios-theme-xfce | xfwm4, terminalrc | all |
| arashios-theme-openbox | themerc, menu.xml | all |
| arashios-icons | Papirus turunan, ikon khusus | all |
| arashios-desktop-common | Skel, zsh, tmux, neovim, font | all |
| arashios-desktop-cinnamon | Cinnamon, Nemo, layout | all |
| arashios-desktop-xfce | XFCE, Thunar, layout | all |
| arashios-desktop-lxqt | LXQt, PCManFM-Qt, Openbox | all |
| arashios-meta-redteam | Daftar paket T0 dan T1 | all |
| arashios-meta-dev | Toolchain dan editor | all |
| arashios-meta-daily | Browser, office, media, utilitas | all |
| arashios-arsenal | CLI installer T2 dan T3 | all |
| arashios-repo-keyring | Kunci GPG repo | all |

### 11.3 Standar Paket

1. debhelper 13.
2. lintian bersih.
3. `debian/copyright` lengkap.
4. `debian/changelog` mengikuti versi rilis.
5. Tidak ada file di luar FHS.
6. Tidak ada postinst yang mengakses jaringan.
7. Postinst harus idempoten.
8. Setiap paket memiliki test install dan remove.
9. Paket `all` untuk aset, arsitektur spesifik untuk binari.
10. Signature paket melalui repo, bukan per file.

---

## 12. Repository APT dan Manajemen Kunci

### 12.1 Arsitektur Repo

```
repo/
├── conf/
│   └── distributions/
├── pool/
│   └── main/
│       ├── a/
│       ├── b/
│       └── ...
└── public/
    ├── dists/
    │   └── stable/
    │       ├── InRelease
    │       ├── Release
    │       └── main/binary-amd64/Packages
    └── pool/
```

### 12.2 Alat

| Kebutuhan | Alat |
|---|---|
| Manajemen repo | aptly |
| Signing | GPG RSA 4096 |
| Keyring | arashios-repo-keyring |
| Snapshot | aptly snapshot |
| Verifikasi | gpgv dan apt-secure |

### 12.3 Kunci

1. Kunci utama RSA 4096, masa berlaku 3 tahun.
2. Subkey signing terpisah.
3. Kunci privat disimpan di perangkat offline atau YubiKey.
4. Kunci publik dipaketkan sebagai `arashios-repo-keyring`.
5. Fingerprint dipublikasikan di website dan README.
6. Rotasi kunci didokumentasikan di `docs/KEY-ROTATION.md`.
7. Kunci darurat disimpan di dua lokasi fisik terpisah.
8. Penghapusan kunci memerlukan dua maintainer.

### 12.4 Konfigurasi Klien

```
deb [signed-by=/usr/share/keyrings/arashios-archive-keyring.gpg] \
    https://repo.arashios.example stable main
```

Domain final ditetapkan pada Fase 0.5. Untuk build lokal, repo diakses melalui `file://`.

### 12.5 Pinning

| Repo | Priority |
|---|---|
| ArashiOS stable | 500 |
| Debian bookworm | 500 |
| Debian security | 500 |
| Debian backports | 100 |
| Vendor T1 | 100 |

Aturan: backports dan vendor tidak boleh menimpa paket stable tanpa izin eksplisit.

---

## 13. CI/CD

### 13.1 Pekerjaan

| Job | Trigger | Runner | Output |
|---|---|---|---|
| Lint | Push dan PR | GitHub hosted | shellcheck, markdownlint, bash -n |
| Validate | Push dan PR | GitHub hosted | validasi config dan paket |
| Package | Push dan PR | GitHub hosted | .deb arashios-* |
| ISO amd64 | Tag dan nightly | Self-hosted amd64 | 3 edisi |
| ISO arm64 | Tag | Self-hosted arm64 atau QEMU | XFCE, LXQt |
| ISO i386 | Tag | Self-hosted amd64 | LXQt, XFCE |
| Boot test | Setelah build | QEMU KVM | Log dan screenshot |
| Smoke test | Setelah boot | QEMU atau hardware | Hasil JSON |
| Sign | Tag v* | Self-hosted | Signature dan checksum |
| Release | Tag v* | Self-hosted | Artefak publik |

### 13.2 Aturan CI

1. Build gagal jika ISO melebihi budget.
2. Build gagal jika smoke test kurang dari 100 persen.
3. Build gagal jika ada paket tanpa manifest lisensi.
4. Build gagal jika signature tidak valid.
5. Build gagal jika ada em dash di dokumen.
6. Artefak nightly disimpan 90 hari.
7. Artefak rilis disimpan permanen.
8. Log build disimpan bersama artefak.

### 13.3 Cache

1. Cache apt-cacher-ng per arsitektur.
2. Cache ccache untuk build paket.
3. Cache Go module dan Cargo registry untuk build T1.
4. Cache tidak boleh dipakai lintas rilis major.

---

## 14. Strategi Multi-Arsitektur

| Arsitektur | Build host | Metode | Tier |
|---|---|---|---|
| amd64 | x86_64 | Native | 1 |
| arm64 | arm64 atau x86_64 | Native runner atau qemu-user-static | 1 untuk XFCE |
| i386 | x86_64 | debootstrap i386, eksekusi native | 3 |

### 14.1 amd64

1. Target utama.
2. Seluruh edisi didukung.
3. Seluruh tool T0 dan T1 didukung.
4. Build dan test berjalan native.

### 14.2 arm64

1. XFCE dan LXQt.
2. Cinnamon tidak dirilis untuk arm64 pada v1.
3. Build memakai runner arm64 atau QEMU dengan binfmt.
4. Waktu build QEMU 2 sampai 4 kali lebih lambat.
5. Tool Go dibangun dengan `GOARCH=arm64`.
6. Tool yang tidak mendukung arm64 dipindahkan ke T3.

### 14.3 i386

1. LXQt default, XFCE alternatif.
2. Cinnamon tidak didukung.
3. Coverage tool T0 minimal 85 persen.
4. Tool Go dan Rust modern mungkin tidak tersedia.
5. Jika coverage di bawah 85 persen, status menjadi build komunitas.
6. Kernel memakai flavour `686-pae`.

---

## 15. Installer, Partisi, Persistence, dan Recovery

### 15.1 Calamares

Modul yang dipakai:

| Urutan | Modul | Fungsi |
|---|---|---|
| 1 | welcome | Sambutan dan pemilihan bahasa |
| 2 | locale | Locale dan timezone |
| 3 | keyboard | Layout keyboard |
| 4 | partition | Skema partisi |
| 5 | users | User, hostname, password |
| 6 | summary | Ringkasan |
| 7 | install | Eksekusi |
| 8 | finished | Restart |

Modul yang tidak dipakai pada v1: netinstall, packagechooser, tracking.

### 15.2 Skema Partisi

| Skema | Deskripsi | Swap | Catatan |
|---|---|---|---|
| Erase disk | GPT, ESP 512 MB, root ext4 | zram | Default |
| Alongside | Memakai ruang kosong | zram | Untuk dual boot |
| Manual | Pengguna menentukan | Sesuai pilihan | Untuk advanced |
| LUKS | Root terenkripsi | zram | Tanpa LVM |
| LUKS + LVM | Root terenkripsi di LV | zram | Untuk fleksibilitas |

Aturan:

1. ESP minimal 512 MB, disarankan 1 GB.
2. Root minimal 32 GB.
3. Tanpa partisi swap default, memakai zram.
4. Swapfile 4 GB disediakan untuk hibernasi opsional.
5. Partisi Windows tidak disentuh tanpa konfirmasi.
6. BitLocker harus disuspend sebelum instalasi.

### 15.3 Bootloader

1. UEFI memakai GRUB EFI di ESP.
2. BIOS memakai GRUB di MBR.
3. `os-prober` aktif untuk mendeteksi Windows dan distro lain.
4. Entri boot lama tidak dihapus.
5. Urutan boot dapat diubah dengan `efibootmgr`.
6. Recovery GRUB didokumentasikan.

### 15.4 Persistence

1. Partisi berlabel `persistence`.
2. File `persistence.conf` berisi `/ home`.
3. Persistence terenkripsi opsional.
4. Data live user disimpan di `/home/arashi`.
5. Tidak ada persistence default pada ISO.

### 15.5 Recovery

| Alat | Fungsi |
|---|---|
| arashios-chroot | Masuk ke sistem terpasang dari live |
| grub-repair | Pasang ulang GRUB |
| timeshift | Snapshot sebelum upgrade |
| testdisk | Recovery partisi |
| photorec | Recovery file |

---

## 16. Mekanisme Update

1. `apt update` mengambil Debian security dan repo ArashiOS.
2. `unattended-upgrades` hanya untuk security.
3. Update major memerlukan konfirmasi pengguna.
4. Snapshot Timeshift dibuat sebelum upgrade.
5. Kernel lama dipertahankan.
6. Rollback dilakukan dengan memilih kernel lama atau snapshot.
7. Kanal edge dan nightly memakai repo terpisah.
8. Paket yang dihapus dari repo diumumkan di release notes.
9. Pinning mencegah backports menimpa stable.
10. Repo ArashiOS ditandatangani dan diverifikasi setiap update.

---

# BAGIAN IV - TOOLSTACK

## 17. Kebijakan Toolstack

| Tier | Sumber | Redistribusi | Target | Contoh |
|---|---|---|---|---|
| T0 | Repo Debian bookworm | Ya, sesuai lisensi | 130 paket | nmap, sqlmap, hashcat |
| T1 | Vendor .deb atau build source | Ya, dengan copyright | 40 paket | metasploit, nuclei, netexec |
| T2 | Unduhan saat pengguna memilih | Tidak | 8 sampai 12 | Burp CE, Nessus, IDA Free |
| T3 | Container image | Tidak | Tidak dibatasi | kali-rolling, lab vulnerable |

Aturan:

1. Tool T0 diutamakan.
2. T1 hanya jika T0 tidak tersedia.
3. T2 untuk tool proprietary atau berukuran besar.
4. T3 untuk tool yang membutuhkan glibc lebih baru atau dependensi konflik.
5. Setiap tool memiliki manifest YAML.
6. Setiap tool memiliki smoke test.
7. Setiap tool memiliki kategori alur kerja.
8. Setiap tool memiliki status dukungan per arsitektur.

### 17.1 Skema Manifest

```yaml
name: nuclei
version: 3.3.5
category: web
workflow: WF-02
tier: T1
source: https://github.com/projectdiscovery/nuclei
license: MIT
arch:
  amd64: supported
  arm64: supported
  i386: unsupported
build:
  language: go
  go_version: "1.23"
  command: "go build -trimpath -ldflags '-s -w' ./cmd/nuclei"
artifact:
  sha256: "0000000000000000000000000000000000000000000000000000000000000000"
install:
  path: /usr/bin/nuclei
test:
  command: "nuclei -version"
  expect: "Nuclei Engine Version"
```

Aturan manifest:

1. Hash wajib diisi sebelum rilis.
2. Versi mengikuti tag upstream, bukan branch.
3. Lisensi diverifikasi dari file LICENSE upstream.
4. Status arch wajib diisi.
5. Test harus dapat dijalankan tanpa jaringan.

---

## 18. Katalog Alur Kerja Keamanan

### 18.1 Reconnaissance

| Tool | Tier | Catatan |
|---|---|---|
| nmap | T0 | Scan port dan service |
| masscan | T0 | Scan cepat |
| arp-scan | T0 | Discovery layer 2 |
| dnsrecon | T0 | Enumerasi DNS |
| dnsutils | T0 | dig, nslookup |
| whois | T0 | Registrasi domain |
| ldap-utils | T0 | Enumerasi LDAP |
| whatweb | T0 | Fingerprint web |
| wafw00f | T0 | Deteksi WAF |
| amass | T1 | Attack surface mapping |
| subfinder | T1 | Subdomain enumeration |
| httpx | T1 | HTTP probing |
| naabu | T1 | Port scanning Go |

### 18.2 Web Testing

| Tool | Tier | Catatan |
|---|---|---|
| sqlmap | T0 | SQL injection |
| nikto | T0 | Web server scanner |
| ffuf | T0 | Fuzzing |
| gobuster | T0 | Directory dan DNS |
| dirb | T0 | Directory brute force |
| dirsearch | T0 | Directory discovery |
| nuclei | T1 | Template scanner |
| feroxbuster | T1 | Content discovery |
| wpscan | T1 | WordPress |
| zaproxy | T1 atau T2 | OWASP ZAP |
| dalfox | T1 | XSS |
| commix | T1 | Command injection |

### 18.3 Exploitation

| Tool | Tier | Catatan |
|---|---|---|
| metasploit-framework | T1 | Framework eksploitasi |
| exploitdb, searchsploit | T1 | Database eksploit |
| msfvenom | T1 | Payload generator |
| sliver | T2 | C2, opt-in |
| havoc | T2 | C2, opt-in |

### 18.4 Password Attack

| Tool | Tier | Catatan |
|---|---|---|
| hydra | T0 | Online brute force |
| medusa | T0 | Parallel brute force |
| john | T0 | Offline cracking |
| hashcat | T0 | GPU cracking |
| crunch | T0 | Wordlist generator |
| cewl | T0 | Wordlist dari web |
| seclists-core | T1 | Wordlist subset |
| rockyou | T2 | Unduhan opt-in |

### 18.5 Active Directory

| Tool | Tier | Catatan |
|---|---|---|
| python3-impacket | T0 | Library dan contoh |
| ldap-utils | T0 | LDAP |
| netexec | T1 | SwisArmy successor |
| evil-winrm | T1 | WinRM shell |
| enum4linux-ng | T1 | Enumerasi SMB |
| kerbrute | T1 | Kerberos brute force |
| certipy | T1 | AD CS |
| ldapdomaindump | T1 | Dump LDAP |
| bloodhound-ce | T2 | Graph AD, ukuran besar |

### 18.6 Wireless

| Tool | Tier | Catatan |
|---|---|---|
| aircrack-ng | T0 | Suite wireless |
| hcxtools | T0 | Capture WPA |
| hcxdumptool | T0 | Capture PMKID |
| reaver | T0 | WPS |
| wifite | T0 | Otomasi wireless |
| kismet | T1 atau T3 | Passive wireless |

### 18.7 Network Interception

| Tool | Tier | Catatan |
|---|---|---|
| wireshark | T0 | GUI packet analysis |
| tshark | T0 | CLI packet analysis |
| tcpdump | T0 | Capture |
| bettercap | T0 | MITM framework |
| mitmproxy | T0 | HTTP interception |
| ettercap-text-only | T0 | MITM klasik |
| responder | T1 | LLMNR, NBT-NS, mDNS |
| socat | T0 | Relay |
| proxychains4 | T0 | Proxy chain |

### 18.8 Pivoting

| Tool | Tier | Catatan |
|---|---|---|
| chisel | T1 | TCP tunnel |
| ligolo-ng | T1 | TUN pivot |
| proxychains4 | T0 | Proxy chain |
| socat | T0 | Relay |
| ssh | T0 | Port forwarding |

### 18.9 Forensics

| Tool | Tier | Catatan |
|---|---|---|
| sleuthkit | T0 | Filesystem forensics |
| testdisk | T0 | Partisi recovery |
| foremost | T0 | File carving |
| binwalk | T0 | Firmware analysis |
| steghide | T0 | Steganography |
| libimage-exiftool-perl | T0 | Metadata |
| volatility3 | T1 | Memory forensics |
| autopsy | T2 | GUI forensics |

### 18.10 Reverse Engineering

| Tool | Tier | Catatan |
|---|---|---|
| gdb | T0 | Debugger |
| strace | T0 | Syscall trace |
| ltrace | T0 | Library trace |
| apktool | T0 | APK decompile |
| python3-pwntools | T0 | Exploit development |
| radare2 | T1 | RE framework |
| rizin | T1 | RE framework |
| cutter | T1 | GUI untuk rizin |
| ghidra | T1 atau T2 | Decompiler |
| jadx | T1 | Java decompiler |
| pwndbg | T1 | GDB plugin |
| frida-tools | T1 | Dynamic instrumentation |
| upx-ucl | T1 | Packer |

### 18.11 Cloud dan Container

| Tool | Tier | Catatan |
|---|---|---|
| kubernetes-client | T0 | kubectl |
| awscli | T0 | AWS |
| azure-cli | T0 | Azure |
| ansible | T0 | Automation |
| podman | T0 | Rootless container |
| buildah | T0 | Image build |
| skopeo | T0 | Image inspection |
| trivy | T1 | Vulnerability scan |
| helm | T1 | Kubernetes package |
| docker.io | T2 | Docker engine |

### 18.12 Reporting

| Tool | Tier | Catatan |
|---|---|---|
| libreoffice | T0 | Dokumen |
| pandoc | T0 | Konversi markdown |
| keepassxc | T0 | Kredensial |
| obsidian | T2 | Catatan |
| template laporan | T0 | Aset ArashiOS |

---

## 19. Strategi Vendor dan Kompatibilitas glibc

### 19.1 Klasifikasi Bahasa

| Bahasa | Tool | Strategi | Risiko |
|---|---|---|---|
| Ruby | metasploit, wpscan | .deb vendor atau gem ter-bundle | Dependensi Ruby |
| Python | responder, volatility3, frida-tools | pipx dengan versi terkunci | Dependensi native |
| Go | nuclei, netexec, chisel, ligolo-ng, feroxbuster | Build statis dengan Go 1.23 | Tidak ada glibc |
| Java | jadx, ghidra, zaproxy | JAR atau .deb vendor | Ukuran |
| C/C++ | kismet | .deb vendor dengan cek glibc | ABI |

### 19.2 Cek glibc

```bash
objdump -T /path/to/binary \
  | grep -o 'GLIBC_[0-9.]*' \
  | sort -Vu \
  | tail -n 1
```

Aturan:

1. glibc bookworm adalah 2.36.
2. Simbol di atas GLIBC_2.36 ditolak.
3. Tool yang ditolak dipindahkan ke T3.
4. Binari Go statis tidak memerlukan cek glibc.
5. Cek dijalankan otomatis di CI untuk setiap T1.

### 19.3 Build Go

1. Go 1.23 dari bookworm-backports atau tarball resmi.
2. `CGO_ENABLED=0` untuk binari statis.
3. `-trimpath` untuk path deterministik.
4. `-ldflags "-s -w"` untuk ukuran.
5. `GOARCH` sesuai arsitektur.
6. Versi modul dikunci di `go.sum`.
7. Build di container bersih.

### 19.4 Build Python

1. pipx untuk aplikasi CLI.
2. Virtualenv terisolasi di `/opt/arashios/venvs/`.
3. Versi dikunci di `requirements.lock`.
4. Tidak ada `pip install` global.
5. Cek kompatibilitas Python 3.11.
6. Dependensi native dibangun di build host.

### 19.5 Build Java

1. OpenJDK 17.
2. JAR disimpan di `/opt/arashios/java/`.
3. Launcher shell di `/usr/bin/`.
4. Ghidra dan ZAP berukuran besar, default T2.
5. Jadx tersedia sebagai T1.

---

## 20. Stack Coding

| Komponen | Versi bookworm | Strategi |
|---|---|---|
| Python | 3.11 | Sistem 3.11, uv untuk proyek, pipx untuk CLI |
| Go | 1.19 | Backports 1.23 atau tarball resmi |
| Rust | 1.63 | rustup stable |
| Node.js | 18 | fnm dengan Node 22 LTS |
| Java | 17 | OpenJDK 17 |
| C/C++ | GCC 12, Clang 14 | build-essential, cmake, ninja, meson |
| PHP | 8.2 | php-cli, composer via installer |
| Ruby | 3.1 | ruby-full, bundler |
| Lua | 5.4 | lua5.4, luarocks opsional |
| Container | Podman rootless | Docker opsional T2 |
| Editor | Neovim, VSCodium | Neovim source build, VSCodium upstream |
| CLI | zsh, starship, tmux, rg, fd, fzf, bat, exa, zoxide, direnv, jq, yq, httpie, gh, git | Debian dan vendor |

Aturan:

1. Tidak ada `pip install` atau `npm install -g` ke sistem.
2. Gunakan venv, uv, pipx, fnm, atau rustup.
3. Semua toolchain user-level dapat dipasang tanpa sudo.
4. Shell startup maksimal 300 ms.
5. VSCodium default, VS Code proprietary via arsenal.
6. Podman rootless default.
7. Docker tidak dijalankan otomatis.
8. Setiap proyek memiliki `.tool-versions` atau `go.mod` atau `pyproject.toml`.
9. Template proyek disediakan di `/usr/share/arashios/templates/`.
10. Dokumentasi offline tersedia di `/usr/share/doc/arashios/`.

---

## 21. Stack Daily Driver

| Kategori | Paket | Catatan |
|---|---|---|
| Browser | firefox-esr, chromium | Firefox default |
| Email | thunderbird | OAuth didukung |
| Office | libreoffice, evince, file-roller, pandoc | Format umum |
| Media | vlc, gimp, inkscape | Editing dasar |
| Utilitas | flameshot, keepassxc, timeshift, gparted, gnome-disk-utility | Maintenance |
| Remote | remmina, filezilla | RDP, VNC, FTP |
| Transfer | qbittorrent | Torrent |
| Network | network-manager, network-manager-gnome | WiFi, VPN |
| Bluetooth | bluez, blueman | Perangkat |
| Audio | pipewire, wireplumber, pavucontrol | Cinnamon dan LXQt |
| Audio XFCE | pulseaudio, pavucontrol | Default Debian |
| Power | tlp, thermald, zram-tools, earlyoom | Laptop |
| Firmware | fwupd, non-free-firmware | Update firmware |
| Print | cups, system-config-printer, sane-utils | Print dan scan |
| Flatpak | flatpak | Tanpa remote default |
| Font | fonts-inter, fonts-jetbrains-mono, fonts-noto-cjk | UI dan CJK |

Aturan:

1. Flatpak tidak menambahkan Flathub otomatis.
2. Firefox tidak mengirim telemetry secara default.
3. Tanpa akun online bawaan.
4. Tanpa layanan cloud bawaan.
5. Print dan scan diuji di hardware nyata.
6. Suspend dan resume diuji 10 kali.

---

## 22. Wordlist dan Data

| Dataset | Ukuran | Lisensi | Distribusi |
|---|---|---|---|
| seclists-core | di bawah 80 MB terkompresi | MIT | ISO |
| seclists-full | sekitar 1.5 GB | MIT | Arsenal |
| rockyou | sekitar 133 MB | Tidak jelas | Arsenal dengan peringatan |
| arashios-wordlists | di bawah 10 MB | CC-BY-SA-4.0 | ISO |
| payloads | di bawah 5 MB | MIT | ISO |

Aturan:

1. Setiap wordlist memiliki checksum.
2. Setiap wordlist memiliki sumber.
3. Dataset tanpa lisensi jelas tidak masuk ISO.
4. rockyou hanya melalui arsenal.
5. Wordlist disimpan di `/usr/share/wordlists/`.
6. Update wordlist mengikuti rilis.

---

## 23. Strategi Container

| Image | Fungsi | Ukuran | Catatan |
|---|---|---|---|
| kali-rolling | Tool yang butuh glibc baru | Besar | Tarik saat dibutuhkan |
| blackarch | Tool spesifik Arch | Besar | Opsional |
| dvwa | Lab web | Sedang | Untuk latihan |
| juice-shop | Lab web | Sedang | Untuk latihan |
| vulnerable-ad | Lab AD | Besar | Untuk latihan |

Aturan:

1. Podman rootless default.
2. Image tidak dibundel di ISO.
3. Image tag immutable, bukan latest.
4. Setiap image memiliki checksum.
5. Container tidak diberi akses ke host network secara default.
6. Dokumentasi peringatan untuk tool C2.

---

## 24. Matriks Lisensi

| Komponen | Lisensi | Redistribusi | Catatan |
|---|---|---|---|
| Metasploit Framework | BSD-3-Clause | Boleh | Sertakan NOTICE |
| NetExec | BSD-2-Clause | Boleh, verifikasi | Cek LICENSE upstream |
| Nuclei, Subfinder, Httpx | MIT | Boleh | Sertakan copyright |
| Ghidra | Apache-2.0 | Boleh | Ukuran besar |
| Radare2 | LGPL-3.0 | Boleh | Source atau tawaran source |
| SecLists | MIT | Boleh | Subset |
| Burp Suite CE | Proprietary | Tidak | Installer |
| Cobalt Strike | Commercial | Tidak | Dokumentasi |
| Nessus | Proprietary | Tidak | Installer |
| Papirus | GPL-3.0 | Boleh | Lisensi |
| Materia atau Arc | GPL-3.0 | Boleh | Tema turunan GPL-3.0 |
| Inter, JetBrains Mono, Shippori Mincho | OFL-1.1 | Boleh | Lisensi |
| Kanagawa | MIT | Boleh | Atribusi |

Aturan:

1. Setiap paket memiliki file copyright.
2. Paket GPL menyertakan source atau tawaran source.
3. Tool proprietary tidak masuk ISO.
4. Lisensi diverifikasi pada Fase 9.
5. Perubahan lisensi upstream dipantau setiap rilis.

---

## 25. Kebijakan Update dan CVE

| Komponen | Sumber | SLA critical | SLA high |
|---|---|---|---|
| Debian security | Debian | 24 jam | 7 hari |
| Kernel | Debian | 7 hari | 14 hari |
| T1 vendor | Upstream | 7 hari | 30 hari |
| T2 | Upstream | Pengguna | Pengguna |
| T3 | Image upstream | 30 hari | 60 hari |

Aturan:

1. CVE critical yang belum dimitigasi memblokir rilis.
2. CVE high memerlukan mitigasi atau dokumentasi.
3. Setiap rilis mencatat CVE yang diketahui.
4. `debsecan` dijalankan di CI.
5. `trivy` dan `grype` dijalankan untuk image container.
6. Security advisory dipublikasikan untuk isu yang memengaruhi pengguna.
7. Patch vendor T1 diuji sebelum masuk repo.
8. Rollback kernel tersedia jika update bermasalah.

---

# BAGIAN V - EKSEKUSI

## 26. Roadmap Fase dan Sub-fase

### Fase 0: Fondasi Proyek

Tujuan: menyiapkan repo, keputusan arsitektur, lingkungan build, dan pemeriksaan legal sebelum menulis kode produksi.

Durasi: 1 minggu. Effort: 1 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 0.1 | Inisialisasi repo dan branch model | Repo git, README, LICENSE, .gitignore | 0.5 hari |
| 0.2 | ADR-001 sampai ADR-012 | docs/adr/*.md | 0.5 hari |
| 0.3 | Provision build host | Skrip check-env, paket host, apt-cacher-ng | 0.5 hari |
| 0.4 | CI skeleton | Lint, validasi config, build dry-run | 1 hari |
| 0.5 | Legal dan trademark | Pencarian nama, domain, lisensi, disclaimer | 0.5 hari |
| 0.6 | Design token v0 | branding/tokens.json dan generator | 1 hari |
| 0.7 | Requirements baseline | Lampiran H dan katalog kebutuhan | 0.5 hari |

Exit gate:

1. `make lint` lulus.
2. Semua ADR disetujui.
3. `scripts/check-env.sh` lulus.
4. Nama ArashiOS tidak bentrok di yurisdiksi target.
5. Token desain tervalidasi.
6. Requirements memiliki ID dan kriteria uji.

### Fase 1: ISO Basis

Tujuan: membuktikan pipeline live-build menghasilkan ISO hybrid yang boot di UEFI dan BIOS.

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 1.1 | Konfigurasi live-build | config/common dan config/editions/xfce | 1 hari |
| 1.2 | Bootstrap bookworm amd64 | Rootfs minimal, live-boot, live-config | 0.5 hari |
| 1.3 | Boot hybrid | ISO boot di QEMU UEFI dan BIOS | 1 hari |
| 1.4 | Harness QEMU | tests/qemu-boot.sh dan screenshot | 1 hari |
| 1.5 | Baseline paket | Sistem, firmware, NetworkManager | 1 hari |
| 1.6 | Cache dan snapshot | apt-cacher-ng, snapshot terkunci | 1 hari |
| 1.7 | Build script | build.sh, versions.env, artefak pertama | 1 hari |
| 1.8 | Dokumentasi build | README dan docs/BUILD.md | 0.5 hari |

Exit gate:

1. ISO boot ke desktop di UEFI dan BIOS.
2. Build dingin maksimal 60 menit, hangat maksimal 20 menit.
3. Nama artefak sesuai pola dan checksum tersedia.
4. Tidak ada dependency error di log.
5. Boot log tersedia melalui entri serial.

### Fase 2: Branding dan Boot Experience

Tujuan: menerapkan identitas Kage pada seluruh boot chain dan sistem.

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 2.1 | Finalisasi logo | SVG mark, wordmark, favicon | 1 hari |
| 2.2 | Wallpaper | 5 wallpaper 4K, sumber SVG | 2 hari |
| 2.3 | GRUB | Tema, menu, entri serial | 1 hari |
| 2.4 | Plymouth | Tema script, progress | 2 hari |
| 2.5 | LightDM | Greeter, autologin live | 1 hari |
| 2.6 | Identitas sistem | os-release, issue, lsb-release | 0.5 hari |
| 2.7 | Paket branding | arashios-branding .deb | 1 hari |
| 2.8 | QA boot | Screenshot, timing, kontras | 1 hari |
| 2.9 | Dokumentasi desain | docs/DESIGN.md | 0.5 hari |

Exit gate:

1. Boot chain konsisten dari GRUB sampai desktop.
2. Tidak ada logo Debian pada layar boot.
3. Atribusi Debian ada di About dan dokumentasi.
4. Waktu boot memenuhi budget.
5. Semua aset memiliki lisensi.
6. Kontras teks lulus AA.

### Fase 3: Desktop dan Tema

Tujuan: menghasilkan tiga edisi desktop dengan tema Kage yang konsisten dan terukur.

Durasi: 4 minggu. Effort: 5 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 3.1 | Desktop common | Font, ikon, kursor, audio, applet | 2 hari |
| 3.2 | GTK3 dan GTK4 | Tema ArashiKage, override libadwaita | 4 hari |
| 3.3 | Qt dan Kvantum | Tema ArashiKage untuk LXQt | 3 hari |
| 3.4 | Cinnamon | cinnamon.css, panel, menu, Nemo | 3 hari |
| 3.5 | XFCE | xfconf, Whisker, Thunar, terminal | 3 hari |
| 3.6 | LXQt | Openbox, Kvantum, panel, PCManFM-Qt | 3 hari |
| 3.7 | Skel dan dotfiles | zsh, starship, tmux, neovim, git | 2 hari |
| 3.8 | Default aplikasi | Terminal, browser, file manager, editor | 1 hari |
| 3.9 | Aksesibilitas | Fokus, kontras, keyboard, reduced motion | 2 hari |
| 3.10 | QA edisi | 3 DE x 2 firmware | 3 hari |
| 3.11 | Dokumentasi | docs/DESKTOP.md | 1 hari |

Exit gate:

1. Ketiga edisi boot tanpa error tema.
2. Budget RAM dan boot terpenuhi.
3. Aplikasi default konsisten dengan token.
4. Navigasi keyboard lulus.
5. Tidak ada fallback ke tema Debian.
6. Checklist VQ-01 sampai VQ-10 lulus.

### Fase 4: Toolstack Keamanan

Tujuan: mengisi 12 alur kerja keamanan dengan tool T0 dan T1 yang lulus uji.

Durasi: 4 minggu. Effort: 5 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 4.1 | Taksonomi dan manifest | vendor/manifests/*.yaml | 2 hari |
| 4.2 | Instalasi T0 | Paket Debian dan konfigurasi | 2 hari |
| 4.3 | Vendor T1 | .deb, Go, pipx, Java | 6 hari |
| 4.4 | Audit glibc | Laporan kompatibilitas | 1 hari |
| 4.5 | Wordlist | seclists-core, wordlist ArashiOS | 1 hari |
| 4.6 | Arsenal | list, info, install, remove, verify | 4 hari |
| 4.7 | Container T3 | Kali rootless, lab image | 2 hari |
| 4.8 | Smoke test | 40 test, hasil JSON | 3 hari |
| 4.9 | Audit lisensi | docs/LICENSES.md | 2 hari |
| 4.10 | Kebijakan update | Pin versi, jadwal review | 1 hari |

Exit gate:

1. Tool T0 dan T1 lulus smoke test.
2. Tidak ada dependency belum terpenuhi.
3. Copyright lengkap.
4. Ukuran ISO dalam budget.
5. Tidak ada repo Kali di sources.list.
6. Arsenal dapat memasang dan menghapus tanpa merusak sistem.
7. Semua 12 workflow memiliki minimal satu tool yang lulus.

### Fase 5: Lingkungan Coding

Tujuan: menyediakan toolchain modern yang tidak merusak stabilitas sistem.

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 5.1 | Toolchain bahasa | Python, Go, Rust, Node, Java, C/C++ | 2 hari |
| 5.2 | Editor | Neovim, VSCodium, konfigurasi | 2 hari |
| 5.3 | Container | Podman rootless, Docker opsional | 1 hari |
| 5.4 | CLI | zsh, starship, tmux, utilitas | 1 hari |
| 5.5 | Dotfiles | /etc/skel, first-run | 1 hari |
| 5.6 | Version manager | uv, fnm, rustup, pipx | 1 hari |
| 5.7 | Template proyek | Python, Go, Rust, Node | 1 hari |
| 5.8 | Dokumentasi offline | Man page, arashios-help | 1 hari |
| 5.9 | Smoke test | Hello world 6 bahasa | 1 hari |

Exit gate:

1. Enam bahasa kompilasi hello world.
2. Tidak ada instalasi global tanpa sudo.
3. Shell startup maksimal 300 ms.
4. Podman rootless berjalan.
5. VSCodium berjalan.
6. Template proyek dapat dipakai.

### Fase 6: Daily Driver dan Hardware

Tujuan: memastikan ArashiOS dapat dipakai sebagai sistem harian di hardware nyata.

Durasi: 3 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 6.1 | Aplikasi harian | Browser, office, media, utilitas | 2 hari |
| 6.2 | Jaringan | NetworkManager, WiFi, Bluetooth, VPN | 2 hari |
| 6.3 | Audio | PipeWire atau PulseAudio per edisi | 2 hari |
| 6.4 | Power | TLP, thermald, zram, earlyoom | 1 hari |
| 6.5 | Print dan scan | CUPS, sane | 1 hari |
| 6.6 | Locale | en_US, id_ID, ja_JP | 1 hari |
| 6.7 | Firmware | non-free-firmware, fwupd, backports | 1 hari |
| 6.8 | QA hardware | 3 mesin, suspend, WiFi, audio | 3 hari |
| 6.9 | Dokumentasi | docs/HARDWARE.md | 1 hari |

Exit gate:

1. Browsing, email, office, media, print lulus.
2. Suspend dan resume 10 dari 10.
3. WiFi, Bluetooth, audio berfungsi di tiga mesin.
4. Locale id_ID dan ja_JP benar.
5. Tidak ada regression dibanding Debian.

### Fase 7: Installer, Persistence, dan Recovery

Tujuan: menyediakan instalasi yang aman untuk disk kosong, dual boot, dan enkripsi.

Durasi: 5 minggu. Effort: 5 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 7.1 | Calamares dan branding | Installer bertema Kage | 3 hari |
| 7.2 | Profil partisi | Erase, alongside, manual | 3 hari |
| 7.3 | LUKS dan LVM | Enkripsi dan volume manager | 4 hari |
| 7.4 | Dual boot Windows | Shrink, ESP, os-prober, BitLocker | 4 hari |
| 7.5 | Persistence | Partisi persistence | 2 hari |
| 7.6 | Recovery | chroot, grub repair, timeshift | 3 hari |
| 7.7 | Secure Boot | Deteksi dan dokumentasi | 1 hari |
| 7.8 | QA instalasi | 10 skenario x 3 edisi | 5 hari |
| 7.9 | Dokumentasi | docs/INSTALL.md | 2 hari |

Exit gate:

1. 30 dari 30 instalasi lulus tanpa data loss.
2. Triple boot Windows, Debian, ArashiOS berhasil.
3. LUKS dan LVM dapat dibuka kembali.
4. GRUB mendeteksi sistem lain.
5. Peringatan BitLocker dan Fast Startup tersedia.
6. Persistence bertahan setelah reboot.

### Fase 8: Paket dan Repository

Tujuan: memindahkan seluruh kustomisasi ke paket dan repo yang ditandatangani.

Durasi: 3 minggu. Effort: 3 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 8.1 | Standar packaging | debhelper, lintian, copyright | 2 hari |
| 8.2 | Build paket | 16 paket .deb | 3 hari |
| 8.3 | Repo aptly | Repo lokal, InRelease, keyring | 3 hari |
| 8.4 | Integrasi ISO | ISO memakai repo lokal | 2 hari |
| 8.5 | Snapshot dan pinning | versions.env, manifest hash | 2 hari |
| 8.6 | Upgrade path | V1.10.21 ke V1.10.28 | 2 hari |
| 8.7 | Backports policy | Hanya kernel dan Go | 1 hari |
| 8.8 | Dokumentasi | docs/PACKAGING.md | 1 hari |

Exit gate:

1. Rebuild offline dari repo/pool berhasil.
2. `apt update` dan `apt upgrade` berhasil.
3. Semua paket lintian clean.
4. Kunci GPG terverifikasi.
5. Upgrade antar rilis tanpa reinstalasi.

### Fase 9: QA, Hardening, dan Kepatuhan

Tujuan: membuktikan kualitas dan keamanan artefak sebelum rilis.

Durasi: 4 minggu. Effort: 3 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 9.1 | Test plan | docs/QA-PLAN.md | 2 hari |
| 9.2 | Boot test otomatis | BIOS, UEFI, 3 edisi, 3 arch | 4 hari |
| 9.3 | Smoke suite | 40 test, hasil JSON | 3 hari |
| 9.4 | Hardening | sysctl, AppArmor, UFW, tanpa sshd | 2 hari |
| 9.5 | Vulnerability scan | debsecan, trivy, grype | 3 hari |
| 9.6 | SBOM | CycloneDX per ISO | 2 hari |
| 9.7 | Artifact signing | minisign atau cosign | 2 hari |
| 9.8 | Audit kepatuhan | Lisensi, export notice, privacy | 2 hari |
| 9.9 | Disclosure policy | SECURITY.md | 1 hari |
| 9.10 | Reproducibility | diffoscope dan laporan | 2 hari |

Exit gate:

1. Tidak ada CVE critical atau high terbuka.
2. SBOM tersedia.
3. Signature valid.
4. Hardening checklist 100 persen.
5. Disclosure policy dipublikasikan.
6. Reproducibility report tersedia.

### Fase 10: Rilis dan Distribusi

Tujuan: mempublikasikan rilis yang dapat diverifikasi dan didistribusikan.

Durasi: 2 minggu. Effort: 2 person-week.

| ID | Sub-fase | Output | Estimasi |
|---|---|---|---|
| 10.1 | Versi dan changelog | CHANGELOG.md, release notes | 1 hari |
| 10.2 | Build matrix | 7 artefak ISO | 2 hari |
| 10.3 | Mirror dan torrent | Mirror, torrent, zsync | 2 hari |
| 10.4 | Website dan docs | Install, dual boot, hardening, FAQ | 3 hari |
| 10.5 | Kanal rilis | stable, edge, nightly | 1 hari |
| 10.6 | Komunitas | Forum atau Matrix, Discussions | 1 hari |
| 10.7 | Monitoring | Hotfix window 7 hari | 1 hari |

Exit gate:

1. Artefak tier 1 tersedia.
2. Checksum dan signature valid.
3. Dokumentasi instalasi dan dual boot lengkap.
4. Kanal update berfungsi.
5. Tim siap hotfix 7 hari.

### Fase 11: Pasca v1

Durasi: berkelanjutan.

| ID | Sub-fase | Target |
|---|---|---|
| 11.1 | ARM SBC | Raspberry Pi 4 dan 5, Pine64 |
| 11.2 | Secure Boot | Shim, MOK, kernel bertanda tangan |
| 11.3 | Wayland | Hyprland atau Sway, eksperimental |
| 11.4 | Arsenal GUI | Control Center GTK4 |
| 11.5 | Cloud dan WSL | Image cloud, rootfs WSL |
| 11.6 | i386 | Evaluasi lanjut atau deprecation |
| 11.7 | Rebase Debian 13 | ArashiOS v2 di trixie |

---

## 27. Dependensi dan Jalur Kritis

```
P0 -> P1 -> P3 -> P4 -> P7 -> P9 -> P10
       \-> P2 ->/
        \-> P5 ->/
         \-> P6 ->/
              P8 ->/
```

| Fase | Depends on | Dapat paralel dengan |
|---|---|---|
| P0 | Tidak ada | Tidak ada |
| P1 | P0 | P2 |
| P2 | P1 | P1, P3 |
| P3 | P1, P2 | P4, P5 |
| P4 | P3 | P5, P6 |
| P5 | P1 | P4, P6 |
| P6 | P3 | P4, P5 |
| P7 | P3, P4 | P8 |
| P8 | P4, P7 | P9 |
| P9 | Semua fase | Tidak ada |
| P10 | P9 | Tidak ada |

Jalur kritis: P0, P1, P3, P4, P7, P9, P10. Keterlambatan pada P3 atau P7 menunda rilis.

---

## 28. Tim, Effort, dan Anggaran

### 28.1 Peran

| Peran | Tanggung jawab | FTE minimum |
|---|---|---|
| Maintainer dan build engineer | Repo, build, CI, rilis | 1.0 |
| Design dan desktop | Tema, aset, layout, aksesibilitas | 0.5 |
| Security dan QA | Toolstack, hardening, test matrix | 0.5 |
| Dokumentasi dan komunitas | Docs, website, dukungan | 0.25 |

Total minimum: 2.25 FTE.

### 28.2 Effort

| Fase | Person-week |
|---|---|
| P0 | 1 |
| P1 | 2 |
| P2 | 2 |
| P3 | 5 |
| P4 | 5 |
| P5 | 2 |
| P6 | 2 |
| P7 | 5 |
| P8 | 3 |
| P9 | 3 |
| P10 | 2 |
| Total | 32 |
| Buffer 15 persen | 5 |
| Total dengan buffer | 37 |

### 28.3 Kalender

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

### 28.4 Anggaran Perkiraan

| Item | Biaya tahun pertama | Catatan |
|---|---|---|
| Build server | USD 1,200 sampai 1,800 | 16 core, 32 GB RAM, NVMe |
| Laptop uji Intel | USD 700 sampai 1,000 | Hardware nyata |
| Perangkat ARM | USD 250 sampai 400 | Raspberry Pi 5 atau setara |
| USB dan media uji | USD 120 | 5 sampai 10 perangkat |
| YubiKey untuk signing | USD 120 | Dua unit |
| Domain dan DNS | USD 30 sampai 60 | Satu tahun |
| CI runner | USD 600 sampai 1,500 | Self-hosted atau cloud |
| Mirror dan bandwidth | USD 300 sampai 900 | Tergantung trafik |
| Total | USD 3,300 sampai 6,000 | Estimasi, bukan komitmen |

Biaya tenaga kerja tidak termasuk. Angka ini diperbarui pada Fase 0.5.

---

# BAGIAN VI - RISIKO, KUALITAS, DAN KEAMANAN

## 29. Risk Register

| ID | Risiko | Prob | Dampak | Mitigasi | Pemicu | Owner |
|---|---|---|---|---|---|---|
| R-01 | Konflik ABI paket Kali dengan bookworm | Sedang | Tinggi | Klasifikasi bahasa, binari statis, cek glibc, T3 | Build dependency gagal | Build |
| R-02 | Coverage tool i386 rendah | Tinggi | Tinggi | LXQt saja, dokumentasi, ambang 85 persen | Tool T0 gagal build | QA |
| R-03 | Build arm64 lambat | Tinggi | Sedang | Runner native, cache, nightly | Build lebih dari 4 jam | Build |
| R-04 | Scope creep desain | Sedang | Sedang | Token dikunci, tanpa DE baru | Permintaan di luar plan | Design |
| R-05 | Masalah lisensi tool | Sedang | Tinggi | Audit per paket, T2 opt-in | Paket tanpa copyright | Legal |
| R-06 | Kapasitas maintainer | Tinggi | Tinggi | Otomasi, scope per rilis, minimal 2 maintainer | Miss 2 sprint | Lead |
| R-07 | ISO membengkak | Sedang | Sedang | Budget ukuran, seclists-core, T2 | ISO di atas budget | Build |
| R-08 | Supply chain compromise | Rendah | Tinggi | Snapshot, signature, SBOM, checksum | Hash vendor berubah | Security |
| R-09 | Secure Boot tidak didukung | Tinggi | Rendah | Dokumentasi, roadmap MOK | Keluhan pengguna | Docs |
| R-10 | Hardware tidak kompatibel | Sedang | Sedang | non-free-firmware, backports, 3 mesin | WiFi atau GPU gagal | QA |
| R-11 | Konflik merek ArashiOS | Rendah | Tinggi | Pencarian merek dan domain | Nama terdaftar | Legal |
| R-12 | Debian 12 EOL 2028 | Pasti | Sedang | Rebase v2 ke Debian 13 | Mendekati Juni 2028 | Lead |
| R-13 | Regresi tema setelah update | Sedang | Sedang | Snapshot visual, test tema | Screenshot berbeda | Design |
| R-14 | Kehilangan kunci signing | Rendah | Tinggi | Dua YubiKey, backup offline, rotasi | Kunci tidak dapat diakses | Security |
| R-15 | Dokumentasi tertinggal | Sedang | Sedang | Docs as code, review PR | Fitur tanpa docs | Docs |

Aturan:

1. Risiko tinggi diperiksa setiap minggu.
2. Risiko dengan pemicu aktif menjadi blocker rilis.
3. Perubahan mitigasi dicatat di risk register.
4. Risiko baru dari audit keamanan masuk sebelum rilis.

---

## 30. Strategi Pengujian

### 30.1 Tingkat Pengujian

| Tingkat | Cakupan | Alat | Waktu |
|---|---|---|---|
| Static | shellcheck, lintian, markdownlint, bash -n | CI | Setiap push |
| Unit | Skrip build, parser manifest, generator tema | pytest atau bats | Setiap push |
| Integration | Build ISO, install paket, repo APT | CI dan QEMU | Setiap PR besar |
| Boot | UEFI, BIOS, tiga edisi | QEMU KVM | Setiap build |
| Install | 10 skenario x 3 edisi | QEMU dan hardware | Setiap rilis |
| Hardware | WiFi, audio, suspend, GPU | 3 mesin | Setiap rilis |
| Security | CVE scan, hardening, signature | debsecan, trivy, grype | Setiap rilis |
| Performance | RAM, boot, ukuran ISO | Skrip ukur | Setiap rilis |
| Accessibility | Keyboard, kontras, skala font | Manual dan skrip | Setiap rilis |
| Regression | Tool dan desktop | Smoke suite | Setiap rilis |

### 30.2 Prinsip

1. Setiap kebutuhan memiliki minimal satu test.
2. Test harus deterministik.
3. Test tidak bergantung pada jaringan kecuali test update.
4. Hasil test disimpan sebagai artefak.
5. Kegagalan test memblokir rilis.
6. Test yang flaky diperbaiki atau dihapus, tidak diabaikan.
7. Test hardware memerlukan bukti foto atau log.

### 30.3 Bukti Rilis

1. Log build.
2. Log boot UEFI dan BIOS.
3. Screenshot desktop tiga edisi.
4. Hasil smoke test JSON.
5. Laporan CVE.
6. SBOM.
7. Checksum dan signature.
8. Laporan diffoscope.
9. Checklist hardening.
10. Checklist aksesibilitas.

---

## 31. Katalog Test Case

### 31.1 Boot

| ID | Skenario | Ekspektasi | Fase |
|---|---|---|---|
| T-BOOT-01 | Boot UEFI amd64 Cinnamon | Desktop muncul, tidak ada error | 1, 3 |
| T-BOOT-02 | Boot BIOS amd64 Cinnamon | Desktop muncul, tidak ada error | 1, 3 |
| T-BOOT-03 | Boot UEFI amd64 XFCE | Desktop muncul, RAM di bawah budget | 3 |
| T-BOOT-04 | Boot BIOS amd64 LXQt | Desktop muncul, RAM di bawah budget | 3 |
| T-BOOT-05 | Boot arm64 XFCE QEMU | Desktop muncul | 1, 3 |
| T-BOOT-06 | Boot i386 LXQt QEMU | Desktop muncul atau kegagalan terdokumentasi | 1, 3 |
| T-BOOT-07 | Boot dengan `nomodeset` | Desktop fallback muncul | 3 |
| T-BOOT-08 | Boot serial console | Log kernel sampai login | 1 |

### 31.2 Instalasi

| ID | Skenario | Ekspektasi | Fase |
|---|---|---|---|
| T-INST-01 | Erase disk UEFI | Sistem boot setelah restart | 7 |
| T-INST-02 | Erase disk BIOS | Sistem boot setelah restart | 7 |
| T-INST-03 | Alongside Windows | Windows dan ArashiOS boot | 7 |
| T-INST-04 | Manual partisi | Sistem boot sesuai layout | 7 |
| T-INST-05 | LUKS | Prompt password dan boot | 7 |
| T-INST-06 | LUKS dan LVM | Volume terbuka dan boot | 7 |
| T-INST-07 | Instalasi tanpa jaringan | Installer selesai | 7 |
| T-INST-08 | Instalasi dengan firmware | WiFi berfungsi setelah boot | 7 |
| T-INST-09 | Persistence live | Data bertahan setelah reboot | 7 |
| T-INST-10 | Recovery GRUB | Sistem dapat boot kembali | 7 |

### 31.3 Tool

| ID | Skenario | Ekspektasi | Fase |
|---|---|---|---|
| T-TOOL-01 | nmap scan localhost | Port terbuka terdeteksi | 4 |
| T-TOOL-02 | sqlmap version | Versi tampil | 4 |
| T-TOOL-03 | msfconsole version | Versi tampil | 4 |
| T-TOOL-04 | netexec version | Versi tampil | 4 |
| T-TOOL-05 | nuclei version | Versi tampil | 4 |
| T-TOOL-06 | hashcat info | Perangkat terdeteksi | 4 |
| T-TOOL-07 | impacket import | Modul dapat diimpor | 4 |
| T-TOOL-08 | wireshark version | Versi tampil | 4 |
| T-TOOL-09 | arsenal install dry-run | Rencana instalasi tampil | 4 |
| T-TOOL-10 | arsenal verify | Checksum valid | 4 |

### 31.4 Desktop

| ID | Skenario | Ekspektasi | Fase |
|---|---|---|---|
| T-DESK-01 | Panel dan menu Cinnamon | Layout sesuai spesifikasi | 3 |
| T-DESK-02 | Panel dan menu XFCE | Layout sesuai spesifikasi | 3 |
| T-DESK-03 | Panel dan menu LXQt | Layout sesuai spesifikasi | 3 |
| T-DESK-04 | Ganti wallpaper | Wallpaper berubah tanpa restart | 3 |
| T-DESK-05 | Skala font 150 persen | Tidak ada clipping | 3 |
| T-DESK-06 | Reduced motion | Animasi berhenti | 3 |

### 31.5 Keamanan

| ID | Skenario | Ekspektasi | Fase |
|---|---|---|---|
| T-SEC-01 | sources.list | Hanya Debian dan ArashiOS | 4, 9 |
| T-SEC-02 | Signature ISO | Valid | 9 |
| T-SEC-03 | SBOM | Memuat paket dan versi | 9 |
| T-SEC-04 | UFW status | Aktif, deny incoming | 9 |
| T-SEC-05 | AppArmor status | Aktif | 9 |
| T-SEC-06 | SSH server | Tidak terpasang | 9 |
| T-SEC-07 | Autologin installed | Tidak aktif | 7 |
| T-SEC-08 | Network call saat boot | Tidak ada koneksi tak diminta | 9 |
| T-SEC-09 | CVE scan | Tidak ada critical atau high | 9 |
| T-SEC-10 | Reproducibility | Hash identik atau selisih terdokumentasi | 9 |

### 31.6 Performa dan Aksesibilitas

| ID | Skenario | Ekspektasi | Fase |
|---|---|---|---|
| T-PERF-01 | RAM idle Cinnamon | Maksimal 800 MB | 3 |
| T-PERF-02 | RAM idle XFCE | Maksimal 550 MB | 3 |
| T-PERF-03 | RAM idle LXQt | Maksimal 420 MB | 3 |
| T-PERF-04 | Boot QEMU | Dalam budget | 3 |
| T-ACC-01 | Navigasi keyboard installer | Selesai tanpa mouse | 7 |
| T-ACC-02 | Fokus terlihat | Outline pada semua kontrol | 3 |
| T-ACC-03 | Kontras teks | Lulus AA | 2 |
| T-ACC-04 | Orca | Screen reader berjalan | 6 |

---

## 32. Budget Performa

| Metrik | Cinnamon | XFCE | LXQt | Metode |
|---|---|---|---|---|
| RAM idle | 800 MB | 550 MB | 420 MB | `free -m` setelah 5 menit idle |
| Boot QEMU KVM | 35 s | 30 s | 25 s | Waktu sampai desktop |
| Boot SSD | 45 s | 40 s | 35 s | Waktu sampai desktop |
| Ukuran ISO | 4.2 GB | 3.9 GB | 3.5 GB | `du -h` |
| Install SSD | 15 min | 13 min | 12 min | Calamares sampai selesai |
| Shell startup | 300 ms | 300 ms | 300 ms | `time zsh -i -c exit` |
| Login greeter | 1 s | 1 s | 1 s | Waktu sampai prompt |
| Shutdown | 10 s | 10 s | 10 s | Waktu sampai power off |

Aturan:

1. Pengukuran dilakukan pada hardware dan QEMU yang sama.
2. Setiap rilis mencatat hasil di `docs/PERFORMANCE.md`.
3. Regresi lebih dari 10 persen memblokir rilis.
4. Ukuran ISO diukur setelah kompresi.
5. RAM diukur tanpa aplikasi tambahan.

---

## 33. Model Ancaman

### 33.1 Aset

1. ISO dan paket rilis.
2. Kunci signing.
3. Repo APT.
4. Build pipeline.
5. Data pengguna.
6. Kredensial pengguna.
7. Reputasi proyek.

### 33.2 STRIDE

| Kategori | Ancaman | Vektor | Mitigasi | Verifikasi |
|---|---|---|---|---|
| Spoofing | ISO palsu | Mirror atau situs tiruan | Signature, checksum, HTTPS, fingerprint | T-SEC-02 |
| Spoofing | Repo palsu | DNS atau mirror | signed-by, keyring, HSTS | T-SEC-01 |
| Tampering | Paket vendor dimodifikasi | Upstream compromise | Hash manifest, build container bersih | T-TOOL-10 |
| Tampering | Build pipeline disusupi | Dependency atau runner | Runner terisolasi, minimal secret | Audit CI |
| Repudiation | Rilis tanpa jejak | Proses manual | Build log, signature, provenance | Review rilis |
| Information disclosure | Telemetry tersembunyi | Aplikasi pihak ketiga | Tanpa telemetry, audit jaringan | T-SEC-08 |
| Information disclosure | Kredensial default | Live user | Tanpa password default, autologin live saja | T-SEC-07 |
| Denial of service | Mirror down | Infrastruktur | Mirror ganda, torrent, zsync | Uji unduh |
| Elevation | Live user sudo | Konfigurasi live | Sudo hanya live, installer membuat user | T-INST-01 |
| Elevation | Installer misconfig | Partisi atau permission | QA 30 skenario, review konfigurasi | T-INST-01..10 |
| Supply chain | Typosquatting package | Nama paket mirip | Manifest, review nama, checksum | Audit manifest |
| Supply chain | Container image berbahaya | Registry publik | Tag immutable, digest, scan | T-SEC-09 |

### 33.3 Ancaman di Luar Scope

1. Serangan fisik dengan akses root.
2. Firmware implant.
3. Serangan hardware side-channel.
4. Kompromi kunci signing di luar prosedur.
5. Malware yang sengaja dijalankan pengguna.

---

## 34. Hardening Default

### 34.1 Checklist

| ID | Kontrol | Nilai default |
|---|---|---|
| H-01 | Firewall | UFW aktif, deny incoming, allow outgoing |
| H-02 | AppArmor | Aktif |
| H-03 | SSH server | Tidak terpasang |
| H-04 | Root login | Tidak diizinkan |
| H-05 | Autologin | Hanya live session |
| H-06 | Password default | Tidak ada |
| H-07 | Update security | unattended-upgrades aktif |
| H-08 | sysctl kptr | 1 |
| H-09 | sysctl dmesg | 1 |
| H-10 | sysctl rp_filter | 1 |
| H-11 | Firejail | Tersedia, tidak aktif |
| H-12 | USBGuard | Tidak aktif untuk mencegah lockout |
| H-13 | Telemetry | Tidak ada |
| H-14 | Akun online | Tidak ada |
| H-15 | Flatpak remote | Tidak ada |

### 34.2 sysctl

```
kernel.kptr_restrict = 1
kernel.dmesg_restrict = 1
kernel.unprivileged_bpf_disabled = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_ra = 0
```

Catatan: beberapa nilai dapat mengganggu tool tertentu. Setiap perubahan diuji terhadap smoke suite.

### 34.3 Layanan

1. NetworkManager aktif.
2. LightDM aktif.
3. Bluetooth aktif tetapi tidak discoverable.
4. CUPS aktif hanya jika printer terdeteksi.
5. Avahi aktif tetapi tidak mengumumkan service sensitif.
6. Tanpa sshd.
7. Tanpa telnet.
8. Tanpa FTP server.
9. Tanpa Samba server.
10. Tanpa remote desktop server default.

---

## 35. Privasi

1. Tanpa telemetry, analytics, atau crash reporting otomatis.
2. Tanpa akun default.
3. Tanpa panggilan jaringan saat boot.
4. Firefox ESR memakai pengaturan privasi wajar.
5. DNS mengikuti NetworkManager, bukan penyedia pihak ketiga.
6. Flatpak tidak menambahkan Flathub otomatis.
7. Tidak ada iklan atau sponsor di ISO.
8. Tidak ada data pengguna yang dikirim ke proyek.
9. Audit jaringan dilakukan pada live session bersih.
10. Kebijakan privasi dipublikasikan di website.

---

## 36. Legal dan Kepatuhan

### 36.1 Lisensi

| Komponen | Lisensi |
|---|---|
| Kode ArashiOS | GPL-3.0-or-later |
| Aset visual | CC-BY-SA-4.0 |
| Dokumentasi | CC-BY-4.0 |
| Tema turunan GPL | GPL-3.0-or-later |
| Font | OFL-1.1 |

### 36.2 Kepatuhan

1. Setiap paket memiliki copyright.
2. Paket GPL menyertakan source atau tawaran source.
3. Tool proprietary tidak didistribusikan.
4. Logo Debian tidak dipakai sebagai identitas.
5. Atribusi "based on Debian" tersedia.
6. Pencarian merek ArashiOS dilakukan sebelum rilis.
7. Disclaimer dual-use disertakan.
8. Kepatuhan ekspor menjadi tanggung jawab pengguna dan distributor.
9. Kebijakan privasi tersedia.
10. Code of Conduct tersedia.

### 36.3 Disclaimer

ArashiOS menyertakan tool keamanan dual-use. Pengguna bertanggung jawab mematuhi hukum yang berlaku. Tool tidak boleh dipakai untuk mengakses sistem tanpa izin. Proyek tidak memberikan jaminan dan tidak bertanggung jawab atas penyalahgunaan.

---

## 37. Responsible Disclosure

1. Kanal privat ditetapkan pada Fase 0.5.
2. Respons awal maksimal 72 jam.
3. Perbaikan critical maksimal 7 hari.
4. Perbaikan high maksimal 30 hari.
5. Kredit peneliti jika diizinkan.
6. Safe harbor untuk riset yang etis.
7. Scope: ISO, paket, repo, website, build pipeline.
8. Laporan diterima dalam bahasa Indonesia atau Inggris.
9. Detail kerentanan tidak dipublikasikan sebelum perbaikan.
10. Kebijakan lengkap di `SECURITY.md`.

---

# BAGIAN VII - RILIS DAN OPERASI

## 38. Versi, Artefak, dan Checklist Rilis

### 38.1 Matriks Artefak

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

1. Pola: `ArashiOS-<arch>-<versi>[-<edisi>].iso`.
2. Edisi default per arch tanpa sufiks: amd64 Cinnamon, arm64 XFCE, i386 LXQt.
3. Edisi non-default memakai sufiks `-xfce` atau `-lxqt`.
4. Arch: `amd64`, `arm64`, `i386`.
5. Tanpa spasi, tanda kurung, atau karakter non-ASCII.
6. Setiap ISO disertai `.sha256`, `.sha512`, `.sig`, `.sbom.json`, dan `.torrent`.

### 38.2 Checklist Rilis

| ID | Item | Bukti |
|---|---|---|
| RC-01 | Semua artefak tier 1 dibangun | Log build |
| RC-02 | Boot UEFI lulus | Screenshot dan log |
| RC-03 | Boot BIOS lulus | Screenshot dan log |
| RC-04 | Installer 30 dari 30 | Log install |
| RC-05 | Smoke test 100 persen | Hasil JSON |
| RC-06 | Tidak ada CVE critical atau high | Laporan scan |
| RC-07 | SBOM tersedia | File CycloneDX |
| RC-08 | Signature valid | Verifikasi minisign |
| RC-09 | Checksum tersedia | SHA256 dan SHA512 |
| RC-10 | Ukuran ISO dalam budget | Laporan ukuran |
| RC-11 | RAM dan boot dalam budget | Laporan performa |
| RC-12 | Dokumentasi instalasi selesai | Link docs |
| RC-13 | Dokumentasi dual boot selesai | Link docs |
| RC-14 | Catatan rilis selesai | CHANGELOG |
| RC-15 | Lisensi lengkap | docs/LICENSES.md |
| RC-16 | Repo APT berfungsi | Uji apt update |
| RC-17 | Upgrade path teruji | Uji V1.10.21 ke V1.10.28 |
| RC-18 | Tidak ada telemetry | Audit jaringan |
| RC-19 | Hardening checklist 100 persen | docs/HARDENING.md |
| RC-20 | Hotfix window siap | Jadwal tim |

### 38.3 Kanan dan Dukungan

| Kanal | Frekuensi | Dukungan |
|---|---|---|
| stable | 4 minggu | 12 bulan |
| edge | 1 minggu | 6 bulan |
| nightly | Harian | Tidak ada |

### 38.4 End of Life

1. Pengumuman EOL 6 bulan sebelumnya.
2. Repo tetap tersedia 12 bulan setelah EOL.
3. Kunci signing tetap dipublikasikan.
4. Dokumentasi migrasi disediakan.
5. Debian 12 EOL Juni 2028 menjadi batas akhir v1.

---

## 39. Respons Insiden

### 39.1 Tingkat Keparahan

| Level | Definisi | Respons |
|---|---|---|
| S1 | Rilis tidak dapat boot atau data loss | 4 jam |
| S2 | Kerentanan critical atau repo compromise | 24 jam |
| S3 | Bug mayor pada tool atau desktop | 72 jam |
| S4 | Bug minor atau dokumentasi | 7 hari |

### 39.2 Prosedur

1. Terima laporan melalui kanal privat.
2. Tentukan severity.
3. Bentuk tim respons.
4. Mitigasi sementara.
5. Perbaiki dan uji.
6. Rilis hotfix.
7. Publikasikan advisory.
8. Postmortem tanpa menyalahkan individu.
9. Perbarui risk register.
10. Perbarui test jika perlu.

### 39.3 Komunikasi

1. Advisory di website dan GitHub Security.
2. Email ke pengguna yang berlangganan.
3. Update di kanal komunitas.
4. Tanpa detail exploit sebelum perbaikan tersedia.

---

## 40. Metrik dan SLO

| ID | Metrik | Target | Frekuensi |
|---|---|---|---|
| M-01 | Boot sukses tier 1 | 100 persen | Setiap build |
| M-02 | Installer sukses | 30 dari 30 | Setiap rilis |
| M-03 | Smoke test | 100 persen | Setiap rilis |
| M-04 | Ukuran ISO | Dalam budget | Setiap build |
| M-05 | RAM idle | Dalam budget | Setiap rilis |
| M-06 | Cold boot | Dalam budget | Setiap rilis |
| M-07 | CVE critical terbuka | 0 | Setiap rilis |
| M-08 | Artefak bertanda tangan | 100 persen | Setiap rilis |
| M-09 | Paket dengan manifest | 100 persen | Setiap rilis |
| M-10 | Build reproducible | Hash identik atau laporan | Setiap rilis |
| M-11 | Respons disclosure | 72 jam | Setiap laporan |
| M-12 | Downtime kanal update | 0 pada hari rilis | Setiap rilis |
| M-13 | Dokumentasi kebutuhan | 100 persen | Setiap rilis |
| M-14 | Test flaky | 0 | Setiap minggu |

---

# BAGIAN VIII - ORGANISASI

## 41. Tata Kelola

### 41.1 Peran

| Peran | Tanggung jawab |
|---|---|
| Lead maintainer | Arah produk, keputusan akhir, rilis |
| Build maintainer | Build, CI, repo, signing |
| Design maintainer | Tema, aset, aksesibilitas |
| Security maintainer | Toolstack, hardening, disclosure |
| QA maintainer | Test matrix, hardware, regression |
| Docs maintainer | Dokumentasi, website, komunitas |

### 41.2 Pengambilan Keputusan

1. Perubahan kecil: pull request dengan satu approval.
2. Perubahan besar: RFC dan diskusi publik.
3. Perubahan arsitektur: ADR baru.
4. Perubahan keamanan: review dua maintainer.
5. Perubahan lisensi: persetujuan lead dan legal review.
6. Perubahan rilis: checklist RC-01 sampai RC-20.

### 41.3 ADR

1. Satu ADR per keputusan arsitektur.
2. Format: konteks, keputusan, konsekuensi, alternatif.
3. Status: proposed, accepted, deprecated, superseded.
4. ADR tidak dihapus, hanya ditandai superseded.
5. ADR disimpan di `docs/adr/`.

### 41.4 Branch dan Commit

1. Trunk-based development.
2. Branch rilis: `release/v1.10.21`.
3. Commit convention: Conventional Commits.
4. Setiap commit harus dapat di-build.
5. DCO wajib pada setiap commit.
6. Tanpa CLA.
7. Force push hanya pada branch fitur.

### 41.5 Review

1. Minimal satu approval untuk perubahan biasa.
2. Dua approval untuk paket, build, dan keamanan.
3. Review desain menyertakan screenshot.
4. Review dokumen menyertakan pemeriksaan em dash.
5. Review keamanan menyertakan threat model.

---

## 42. Dokumentasi dan Komunitas

### 42.1 Dokumen Wajib

| Dokumen | Isi |
|---|---|
| README.md | Ringkasan, screenshot, build |
| INSTALL.md | Instalasi, dual boot, LUKS |
| HARDENING.md | Hardening setelah instalasi |
| CONTRIBUTING.md | Alur kontribusi |
| CODE_OF_CONDUCT.md | Contributor Covenant 2.1 |
| SECURITY.md | Disclosure policy |
| CHANGELOG.md | Riwayat rilis |
| docs/ARCHITECTURE.md | Arsitektur |
| docs/DESIGN.md | Design system |
| docs/QA-PLAN.md | Rencana uji |
| docs/LICENSES.md | Matriks lisensi |
| docs/KEY-ROTATION.md | Rotasi kunci |
| docs/THREAT-MODEL.md | Model ancaman |
| docs/RELEASE.md | Proses rilis |
| docs/SUPPORT.md | Siklus dukungan |

### 42.2 Website

1. Halaman unduh dengan checksum dan signature.
2. Dokumentasi instalasi dan dual boot.
3. Perbandingan edisi.
4. Changelog.
5. Halaman kontribusi.
6. Kebijakan privasi.
7. Tanpa analytics pihak ketiga.

### 42.3 Kanal

1. GitHub Discussions untuk pertanyaan dan bug.
2. Matrix atau forum untuk diskusi.
3. Kanal privat untuk security disclosure.
4. Tanpa kanal resmi yang meminta kredensial.
5. Moderasi mengikuti Code of Conduct.

### 42.4 Terjemahan

1. Bahasa utama: Indonesia dan Inggris.
2. Jepang sebagai bahasa tambahan untuk dokumentasi desain.
3. Dokumen rilis wajib tersedia dalam Inggris.
4. Terjemahan komunitas diverifikasi maintainer.

---

## 43. Definisi Selesai v1.0

v1.0 selesai jika seluruh poin berikut terpenuhi:

1. Tujuh artefak ISO pada matriks rilis berhasil dibangun.
2. Semua artefak tier 1 boot di UEFI dan BIOS.
3. Installer lulus 30 skenario tanpa data loss.
4. Triple boot Windows, Debian, ArashiOS teruji.
5. Ketiga edisi memenuhi budget RAM, boot, dan ukuran.
6. Tool T0 dan T1 lulus smoke test.
7. Toolchain enam bahasa lulus hello world.
8. Tugas harian lulus di tiga mesin.
9. Tidak ada CVE critical atau high terbuka.
10. SBOM, checksum, dan signature tersedia.
11. Dokumentasi instalasi, dual boot, dan hardening selesai.
12. Repo APT berfungsi dan upgrade teruji.
13. Kage konsisten dari boot sampai terminal.
14. Tidak ada telemetry atau panggilan otomatis.
15. Audit lisensi selesai.
16. Semua 12 workflow memiliki tool yang lulus.
17. Checklist aksesibilitas lulus.
18. Risk register diperbarui.
19. Hotfix window dan tim dukungan siap.
20. Pengumuman rilis disetujui lead maintainer.

---

# BAGIAN IX - LAMPIRAN

## Lampiran A: Struktur Repository Target

```
arashios/
├── plan.md
├── README.md
├── LICENSE
├── build.sh
├── Makefile
├── versions.env
├── .github/
│   └── workflows/
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
│   ├── tokens.json
│   ├── logo/
│   ├── wallpaper/
│   ├── grub/
│   ├── plymouth/
│   └── lightdm/
├── packages/
├── vendor/
├── repo/
├── scripts/
├── tests/
├── docs/
└── out/
```

## Lampiran B: Perintah Build dan Uji

```bash
./scripts/check-env.sh
make lint
./build.sh --edition cinnamon --arch amd64
./tests/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso uefi
./tests/qemu-boot.sh out/ArashiOS-amd64-V1.10.21.iso bios
./tests/verify-artifact.sh out/ArashiOS-amd64-V1.10.21.iso
```

## Lampiran C: Status Paket Terverifikasi

Verifikasi dilakukan pada 2026-10-21 terhadap indeks bookworm amd64, komponen main, contrib, non-free, dan non-free-firmware.

| Kelompok | Jumlah | Keterangan |
|---|---|---|
| Tersedia di Debian | 130 | Kandidat T0 |
| Tidak tersedia | 39 | Masuk T1, T2, atau T3 |
| Backports | linux-image-amd64, linux-headers-amd64, golang-1.22, golang-1.23 | Dipakai terbatas |
| Alias | libimage-exiftool-perl, python3-impacket, kubernetes-client, python3-pwntools, python3-scapy | Nama berbeda |

Paket tidak tersedia dan strateginya:

| Paket | Strategi |
|---|---|
| metasploit-framework | T1 .deb vendor |
| netexec | T1 Go build |
| evil-winrm | T1 Ruby gem |
| responder | T1 Python pipx |
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
| ghidra | T1 atau T2 |
| radare2 | T1 source build |
| rizin | T1 source build |
| cutter | T1 source build |
| upx-ucl | T1 source build |
| pwndbg | T1 git tag |
| volatility3 | T1 pipx |
| frida-tools | T1 pipx |
| trivy | T1 binari upstream |
| helm | T1 binari upstream |
| starship | T1 binari upstream |
| uv | T1 binari upstream |
| eza | T1 cargo build |
| fastfetch | T1 source build atau neofetch |
| code | T2 atau VSCodium |
| codium | T1 binari upstream |

## Lampiran D: Skema Manifest Tool

```yaml
name: tool-name
version: 1.2.3
category: web
workflow: WF-02
tier: T1
source: https://example.com/upstream
license: MIT
arch:
  amd64: supported
  arm64: supported
  i386: unsupported
build:
  language: go
  go_version: "1.23"
  command: "go build -trimpath -ldflags '-s -w' ./cmd/tool"
artifact:
  sha256: "64-hex-character"
install:
  path: /usr/bin/tool
test:
  command: "tool --version"
  expect: "1.2.3"
```

## Lampiran E: Matriks Penamaan ISO

| Arch | Edisi | Tier | Nama |
|---|---|---|---|
| amd64 | Cinnamon | 1 | ArashiOS-amd64-V1.10.21.iso |
| amd64 | XFCE | 1 | ArashiOS-amd64-V1.10.21-xfce.iso |
| amd64 | LXQt | 1 | ArashiOS-amd64-V1.10.21-lxqt.iso |
| arm64 | XFCE | 1 | ArashiOS-arm64-V1.10.21.iso |
| arm64 | LXQt | 2 | ArashiOS-arm64-V1.10.21-lxqt.iso |
| i386 | XFCE | 3 | ArashiOS-i386-V1.10.21-xfce.iso |
| i386 | LXQt | 3 | ArashiOS-i386-V1.10.21.iso |

## Lampiran F: Aturan Penulisan Dokumen

1. Dilarang memakai em dash dan en dash. Gunakan hyphen, koma, titik dua, atau susun ulang kalimat.
2. Dilarang memakai emoji di dokumen teknis.
3. Dilarang memakai tanda seru.
4. Setiap klaim performa disertai angka dan metode ukur.
5. Setiap persyaratan dapat diuji.
6. Gunakan kalimat aktif dan present tense.
7. Hindari kata pengisi: seamless, robust, powerful, cutting-edge, next-generation, revolution, unleash, elevate, empower, holistic, synergy, game-changer, effortless, world-class, best-in-class, state-of-the-art, delve, leverage, utilize.
8. Gunakan istilah teknis Inggris jika istilah Indonesia tidak baku.
9. Tabel dipakai untuk spesifikasi.
10. Setiap fase memiliki exit gate.

## Lampiran G: Glosarium

| Istilah | Definisi |
|---|---|
| T0 | Paket tersedia langsung di repo Debian |
| T1 | Paket vendor atau build dengan versi terkunci |
| T2 | Tool proprietary lewat installer opt-in |
| T3 | Tool yang dijalankan di container |
| Hybrid ISO | ISO yang boot pada BIOS dan UEFI |
| ESP | EFI System Partition |
| LUKS | Linux Unified Key Setup |
| LVM | Logical Volume Manager |
| SBOM | Software Bill of Materials |
| MOK | Machine Owner Key |
| Kage | Design system ArashiOS |
| Shizukesa | Nama rilis V1.10.21 |
| Exit gate | Kriteria minimum penyelesaian fase |
| WF | Workflow keamanan |
| RC | Release checklist |

## Lampiran H: Traceability Matrix

| Requirement | Fase | Test |
|---|---|---|
| FR-001 | 1, 3 | T-BOOT-01..04 |
| FR-002 | 3 | T-DESK-01..03 |
| FR-003 | 1 | T-BOOT-01 |
| FR-004 | 7 | T-INST-01..04 |
| FR-005 | 7 | T-INST-05..06 |
| FR-006 | 7 | T-INST-09 |
| FR-007 | 4 | T-TOOL-01..10 |
| FR-008 | 4 | T-TOOL-01..10 |
| FR-009 | 4 | T-TOOL-09..10 |
| FR-010 | 5 | Smoke test bahasa |
| FR-011 | 5 | Podman hello-world |
| FR-012 | 6 | Uji harian |
| FR-013 | 8 | Uji update |
| FR-014 | 7 | T-INST-10 |
| FR-015 | 1, 10 | Matriks artefak |
| SR-001 | 4, 9 | T-SEC-01 |
| SR-002 | 9 | T-SEC-02 |
| SR-003 | 10 | Verifikasi checksum |
| SR-004 | 9 | T-SEC-03 |
| SR-005 | 9 | T-SEC-08 |
| SR-006 | 7 | T-SEC-07 |
| SR-007 | 9 | T-SEC-04..05 |
| SR-008 | 9 | T-SEC-06 |
| SR-009 | 4 | T-TOOL-10 |
| SR-010 | 4 | Audit glibc |
| SR-011 | 9 | Audit build |
| SR-012 | 9 | T-SEC-09 |
| SR-013 | 9 | Review SECURITY.md |
| SR-014 | 9 | Audit lisensi |
| SR-015 | 9 | T-SEC-10 |
| PR-001..003 | 3 | T-PERF-01..03 |
| PR-004..006 | 3 | T-PERF-04 |
| PR-007..009 | 4 | Ukuran ISO |
| PR-010 | 5 | Shell startup |
| UX-001 | 2, 3 | Review visual |
| UX-002 | 2 | T-ACC-03 |
| UX-003 | 3 | T-ACC-02 |
| UX-004 | 3, 7 | T-ACC-01 |
| UX-005 | 3 | T-DESK-06 |
| UX-006 | 3 | T-DESK-05 |
| UX-007 | 3 | Review visual |
| UX-008 | 6 | Uji locale |
| UX-009 | 6 | T-ACC-04 |
| UX-010 | 7 | Review installer |
| CR-001..008 | 0, 2, 9 | Audit kepatuhan |

---

Dokumen ini menjadi acuan eksekusi Fase 0. Perubahan scope, arsitektur, atau jadwal wajib dicatat sebagai revisi dengan tanggal dan alasan.
