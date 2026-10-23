# Image ARM SBC

ArashiOS menyediakan image untuk perangkat ARM single board computer.

## 1. Target

1. Raspberry Pi 4.
2. Raspberry Pi 5.
3. Pine64.

## 2. Lingkup

1. Edisi XFCE sebagai default.
2. LXQt sebagai alternatif ringan.
3. Boot UEFI jika didukung perangkat.

## 3. Konfigurasi

Berkas konfigurasi berada di `config/sbc/`. Setiap perangkat memiliki
berkas pengaturan partisi, firmware, dan kernel.

## 4. Build

Gunakan `scripts/build-sbc-image.sh`. Image diuji pada perangkat nyata
sebelum rilis.

## 5. Batasan

1. Cinnamon tidak didukung pada SBC.
2. Beberapa tool Go perlu dibangun dengan `GOARCH=arm64`.
3. Tool yang tidak mendukung arm64 dipindahkan ke T3.
