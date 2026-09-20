import re

with open("usr/bin/safebox-setup", "r") as f:
    content = f.read()

old_verify = """# RootFS bileşenlerini doğrulama
print_info "Cinnamon bileşenleri doğrulanıyor..."
MISSING_BIN=""
for bin in cinnamon cinnamon-session nemo gnome-terminal gnome-system-monitor gedit epiphany-browser dbus-daemon; do
    if [ ! -f "$ROOTFS_TMP/usr/bin/$bin" ] && [ ! -f "$ROOTFS_TMP/bin/$bin" ]; then
        MISSING_BIN="$MISSING_BIN $bin"
    fi
done

if [ -n "$MISSING_BIN" ]; then
    print_error "Eksik bileşenler tespit edildi: $MISSING_BIN"
    print_error "Kurulum başarısız oldu!"
    exit 1
fi
print_ok "Tüm Cinnamon bileşenleri başarıyla kuruldu."
"""

new_verify = """# RootFS bileşenlerini doğrulama
print_info "Cinnamon bileşenleri doğrulanıyor..."
MISSING_BIN=""
for bin in cinnamon cinnamon-session nemo gnome-terminal gnome-system-monitor gedit epiphany-browser dbus-daemon; do
    if [ ! -f "$ROOTFS_TMP/usr/bin/$bin" ] && [ ! -f "$ROOTFS_TMP/bin/$bin" ]; then
        MISSING_BIN="$MISSING_BIN $bin"
    fi
done

if [ -n "$MISSING_BIN" ]; then
    print_error "Eksik bileşenler tespit edildi: $MISSING_BIN"
    print_error "Kurulum başarısız oldu!"
    exit 1
fi

# Gerçek çalışma testleri (version sorgusu)
chroot "$ROOTFS_TMP" cinnamon-session --version > /dev/null 2>&1 || { print_error "cinnamon-session çalıştırılamıyor!"; exit 1; }
chroot "$ROOTFS_TMP" cinnamon --version > /dev/null 2>&1 || { print_error "cinnamon çalıştırılamıyor!"; exit 1; }
chroot "$ROOTFS_TMP" nemo --version > /dev/null 2>&1 || { print_error "nemo çalıştırılamıyor!"; exit 1; }

print_ok "Tüm Cinnamon bileşenleri başarıyla kuruldu ve çalıştırılabilir durumda."
"""
content = content.replace(old_verify, new_verify)

with open("usr/bin/safebox-setup", "w") as f:
    f.write(content)
