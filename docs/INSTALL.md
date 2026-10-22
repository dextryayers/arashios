# Instalasi ArashiOS

Dokumen ini menjelaskan instalasi ArashiOS dengan Calamares, profil partisi,
enkripsi, boot ganda, Secure Boot, dan boot ulang.

## 1. Prasyarat

| Kebutuhan | Keterangan |
|---|---|
| Memori | 2 GB untuk edisi LXQt, 4 GB untuk edisi Cinnamon |
| Disk | 15 GB minimum, 40 GB untuk pemakaian harian |
| Boot | UEFI atau BIOS, UEFI untuk arm64 |
| Secure Boot | Harus dinonaktifkan, kernel ArashiOS belum ditandatangani |
| Jaringan | Tidak wajib, paket sudah ada di image |

## 2. Menjalankan installer

1. Boot dari image ArashiOS pada mode UEFI bila firmware mendukungnya.
2. Login sebagai pengguna `arashi` pada sesi live.
3. Jalankan aplikasi **Install ArashiOS** dari menu aplikasi.
4. Masukkan kata sandi untuk installer bila diminta.
5. Ikuti langkah demi langkah.

Installer memakai branding Kage, wallpaper yang sama dengan desktop, dan tidak
mengirim log ke server mana pun.

User live bernama `arashi` dan dihapus dari sistem terpasang. Akun yang
dibuat installer memakai nama berbeda, misalnya `arashios`, dan dapat diganti
pada langkah user.

## 3. Langkah instalasi

| Langkah | Isi | Pilihan |
|---|---|---|
| Welcome | Ringkasan dan tautan dokumentasi | Lanjut atau batal |
| Locale | Bahasa dan format | en_US, id_ID, ja_JP |
| Keyboard | Tata letak keyboard | Standar US |
| Partition | Profil partisi | Erase, alongside, manual |
| User | Nama, nama lengkap, kata sandi | User standar, tanpa autologin |
| Display manager | LightDM | Terpilih otomatis |
| Packages | Tidak ada paket tambahan | Lewati |
| Summary | Ringkasan perubahan | Setujui |

## 4. Profil partisi

### 4.1 Erase disk

Menghapus seluruh isi disk dan membuat partisi baru. Partisi ESP berukuran
512 MiB, partisi root ext4, dan swap memakai zram sehingga tidak ada partisi
swap.

### 4.2 Berdampingan

Memperkecil partisi yang sudah ada dan memasang ArashiOS di ruang kosong.
Partisi lain tidak diubah jenisnya.

### 4.3 Manual

Semua partisi dibuat manual. Panduan lengkap ada di bagian manual di bawah.

## 5. Enkripsi

1. Aktifkan enkripsi pada langkah partisi.
2. Pilih LUKS2 dengan ext4 di dalamnya. Partisi ESP tetap tidak terenkripsi
   agar dapat dipakai untuk boot.
3. Masukkan passphrase yang kuat dan simpan di tempat aman.
4. Partisi root terenkripsi dengan nama volume `cryptroot`.

Passphrase ditanyakan saat boot. Untuk mesin pribadi, opsi boot key dapat
dibuka lewat modul `luksbootkeyfile` agar passphrase tidak diminta setiap kali
booting. Kunci boot disimpan di partisi ESP.

## 6. Manual dengan LUKS dan LVM

Calamares 3.2 belum punya modul LVM bawaan. Volume LVM disiapkan manual
sebelum installer dijalankan.

```bash
# 1. Partisi manual
parted /dev/sdX
mklabel gpt
mkpart ESP fat32 1MiB 513MiB
set 1 esp on
mkpart primary ext4 513MiB 100%
mkpart primary 100% 100%
# Lihat nomor partisi yang dipakai
```

```bash
# 2. Partisi EFI
mkfs.fat -F32 /dev/sdX1
mount /dev/sdX1 /mnt/esp

# 3. Volume LVM
pvcreate /dev/sdX3
vgcreate arashios /dev/sdX3
lvcreate -L 20G -n root arashios
lvcreate -L 8G -n swap arashios
lvcreate -L 100%FREE -n home arashios
```

