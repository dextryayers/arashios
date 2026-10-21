# Design System Kage

Kage adalah bahasa visual ArashiOS. Kage berarti bayangan. Arahnya adalah
minimalisme Jepang dengan disiplin red team: ruang kosong yang lapang, satu
aksen vermilion, geometri tajam, dan tipografi yang tenang. Tujuannya bukan
dekorasi. Tujuannya adalah antarmuka yang cepat dibaca, tidak melelahkan, dan
tidak menyembunyikan informasi penting.

Dokumen ini menjelaskan implementasi Fase 2 dan Fase 3 pada tingkat statis.
Spesifikasi produk lengkap ada di [plan.md](../plan.md) bagian 6 dan 7. Hasil
pengujian dan batas yang belum diverifikasi dicatat pada
[PHASE-2-3-REPORT.md](PHASE-2-3-REPORT.md).

## 1. Prinsip

1. **Ma, ruang kosong yang disengaja.** Jarak adalah bagian dari komposisi.
   Panel tidak dipenuhi kontrol. Menu tidak dipenuhi label.
2. **Satu benang merah.** Vermilion dipakai untuk aksi utama, fokus, dan
   penanda risiko. Jika semua elemen berwarna merah, tidak ada yang menonjol.
3. **Tenang, bukan lemah.** Permukaan gelap dan tipis, tanpa bayangan
   berlebihan. Kontras teks tetap tinggi.
4. **Bentuk mengikuti fungsi.** Sudut kecil, garis tipis, dan ikon sederhana.
   Tidak ada ornamen yang mengganggu alur kerja.
5. **Kejelasan lebih dulu.** Warna status tidak boleh menjadi satu-satunya
   pembeda. Teks, ikon, dan bentuk harus tetap jelas pada mode gelap.
6. **Konsisten lintas desktop.** Cinnamon, XFCE, dan LXQt memakai token yang
   sama, meskipun toolkit dan komponennya berbeda.

## 2. Nama dan Narasi

Nama Arashi berarti badai. Mark memakai enso, lingkaran kuas yang tidak
tertutup, sebagai simbol proses yang tidak pernah selesai dan kewaspadaan yang
terus berjalan. Kanji 嵐 di tengah mark merujuk pada badai. Segel vermilion di
kanan bawah adalah tanda tangan, bukan hiasan.

Wallpaper memakai frasa 静けさの中に、強さ。 yang berarti kekuatan di dalam
ketenangan. Frasa ini menjadi arahan nada visual: tidak berteriak, tetapi
siap.

Aturan narasi:

1. Bahasa visual tidak memakai ninja kartun, pedang, atau simbol klise.
2. Tidak ada maskot.
3. Tidak ada efek suara atau animasi berlebihan pada boot.
4. Tidak ada klaim keamanan yang tidak dapat dibuktikan.

## 3. Token dan Pipeline

Sumber kebenaran token adalah [branding/tokens.json](../branding/tokens.json).
Versi token saat ini adalah `0.2.0`. File turunan tidak boleh diedit manual.

| Keluaran | Kegunaan |
|---|---|
| `build/tokens/tokens.css` | Variabel CSS untuk web, dokumentasi, dan komponen GTK |
| `build/tokens/_tokens.scss` | Variabel SCSS |
| `build/tokens/kage.qss` | Stylesheet Qt untuk LXQt dan aplikasi Qt |
| `build/tokens/tokens.resolved.json` | Nilai token yang sudah diresolusi |
| `build/tokens/contrast.md` | Laporan kontras WCAG |
| `build/tokens/preview.html` | Preview palet dan komponen |
| `build/theme/themes/ArashiKage` | Tema normal untuk GTK, Cinnamon, XFCE, Openbox, dan Kvantum |
| `build/theme/themes/ArashiKage-HC` | Tema kontras tinggi |
| `build/theme/Kvantum` | Konfigurasi dan SVG Kvantum kedua varian |
| `build/theme/manifest.json` | SHA-256 dari 164 file tema yang dihasilkan |

Perintah:

```bash
./scripts/generate-tokens.py
./scripts/generate-brand-assets.py
./scripts/generate-theme.py
./scripts/generate-theme.py --check
```

`generate-theme.py --check` menolak keluaran yang hilang, kedaluwarsa, atau
memiliki hash manifest yang salah. Pipeline tema memakai template di
`branding/theme/templates/` dan tidak memanggil renderer SVG eksternal.

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

Ambang mengikuti WCAG 2.1. Teks normal minimal 4.5:1. Teks besar dan komponen
UI minimal 3:1. Pasangan teks utama memakai ambang 7:1.

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

