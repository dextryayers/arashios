# Container ArashiOS

Dokumen ini menjelaskan kebijakan container, template pengembangan, dan lab
container yang disediakan ArashiOS.

## 1. Kebijakan

1. Podman rootless adalah default. Docker tidak pernah berjalan otomatis.
2. Container tidak memakai mode privileged.
3. Container memakai jaringan bridge dan tidak mendapat akses jaringan host.
4. Image lab dikunci dengan digest. Tag `latest` ditolak.
5. Image tidak dibundel dalam image ISO. Image ditarik saat dibutuhkan.
6. Template container memakai image dasar dengan digest terkunci.
7. `policy.json` menolak registry yang tidak dikenal.

## 2. Konfigurasi sistem

| Berkas | Isi |
|---|---|
| `/etc/containers/containers.conf` | Default engine, runtime crun, batas PID |
| `/etc/containers/containers.conf.d/90-arashios.conf` | Kebijakan user namespace dan PID |
| `/etc/containers/registries.conf` | Short name enforcing, registry docker.io |
| `/etc/containers/policy.json` | Registry lain ditolak |
| `/etc/skel/.config/containers/containers.conf` | Preferensi pengguna rootless |

Pemetaan user untuk container rootless memakai `/etc/subuid` dan
`/etc/subgid` yang sudah diisi oleh image.

## 3. Diagnosa

```bash
arashios-container doctor --json
```

Pemeriksaan meliputi keberadaan Podman, status rootless, `newuidmap`,
`newgidmap`, isi `/etc/subuid` dan `/etc/subgid`, versi cgroup, dan
kehadiran `fuse-overlayfs`.

## 4. Template pengembangan

```bash
arashios-container list
arashios-container build python --tag arashios/dev-python:local
arashios-container run python --project ~/proyek
```

| Template | Image dasar | Digest |
|---|---|---|
| base | debian 12 slim | dikunci |
| python | python 3.11 slim | dikunci |
| go | golang 1.23 bookworm | dikunci |
| rust | rust 1.83 bookworm | dikunci |
| node | node 22 bookworm slim | dikunci |
| security | debian 12 slim | dikunci |

Semua template membuat user `arashi` dengan uid 1000 dan menjalankan
container dari direktori proyek.

## 5. Lab container

```bash
arashios-lab list
arashios-lab info dvwa
arashios-lab plan dvwa
arashios-lab pull dvwa
arashios-lab run dvwa
```

| Lab | Image | Status | Risiko |
|---|---|---|---|
| dvwa | docker.io/vulnerables/web-dvwa | digest terkunci | medium |
| juice-shop | docker.io/juice-shop/juice-shop | digest belum terkunci | medium |
| debian-base | docker.io/library/debian | digest terkunci | low |
| kali-rolling | docker.io/kalilinux/kali-rolling | digest terkunci | high |

Lab dengan risiko tinggi memuat tool offensive dan command and control.
Lab tersebut hanya dipakai pada sistem milik sendiri.

Image tanpa digest ditolak oleh `arashios-lab`. Initializer digest dilakukan
dengan mengambil header registry:

```bash
curl -fsSI -H "Accept: application/vnd.oci.image.index.v1+json" \
  https://registry-1.docker.io/v2/library/debian/manifests/12-slim
```

## 6. Pemeriksaan

```bash
python3 scripts/check-toolstack.py
./tests/toolstack.sh
```

## 7. Batasan saat ini

1. Host pengembangan tidak memasang Podman sehingga diagnosis container
   menandai masalah.
2. Lab image belum pernah ditarik pada host ini.
3. Image juice-shop belum memiliki digest dan ditolak sampai digest tersedia.
4. Perilaku cgroup dan fuse-overlayfs harus diuji ulang pada image bookworm.
