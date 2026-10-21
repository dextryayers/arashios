# Design System Kage

Kage adalah bahasa visual ArashiOS. Kage berarti bayangan. Arahnya adalah minimalisme Jepang dengan disiplin red team: ruang kosong yang lapang, satu aksen vermilion, geometri tajam, dan tipografi yang tenang. Tujuannya bukan dekorasi. Tujuannya adalah antarmuka yang cepat dibaca, tidak melelahkan, dan tidak menyembunyikan informasi penting.

Dokumen ini menjelaskan sumber token, aturan pemakaian, aset boot, dan batas implementasi pada Fase 1. Spesifikasi produk lengkap ada di [plan.md](../plan.md) bagian 6 dan 7.

## 1. Prinsip

1. **Ma, ruang kosong yang disengaja.** Jarak adalah bagian dari komposisi. Panel tidak dipenuhi kontrol. Menu tidak dipenuhi label.
2. **Satu benang merah.** Vermilion dipakai untuk aksi utama, fokus, dan penanda risiko. Jika semua elemen berwarna merah, tidak ada yang menonjol.
3. **Tenang, bukan lemah.** Permukaan gelap dan tipis, tanpa bayangan berlebihan. Kontras teks tetap tinggi.
4. **Bentuk mengikuti fungsi.** Sudut kecil, garis tipis, dan ikon sederhana. Tidak ada ornamen yang mengganggu alur kerja.
5. **Kejelasan lebih dulu.** Warna status tidak boleh menjadi satu-satunya pembeda. Teks, ikon, dan bentuk harus tetap jelas pada mode gelap.
6. **Konsisten lintas desktop.** Cinnamon, XFCE, dan LXQt memakai token yang sama, meskipun toolkit dan komponennya berbeda.

## 2. Nama dan Narasi

Nama Arashi berarti badai. Mark memakai ensō, lingkaran kuas yang tidak tertutup, sebagai simbol proses yang tidak pernah selesai dan kewaspadaan yang terus berjalan. Kanji 嵐 di tengah mark merujuk pada badai. Segel vermilion di kanan bawah adalah tanda tangan, bukan hiasan.

Wallpaper memakai frasa 静けさの中に、強さ。 yang berarti kekuatan di dalam ketenangan. Frasa ini menjadi arahan nada visual: tidak berteriak, tetapi siap.

Aturan narasi:

1. Bahasa visual tidak memakai ninja kartun, pedang, atau simbol klise.
2. Tidak ada maskot.
3. Tidak ada efek suara atau animasi berlebihan pada boot.
4. Tidak ada klaim keamanan yang tidak dapat dibuktikan.

## 3. Token

Sumber kebenaran token adalah [branding/tokens.json](../branding/tokens.json). Generator menghasilkan:

| Berkas | Kegunaan |
|---|---|
| `build/tokens/tokens.css` | Variabel CSS untuk web, dokumentasi, dan komponen GTK |
| `build/tokens/_tokens.scss` | Variabel SCSS |
| `build/tokens/kage.qss` | Stylesheet Qt untuk LXQt dan aplikasi Qt |
| `build/tokens/tokens.resolved.json` | Nilai token yang sudah diresolusi |
| `build/tokens/contrast.md` | Laporan kontras WCAG |
| `build/tokens/preview.html` | Preview palet dan komponen |

`build/tokens` adalah hasil generate. Jangan mengedit berkas di dalamnya. Ubah `branding/tokens.json`, lalu jalankan:

```bash
./scripts/generate-tokens.py
```

Validasi sinkronisasi:

```bash
./scripts/generate-tokens.py --check
```

## 4. Warna

### 4.1 Palet