1. `vermilion.500` tidak dipakai untuk teks kecil di atas `sumi.800`.
2. Teks di atas `ember.500` memakai `sumi.900`, bukan putih.
3. Status tidak boleh hanya dibedakan dengan warna. Sertakan ikon atau teks.
4. Jangan menambah warna baru di luar token tanpa ADR atau pembaruan token.

## 5. Tipografi

| Peran | Keluarga | Ukuran | Pemakaian |
|---|---|---|---|
| UI | Inter | 10pt | Panel, dialog, menu, label |
| Teks isi | Inter | 10pt sampai 11pt | Aplikasi GTK dan Qt |
| Mono sistem | JetBrains Mono | 10pt | Data dan label teknis |
| Terminal | JetBrains Mono | 11pt | GNOME Terminal, XFCE Terminal, QTerminal |
| CJK | Noto Sans CJK JP | Mengikuti UI | Teks Jepang |

Fallback:

- Inter, Noto Sans, DejaVu Sans, sans-serif.
- JetBrains Mono, DejaVu Sans Mono, monospace.
- Noto Sans CJK JP untuk teks Jepang.

Aturan:

1. Tidak memakai lebih dari tiga ukuran dalam satu panel.
2. Label kapital hanya untuk kategori pendek, bukan paragraf.
3. Teks terminal memakai mono dan tidak memakai letter spacing lebar.
4. Nama berkas dan perintah selalu memakai mono.
5. Shippori Mincho tidak tersedia di bookworm. Wordmark memakai aset vektor,
   bukan font yang dipasang ke sistem.

## 6. Spacing, Radius, Elevasi, dan Gerak

Spacing mengikuti skala 4 piksel:

| Token | Nilai | Pemakaian |
|---|---:|---|
| `1` | 4px | Jarak ikon dan label |
| `2` | 8px | Padding kontrol kecil |
| `3` | 12px | Padding kontrol |
| `4` | 16px | Jarak antar elemen |
| `6` | 24px | Jarak antarkelompok |
| `8` | 32px | Margin dialog |
| `12` | 48px | Ruang kosong besar |

Radius:

| Token | Nilai | Pemakaian |
|---|---:|---|
| `none` | 0 | Pemisah dan garis |
| `sm` | 2px | Tombol kecil, input, kontrol |
| `md` | 4px | Dialog dan kartu |
| `lg` | 4px | Panel dan permukaan |
| `xl` | 4px | Dialog besar |
| `full` | 9999px | Pill, avatar, dan kontrol melingkar |

Radius di atas 4px hanya dipakai untuk kontrol melingkar dan pill. Pemeriksaan
tema menolak radius besar pada selector biasa.

Elevasi:

| Token | Nilai | Pemakaian |
|---|---|---|
| `sm` | 0 1px 2px rgba(0,0,0,0.40) | Kontrol |
| `md` | 0 8px 24px rgba(0,0,0,0.45) | Menu dan popover |

Gerak:

| Aksi | Durasi | Easing |
|---|---|---|
| Hover | 120ms | cubic-bezier(0.2, 0, 0, 1) |
| Panel | 180ms | cubic-bezier(0.2, 0, 0, 1) |
| Dialog | 280ms | cubic-bezier(0.2, 0, 0, 1) |

Tidak ada bounce, parallax, atau animasi di atas 300ms. Mode reduced motion
mematikan animasi antarmuka melalui `arashios-accessibility motion off` dan
menghormati pengaturan GTK `gtk-enable-animations`.

## 7. Komponen

### 7.1 Panel

Panel berada di atas pada ketiga edisi, dengan tinggi 30px, latar `sumi.900`
96 persen, border bawah 1px `sumi.500`, dan tanpa bayangan. Panel tidak
memakai dock melayang dan tidak menampilkan label jendela pada Cinnamon.

### 7.2 Tombol dan Input

| Varian | Latar | Teks | Border |
|---|---|---|---|
| Primer | `ember.500` | `sumi.900` | Tanpa border |
| Sekunder | `sumi.600` | `washi.100` | `sumi.500` |
| Danger | `vermilion.500` | `washi.50` | Tanpa border |
| Ghost | Transparan | `washi.100` | `sumi.500` |

Tinggi tombol 32px, radius `sm`, padding horizontal 12px. Fokus memakai cincin
2px `ember.400` dengan offset 2px. Input memakai latar `sumi.900`, border
`sumi.500`, dan placeholder `ash.500`.

### 7.3 Menu dan Notifikasi

