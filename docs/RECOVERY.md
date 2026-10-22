# Pemulihan ArashiOS

Dokumen ini menjelaskan prosedur pemulihan sistem ArashiOS yang gagal boot,
termasuk mount partisi, membuka volume terenkripsi, memasang ulang GRUB, dan
memulihkan partisi EFI.

## 1. Memulai dari live session

1. Boot dari image ArashiOS pada mode firmware yang sama dengan sistem yang
   rusak.
2. Login sebagai pengguna `arashi`.
3. Buka terminal.

## 2. Diagnosis

```bash
arashios-recovery diagnose
```

Perintah menampilkan:

1. Versi kernel dan arsitektur.
2. Mode firmware UEFI atau BIOS.
3. Status Secure Boot.
4. Daftar disk dan partisi beserta mount point.
5. Entri EFI dan urutan boot.
6. Lokasi konfigurasi GRUB dan jumlah entri menu.
7. Error terakhir dari boot sebelumnya.

## 3. Membuka volume terenkripsi

```bash
sudo arashios-recovery luks-open cryptroot /dev/sda3
```

Volume terenkripsi muncul sebagai `/dev/mapper/cryptroot`. Untuk sistem dengan
LVM:

```bash
sudo arashios-recovery lvm-scan
```

## 4. Mount dan chroot

```bash
sudo arashios-recovery chroot
```

Sistem target dipasang di `/mnt/arashios` bersama `/proc`, `/sys`, `/dev`, dan
partisi EFI. Perintah masuk ke shell di dalam sistem target. Untuk menjalankan
satu perintah saja:

```bash
sudo arashios-recovery chroot "systemctl status NetworkManager"
```

## 5. Memasang ulang GRUB

```bash
sudo arashios-recovery grub-install
sudo arashios-recovery grub-update
```

Perintah memilih target otomatis: `x86_64-efi` untuk UEFI amd64 dan
`i386-pc` untuk BIOS. Di dalam chroot, instalasi manual dapat dilakukan dengan:

```bash
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=ArashiOS
grub-mkconfig -o /boot/grub/grub.cfg
```

Tema Kage tetap dipakai karena `/etc/default/grub` sudah berisi:

```text
GRUB_THEME="/usr/share/grub/themes/arashios/theme.txt"
```

## 6. Cadangan dan pemulihan EFI

```bash
sudo arashios-recovery backup-efi /mnt/backup-efi
sudo arashios-recovery restore-efi /mnt/backup-efi
```

Cadangan menyimpan berkas EFI seperti `EFI/BOOT/BOOTX64.EFI` dan entri
startup. Pemulihan menimpa berkas di partisi EFI.

## 7. Snapshot Timeshift

Timeshift terpasang pada sistem terpasang dan membuat snapshot pertama saat
instalasi selesai.

```bash
sudo timeshift --list
sudo timeshift --create --comments "sebelum perubahan"
sudo timeshift --restore
```

Snapshot memakai rsync dan tidak mengubah partisi lain.

## 8. Pemeriksaan umum

| Gejala | Penyebab | Tindakan |
|---|---|---|
| GRUB tidak muncul | Partisi EFI tidak terpasang | `arashios-recovery grub-install` |
| Sistem minta password yang salah | Volume LUKS belum dibuka | `arashios-recovery luks-open` |
| `ls: cannot access /boot/efi` | ESP tidak dipasang | mount ESP manual lalu chroot |
| Driver WiFi hilang | Firmware belum terpasang | pasang `firmware-iwlwifi` di chroot |
| Zona waktu salah | Zona waktu tidak tersimpan | `ln -sf /usr/share/zoneinfo/Asia/Jakarta /etc/localtime` |
| Perintah tidak ditemukan | PATH chroot salah | `export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin` |

## 9. Batasan saat ini

1. Belum ada prosedur pemulihan yang diuji pada image ISO.
2. Partisi LVM belum diuji pada sistem terpasang.
3. Pemulihan EFI pada sistem dengan beberapa entri EFI belum diuji.