| Kelompok | Token | Hex | Peran |
|---|---|---|---|
| Sumi | `sumi.900` | `#070709` | Latar paling gelap, teks di atas aksen terang |
| Sumi | `sumi.800` | `#0A0A0C` | Latar utama |
| Sumi | `sumi.700` | `#121216` | Permukaan panel |
| Sumi | `sumi.600` | `#1B1B21` | Permukaan terangkat |
| Sumi | `sumi.500` | `#25252D` | Border |
| Sumi | `sumi.400` | `#34343E` | Border kuat |
| Washi | `washi.50` | `#F7F4EE` | Teks pada latar sangat gelap |
| Washi | `washi.100` | `#EDE8DE` | Teks utama |
| Washi | `washi.200` | `#D8D2C6` | Teks sekunder terang |
| Ash | `ash.300` | `#B8B2A7` | Teks menu tidak aktif |
| Ash | `ash.400` | `#8B867D` | Teks muted |
| Ash | `ash.500` | `#6B675F` | Teks subtle, metadata |
| Ember | `ember.400` | `#E8917A` | Hover dan fokus |
| Ember | `ember.500` | `#DD785B` | Aksen utama dan link |
| Ember | `ember.600` | `#C46248` | Aksen ditekan |
| Vermilion | `vermilion.400` | `#D05545` | Danger dan peringatan kuat |
| Vermilion | `vermilion.500` | `#BF4432` | Segel, aksen kuat, garis |
| Vermilion | `vermilion.600` | `#9E3527` | Danger ditekan |
| Jade | `jade.400` | `#5FA88C` | Sukses |
| Jade | `jade.500` | `#3E8A72` | Sukses kuat |
| Gold | `gold.400` | `#D6B36A` | Peringatan |
| Gold | `gold.500` | `#B8934A` | Peringatan kuat |

### 4.2 Peran Semantik

| Peran | Token | Pemakaian |
|---|---|---|
| `bg` | `sumi.800` | Latar jendela dan desktop |
| `bgAlt` | `sumi.900` | Latar terminal dan area tenggelam |
| `surface` | `sumi.700` | Panel, sidebar, kartu |
| `surfaceRaised` | `sumi.600` | Dialog dan menu |
| `text` | `washi.100` | Teks utama |
| `textMuted` | `ash.400` | Label sekunder |
| `textSubtle` | `ash.500` | Metadata dan placeholder |
| `accent` | `ember.500` | Tombol utama, link, seleksi |
| `accentStrong` | `vermilion.500` | Penanda risiko dan segel |
| `success` | `jade.400` | Status berhasil |
| `warning` | `gold.400` | Status peringatan |
| `danger` | `vermilion.400` | Status gagal |
| `border` | `sumi.500` | Garis pemisah |
| `focus` | `ember.400` | Cincin fokus |

### 4.3 Kontras

Ambang mengikuti WCAG 2.1. Teks normal minimal 4.5:1. Teks besar dan komponen UI minimal 3:1. Pasangan teks utama memakai ambang 7:1.

| Pemakaian | Foreground | Background | Rasio | Status |
|---|---|---|---:|---|
| Teks utama | `washi.100` | `sumi.800` | 16.20:1 | Lulus |
| Teks utama pada panel | `washi.100` | `sumi.700` | 15.30:1 | Lulus |
| Teks muted | `ash.400` | `sumi.800` | 5.47:1 | Lulus |
| Teks muted pada panel | `ash.400` | `sumi.700` | 5.16:1 | Lulus |
| Link dan aksen | `ember.500` | `sumi.800` | 6.51:1 | Lulus |
| Aksen besar dan fill | `vermilion.500` | `sumi.800` | 3.85:1 | Lulus untuk teks besar |
| Label tombol utama | `sumi.900` | `ember.500` | 6.62:1 | Lulus |
| Sukses | `jade.400` | `sumi.800` | 7.03:1 | Lulus |
| Peringatan | `gold.400` | `sumi.800` | 9.90:1 | Lulus |
| Danger | `vermilion.400` | `sumi.800` | 4.77:1 | Lulus |

Aturan:

1. `vermilion.500` tidak dipakai untuk teks kecil di atas `sumi.800`. Rasio 3.85:1 hanya memenuhi ambang teks besar.
2. Teks di atas `ember.500` memakai `sumi.900`, bukan putih.
3. Status tidak boleh hanya dibedakan dengan warna. Sertakan ikon atau teks.
4. Jangan menambah warna baru di luar token tanpa ADR atau pembaruan token.

## 5. Tipografi

| Peran | Keluarga | Fallback |
|---|---|---|
| Sans | Inter | Noto Sans, DejaVu Sans, sans-serif |
| Display | Inter | Noto Sans JP, Noto Sans, sans-serif |
| Mono | JetBrains Mono | DejaVu Sans Mono, monospace |
| CJK | Noto Sans CJK JP | Noto Sans JP |

Skala:

