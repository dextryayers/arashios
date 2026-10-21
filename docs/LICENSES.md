# Matriks Lisensi Tool ArashiOS

Dokumen ini dihasilkan dari `tools/catalog.yaml` dengan
`scripts/check-licenses.py --update`. Setiap tool tier 1 yang
dibundel harus mencantumkan lisensi upstream dan sumbernya.

| Tool | Tier | Lisensi | Distribusi | Sumber |
|---|---|---|---|---|
| `amass` | T1 | Apache-2.0 | vendor | https://github.com/owasp-amass/amass.git |
| `certipy` | T1 | GPL-3.0-only | vendor | https://github.com/ly4k/Certipy.git |
| `chisel` | T1 | MIT | vendor | https://github.com/jpillora/chisel.git |
| `commix` | T1 | GPL-2.0-only | vendor | https://github.com/commixproject/commix.git |
| `cutter` | T1 | GPL-2.0-only | vendor | https://github.com/rizinorg/cutter.git |
| `dalfox` | T1 | MIT | vendor | https://github.com/hahwul/dalfox.git |
| `dnsx` | T1 | MIT | vendor | https://github.com/projectdiscovery/dnsx.git |
| `enum4linux-ng` | T1 | GPL-3.0-only | vendor | https://github.com/CiscoCXSecurity/enum4linux-ng.git |
| `evil-winrm` | T1 | GPL-3.0-only | vendor | https://github.com/Hackplayers/evil-winrm.git |
| `exploitdb` | T1 | GPL-2.0-only | vendor | https://github.com/offensive-security/exploitdb.git |
| `fastfetch` | T1 | MIT | vendor | https://github.com/fastfetch-cli/fastfetch.git |
| `feroxbuster` | T1 | MIT | vendor | https://github.com/epi052/feroxbuster.git |
| `frida-tools` | T1 | wxWindows-Licence | vendor | https://github.com/frida/frida.git |
| `gau` | T1 | MIT | vendor | https://github.com/lc/gau.git |
| `gospider` | T1 | MIT | vendor | https://github.com/jaeles-project/gospider.git |
| `hakrawler` | T1 | MIT | vendor | https://github.com/hakluke/hakrawler.git |
| `helm` | T1 | Apache-2.0 | vendor | https://github.com/helm/helm.git |
| `httpx` | T1 | MIT | vendor | https://github.com/projectdiscovery/httpx.git |
| `jadx` | T1 | Apache-2.0 | vendor | https://github.com/skylot/jadx.git |
| `katana` | T1 | MIT | vendor | https://github.com/projectdiscovery/katana.git |
| `kerbrute` | T1 | GPL-3.0-only | vendor | https://github.com/ropnop/kerbrute.git |
| `kismet` | T1 | GPL-3.0-only | vendor | https://github.com/kismetwireless/kismet.git |
| `ldapdomaindump` | T1 | Apache-2.0 | vendor | https://github.com/dirkjanm/ldapdomaindump.git |
| `ligolo-ng` | T1 | MIT | vendor | https://github.com/nicocha30/ligolo-ng.git |
| `metasploit-framework` | T1 | BSD-3-Clause | vendor | https://github.com/rapid7/metasploit-framework.git |
| `naabu` | T1 | MIT | vendor | https://github.com/projectdiscovery/naabu.git |
| `netexec` | T1 | BSD-2-Clause | vendor | https://github.com/Pennyw0rth/NetExec.git |
| `nuclei` | T1 | MIT | vendor | https://github.com/projectdiscovery/nuclei.git |
| `pwndbg` | T1 | MIT | vendor | https://github.com/pwndbg/pwndbg.git |
| `radare2` | T1 | LGPL-3.0-only | vendor | https://github.com/radareorg/radare2.git |
| `responder` | T1 | GPL-3.0-only | vendor | https://github.com/lgandx/Responder.git |
| `rizin` | T1 | LGPL-3.0-only | vendor | https://github.com/rizinorg/rizin.git |
| `seclists-core` | T1 | MIT | vendor | https://github.com/danielmiessler/SecLists.git |
| `subfinder` | T1 | MIT | vendor | https://github.com/projectdiscovery/subfinder.git |
| `termshark` | T1 | MIT | vendor | https://github.com/gcla/termshark.git |
| `trivy` | T1 | Apache-2.0 | vendor | https://github.com/aquasecurity/trivy.git |
| `upx` | T1 | GPL-2.0-only | vendor | https://github.com/upx/upx.git |
| `volatility3` | T1 | VSL | vendor | https://github.com/volatilityfoundation/volatility3.git |
| `waybackurls` | T1 | MIT | vendor | https://github.com/tomnomnom/waybackurls.git |
| `wpscan` | T1 | MIT | vendor | https://github.com/wpscanteam/wpscan.git |
| `zaproxy` | T1 | Apache-2.0 | vendor | https://github.com/zaproxy/zaproxy.git |

## Aturan

1. Tool proprietary tidak pernah masuk image dan hanya tersedia
   lewat tier 2 atau tier 3.
2. Tool GPL menyertakan source code atau tawaran source sesuai
   kewajiban lisensi.
3. Perubahan lisensi upstream dipantau pada setiap rilis dan
   tercatat di CHANGELOG.
4. Wordlist ArashiOS memakai CC-BY-SA-4.0 dan dicatat di NOTICE.
