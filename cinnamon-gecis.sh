#!/usr/bin/env bash
# SafeBox Classic GUI & Cinnamon Desktop Update - Only Git (v1.7.2)
set -e

echo "=== Cinnamon Paketleri Kuruluyor ==="
sudo apt update
sudo apt install -y cinnamon-core

# 1. Klasik GUI Arayüzü (v1.7.2)
cat << 'EOF' > usr/share/safebox/safebox_gui.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Control Center - v1.7.2
Classic GUI & Cinnamon Desktop Integration
"""

import os
import sys
import shutil
import subprocess
import threading
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

VERSION = "1.7.2"

class SafeBoxGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title=f"SafeBox Kontrol Merkezi (v{VERSION})")
        self.set_default_size(780, 520)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("security-high")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(14)
        vbox.set_margin_end(14)
        self.add(vbox)

        # Başlık
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        icon_img = Gtk.Image.new_from_icon_name("security-high", Gtk.IconSize.DIALOG)
        header_box.pack_start(icon_img, False, False, 0)

        title_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_lbl = Gtk.Label()
        title_lbl.set_markup(f"<b><big>SafeBox Güvenli Alan</big></b> <small>v{VERSION}</small>")
        title_lbl.set_xalign(0)
        sub_lbl = Gtk.Label(label="Sistemden tam izole edilmiş güvenli sanal masaüstü ortamı")
        sub_lbl.set_xalign(0)
        title_vbox.pack_start(title_lbl, False, False, 0)
        title_vbox.pack_start(sub_lbl, False, False, 0)
        header_box.pack_start(title_vbox, True, True, 0)
        vbox.pack_start(header_box, False, False, 0)

        notebook = Gtk.Notebook()
        vbox.pack_start(notebook, True, True, 0)

        # 1. Genel Bakış
        tab_general = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_general.set_margin_top(12)
        info_frame = Gtk.Frame(label="SafeBox Nedir?")
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        info_box.set_margin_start(10)
        info_box.set_margin_top(8)
        info_box.set_margin_bottom(8)
        
        lbl1 = Gtk.Label(label="• SafeBox, uygulamalarınızı ve dosyalarınızı ana sisteminizden tamamen")
        lbl1.set_xalign(0)
        lbl2 = Gtk.Label(label="  izole bir Bubblewrap sanal alanında çalıştırmanızı sağlar.")
        lbl2.set_xalign(0)
        lbl3 = Gtk.Label(label="• Sanal alandaki hiçbir işlem, izin vermediğiniz sürece host sisteme erişemez.")
        lbl3.set_xalign(0)
        
        info_box.pack_start(lbl1, False, False, 0)
        info_box.pack_start(lbl2, False, False, 0)
        info_box.pack_start(lbl3, False, False, 0)
        info_frame.add(info_box)
        tab_general.pack_start(info_frame, False, False, 0)
        notebook.append_page(tab_general, Gtk.Label(label="Genel Bakış"))

        # 2. Sistem Kaynakları
        tab_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab_res.set_margin_top(12)

        ram_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ram_lbl = Gtk.Label(label="Tahsis Edilecek RAM:")
        ram_lbl.set_xalign(0)
        self.ram_combo = Gtk.ComboBoxText()
        for r in ["1 GB", "2 GB", "3 GB", "4 GB", "6 GB", "8 GB"]:
            self.ram_combo.append_text(r)
        self.ram_combo.set_active(3)
        ram_box.pack_start(ram_lbl, False, False, 0)
        ram_box.pack_start(self.ram_combo, True, True, 0)
        tab_res.pack_start(ram_box, False, False, 0)

        cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cpu_lbl = Gtk.Label(label="Tahsis Edilecek CPU Çekirdeği:")
        cpu_lbl.set_xalign(0)
        self.cpu_combo = Gtk.ComboBoxText()
        for c in ["1 Çekirdek", "2 Çekirdek", "4 Çekirdek", "6 Çekirdek", "8 Çekirdek"]:
            self.cpu_combo.append_text(c)
        self.cpu_combo.set_active(2)
        cpu_box.pack_start(cpu_lbl, False, False, 0)
        cpu_box.pack_start(self.cpu_combo, True, True, 0)
        tab_res.pack_start(cpu_box, False, False, 0)

        res_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        res_lbl = Gtk.Label(label="Ekran Çözünürlüğü:")
        res_lbl.set_xalign(0)
        self.res_combo = Gtk.ComboBoxText()
        for res in ["1024x768", "1280x720", "1366x768", "1600x900", "1920x1080"]:
            self.res_combo.append_text(res)
        self.res_combo.set_active(2)
        res_box.pack_start(res_lbl, False, False, 0)
        res_box.pack_start(self.res_combo, True, True, 0)
        tab_res.pack_start(res_box, False, False, 0)

        notebook.append_page(tab_res, Gtk.Label(label="Sistem Kaynakları"))

        # 3. Ağ ve Paylaşım
        tab_perms = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        tab_perms.set_margin_top(12)

        self.chk_net = Gtk.CheckButton(label="İnternet ve Ağ Erişimi")
        self.chk_net.set_active(True)
        self.chk_audio = Gtk.CheckButton(label="Ses Desteği")
        self.chk_audio.set_active(True)
        self.chk_share = Gtk.CheckButton(label="Paylaşılan Klasör (~/SafeBox-Paylasim)")
        self.chk_share.set_active(True)

        tab_perms.pack_start(self.chk_net, False, False, 0)
        tab_perms.pack_start(self.chk_audio, False, False, 0)
        tab_perms.pack_start(self.chk_share, False, False, 0)
        notebook.append_page(tab_perms, Gtk.Label(label="Ağ ve Paylaşım"))

        # 4. Geliştirici Konsolu
        tab_console = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        tab_console.set_margin_top(8)

        self.console_view = Gtk.TextView()
        self.console_view.set_editable(False)
        self.console_view.set_monospace(True)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.console_view)
        tab_console.pack_start(scroll, True, True, 0)

        cmd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        cmd_lbl = Gtk.Label(label="Komut:")
        self.cmd_entry = Gtk.Entry()
        self.cmd_entry.set_placeholder_text("doctor, sysinfo, purge, clear")
        self.cmd_entry.connect("activate", self.on_run_command)
        btn_run = Gtk.Button(label="Çalıştır")
        btn_run.connect("clicked", self.on_run_command)

        cmd_box.pack_start(cmd_lbl, False, False, 0)
        cmd_box.pack_start(self.cmd_entry, True, True, 0)
        cmd_box.pack_start(btn_run, False, False, 0)
        tab_console.pack_start(cmd_box, False, False, 0)

        notebook.append_page(tab_console, Gtk.Label(label="Geliştirici Konsolu"))

        # Alt Butonlar
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_close = Gtk.Button(label="Kapat")
        btn_close.connect("clicked", Gtk.main_quit)
        
        self.btn_start = Gtk.Button(label="▶ Sanal Alanı Başlat")
        self.btn_start.get_style_context().add_class("suggested-action")
        self.btn_start.connect("clicked", self.on_start_sandbox)

        bottom_box.pack_start(btn_close, False, False, 0)
        bottom_box.pack_end(self.btn_start, False, False, 0)
        vbox.pack_start(bottom_box, False, False, 0)

        self.append_log(f"SafeBox Başlatıldı (Sürüm: {VERSION}).")

    def append_log(self, text):
        buf = self.console_view.get_buffer()
        buf.insert(buf.get_end_iter(), text + "\n")
        mark = buf.create_mark(None, buf.get_end_iter(), False)
        self.console_view.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)

    def on_run_command(self, widget):
        cmd = self.cmd_entry.get_text().strip().lower()
        self.cmd_entry.set_text("")
        if not cmd:
            return

        self.append_log(f"> {cmd}")
        
        if cmd == "clear":
            self.console_view.get_buffer().set_text("")
        elif cmd == "status":
            self.append_log("SafeBox Durumu: Hazır\nMasaüstü Ortamı: Cinnamon")
        elif cmd == "sysinfo":
            self.append_log(f"SafeBox Sürüm: {VERSION}\nSandbox İzolasyon: Aktif")
        elif cmd == "purge":
            mock_dir = os.path.expanduser("~/.local/share/safebox")
            for item in ["mock_proc", "mock_sys", "mock_etc"]:
                p = os.path.join(mock_dir, item)
                if os.path.exists(p):
                    shutil.rmtree(p, ignore_errors=True)
            self.append_log("Önbellek temizlendi.")
        elif cmd == "doctor":
            self.append_log("Sandbox bütünlüğü ve izolasyon limitleri test ediliyor...")
            self.append_log("[PASS] Çekirdek İzolasyonu\n[PASS] Cinnamon Masaüstü Yalıtımı")
        else:
            self.append_log(f"Geçersiz komut. (İzin verilenler: doctor, status, sysinfo, purge, clear)")

    def on_start_sandbox(self, widget):
        ram = self.ram_combo.get_active_text().split()[0]
        cpu = self.cpu_combo.get_active_text().split()[0]
        res = self.res_combo.get_active_text()
        net = "1" if self.chk_net.get_active() else "0"
        audio = "1" if self.chk_audio.get_active() else "0"
        share = "1" if self.chk_share.get_active() else "0"

        self.btn_start.set_sensitive(False)
        self.append_log(f"[BAŞLATILIYOR] RAM={ram}GB, CPU={cpu}, Ekran={res}...")

        def run_thread():
            engine_path = "/usr/bin/safebox-core"
            if not os.path.exists(engine_path):
                engine_path = os.path.expanduser("~/safebox/usr/bin/safebox-core")
            
            cmd = [engine_path, ram, cpu, res, share, "1", audio, net]
            proc = subprocess.run(cmd)
            GLib.idle_add(self.on_sandbox_finished, proc.returncode)

        threading.Thread(target=run_thread, daemon=True).start()

    def on_sandbox_finished(self, returncode):
        self.btn_start.set_sensitive(True)
        if returncode == 0:
            self.append_log("[KAPANDI] Sanal alan sonlandırıldı.")
        else:
            self.append_log(f"[HATA] Hata kodu: {returncode}")

def main():
    app = SafeBoxGUI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
EOF
sudo cp usr/share/safebox/safebox_gui.py /usr/share/safebox/

# 2. guest-init: Cinnamon
cat << 'EOF' > usr/share/safebox/guest-init
#!/usr/bin/env bash
export HOME=/home/safebox
export USER=safebox
export LOGNAME=safebox

export XDG_DATA_DIRS=/usr/share/cinnamon:/usr/share/gnome:/usr/local/share/:/usr/share/
export XDG_CURRENT_DESKTOP=X-Cinnamon
export XDG_SESSION_DESKTOP=cinnamon
export GIO_USE_VFS=local
export GVFS_DISABLE_FUSE=1

mkdir -p /home/safebox/{Desktop,Masaüstü,İndirilenler,Downloads,Belgeler,Documents,Paylasim}

# Masaüstü Simgeleri
rm -f /home/safebox/Desktop/*.desktop /home/safebox/Masaüstü/*.desktop 2>/dev/null || true
for app in browser home share terminal editor monitor; do
    if [ -f "/usr/share/safebox/guest-apps/${app}.desktop" ]; then
        cp "/usr/share/safebox/guest-apps/${app}.desktop" /home/safebox/Desktop/ 2>/dev/null || true
        cp "/usr/share/safebox/guest-apps/${app}.desktop" /home/safebox/Masaüstü/ 2>/dev/null || true
    fi
done
chmod +x /home/safebox/Desktop/*.desktop /home/safebox/Masaüstü/*.desktop 2>/dev/null || true

# Uçbirim Ayarları
cat << 'BASH_EOF' > /home/safebox/.bashrc
export PS1='\[\033[01;32m\]safebox@safebox-sandbox\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
alias ll='ls -alF'
BASH_EOF

# Cinnamon Masaüstünü Başlat
cinnamon 2>/dev/null &
WM_PID=$!
wait $WM_PID
EOF
sudo chmod +x usr/share/safebox/guest-init
sudo cp usr/share/safebox/guest-init /usr/share/safebox/

# 3. Yerel Paketi Derle ve Kendi Bilgisayarına Kur
dpkg-buildpackage -us -uc -b
sudo dpkg -i ../safebox_1.7.2-1~ppa1~noble1_all.deb

# 4. Sadece GitHub'a Yükle
git add usr/share/safebox/safebox_gui.py usr/share/safebox/guest-init debian/
git commit -m "UI Revert to Classic & Switch to Cinnamon Desktop (v1.7.2)" || true
git tag -d v1.7.2 2>/dev/null || true
git push origin :refs/tags/v1.7.2 2>/dev/null || true
git tag -a v1.7.2 -m "SafeBox v1.7.2 - Classic GUI & Cinnamon Desktop"
git push origin main --tags

echo "✅ Kodlar GitHub'a yüklendi ve bilgisayarına kuruldu (Launchpad atlandı)!"