| Token | Ukuran | Pemakaian |
|---|---:|---|
| `xs` | 0.75rem | Metadata, badge |
| `sm` | 0.875rem | Label, menu sekunder |
| `base` | 1rem | Teks tubuh |
| `lg` | 1.125rem | Subjudul |
| `xl` | 1.25rem | Judul panel |
| `2xl` | 1.5rem | Judul dialog |
| `3xl` | 2rem | Judul halaman |
| `4xl` | 3rem | Hero dan wallpaper |

Line height: 1.2 untuk judul, 1.5 untuk teks tubuh, 1.7 untuk dokumentasi panjang. Letter spacing: `-0.01em` untuk judul besar, `0` untuk teks tubuh, `0.08em` untuk label kapital.

Aturan:

1. Tidak memakai lebih dari tiga ukuran dalam satu panel.
2. Label kapital hanya untuk kategori pendek, bukan paragraf.
3. Teks terminal memakai mono dan tidak memakai letter spacing lebar.
4. Nama berkas dan perintah selalu memakai mono.

## 6. Spacing, Radius, Elevasi, dan Gerak

Spacing mengikuti skala 4 piksel:

| Token | Nilai | Pemakaian |
|---|---:|---|
| `1` | 4px | Jarak ikon dan label |
| `2` | 8px | Padding kontrol kecil |
| `3` | 12px | Padding kontrol |
| `4` | 16px | Jarak antar elemen |
| `5` | 20px | Padding panel |
| `6` | 24px | Jarak antarkelompok |
| `7` | 32px | Margin dialog |
| `8` | 40px | Jarak bagian |
| `9` | 48px | Ruang kosong besar |
| `10` | 64px | Hero |
| `11` | 96px | Wallpaper |
| `12` | 128px | Komposisi boot |

Radius:

| Token | Nilai | Pemakaian |
|---|---:|---|
| `none` | 0 | Pemisah dan garis |
| `sm` | 4px | Tombol kecil, badge |
| `md` | 8px | Tombol, input |
| `lg` | 12px | Kartu dan panel |
| `xl` | 16px | Dialog |
| `full` | 9999px | Avatar dan pill |

Elevasi:

| Token | Nilai | Pemakaian |
|---|---|---|
| `sm` | 0 1px 2px rgba(0,0,0,0.40) | Kontrol |
| `md` | 0 4px 12px rgba(0,0,0,0.35) | Menu |
| `lg` | 0 12px 32px rgba(0,0,0,0.45) | Dialog |
| `glow` | cincin ember 35 persen | Fokus |

Gerak:

| Token | Nilai | Pemakaian |
|---|---|---|
| `durationFast` | 120ms | Hover dan tekan |
| `durationBase` | 180ms | Buka menu |
| `durationSlow` | 280ms | Dialog |
| `easingStandard` | cubic-bezier(0.2, 0, 0, 1) | Semua transisi |

Gerak harus menghormati preferensi pengurangan animasi. Pada desktop, animasi tidak boleh menunda input.

## 7. Komponen

### 7.1 Tombol

| Varian | Latar | Teks | Border |
|---|---|---|---|
| Primer | `ember.500` | `sumi.900` | Tanpa border |
| Sekunder | `sumi.600` | `washi.100` | `sumi.500` |
| Danger | `vermilion.500` | `washi.50` | Tanpa border |
| Ghost | Transparan | `washi.100` | `sumi.500` |

Tinggi tombol: 32px untuk kontrol rapat, 36px untuk toolbar, 40px untuk dialog. Radius `md`. Padding horizontal 12px sampai 16px. Fokus memakai cincin 2px `ember.400` dengan offset 2px.

### 7.2 Input

Input memakai latar `sumi.900`, border `sumi.500`, teks `washi.100`, dan placeholder `ash.500`. Fokus memakai border `ember.400` dan glow tipis. Pesan error memakai `vermilion.400` dengan ikon, bukan hanya warna.

### 7.3 Menu dan Panel

Menu memakai `surfaceRaised`, border `sumi.500`, radius `md`, dan shadow `md`. Item terpilih memakai `ember.500` dengan teks `sumi.900`. Panel desktop memakai `sumi.800` dengan opacity tinggi, border bawah `sumi.500`, dan tinggi 32px sampai 40px.

### 7.4 Terminal

