# Integrasi Desktop

Dokumen ini mencatat konfigurasi desktop yang dikirim oleh ArashiOS pada Fase
2 dan Fase 3. Semua konfigurasi masih berada pada tingkat statis. Validasi
login, panel, window manager, dan rendering toolkit memerlukan ISO dan sesi
nyata.

## 1. Lapisan Bersama

| Komponen | Path | Isi |
|---|---|---|
| Tema dan aset | `/usr/share/themes`, `/usr/share/Kvantum`, `/usr/share/backgrounds/arashios` | Paket `arashios-branding` |
| GTK3 | `/etc/gtk-3.0/settings.ini` | Tema, ikon, kursor, font |
| GTK4 | `/etc/gtk-4.0/settings.ini`, `/etc/xdg/gtk-4.0/gtk.css` | Tema dan import libadwaita |
| GTK2 | `/etc/gtk-2.0/gtkrc`, `/etc/skel/.gtkrc-2.0` | Fallback aplikasi lama |
| Qt | `/etc/xdg/qt5ct/qt5ct.conf`, `/etc/xdg/Kvantum/kvantum.kvconfig` | Kvantum dan qt5ct |
| Lingkungan | `/etc/environment` | `QT_QPA_PLATFORMTHEME=qt5ct`, `QT_STYLE_OVERRIDE=kvantum` |
| LightDM | `/etc/lightdm/lightdm-gtk-greeter.conf.d/50-arashios.conf` | Tema, wallpaper, panel atas |
| Wallpaper | `/etc/xdg/autostart/arashios-wallpaper.desktop` | Penerapan wallpaper per desktop |
| Aksesibilitas | `/usr/local/bin/arashios-accessibility`, `/usr/local/bin/kage-contrast` | Kontras, gerak, status |

Paket `arashios-branding` bergantung pada `gtk2-engines-murrine`,
`qt5-style-kvantum`, `qt5ct`, `papirus-icon-theme`, `bibata-cursor-theme`,
`fonts-inter`, dan `fonts-jetbrains-mono`. Paket ini tidak memasang desktop
atau window manager.

## 2. Cinnamon

| Path | Fungsi |
|---|---|
| `/etc/dconf/db/local.d/00-arashios` | Default panel, tema GTK dan Muffin, wallpaper, workspace, Nemo, media, dan GNOME Terminal |
| `/etc/lightdm/lightdm.conf.d/50-arashios.conf` | Sesi Cinnamon dan autologin live |
| `/etc/xdg/mimeapps.list` | Asosiasi Nemo, Gedit, Eye of GNOME, dan Firefox |
| `/etc/dconf/profile/user` | Urutan database user dan sistem |

Default utama:

1. Panel atas 30px dengan menu, grouped window list, kalender, workspace
   switcher, systray, notifikasi, keyboard, suara, dan power.
2. Empat workspace.
3. Tema `ArashiKage` untuk GTK, Cinnamon, dan Muffin, ikon `Papirus-Dark`,
   kursor `Bibata-Modern-Classic`.
4. Wallpaper `kage-sumi.png`.
5. Ikon desktop Nemo nonaktif.
6. GNOME Terminal memakai profil `Kage` dengan palet token.
7. Toolkit accessibility aktif.

Hook `0100-branding.chroot` mempatch default JSON applet Cinnamon untuk format
kalender, ikon menu, label menu, dan workspace switcher. Pembaruan paket
Cinnamon dapat menimpa file JSON tersebut. Hook yang sama menjalankan
`dconf update`.

## 3. XFCE

| Path | Fungsi |
|---|---|
| `xfconf/xfce-perchannel-xml/xsettings.xml` | Tema, ikon, kursor, font, dan aksesibilitas |
| `xfconf/xfce-perchannel-xml/xfwm4.xml` | Tema window manager, tombol, dan workspace |
| `xfconf/xfce-perchannel-xml/xfce4-panel.xml` | Panel atas dan plugin |
| `xfconf/xfce-perchannel-xml/xfce4-desktop.xml` | Wallpaper dan ikon desktop |
| `xfconf/xfce-perchannel-xml/xfce4-session.xml` | Sesi dan logout |
| `xfconf/xfce-perchannel-xml/thunar.xml` | Thunar list view |
| `/etc/lightdm/lightdm.conf.d/50-arashios.conf` | Sesi XFCE dan autologin live |
| `/etc/xdg/mimeapps.list` | Asosiasi Thunar, Mousepad, Ristretto, dan Firefox |

Panel berisi 11 plugin:

1. Whisker Menu.
2. Separator.
3. Tasklist.
4. Separator.
5. Jam.
6. Separator.
7. Systray.
8. PulseAudio.
9. Power manager.
10. Notifikasi.
11. Pager.