Menu memakai `surfaceRaised`, border `sumi.500`, radius `md`, dan shadow `md`.
Item terpilih memakai `ember.500` dengan teks `sumi.900`. Notifikasi muncul di
kanan atas, memakai border kiri 3px sesuai status, dan tidak hanya bergantung
pada warna. Notifikasi kritis tidak hilang otomatis.

### 7.4 Terminal

Terminal memakai latar `sumi.900`, teks `washi.100`, kursor `ember.500`, dan
selection `vermilion.500` dengan teks `washi.50`. Palet 16 warna diturunkan
langsung dari token `terminal`. Transparansi tidak aktif secara default.

Profil terminal yang disediakan:

- GNOME Terminal: profil dconf `Kage` dengan font JetBrains Mono 11.
- XFCE Terminal: `terminalrc` dengan ColorPalette token Kage.
- QTerminal: `qterminal.ini` dengan palet token Kage.

## 8. Logo dan Wallpaper

### 8.1 Mark

Mark adalah enso terbuka dengan kanji 嵐 dan segel vermilion. Mark tersedia
dalam format SVG dan raster:

- `branding/logo/arashios-mark.svg`
- `branding/logo/arashios-wordmark.svg`
- `branding/logo/arashios-mark-mono.svg`
- `branding/logo/arashios-mark-dark.svg`
- `branding/logo/arashios-favicon.svg`
- `branding/logo/hicolor/<size>x<size>/apps/arashios.png`

Aturan:

1. Mark tidak diputar, tidak diberi bayangan tambahan, dan tidak diubah
   warnanya di luar varian yang disediakan.
2. Ukuran minimum mark digital adalah 24px. Di bawah ukuran itu, gunakan hanya
   segel atau ikon monokrom.
3. Ruang kosong di sekitar mark minimal setengah tinggi mark.
4. Mark tidak diletakkan di atas latar ramai tanpa bidang pemisah.
5. Wordmark dipakai untuk dokumen dan wallpaper. Mark dipakai untuk ikon dan
   boot.

### 8.2 Wallpaper

Wallpaper didistribusikan sebagai PNG 3840x2160. Sumber SVG tetap disimpan
untuk edit dan audit.

| Nama | Deskripsi | Mode |
|---|---|---|
| `kage-sumi` | Gradien sumi, enso, grain halus | Gelap, default |
| `kage-shuriken` | Pola geometri shuriken kontras rendah | Gelap |
| `kage-bamboo` | Siluet bambu rendah kontras | Gelap |
| `kage-washi` | Tekstur washi dengan segel merah | Terang |
| `kage-storm` | Garis isobar dan petir tipis | Gelap |

Komposisi `kage-sumi`:

1. Latar gradien sumi dari `#070709` ke `#121216`.
2. Grid tipis 80px dengan opacity rendah.
3. Glow vermilion di kanan atas.
4. Enso besar di kanan.
5. Garis potong vertikal di kiri.
6. Wordmark dan frasa Jepang di kiri bawah.

Wallpaper tidak memakai teks yang menutupi ikon desktop. Ikon desktop
dinonaktifkan pada Cinnamon, XFCE, dan LXQt.

## 9. Boot Experience

### 9.1 GRUB

Tema GRUB berada di `branding/grub/theme.txt` dan dipasang ke
`/usr/share/grub/themes/arashios/`. Latar `background.png` 1920x1080 dihasilkan
oleh `scripts/generate-brand-assets.py`. Menu memakai label `ARASHIOS / KAGE`
dan `SECURITY FIRST`.

Untuk ISO live, tema khusus berada di
`config/common/bootloaders/grub-pc/live-theme/theme.txt`. Tema ini memakai
`../splash.png`, yaitu `branding/boot/grub-splash.png` 1024x768, dan menyertakan
progress bar timeout. `build.sh` menyalin pixmap nine-slice `select_*.png` dari
`branding/grub/` ke direktori live tersebut. Dengan begitu menu GRUB live
memakai komposisi Kage, bukan tema bawaan live-build.

Konfigurasi live memakai `config/common/bootloaders/grub-pc/config.cfg` dengan
aturan:

1. Timeout 5 detik.
2. Resolusi 1024x768, dengan fallback 800x600 dan mode otomatis.
3. Entri serial `ArashiOS serial console` dengan `console=ttyS0,115200`.
4. Tidak ada logo Debian.
5. Tidak ada beep atau suara boot.

### 9.2 Plymouth

