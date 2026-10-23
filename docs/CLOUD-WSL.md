# Image Cloud dan WSL

ArashiOS menyediakan image cloud dan rootfs WSL pada pasca v1.

## 1. Image Cloud

1. Format qcow2 dan raw.
2. cloud-init untuk konfigurasi awal.
3. Tidak ada akun default.

## 2. Rootfs WSL

1. Rootfs tarball untuk WSL2.
2. Tidak ada systemd by default.
3. Dokumentasi instalasi di `docs/INSTALL.md`.

## 3. Build

Gunakan `scripts/build-cloud-image.sh`. Image diuji pada cloud provider
dan WSL2 sebelum rilis.

## 4. Batasan

1. Secure Boot tidak berlaku pada WSL.
2. Hardware fisik tidak tersedia.
3. GPU passthrough memerlukan konfigurasi tambahan.