Konfigurasi wallpaper memakai `monitor0` dan `workspace0`. Autostart
`arashios-wallpaper` mencoba menerapkan wallpaper ke properti monitor yang
ditemukan saat sesi berjalan. Perilaku ini perlu diuji pada perangkat dengan
nama monitor berbeda.

## 4. LXQt

| Path | Fungsi |
|---|---|
| `/etc/xdg/lxqt/lxqt.conf` | Tema, ikon, font, dan gaya Kvantum |
| `/etc/xdg/lxqt/panel.conf` | Panel atas, quick launch, taskbar, tray, jam |
| `/etc/xdg/lxqt/session.conf` | Kursor dan sesi |
| `/etc/xdg/pcmanfm-qt/lxqt/settings.conf` | Wallpaper, list view, media, dan terminal |
| `/etc/xdg/openbox/rc.xml` | Tema Openbox, border, tombol, dan workspace |
| `/etc/xdg/openbox/menu.xml` | Menu Openbox |
| `/etc/lightdm/lightdm.conf.d/50-arashios.conf` | Sesi LXQt dan autologin live |
| `/etc/xdg/mimeapps.list` | Asosiasi PCManFM-Qt, Featherpad, LXImage-Qt, dan Firefox |

Panel memakai plugin `mainmenu`, `quicklaunch`, `taskbar`, `desktopswitch`,
`statusnotifier`, `tray`, `volume`, `worldclock`, dan `showdesktop`. Quick
launch berisi QTerminal, PCManFM-Qt, dan Firefox ESR melalui QSettings array
`apps\size` dan `apps\<n>\desktop`.

Openbox memakai tema `ArashiKage`, title layout `IMC`, border aktif 2px
`vermilion.500`, dan empat workspace. PCManFM-Qt memakai wallpaper
`kage-sumi.png` dengan mode zoom dan tanpa desktop shortcut.

## 5. Aksesibilitas

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

`contrast on` memilih `ArashiKage-HC` pada GTK, Cinnamon, XFCE, Openbox, dan
Kvantum. `motion off` menulis `gtk-enable-animations=false` dan pengaturan
desktop yang tersedia. Perubahan tidak memulai ulang aplikasi yang sedang
berjalan.

`tests/desktop-matrix.sh` menjalankan helper ini dengan `HOME` sementara dan
memeriksa file GTK3, GTK4, dan Kvantum. Pengujian ini tidak memerlukan sesi
grafis.

## 6. Perintah Verifikasi

```bash
./tests/theme.sh
./tests/desktop-matrix.sh
./tests/branding-package.sh
./scripts/validate-config.sh
```

`tests/theme.sh` memeriksa 164 file tema, manifest SHA-256, XML, radius,
warna, dan parser CSS GTK3 serta GTK4. `tests/desktop-matrix.sh` memeriksa
konfigurasi dconf, XFCE, LXQt, Openbox, MIME, dan helper aksesibilitas.
`tests/branding-package.sh` memeriksa isi paket, `md5sums`, metadata, dan
reproduksibilitas paket.

## 7. Checklist Runtime

Checklist berikut belum dijalankan sampai ISO tersedia:

1. LightDM menampilkan wallpaper, font, dan sesi yang benar.
2. Login Cinnamon, XFCE, dan LXQt berhasil.
3. Panel atas 30px tampil pada ketiga edisi.
4. Ikon desktop tidak muncul.
5. Wallpaper tampil pada monitor utama dan monitor kedua.
6. Nemo, Thunar, dan PCManFM-Qt memakai tema dan ikon Kage.
7. GNOME Terminal, XFCE Terminal, dan QTerminal memakai palet Kage.
8. Whisker Menu, menu Cinnamon, dan menu LXQt dapat dibuka dengan keyboard.
9. Openbox menampilkan border dan tombol yang benar.
10. Kvantum merender dialog Qt tanpa artefak.
11. Mode kontras tinggi dapat diaktifkan dan dimatikan.
12. Reduced motion mematikan animasi antarmuka.
13. Font scaling 125 dan 150 persen tidak memotong label.
14. Logout dan login ulang mempertahankan pilihan tema.
15. GRUB dan Plymouth tidak menampilkan logo Debian.

## 8. Batasan

1. Konfigurasi telah diperiksa secara statis, bukan pada sesi live.
2. Parser CSS GTK4 memakai GTK 4.18 di host pengembangan. Target bookworm
   memakai GTK 4.8 dan perlu diuji pada ISO.
3. Kvantum belum dijalankan pada sesi Qt nyata.
4. Nama monitor XFCE dapat berbeda pada perangkat keras nyata.
5. Patch JSON applet Cinnamon dapat tertimpa pembaruan paket.
6. Aplikasi yang berjalan tidak dimulai ulang otomatis setelah tema berubah.
7. Autologin live masih aktif sampai Calamares menghapusnya pada Fase 7.
