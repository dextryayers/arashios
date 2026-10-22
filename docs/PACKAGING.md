# Packaging ArashiOS

Dokumen ini menjelaskan standar packaging, proses build paket, dan aturan
mutu yang dijalankan pada setiap paket ArashiOS.

## 1. Standar

Aturan berasal dari plan.md bagian 11.3 dan diterapkan oleh
`scripts/check-packages.py`.

| Aturan | Penerapan |
|---|---|
| debhelper 13 | Equivalent: control, copyright, changelog, md5sums dibuat otomatis |
| lintian bersih | `scripts/check-packages.py` memeriksa field, path, dan deterministic build |
| copyright lengkap | Setiap paket membawa `DEBIAN/copyright` |
| changelog mengikuti rilis | Versi paket mengikuti `ARASHIOS_VERSION` |
| Tidak ada file di luar FHS | Hanya `usr`, `etc`, `var`, `opt`, `srv` |
| Tidak ada postinst yang mengakses jaringan | Tidak ada skrip pemelihara yang memanggil jaringan |
| Postinst idempoten | `arashios-postinstall` dapat dijalankan ulang |
| Test install dan remove | `tests/installer.sh` dan `tests/branding-package.sh` |
| Paket all untuk aset | Seluruh paket v1 berarsitektur all |
| Signature lewat repo | InRelease dan Release.gpg di repository |

## 2. Daftar paket

| Paket | Isi | Sumber payload |
|---|---|---|
| arashios-branding | Tema, wallpaper, ikon, aset GRUB dan Plymouth | `scripts/build-branding-package.sh` |
| arashios-theme-gtk | GTK2, GTK3, GTK4, libadwaita | `build/theme/themes` |
| arashios-theme-cinnamon | Cinnamon stylesheet | `build/theme/themes` |
| arashios-theme-qt | Kvantum dan qt5ct | `build/theme/Kvantum` |
| arashios-theme-xfce | xfwm4 dan terminalrc | `build/theme/themes` |
| arashios-theme-openbox | Openbox themerc | `build/theme/themes` |
| arashios-icons | Ikon aplikasi hicolor | `branding/logo/hicolor` |
| arashios-desktop-common | Skel, Zsh, tmux, Neovim, helper | `config/common/includes.chroot` |
| arashios-desktop-cinnamon | dconf Cinnamon, LightDM, wallpaper | `config/editions/cinnamon` |
| arashios-desktop-xfce | xfconf, LightDM, wallpaper | `config/editions/xfce` |
| arashios-desktop-lxqt | lxqt.conf, Openbox, wallpaper | `config/editions/lxqt` |
| arashios-meta-redteam | Metapaket tool keamanan | Daftar paket keamanan |
| arashios-meta-dev | Metapaket toolchain | Daftar paket dev |
| arashios-meta-daily | Metapaket aplikasi harian | Daftar paket harian |
| arashios-arsenal | Perintah arsenal dan katalog runtime | `config/common/includes.chroot` |
| arashios-repo-keyring | Kunci publik repository | `repo/keys` |

Metapaket memakai daftar paket yang diaudit, sehingga isinya selalu sama
dengan image.

## 3. Build paket

```bash
python3 scripts/build-packages.py --list
python3 scripts/build-packages.py --package arashios-theme-gtk
python3 scripts/build-packages.py --all
```

Proses:

1. Payload disalin dari pohon sumber ke direktori staging.
2. `DEBIAN/control` ditulis dari `packages/packages.yaml`.
3. `DEBIAN/copyright` dan `DEBIAN/changelog` dibuat dengan versi rilis.
4. `DEBIAN/md5sums` dihitung dari payload.
5. Timestamp semua berkas disamakan dengan `SOURCE_DATE_EPOCH`.
6. Paket dibangun dengan `dpkg-deb --root-owner-group --build`.

Hasilnya deterministik. Build dengan `SOURCE_DATE_EPOCH` yang sama menghasilkan
berkas identik.

## 4. Pemeriksaan

```bash
python3 scripts/check-packages.py
```

Pemeriksaan meliputi:

1. Spesifikasi memuat 16 paket dengan nama, deskripsi, dan arsitektur yang benar.
2. Semua paket yang dijadwalkan benar-benar dibangun.
3. Field control lengkap dan Maintainer valid.
4. Tidak ada berkas di luar FHS.
5. Timestamp berkas seragam per paket.
6. Indeks repository memakai path relatif dan memuat checksum.
7. `InRelease` terverifikasi dengan kunci repository.

## 5. Pembaruan paket

1. Ubah `packages/packages.yaml` untuk menambah payload, dependensi, atau
   deskripsi.
2. Jalankan `python3 scripts/build-packages.py --all`.
3. Jalankan `python3 scripts/check-packages.py`.
4. Bangun repository dengan `scripts/build-repo.py`.
5. Perbarui `CHANGELOG.md` dan `docs/LICENSES.md` bila lisensi berubah.

## 6. Aturan lisensi paket

| Komponen | Lisensi |
|---|---|
| Kode ArashiOS | GPL-3.0-or-later |
| Aset visual | CC-BY-SA-4.0 |
| Dokumentasi | CC-BY-4.0 |
| Paket Debian | Lisensi masing-masing |

Setiap paket membawa berkas `copyright` dengan teks GPL-3.0-or-later dan
menunjuk ke `/usr/share/common-licenses/GPL-3` pada sistem terpasang.

## 7. Batasan saat ini

1. Pemeriksaan berjalan di luar lintian. Lintian penuh memerlukan paket
   `lintian` pada host build dan belum dijalankan.
2. Sumber paket belum memakai debhelper dan format quilt. Builder memakai
   `dpkg-deb` langsung agar deterministik dan tanpa dependensi tambahan.
3. Skrip pemelihara belum diuji pada chroot Debian 12 karena image belum
   dibangun.
