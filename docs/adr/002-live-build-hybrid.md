# ADR-002: live-build dan ISO hybrid

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

ArashiOS memerlukan pipeline build yang dapat direproduksi, mendukung boot BIOS dan UEFI dari satu artefak, serta memakai toolchain yang dipelihara oleh Debian.

## Keputusan

Pipeline utama memakai live-build dengan `--binary-images iso-hybrid`, squashfs, dan bootloader `syslinux` untuk BIOS serta `grub-efi` untuk UEFI pada amd64 dan i386. arm64 memakai `grub-efi` saja. Konfigurasi dibagi menjadi lapisan `config/common` dan overlay `config/editions/<edition>`.

## Konsekuensi

1. Build host membutuhkan live-build, debootstrap, xorriso, squashfs-tools, syslinux, GRUB EFI, mtools, dan dosfstools.
2. Satu ISO dapat ditulis ke USB dan dipakai pada firmware BIOS maupun UEFI.
3. label ISO dan metadata dapat dikustomisasi.
4. live-build menghasilkan berkas antara yang besar, sehingga build membutuhkan ruang disk dan waktu.
5. Perubahan konfigurasi harus diuji pada kedua mode firmware.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| debos | Kurang matang untuk kombinasi hybrid multi-boot dan overlay edisi |
| mkosi | Berorientasi image sistem, bukan live ISO interaktif |
| Skrip build kustom | Biaya pemeliharaan tinggi dan risiko regresi boot |
| Kali live-build fork | Ketergantungan pada repositori dan kebijakan pihak lain |
