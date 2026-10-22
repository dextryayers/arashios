# Persistensi Sesi Live ArashiOS

Dokumen ini menjelaskan cara menyimpan perubahan sesi live di partisi
persistensi.

## 1. Prinsip

1. Sesi live berjalan dari media yang hanya bisa dibaca.
2. Partisi persistensi menyimpan perubahan sehingga tetap ada saat boot ulang.
3. Partisi diberi label `persistence` dan berisi berkas `persistence.conf`
   dengan direktif `/ union`.
4. Data di partisi persistensi tidak terenkripsi kecuali partisi dibuat
   terenkripsi secara manual.

## 2. Menyiapkan partisi

```bash
# Lihat kandidat partisi
arashios-persistence list

# Siapkan partisi, contoh /dev/sdb1
sudo arashios-persistence setup /dev/sdb1

# Periksa isi partisi
sudo arashios-persistence verify /dev/sdb1
```

Perintah `setup` membuat sistem berkas ext4, memberi label `persistence`, dan
menulis berkas berikut:

```text
/persistence.conf
```

```text
/ union
```

Partisi yang sudah berisi data tidak akan diubah.

## 3. Boot dengan persistensi

1. Tutup sesi live dengan shuts down, bukan restart.
2. Boot ulang dari media yang sama.
3. Sesi live menemukan partisi berlabel `persistence` dan memakai union
   mount, sehingga perubahan tersimpan.

Bila partisi tidak terdeteksi, periksa dengan `arashios-persistence status`
dan pastikan label partisi tepat `persistence`.

## 4. Batas

| Aspek | Batas |
|---|---|
| Ukuran | Dibatasi ukuran partisi yang dibuat |
| Data | Hanya perubahan pada direktori sistem yang disimpan |
| Performa | Union mount menambah penulisan disk |
| Keamanan | Tidak terenkripsi secara bawaan |
| Kernel | Union mount memerlukan modul overlay atau aufs |

## 5. Encrypt partisi

Partisi persistensi dapat dibuat secara manual dengan enkripsi:

```bash
sudo cryptsetup luksFormat --type luks2 /dev/sdb1
sudo cryptsetup open /dev/sdb1 persistence
sudo mkfs.ext4 -L persistence /dev/mapper/persistence
sudo mkdir -p /mnt/persistence
sudo mount /dev/mapper/persistence /mnt/persistence
echo '/ union' | sudo tee /mnt/persistence/persistence.conf
sudo umount /mnt/persistence
```

Partisi yang terenkripsi tidak dikenali otomatis saat boot karena kunci
harus dibuka lebih dahulu. Gunakan `arashios-persistence verify` setelah
membuka kunci secara manual.

## 6. Pemeriksaan

```bash
arashios-persistence status
arashios-persistence list
```

## 7. Batasan saat ini

1. Persistensi belum diuji pada image ISO karena image belum dibangun.
2. Pemeriksaan otomatis label partisi saat boot berasal dari paket live-boot
   Debian dan belum diverifikasi pada ArashiOS.
3. Union mount dengan overlayfs perlu diverifikasi pada kernel Debian 12.