Tema Plymouth berada di `branding/plymouth/`. Komposisi berupa latar sumi,
logo enso, teks `ARASHIOS` dengan font Sans 26, subjudul `KAGE` berwarna
ember, dan progress line 320x2. Hanya progress line yang bergerak.

Aset:

- `logo.png`
- `progress_box.png`
- `progress_bar.png`
- `arashios.script`
- `arashios.plymouth`

Progress line memakai `Plymouth.SetBootProgressFunction`. Tidak ada suara,
video, atau animasi berulang.

### 9.3 LightDM

Greeter memakai `lightdm-gtk-greeter` dengan tema `ArashiKage`, ikon
`Papirus-Dark`, kursor `Bibata-Modern-Classic`, font `Inter 10`, panel atas,
dan wallpaper `kage-sumi.png`. Sesi yang tersedia mengikuti edisi yang
dipasang.

Autologin hanya aktif pada sesi live. Fase 7 harus menghapus autologin pada
sistem terpasang.

## 10. Pemetaan Desktop

| Elemen | Cinnamon | XFCE | LXQt |
|---|---|---|---|
| Panel | Atas, 30px | Atas, 30px | Atas, 30px |
| Menu | Menu Cinnamon | Whisker Menu | Menu aplikasi LXQt |
| Window list | Grouped window list, ikon saja | Tasklist | Taskbar |
| Workspace | 4, indikator vertikal | 4, pager | 4, desktop switch |
| File manager | Nemo | Thunar | PCManFM-Qt |
| Terminal | GNOME Terminal | XFCE Terminal | QTerminal |
| Editor | Gedit | Mousepad | Featherpad |
| Image viewer | Eye of GNOME | Ristretto | LXImage-Qt |
| Tema GTK | ArashiKage | ArashiKage | ArashiKage |
| Tema Qt | Kvantum ArashiKage | Tidak berlaku | Kvantum ArashiKage |
| Window manager | Muffin | xfwm4 | Openbox |
| Ikon desktop | Nonaktif | Nonaktif | Nonaktif |

### 10.1 Cinnamon

1. Panel atas 30px dengan menu, grouped window list, kalender, workspace
   switcher, systray, notifikasi, keyboard, suara, dan power.
2. Empat workspace.
3. Nemo list view, thumbnail nonaktif, hidden file nonaktif.
4. Desktop tanpa ikon.
5. Screensaver aktif dengan lock delay 0.
6. Automount dan autorun dimatikan.
7. GNOME Terminal memakai profil Kage.
8. Muffin dan border jendela memakai tema ArashiKage.

### 10.2 XFCE

1. Panel atas 30px dengan Whisker Menu, tasklist, jam, systray, pulseaudio,
   power manager, notifikasi, dan pager.
2. xfwm4 memakai tema ArashiKage, compositor dengan shadow halus, tanpa blur.
3. Thunar list view dan volume management.
4. Desktop tanpa ikon, trash, home, atau filesystem.
5. Wallpaper `kage-sumi.png` dengan mode zoom.
6. XFCE Terminal memakai palet token.

### 10.3 LXQt

1. Panel atas 30px dengan menu, quick launch, taskbar, desktop switch,
   status notifier, tray, volume, jam, dan show desktop.
2. Quick launch berisi QTerminal, PCManFM-Qt, dan Firefox ESR.
3. Openbox memakai border aktif vermilion 2px, title layout `IMC`, dan empat
   workspace.
4. PCManFM-Qt list view, wallpaper `kage-sumi.png`, tanpa desktop shortcut.
5. Kvantum ArashiKage untuk seluruh aplikasi Qt.
6. Tanpa compositor berat.

## 11. Aksesibilitas

Perintah:

```bash
arashios-accessibility contrast on
arashios-accessibility contrast off
arashios-accessibility contrast toggle
arashios-accessibility motion on
arashios-accessibility motion off
arashios-accessibility status
kage-contrast on
```

Perilaku:

1. Mode kontras memakai tema `ArashiKage-HC` pada GTK3, GTK4, Cinnamon,
   XFCE, Openbox, dan Kvantum.
2. Mode motion menulis `gtk-enable-animations` dan pengaturan desktop yang
   tersedia. Efek kompositor tidak dimatikan paksa.
3. Status menampilkan desktop, tema, dan status animasi jika toolkit
   menyediakan query.
4. Aplikasi yang sudah berjalan perlu dimulai ulang. Beberapa window manager
   perlu logout dan login ulang.
5. Fokus keyboard memakai outline 2px `ember.400`, bukan hanya perubahan
   warna.
