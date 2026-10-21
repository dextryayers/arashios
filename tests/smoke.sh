#!/usr/bin/env bash
# ArashiOS smoke test. Run inside the live session or an installed system.
set -uo pipefail

export PATH="$PATH:/usr/sbin:/sbin"

PASS=0
FAIL=0

pass() {
    printf 'PASS  %s\n' "$1"
    PASS=$((PASS + 1))
}

fail() {
    printf 'FAIL  %s\n' "$1"
    FAIL=$((FAIL + 1))
}

check_cmd() {
    if command -v "$1" >/dev/null 2>&1; then
        pass "command $1"
    else
        fail "command $1"
    fi
}

check_file() {
    if [ -f "$1" ]; then
        pass "file $1"
    else
        fail "file $1"
    fi
}

check_exec() {
    if [ -x "$1" ]; then
        pass "executable $1"
    else
        fail "executable $1"
    fi
}

check_grep() {
    local pattern="$1"
    local file="$2"
    local label="$3"
    if grep -q "$pattern" "$file" 2>/dev/null; then
        pass "$label"
    else
        fail "$label"
    fi
}

check_sysctl() {
    local key="$1"
    local expected="$2"
    local actual
    actual="$(sysctl -n "$key" 2>/dev/null || printf 'missing')"
    if [ "$actual" = "$expected" ]; then
        pass "sysctl $key=$expected"
    else
        fail "sysctl $key=$expected (aktual: $actual)"
    fi
}

printf 'ArashiOS smoke test\n\n'
if [ ! -f /etc/arashios/arch ]; then
    printf 'ERROR: jalankan smoke test di dalam sesi live atau sistem ArashiOS terpasang.\n' >&2
    exit 2
fi

if [ "$(id -u)" -eq 0 ]; then
    printf 'WARN  jalankan sebagai user arashi agar pemeriksaan Podman rootless valid.\n\n'
fi

ARCH="$(cat /etc/arashios/arch 2>/dev/null || printf 'unknown')"
EDITION="$(cat /etc/arashios/edition 2>/dev/null || printf 'unknown')"
VERSION="$(cat /etc/arashios/version 2>/dev/null || printf 'unknown')"

printf 'Identitas sistem:\n'
check_file /etc/os-release
check_grep '^ID=arashios$' /etc/os-release 'os-release ID=arashios'
check_grep '^ID_LIKE=debian$' /etc/os-release 'os-release ID_LIKE=debian'
case "$VERSION" in
    V[0-9]*.[0-9][0-9].[0-9][0-9]) pass "version $VERSION" ;;
    *) fail "version tidak valid: $VERSION" ;;
esac
case "$EDITION" in
    cinnamon|xfce|lxqt) pass "edition $EDITION" ;;
    *) fail "edition tidak valid: $EDITION" ;;
esac
case "$ARCH" in
    amd64|arm64|i386) pass "arch $ARCH" ;;
    *) fail "arch tidak valid: $ARCH" ;;
esac
check_file /etc/arashios/build-info

printf '\nBranding dan tema:\n'
for wallpaper in kage-sumi kage-shuriken kage-bamboo kage-washi kage-storm; do
    check_file "/usr/share/backgrounds/arashios/$wallpaper.png"
