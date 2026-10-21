# Architecture Decision Records

Dokumen ini mencatat keputusan arsitektur yang mengikat proyek. Setiap ADR memiliki status, konteks, keputusan, konsekuensi, dan alternatif yang ditolak.

| ADR | Judul | Status |
|---|---|---|
| 001 | Debian 12 bookworm sebagai basis | Accepted |
| 002 | live-build dan ISO hybrid | Accepted |
| 003 | Tiga edisi desktop | Accepted |
| 004 | Vendoring tool non-Debian | Accepted |
| 005 | Calamares sebagai installer | Accepted |
| 006 | Design system Kage | Accepted |
| 007 | Skema versi dan nama ISO | Accepted |
| 008 | Tanpa telemetry secara default | Accepted |
| 009 | systemd sebagai init | Accepted |
| 010 | Podman rootless sebagai default | Accepted |
| 011 | Neovim dan VSCodium | Accepted |
| 012 | Cakupan legacy i386 | Accepted |

## Format

Setiap ADR baru memakai template:

```markdown
# ADR-NNN: Judul

- Status: Proposed | Accepted | Superseded | Rejected
- Tanggal: YYYY-MM-DD
- Pengganti: ADR-NNN atau kosong

## Konteks
## Keputusan
## Konsekuensi
## Alternatif yang ditolak
```

ADR yang sudah Accepted tidak diubah isinya. Perubahan dilakukan dengan ADR baru yang menyatakan supersede.