6. Target klik minimal 32x32px.
7. Teks tidak lebih kecil dari 10pt untuk UI dan 11pt untuk terminal.
8. Wallpaper tidak mengganggu keterbacaan label.

Pengujian screen reader, scaling 125 dan 150 persen, serta navigasi installer
tanpa mouse termasuk Fase 6, 7, dan 10.

## 12. Verifikasi

Pemeriksaan statis yang tersedia:

```bash
./tests/theme.sh
./tests/desktop-matrix.sh
./tests/branding-package.sh
./scripts/validate-config.sh
```

Cakupan:

1. 164 file tema dengan hash manifest dan XML yang dapat diparse.
2. 70 aset XFWM per varian tema.
3. Parser CSS GTK3 untuk kedua varian.
4. Pemeriksaan warna, radius, durasi transisi, dan ukuran panel.
5. Pemeriksaan dconf Cinnamon dengan `dconf compile`.
6. Pemeriksaan XML XFCE, Openbox, dan Kvantum.
7. Pemeriksaan MIME, paket, dan layout panel.
8. Pemeriksaan isi dan metadata paket `arashios-branding`.

Angka aktual dan batas pengujian dicatat di
[PHASE-2-3-REPORT.md](PHASE-2-3-REPORT.md).

## 13. Batas Implementasi

1. ISO belum dibangun pada host ini karena `lb`, `debootstrap`, `xorriso`,
   dan QEMU belum tersedia.
2. Boot GRUB, Plymouth, LightDM, login desktop, panel XFCE, Openbox, dan
   rendering Kvantum belum diuji pada sesi nyata.
3. Parser CSS GTK4 dilewati karena PyGObject GTK4 tidak tersedia di host.
4. arm64 dan i386 belum diuji secara runtime.
5. Screenshot sebelum dan sesudah belum tersedia.
6. Cinnamon applet default dipatch melalui hook. Pembaruan paket Cinnamon
   dapat menimpa file JSON sistem.
7. Aplikasi yang sudah berjalan tidak dimulai ulang otomatis setelah tema
   diganti.
8. Autologin masih aktif pada sistem terpasang sampai Fase 7.
9. Starship dan Shippori Mincho tidak tersedia di bookworm. Prompt memakai
   fallback Zsh, wordmark memakai aset vektor.
10. Alamat maintainer memakai domain contoh `.example` sampai domain proyek
    diverifikasi.

## 14. Checklist QA Visual

Checklist ini wajib dijalankan saat ISO dan sesi desktop tersedia.

| ID | Pemeriksaan | Lulus jika |
|---|---|---|
| VQ-01 | Palet | Tidak ada warna di luar token |
| VQ-02 | Kontras | Semua teks lulus AA |
| VQ-03 | Tipografi | Maksimal dua keluarga font per layar |
| VQ-04 | Spacing | Semua jarak kelipatan 4px |
| VQ-05 | Radius | Tidak ada radius di atas 4px kecuali pill |
| VQ-06 | Shadow | Hanya menu dan popover |
| VQ-07 | Aksen | Maksimal satu aksen merah per layar |
| VQ-08 | Ikon | Tidak ada emoji di UI sistem |
| VQ-09 | Motion | Tidak ada animasi di atas 300ms |
| VQ-10 | Empty state | Setiap layar kosong punya pesan jelas |
| VQ-11 | Boot | GRUB dan Plymouth tidak menampilkan logo Debian |
| VQ-12 | Greeter | LightDM menampilkan sesi yang benar |
| VQ-13 | Desktop | Panel, wallpaper, dan ikon sesuai edisi |
| VQ-14 | Focus | Fokus terlihat pada tombol, input, menu, dan panel |
| VQ-15 | Keyboard | Greeter dan desktop dapat dinavigasi tanpa mouse |
| VQ-16 | Scaling | 100, 125, dan 150 persen tidak memotong label |

## 15. Lisensi

| Aset | Lisensi |
|---|---|
| Mark, wordmark, wallpaper, tema GRUB, tema Plymouth | CC-BY-SA-4.0 |
| Token dan stylesheet | CC-BY-SA-4.0 |
| Kode generator dan tema | GPL-3.0-or-later |
| Dokumentasi | CC-BY-4.0 |
| Font | Lisensi masing-masing, umumnya OFL |
| Papirus | GPL-3.0 |
| Bibata | GPL-3.0 |
| Inspirasi palet terminal | MIT, Kanagawa.nvim |

Atribusi dan batasan merek dijelaskan di [LEGAL.md](LEGAL.md) dan
[TRADEMARK.md](TRADEMARK.md).
