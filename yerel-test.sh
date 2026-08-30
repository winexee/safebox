#!/usr/bin/env bash
set -e

# 1. guest-init: Cinnamon yerine sorunsuz çalışan orijinal XFCE bileşenlerini geri getir
cat << 'EOF' > usr/share/safebox/guest-init
#!/usr/bin/env bash
export HOME=/home/safebox
export USER=safebox
export LOGNAME=safebox

export XDG_DATA_DIRS=/usr/local/share/:/usr/share/
export GIO_USE_VFS=local
export GVFS_DISABLE_FUSE=1

mkdir -p /home/safebox/{Desktop,Masaüstü,İndirilenler,Belgeler,Paylasim}

# Masaüstü Simgeleri
for app in browser home share terminal editor monitor; do
    if [ -f "/usr/share/safebox/guest-apps/${app}.desktop" ]; then
        cp "/usr/share/safebox/guest-apps/${app}.desktop" /home/safebox/Desktop/ 2>/dev/null || true
        cp "/usr/share/safebox/guest-apps/${app}.desktop" /home/safebox/Masaüstü/ 2>/dev/null || true
    fi
done
chmod +x /home/safebox/Desktop/*.desktop /home/safebox/Masaüstü/*.desktop 2>/dev/null || true

# Orijinal hafif ve kararlı masaüstü başlatıcıları
xfwm4 &
pcmanfm --desktop &
tint2 &
wait
EOF
sudo chmod +x usr/share/safebox/guest-init
sudo cp usr/share/safebox/guest-init /usr/share/safebox/

# 2. Yerel Paketi Derle ve Sadece Sisteme Kur (Git İptal)
dpkg-buildpackage -us -uc -b
sudo dpkg -i ../safebox_1.7.4-1~ppa1~noble1_all.deb

echo "✅ Sistem onarıldı ve SADECE yerel bilgisayarına kuruldu. Git'e dokunulmadı!"