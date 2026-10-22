# Hardening ArashiOS

Dokumen ini menjelaskan kontrol keamanan bawaan ArashiOS, cara memverifikasi
kontrol tersebut, dan bukti yang tersimpan untuk setiap rilis.

## 1. Checklist Kontrol

| ID | Kontrol | Nilai bawaan | Verifikasi |
|---|---|---|---|
| H-01 | Firewall | UFW aktif, deny incoming, allow outgoing | `ufw status` |
| H-02 | AppArmor | Aktif | `systemctl is-active apparmor` |
| H-03 | Server SSH | Tidak dipasang, unit dimask | `dpkg -l openssh-server` |
| H-04 | Login root | Dilarang | `/etc/ssh/sshd_config` |
| H-05 | Autologin | Hanya sesi live | `/etc/lightdm/lightdm.conf.d/50-arashios.conf` |
| H-06 | Password default | Tidak ada | `/etc/passwd` |
| H-07 | Update keamanan | unattended-upgrades aktif | `systemctl is-active unattended-upgrades` |
| H-08 | kernel.kptr_restrict | 1 | `sysctl -n kernel.kptr_restrict` |
| H-09 | kernel.dmesg_restrict | 1 | `sysctl -n kernel.dmesg_restrict` |
| H-10 | rp_filter | 1 | `sysctl -n net.ipv4.conf.all.rp_filter` |
| H-11 | Firejail | Tersedia, tidak aktif | `dpkg -l firejail` |
| H-12 | USBGuard | Tidak aktif | `systemctl is-active usbguard` |
| H-13 | Telemetry | Tidak ada | `docs/PRIVACY.md` |
| H-14 | Akun daring | Tidak ada | `docs/PRIVACY.md` |
| H-15 | Remote Flatpak | Tidak ada | `/etc/flatpak/remotes.d` |

## 2. Pemeriksaan

```bash
# Pemeriksaan konfigurasi sumber, tanpa sistem berjalan
python3 scripts/check-hardening.py --config

# Pemeriksaan runtime pada sesi live atau sistem terpasang
python3 scripts/check-hardening.py --runtime --output build/hardening.json
```

Pemeriksaan konfigurasi membaca tree sumber dan dapat dijalankan pada host
build. Pemeriksaan runtime memverifikasi state sistem dan menulis laporan JSON.

## 3. sysctl

Berkas `/etc/sysctl.d/99-arashios-hardening.conf` memuat:

```text
kernel.kptr_restrict = 1
kernel.dmesg_restrict = 1
kernel.unprivileged_bpf_disabled = 2
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.tcp_syncookies = 1
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_ra = 0
```

Nilai `kernel.unprivileged_bpf_disabled = 2` dipakai karena kernel Debian 12
mengatur `CONFIG_BPF_UNPRIV_DEFAULT_OFF`, sehingga knob tidak dapat diturunkan
ke 1 setelah dikunci. Nilai 2 lebih ketat.

## 4. Layanan

| Layanan | State | Catatan |
|---|---|---|
| NetworkManager | aktif | managing jaringan |
| lightdm | aktif | display manager |
| bluetooth | aktif | tidak discoverable secara bawaan |
| avahi-daemon | aktif | penemuan jaringan lokal |
| cups.socket | aktif | printer hanya berjalan saat dibutuhkan |
| sshd | dimask | tidak ada server SSH |
| power-profiles-daemon | dimask | TLP yang mengelola daya |

## 5. Privasi

1. Tidak ada telemetry, analytics, atau crash reporting otomatis.
2. Tidak ada akun daring bawaan.
3. Tidak ada panggilan jaringan saat boot.
4. DNS mengikuti NetworkManager.
5. Flatpak tidak menambahkan remote bawaan.
6. Firefox ESR tidak memakai telemetry bawaan.
7. Tidak ada data pengguna yang dikirim ke proyek.

## 6. Bukti Rilis

| Bukti | Perintah |
|---|---|
| Hardening config | `python3 scripts/check-hardening.py --config` |
| Hardening runtime | `python3 scripts/check-hardening.py --runtime --output build/hardening.json` |
| Kepatuhan | `python3 scripts/check-compliance.py --output build/compliance-report.json` |
| Kerentanan | `./scripts/scan-vulnerabilities.sh --output build/vulnerability-report.json` |

## 7. Batasan saat ini

1. Pemeriksaan runtime belum dijalankan pada image ArashiOS.
2. Audit jaringan pada sesi live bersih belum dilakukan.
3. AppArmor belum diuji dengan profil khusus untuk tool keamanan.
