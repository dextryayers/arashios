# Secure Boot

Secure Boot belum didukung pada rilis v1. Fitur ini dijadwalkan pada
pasca v1.

## 1. Komponen

1. Shim yang ditandatangani.
2. MOK untuk kunci kustom.
3. Kernel yang ditandatangani.
4. GRUB yang ditandatangani.

## 2. Alur

1. Boot melalui shim.
2. Shim memverifikasi GRUB.
3. GRUB memverifikasi kernel.
4. Pengguna dapat mendaftarkan MOK kustom.

## 3. Konfigurasi

Berkas konfigurasi berada di `config/secureboot/`. Kebijakan signing
terdokumentasi di `config/secureboot/policy.md`.

## 4. Verifikasi

`scripts/verify-secureboot.sh` memeriksa tanda tangan binary dan
konfigurasi MOK.

## 5. Catatan

Secure Boot memerlukan kunci yang terpisah dari kunci rilis. Kunci
disimpan pada media offline.