```bash
# 4. Enkripsi LUKS pada volume logis
cryptsetup luksFormat --type luks2 /dev/arashios/root
cryptsetup open /dev/arashios/root cryptroot
mkfs.ext4 /dev/mapper/cryptroot
mount /dev/mapper/cryptroot /mnt
```

Lalu jalankan installer dengan profil manual, tunjuk `/dev/mapper/cryptroot`
sebagai root, dan pasang `/dev/sdX1` sebagai `/boot/efi`. Setelah instalasi
selesai, aktifkan volume LVM dengan:

```bash
sudo arashios-recovery lvm-scan
```

## 7. Boot ganda dengan Windows

### 7.1 Persiapan di Windows

1. Matikan Fast Startup: Panel Kontrol, Opsi Daya, tombol Mulai, shut down
   cepat.
2. Buka kunci BitLocker bila partisi Windows terenkripsi.
3. Kurangi partisi Windows dari Koutil Partisi Windows.

### 7.2 Pemeriksaan sebelum partisi

```bash
arashios-dualboot-check
```

Perintah ini melaporkan partisi Windows, Fast Startup, BitLocker, dan status
Secure Boot. Partisi tidak boleh diubah bila masih ada masalah.

### 7.3 Deteksi sistem lain

os-prober terpasang dan `GRUB_DISABLE_OS_PROBER=false` disetel pada
`/etc/default/grub`. Entri Windows muncul sebagai "Windows Boot Manager" pada
menu GRUB.

## 8. Secure Boot

1. Status Secure Boot diperiksa dengan `mokutil --sb-state`.
2. ArashiOS belum menandatangani kernel dan bootloader, sehingga Secure Boot
   harus dinonaktifkan di firmware sebelum instalasi.
3. Setelah mengubah pengaturan, `sudo arashios-recovery diagnose` menampilkan status
   Secure Boot, entri EFI, dan konfigurasi GRUB.

## 9. Setelah instalasi

| Tindakan | Otomatis oleh |
|---|---|
| Autologin dimatikan | arashios-postinstall |
| Installer dihapus dari sistem | arashios-postinstall |
| Snapshot pertama Timeshift | arashios-postinstall |
| Layanan harian diaktifkan | services-systemd dan arashios-postinstall |
| SSH dimask | services-systemd |
| Tema Kage dan GRUB | paket arashios-branding |

Periksa hasilnya:

```bash
arashios-doctor
arashios-daily
```

## 10. Pemulihan

Prosedur pemulihan ada di [RECOVERY.md](RECOVERY.md). Ringkas:

```bash
arashios-recovery diagnose
arashios-recovery chroot
sudo arashios-recovery grub-install
```

## 11. Checklist sepuluh skenario

| ID | Skenario | Edisi |
|---|---|---|
| INST-01 | Erase disk pada UEFI | Cinnamon, XFCE, LXQt |
| INST-02 | Erase disk pada BIOS | Cinnamon, LXQt |
| INST-03 | Berdampingan dengan Linux | Cinnamon, XFCE, LXQt |
| INST-04 | Berdampingan dengan Windows | Cinnamon, XFCE |
| INST-05 | Manual dengan LUKS2 | Cinnamon, XFCE, LXQt |
| INST-06 | Manual dengan LUKS2 dan LVM | Cinnamon |
| INST-07 | Suspend dan resume setelah instalasi | Cinnamon, XFCE, LXQt |
| INST-08 | Pembaruan APT tanpa regresi | Cinnamon, XFCE, LXQt |
| INST-09 | Boot ulang dua kali | Cinnamon, XFCE, LXQt |
| INST-10 | Snapshot Timeshift dan restore | Cinnamon, XFCE, LXQt |

Lolos bila tiga puluh kombinasi skenario dan edisi selesai tanpa kehilangan
data.

## 12. Batasan saat ini

1. Skenario instalasi belum dijalankan karena image ISO belum dibangun.
2. Modul LVM bawaan Calamares belum tersedia, LVM disiapkan manual.
3. Secure Boot belum didukung, hanya dapat dideteksi dan didokumentasikan.
4. Triple boot Windows, Debian, dan ArashiOS belum diuji pada perangkat nyata.
