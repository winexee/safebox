#!/usr/bin/env bash
set -e

echo "=== Gerekli Tema Paketleri Kontrol Ediliyor ==="
sudo apt-get install -y yaru-theme-gtk yaru-theme-icon

# guest-init: PCManFM ve Tint2'yi Cinnamon Tarzında Giydir
cat << 'EOF' > usr/share/safebox/guest-init
#!/usr/bin/env bash
export HOME=/home/safebox
export USER=safebox
export LOGNAME=safebox

export XDG_DATA_DIRS=/usr/share/ubuntu:/usr/share/gnome:/usr/local/share/:/usr/share/
export GIO_USE_VFS=local
export GVFS_DISABLE_FUSE=1

mkdir -p $HOME/{Desktop,Masaüstü,İndirilenler,Belgeler,Paylasim,Resimler}
mkdir -p $HOME/.config/gtk-3.0
mkdir -p $HOME/.config/pcmanfm/default
mkdir -p $HOME/.config/tint2

# 1. Cinnamon Tarzı Koyu Tema ve Modern Simgeler
cat << 'GTK_EOF' > $HOME/.config/gtk-3.0/settings.ini
[Settings]
gtk-theme-name=Yaru-dark
gtk-icon-theme-name=Yaru
gtk-font-name=Ubuntu 10
gtk-application-prefer-dark-theme=1
GTK_EOF

cat << 'GTK2_EOF' > $HOME/.gtkrc-2.0
gtk-theme-name="Yaru-dark"
gtk-icon-theme-name="Yaru"
gtk-font-name="Ubuntu 10"
GTK2_EOF

# 2. Arka Plan ve Masaüstü Yazı Tipi (Şık Koyu Gri)
cat << 'PCMAN_EOF' > $HOME/.config/pcmanfm/default/desktop.conf
[desktop]
wallpaper_mode=color
desktop_bg=#242424
desktop_shadow=1
fg_color=#ffffff
font=Ubuntu 10
show_wm_menu=0
sort=mtime;ascending;
show_hidden=0
PCMAN_EOF

# 3. Tint2'yi Birebir Cinnamon Görev Çubuğuna Çevir (Kalın alt panel, sağda saat)
cat << 'TINT_EOF' > $HOME/.config/tint2/tint2rc
panel_position = bottom center horizontal
panel_size = 100% 40
panel_margin = 0 0
panel_padding = 4 2 4
panel_background_id = 1
wm_menu = 1
panel_dock = 0
panel_layer = top
font_shadow = 0
taskbar_padding = 4 0 4
taskbar_background_id = 0
taskbar_active_background_id = 2
task_icon_asb = 100 0 0
task_text = 1
task_centered = 1
task_font = Ubuntu 10
task_font_color = #ffffff 100
task_active_font_color = #ffffff 100
systray_padding = 6 2 2
systray_background_id = 0
systray_sort = ascending
systray_icon_size = 24
systray_icon_asb = 100 0 0
clock_font = Ubuntu 10
clock_font_color = #ffffff 100
clock_padding = 10 4
clock_background_id = 0
time1_format = %H:%M
time2_format = %d %b %Y
time1_font = Ubuntu 11
time2_font = Ubuntu 8
background 1
rounded = 0
border_width = 0
background_color = #1e1e1e 90
background 2
rounded = 4
border_width = 0
background_color = #444444 90
TINT_EOF

# Masaüstü Simgelerini Yerleştir
rm -f $HOME/Desktop/*.desktop $HOME/Masaüstü/*.desktop 2>/dev/null || true
for app in browser home share terminal editor monitor; do
    if [ -f "/usr/share/safebox/guest-apps/${app}.desktop" ]; then
        cp "/usr/share/safebox/guest-apps/${app}.desktop" $HOME/Desktop/ 2>/dev/null || true
        cp "/usr/share/safebox/guest-apps/${app}.desktop" $HOME/Masaüstü/ 2>/dev/null || true
    fi
done
chmod +x $HOME/Desktop/*.desktop $HOME/Masaüstü/*.desktop 2>/dev/null || true

# Orijinal hafif ve kararlı bileşenleri temalanmış şekilde başlat
xfwm4 &
pcmanfm --desktop &
tint2 &
wait
EOF

sudo chmod +x usr/share/safebox/guest-init
sudo cp usr/share/safebox/guest-init /usr/share/safebox/

# 3. Yerel Paketi Derle ve Sisteme Kur
dpkg-buildpackage -us -uc -b
sudo dpkg -i ../safebox_1.7.4-1~ppa1~noble1_all.deb

echo "✅ Arayüz temalandırıldı ve yerel bilgisayarına kuruldu. Git'e dokunulmadı!"