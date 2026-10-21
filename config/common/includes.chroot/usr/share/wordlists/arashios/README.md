# ArashiOS wordlists

Koleksi wordlist kecil yang dikurasi untuk pengujian pada sistem yang diizinkan.
Seluruh isi dibuat khusus untuk ArashiOS dan tidak diambil dari dataset pihak
ketiga, sehingga lisensi dan provenance jelas.

| Berkas | Isi | Kegunaan |
|---|---|---|
| `common-paths.txt` | Path web umum | Brute force direktori dan fuzzing path |
| `common-usernames.txt` | Nama pengguna umum | Brute force login |
| `common-passwords.txt` | Password default umum | Brute force login dan audit konfigurasi |
| `common-subdomains.txt` | Subdomain umum | Enumerasi subdomain |
| `common-parameters.txt` | Parameter HTTP umum | Fuzzing parameter |
| `detection-payloads.txt` | String uji non-destruktif | Deteksi kelas kerentanan |

## Pemakaian

```bash
ffuf -u https://target/FUZZ -w /usr/share/wordlists/arashios/common-paths.txt
gobuster dir -u https://target -w /usr/share/wordlists/arashios/common-paths.txt
hydra -L /usr/share/wordlists/arashios/common-usernames.txt \
      -P /usr/share/wordlists/arashios/common-passwords.txt ssh://target
```

## Aturan

1. Gunakan hanya pada sistem yang Anda miliki atau telah mendapat izin tertulis.
2. Jangan memakai wordlist ini untuk membanjiri layanan pihak ketiga.
3. Dataset seklits, rockyou, dan wordlist pihak ketiga lain tidak disertakan.
  _dataset seklits_(https://github.com/danielmiessler/SecLists) diunduh lewat
   Arsenal pada tier T1, dan rockyou hanya lewat tier T2 dengan peringatan.
4. Wordlist ArashiOS diperbarui pada setiap rilis dan checksum selalu dicatat
   di `manifest.json`.

## Lisensi

Isi wordlist berlisensi CC-BY-SA-4.0. Lihat `LICENSE` untuk teks lengkap.
