# ADR-010: Podman rootless sebagai default

- Status: Accepted
- Tanggal: 2026-10-21
- Pengganti: kosong

## Konteks

Alur kerja keamanan dan pengembangan modern membutuhkan container. Docker daemon berjalan sebagai root dan menambah permukaan serangan yang signifikan pada sistem desktop.

## Keputusan

Podman rootless menjadi runtime container default. Buildah dan skopeo disertakan. Docker CLI compatibility disediakan sebagai paket opsional, bukan default. Socket Docker tidak diaktifkan.

## Konsekuensi

1. Container berjalan tanpa daemon root.
2. Beberapa image dan tool membutuhkan penyesuaian.
3. Pengguna harus memahami user namespace.
4. `podman-docker` dapat dipasang manual jika diperlukan.
5. Kubernetes tooling tetap kompatibel melalui API standar.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Docker CE | Daemon root dan repository pihak ketiga |
| containerd tanpa CLI | Kurang ramah untuk alur kerja harian |
| Tanpa container | Menghilangkan kebutuhan utama red team dan coding |