done
check_file /usr/share/icons/hicolor/scalable/apps/arashios.svg
check_file /usr/share/icons/hicolor/256x256/apps/arashios.png
check_file /usr/share/grub/themes/arashios/theme.txt
check_file /usr/share/grub/themes/arashios/background.png
check_file /usr/share/plymouth/themes/arashios/arashios.plymouth
check_file /usr/share/plymouth/themes/arashios/arashios.script
check_file /usr/share/plymouth/themes/arashios/logo.png
check_file /usr/share/plymouth/themes/arashios/progress_box.png
check_file /usr/share/plymouth/themes/arashios/progress_bar.png
check_grep 'SetBootProgressFunction' /usr/share/plymouth/themes/arashios/arashios.script 'progress Plymouth'
check_file /usr/share/arashios/theme/kage.qss
check_file /usr/share/arashios/theme/tokens.css
check_file /usr/share/arashios/theme/theme-manifest.json
check_file /usr/share/themes/ArashiKage/index.theme
check_file /usr/share/themes/ArashiKage/gtk-3.0/gtk.css
check_file /usr/share/themes/ArashiKage/gtk-4.0/gtk.css
check_file /usr/share/themes/ArashiKage-HC/index.theme
check_file /usr/share/Kvantum/ArashiKage/ArashiKage.kvconfig
check_exec /usr/local/bin/arashios-wallpaper
check_exec /usr/local/bin/arashios-accessibility
check_exec /usr/local/bin/kage-contrast
check_file /etc/xdg/autostart/arashios-wallpaper.desktop
check_grep '^gtk-theme-name=ArashiKage$' /etc/gtk-3.0/settings.ini 'tema GTK3 ArashiKage'
check_grep '^gtk-icon-theme-name=Papirus-Dark$' /etc/gtk-3.0/settings.ini 'ikon Papirus-Dark'
check_grep '^gtk-cursor-theme-name=Bibata-Modern-Classic$' /etc/gtk-3.0/settings.ini 'kursor Bibata'
check_grep '^gtk-theme-name = "ArashiKage"$' /etc/gtk-2.0/gtkrc 'tema GTK2 ArashiKage'
check_grep 'ArashiKage/gtk-4.0/gtk.css' /etc/xdg/gtk-4.0/gtk.css 'import GTK4 XDG'
check_grep '^theme-name = ArashiKage$' /etc/lightdm/lightdm-gtk-greeter.conf.d/50-arashios.conf 'tema LightDM ArashiKage'
check_grep '^background = /usr/share/backgrounds/arashios/kage-sumi.png$' /etc/lightdm/lightdm-gtk-greeter.conf.d/50-arashios.conf 'wallpaper LightDM PNG'
if /usr/local/bin/kage-contrast status >/dev/null 2>&1; then
    pass 'status aksesibilitas Kage'
else
    fail 'status aksesibilitas Kage'
fi

printf '\nLayanan dan keamanan:\n'
if systemctl is-active --quiet lightdm 2>/dev/null; then pass 'lightdm aktif'; else fail 'lightdm tidak aktif'; fi
if systemctl is-active --quiet NetworkManager 2>/dev/null; then pass 'NetworkManager aktif'; else fail 'NetworkManager tidak aktif'; fi
if systemctl is-active --quiet ssh 2>/dev/null; then fail 'ssh aktif, seharusnya tidak ada'; else pass 'ssh tidak aktif'; fi
check_grep '^ENABLED=yes$' /etc/ufw/ufw.conf 'UFW enabled'
if /usr/sbin/aa-status --enabled >/dev/null 2>&1; then pass 'AppArmor aktif'; else fail 'AppArmor tidak aktif'; fi
check_sysctl kernel.kptr_restrict 1
check_sysctl kernel.dmesg_restrict 1
check_sysctl kernel.unprivileged_bpf_disabled 2
check_sysctl net.ipv4.conf.all.rp_filter 1
check_sysctl net.ipv4.conf.default.rp_filter 1
check_sysctl net.ipv4.tcp_syncookies 1
check_sysctl net.ipv6.conf.all.accept_redirects 0
check_sysctl net.ipv6.conf.all.accept_ra 0

if grep -R -i -q 'kali' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null; then
    fail 'repository Kali ditemukan'
else
    pass 'tidak ada repository Kali'
fi

printf '\nLocale dan waktu:\n'
if locale -a 2>/dev/null | grep -qi '^en_US.utf8$'; then pass 'locale en_US.UTF-8'; else fail 'locale en_US.UTF-8 tidak tersedia'; fi
if [ "$(cat /etc/timezone 2>/dev/null)" = 'Etc/UTC' ]; then pass 'timezone Etc/UTC'; else fail 'timezone bukan Etc/UTC'; fi