Terminal memakai latar `sumi.900`, teks `washi.100`, kursor `ember.500`, dan selection `vermilion.500` dengan teks `washi.50`. Font JetBrains Mono 11pt sampai 12pt. Transparansi tidak aktif secara default agar teks tetap terbaca.

### 7.5 Notifikasi

Notifikasi memakai `surfaceRaised`, border kiri 3px sesuai status, judul `washi.100`, isi `ash.300`, dan aksi `ember.500`. Durasi default 6 detik. Notifikasi kritis tidak hilang otomatis.

## 8. Logo dan Wallpaper

### 8.1 Mark

Mark adalah ensō terbuka dengan kanji 嵐 dan segel vermilion. Mark tersedia di:

- `branding/logo/arashios-mark.svg`
- `branding/logo/arashios-wordmark.svg`

Aturan:

1. Mark tidak diputar, tidak diberi bayangan tambahan, dan tidak diubah warnanya di luar varian yang disediakan.
2. Ukuran minimum mark digital adalah 24px. Di bawah ukuran itu, gunakan hanya segel atau ikon monokrom.
3. Ruang kosong di sekitar mark minimal 25 persen dari lebar mark.
4. Mark tidak diletakkan di atas latar ramai tanpa bidang pemisah.
5. Wordmark dipakai untuk dokumen dan wallpaper. Mark dipakai untuk ikon dan boot.

### 8.2 Wallpaper

Wallpaper utama adalah `branding/wallpaper/kage-sumi.svg` dengan kanvas 3840x2160. Komposisi:

1. Latar gradien sumi dari `#070709` ke `#121216`.
2. Grid tipis 80px dengan opacity 3.5 persen.
3. Glow vermilion di kanan atas.
4. Ensō besar di kanan.
5. Garis potong vertikal di kiri.
6. Wordmark dan frasa Jepang di kiri bawah.

Wallpaper tidak memakai teks yang menutupi ikon desktop. Area kiri bawah sengaja gelap agar label ikon tetap terbaca. Wallpaper tambahan direncanakan pada Fase 2.

## 9. Boot Experience

### 9.1 GRUB

Tema GRUB berada di `branding/grub/theme.txt` dan dipasang ke `/usr/share/grub/themes/arashios/`. Latar `background.png` dihasilkan oleh `scripts/generate-brand-assets.py` dari komposisi SVG. Menu ditempatkan di 58 persen kiri, dengan label `ARASHIOS / KAGE` dan `SECURITY FIRST`.

Aturan:

1. Menu tidak menutupi mark.
2. Item terpilih memakai `select_*.png` nine-slice dengan teks `sumi.900`.
3. Tidak ada logo Debian pada layar boot.
4. Entri serial disediakan untuk debugging.
5. Timeout default 5 detik, dapat diubah pada Fase 7.

### 9.2 Plymouth

Tema Plymouth berada di `branding/plymouth/`. Komposisi berupa latar gelap, logo, teks `ARASHIOS`, dan subjudul `KAGE` berwarna ember. Tidak ada progress bar dinamis pada Fase 1. Animasi halus direncanakan pada Fase 2 setelah kompatibilitas Plymouth diverifikasi pada boot nyata.

### 9.3 LightDM

Greeter memakai `lightdm-gtk-greeter` dengan latar `sumi.800`, teks `washi.100`, dan aksen `ember.500`. Autologin hanya aktif untuk sesi live. Fase 7 harus menghapus autologin pada sistem terpasang.

## 10. Pemetaan Desktop

| Elemen | Cinnamon | XFCE | LXQt |
|---|---|---|---|
| Panel | Bawah, 40px | Atas, 32px | Bawah, 32px |
| Menu | Menu aplikasi | Whisker Menu | Menu aplikasi LXQt |
| File manager | Nemo | Thunar | PCManFM-Qt |
| Terminal | GNOME Terminal | XFCE Terminal | QTerminal |
| Editor | Gedit | Mousepad | Featherpad |
| Tema GTK | Adwaita gelap, token Kage | Adwaita gelap, token Kage | Qt Kage QSS |
| Ikon | Papirus | Papirus | Papirus |

Pada Fase 1, desktop memakai basis Adwaita dan Papirus. Tema GTK dan Qt penuh, kursor, dan layout panel final dikerjakan pada Fase 2 dan Fase 3. Token dan QSS sudah tersedia, tetapi belum diterapkan ke seluruh toolkit.

## 11. Terminal dan Editor

Shell default adalah Zsh. Script live-config `9990-arashios-shell` menetapkan Zsh sebagai shell user live setelah user dibuat. Prompt memakai prompt bawaan Zsh dan warna palet Kage. Konfigurasi Starship sudah disiapkan di `.config/starship.toml`; integrasi akan aktif setelah biner Starship di-vendor pada Fase 4 atau Fase 5. `.zshrc` memuat Starship hanya jika perintah tersedia. Konfigurasi ada di:

- `config/common/includes.chroot/etc/skel/.zshrc`
- `config/common/includes.chroot/etc/skel/.config/starship.toml`
- `config/common/includes.chroot/etc/skel/.tmux.conf`
- `config/common/includes.chroot/etc/skel/.config/nvim/init.lua`

Neovim memakai konfigurasi Lua tanpa plugin berat pada Fase 1. VSCodium ditambahkan pada Fase 5. Editor harus tetap dapat dijalankan tanpa koneksi jaringan.

## 12. Aksesibilitas

1. Kontras teks memenuhi WCAG AA. Pasangan utama memenuhi AAA.
2. Fokus selalu terlihat dan tidak hanya bergantung pada warna.
3. Status memakai ikon atau teks.
4. Animasi dapat dimatikan.
5. Ukuran teks dapat diperbesar tanpa memotong label.
6. Terminal tidak memakai transparansi default.
7. Wallpaper tidak mengganggu keterbacaan label ikon.
8. LightDM menyediakan pilihan sesi dan keyboard.

Pengujian aksesibilitas penuh, termasuk screen reader dan scaling, dilakukan pada Fase 10.

## 13. Pipeline Aset

```bash
# Token dan stylesheet
./scripts/generate-tokens.py

# Latar GRUB, nine-slice, dan logo Plymouth
./scripts/generate-brand-assets.py

# Verifikasi tanpa menulis ulang
./scripts/generate-tokens.py --check
./scripts/generate-brand-assets.py --check
```

Aset raster dihasilkan dari kode agar tidak bergantung pada renderer SVG di host. Jika aset berubah, jalankan generator dan commit hasilnya bersama sumbernya.

## 14. Lisensi

| Aset | Lisensi |
|---|---|
| Mark, wordmark, wallpaper, tema GRUB, tema Plymouth | CC-BY-SA-4.0 |
| Token dan stylesheet | CC-BY-SA-4.0 |
| Kode generator | GPL-3.0-or-later |
| Dokumentasi | CC-BY-4.0 |
| Font | Lisensi masing-masing, umumnya OFL |

Atribusi dan batasan merek dijelaskan di [docs/LEGAL.md](LEGAL.md) dan [docs/TRADEMARK.md](TRADEMARK.md).

## 15. Checklist QA Visual

1. Mark tidak terpotong pada ukuran 24px, 48px, dan 256px.
2. Wordmark terbaca pada latar terang dan gelap.
3. Tidak ada teks yang jatuh di bawah rasio kontras minimum.
4. Fokus terlihat pada tombol, input, menu, dan panel.
5. Status sukses, peringatan, dan danger dapat dibedakan tanpa warna.
6. Wallpaper tidak menutupi label ikon desktop.
7. GRUB menampilkan menu dan mark tanpa tumpang tindih.
8. Plymouth menampilkan logo tanpa pecah pada resolusi 1024x768 dan 1920x1080.
9. LightDM menampilkan sesi yang benar untuk edisi yang dipasang.
10. Terminal dan editor memakai font yang tersedia di image.
11. Tidak ada aset Debian yang tersisa pada layar boot.
12. Semua aset baru memiliki lisensi dan sumber.

## 16. Batas Fase 1

1. Tema GTK penuh belum ada.
2. Tema Qt penuh belum diterapkan ke seluruh aplikasi.
3. Kursor Kage belum ada.
4. Ikon khusus ArashiOS baru mark aplikasi.
5. Wallpaper baru satu.
6. Animasi Plymouth belum diverifikasi pada boot nyata.
7. Layout panel final belum dikunci.
8. QA visual pada perangkat keras nyata belum dilakukan.