printf '\nTool keamanan:\n'
for tool in nmap masscan nikto gobuster ffuf dirsearch wfuzz sqlmap hydra john hashcat \
            aircrack-ng wifite reaver hcxdumptool hcxpcapngtool ettercap bettercap \
            wireshark tshark tcpdump mitmproxy binwalk foremost fls exiftool steghide \
            ddrescue dcfldd guymager podman buildah skopeo kubectl ansible; do
    check_cmd "$tool"
done

printf '\nTool coding:\n'
for tool in gcc g++ make cmake ninja meson pkg-config gdb strace \
            python3 pip3 pipx go git nvim tmux zsh fzf jq yq http sqlite3 \
            psql mariadb redis-cli; do
    check_cmd "$tool"
done

case "$ARCH" in
    amd64|i386) check_cmd ltrace ;;
    *) printf '\nTool debug ltrace dilewati untuk %s.\n' "$ARCH" ;;
esac

case "$ARCH" in
    amd64|arm64)
        printf '\nTool coding modern (%s):\n' "$ARCH"
        for tool in clang clang-format shellcheck rustc cargo node npm java php ruby lua5.4 gh rg fd bat exa zoxide direnv; do
            check_cmd "$tool"
        done
        ;;
    *)
        printf '\nTool coding modern dilewati untuk %s.\n' "$ARCH"
        ;;
esac

if [ "$ARCH" = "amd64" ]; then
    printf '\nLab virtual amd64:\n'
    check_cmd qemu-system-x86_64
    check_cmd qemu-img
fi

printf '\nAplikasi harian:\n'
for tool in firefox-esr thunderbird libreoffice vlc gimp inkscape evince \
            file-roller flameshot keepassxc timeshift gparted remmina filezilla qbittorrent; do
    check_cmd "$tool"
done
check_cmd cupsd
check_cmd system-config-printer

printf '\nDesktop dan sesi:\n'
case "$EDITION" in
    cinnamon)
        check_cmd cinnamon
        check_cmd nemo
        check_cmd gnome-terminal
        check_cmd gedit
        check_cmd eog
        check_file /usr/share/themes/ArashiKage/cinnamon/cinnamon.css
        check_grep "name='ArashiKage'" /etc/dconf/db/local.d/00-arashios 'tema Cinnamon ArashiKage'
        check_grep "visible-name='Kage'" /etc/dconf/db/local.d/00-arashios 'profil GNOME Terminal Kage'
        ;;
    xfce)
        check_cmd xfce4-session
        check_cmd xfce4-terminal
        check_cmd thunar
        check_cmd mousepad
        check_cmd ristretto
        check_file /usr/share/themes/ArashiKage/xfwm4/themerc
        check_grep 'value="ArashiKage"' /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml 'tema XFCE ArashiKage'
        ;;
    lxqt)
        check_cmd lxqt-session
        check_cmd qterminal
        check_cmd pcmanfm-qt
        check_cmd featherpad
        check_cmd lximage-qt
        check_cmd openbox
        check_file /usr/share/themes/ArashiKage/openbox-3/themerc
        check_grep '^theme=ArashiKage$' /etc/xdg/lxqt/lxqt.conf 'tema LXQt ArashiKage'
        ;;
esac
check_grep '^autologin-user=arashi$' /etc/lightdm/lightdm.conf.d/50-arashios.conf 'autologin live user'
if [ "$(getent passwd arashi | cut -d: -f7)" = "/usr/bin/zsh" ]; then
    pass 'shell live user zsh'
else
    fail 'shell live user bukan zsh'
fi
check_file /etc/skel/.zshrc
check_file /etc/skel/.config/nvim/init.lua
check_file /etc/skel/.config/starship.toml

printf '\nContainer rootless:\n'
if command -v podman >/dev/null 2>&1; then
    if podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null | grep -qx 'true'; then
        pass 'Podman rootless'
    else
        fail 'Podman bukan rootless'
    fi
    if podman unshare true >/dev/null 2>&1; then
        pass 'Podman user namespace'
    else
        fail 'Podman user namespace gagal'
    fi
else
    fail 'Podman tidak tersedia'
fi

printf '\nRingkasan: %s lulus, %s gagal.\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
