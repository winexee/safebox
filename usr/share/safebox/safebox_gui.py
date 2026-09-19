#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Control Center - v1.7.6
Original Classic UI & Cinnamon Integration
"""

import os
import sys
import subprocess
import shlex
import threading
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

VERSION = "1.7.6"

class SafeBoxGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title=f"SafeBox Kontrol Merkezi (v{VERSION})")
        self.set_default_size(700, 480)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("security-high")

        self.dev_mode = False

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(15)
        vbox.set_margin_bottom(15)
        vbox.set_margin_start(15)
        vbox.set_margin_end(15)
        self.add(vbox)

        # Başlık Alanı
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        icon_img = Gtk.Image.new_from_icon_name("security-high", Gtk.IconSize.DIALOG)
        header_box.pack_start(icon_img, False, False, 0)

        title_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_lbl = Gtk.Label()
        title_lbl.set_markup(f"<b><big>SafeBox Güvenli Alan</big></b> <small>v{VERSION}</small>")
        title_lbl.set_xalign(0)
        sub_lbl = Gtk.Label(label="Sınırlandırılmış (Sandboxed) kontrollü sanal masaüstü ortamı")
        sub_lbl.set_xalign(0)
        title_vbox.pack_start(title_lbl, False, False, 0)
        title_vbox.pack_start(sub_lbl, False, False, 0)
        header_box.pack_start(title_vbox, True, True, 0)
        vbox.pack_start(header_box, False, False, 0)

        # Sekmeler
        notebook = Gtk.Notebook()
        vbox.pack_start(notebook, True, True, 0)

        # 1. Genel Bakış
        tab_general = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_general.set_margin_top(10)
        info_frame = Gtk.Frame(label="Güvenlik Profili")
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        info_box.set_margin_start(10)
        info_box.set_margin_top(8)
        info_box.set_margin_bottom(8)
        
        lbl1 = Gtk.Label(label="• Çekirdek İzolasyonu: Bubblewrap User, PID, UTS, IPC & Mount Namespaces")
        lbl1.set_xalign(0)
        lbl2 = Gtk.Label(label="• Gerçek Donanım Sınırı: Linux cgroup v2 (MemoryMax & CPUQuota)")
        lbl2.set_xalign(0)
        lbl3 = Gtk.Label(label="• Kimlik Yalıtımı: Statik passwd/group/shadow/machine-id ve sahte hostname")
        lbl3.set_xalign(0)
        
        info_box.pack_start(lbl1, False, False, 0)
        info_box.pack_start(lbl2, False, False, 0)
        info_box.pack_start(lbl3, False, False, 0)
        info_frame.add(info_box)
        tab_general.pack_start(info_frame, False, False, 0)
        notebook.append_page(tab_general, Gtk.Label(label="Genel Bakış"))

        # 2. Kaynak ve Ekran
        tab_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab_res.set_margin_top(12)

        ram_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ram_lbl = Gtk.Label(label="Maksimum RAM Sınırı (Cgroup v2):")
        ram_lbl.set_xalign(0)
        self.ram_combo = Gtk.ComboBoxText()
        for r in ["1 GB", "2 GB", "3 GB", "4 GB", "6 GB", "8 GB"]:
            self.ram_combo.append_text(r)
        self.ram_combo.set_active(3)
        ram_box.pack_start(ram_lbl, False, False, 0)
        ram_box.pack_start(self.ram_combo, True, True, 0)
        tab_res.pack_start(ram_box, False, False, 0)

        cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cpu_lbl = Gtk.Label(label="CPU Kullanım Sınırı (Çekirdek Eşdeğeri):")
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

        notebook.append_page(tab_res, Gtk.Label(label="Kaynak ve Ekran"))

        # 3. İzinler ve İzolasyon
        tab_perms = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_perms.set_margin_top(12)

        self.chk_net = Gtk.CheckButton(label="İnternet ve Ağ Erişimi (Ana sistem ağı paylaşılır)")
        self.chk_net.set_active(True)
        self.chk_audio = Gtk.CheckButton(label="Ses Desteği (PulseAudio / PipeWire Soketi)")
        self.chk_audio.set_active(True)
        self.chk_share = Gtk.CheckButton(label="Paylaşılan Klasör (~/SafeBox-Paylasim Köprüsü)")
        self.chk_share.set_active(True)

        tab_perms.pack_start(self.chk_net, False, False, 0)
        tab_perms.pack_start(self.chk_audio, False, False, 0)
        tab_perms.pack_start(self.chk_share, False, False, 0)
        notebook.append_page(tab_perms, Gtk.Label(label="İzinler ve İzolasyon"))

        # 4. Konsol ve Günlük
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
        self.cmd_entry.set_placeholder_text("developer, doctor, sysinfo, purge, clear")
        self.cmd_entry.connect("activate", self.on_run_command)
        btn_run = Gtk.Button(label="Çalıştır")
        btn_run.connect("clicked", self.on_run_command)

        cmd_box.pack_start(cmd_lbl, False, False, 0)
        cmd_box.pack_start(self.cmd_entry, True, True, 0)
        cmd_box.pack_start(btn_run, False, False, 0)
        tab_console.pack_start(cmd_box, False, False, 0)

        notebook.append_page(tab_console, Gtk.Label(label="Konsol ve Günlük"))

        # Butonlar
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_close = Gtk.Button(label="Kapat")
        btn_close.connect("clicked", Gtk.main_quit)
        
        self.btn_start = Gtk.Button(label="▶ Sanal Alanı Başlat")
        self.btn_start.get_style_context().add_class("suggested-action")
        self.btn_start.connect("clicked", self.on_start_sandbox)

        bottom_box.pack_start(btn_close, False, False, 0)
        bottom_box.pack_end(self.btn_start, False, False, 0)
        vbox.pack_start(bottom_box, False, False, 0)

        self.append_log(f"SafeBox Kontrol Merkezi Hazır (Sürüm: {VERSION}).")

    def append_log(self, text):
        buf = self.console_view.get_buffer()
        buf.insert(buf.get_end_iter(), text + "\n")
        mark = buf.create_mark(None, buf.get_end_iter(), False)
        self.console_view.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)

    def on_run_command(self, widget):
        raw_cmd = self.cmd_entry.get_text().strip()
        self.cmd_entry.set_text("")
        if not raw_cmd:
            return

        cmd = raw_cmd.lower()
        self.append_log(f"> {raw_cmd}")
        
        # Izin verilen komutlar (whitelist)
        ALLOWED_DEV_CMDS = {"uname", "whoami", "pwd", "ls", "echo", "date"}
        
        if cmd == "clear":
            self.console_view.get_buffer().set_text("")
        elif cmd == "developer":
            self.dev_mode = not self.dev_mode
            st = "AÇIK" if self.dev_mode else "KAPALI"
            self.append_log(f"Geliştirici Modu: {st}")
            self.append_log("İzin verilen komutlar: uname, whoami, pwd, ls, echo, date")
        elif cmd == "status":
            self.append_log("SafeBox Durumu: Hazır\nMasaüstü: Cinnamon")
        elif cmd == "sysinfo":
            self.append_log(f"SafeBox Sürüm: {VERSION}\nMasaüstü: Cinnamon 2D")
        elif cmd == "purge":
            try:
                import glob

                targets = glob.glob(
                    os.path.expanduser("~/.local/share/safebox/mock_*")
                )

                for target in targets:
                    subprocess.run(
                        ["rm", "-rf", "--", target],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )

                self.append_log(
                    f"Önbellek temizlendi. Öğeler: {len(targets)}"
                )
            except Exception as e:
                self.append_log(f"[HATA] Purge başarısız: {e}")
        elif cmd == "doctor":
            self.append_log("[🔍 SISTEM TESTİ BAŞLANIYOR]")
            tests_passed = 0
            tests_total = 0
            
            # Test 1: RootFS kontrolü
            tests_total += 1
            if os.path.exists("/var/lib/safebox/rootfs/.safebox-rootfs-complete"):
                self.append_log("✓ RootFS: Tam ve eksiksiz kurulu (.safebox-rootfs-complete)")
                tests_passed += 1
            else:
                self.append_log("✗ RootFS: Eksik veya hatalı kurulum (sudo safebox-setup gerekli)")
            
            # Test 2: SafeBox-Core Çalışıyor mu?
            tests_total += 1
            pid_file = "/tmp/safebox-core.pid"
            core_pid = None
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, "r") as f:
                        core_pid = f.read().strip()
                    # PID hala hayatta mı ve safebox-core mu?
                    result = subprocess.run(["ps", "-p", core_pid, "-o", "comm="], capture_output=True, text=True)
                    if "safebox-core" in result.stdout:
                        self.append_log(f"✓ Arka Plan Süreci: safebox-core aktif (PID: {core_pid})")
                        tests_passed += 1
                        
                        # Test 3: Cgroup Limiti
                        tests_total += 1
                        cgroup_res = subprocess.run(["systemctl", "--user", "show", "safebox-app.scope", "--property=MemoryMax,CPUQuota"], capture_output=True, text=True, timeout=2)
                        if "MemoryMax=" in cgroup_res.stdout and "infinity" not in cgroup_res.stdout:
                            self.append_log("✓ Kaynak Sınırları: safebox-app.scope aktif ve limitli")
                            tests_passed += 1
                        else:
                            self.append_log("⚠ Kaynak Sınırları: safebox-app.scope saptanamadı veya limitsiz")
                    else:
                        self.append_log("ℹ Arka Plan Süreci: Çalışan bir SafeBox oturumu yok")
                except Exception as e:
                    self.append_log(f"✗ Arka Plan Kontrolü: {e}")
            else:
                self.append_log("ℹ Arka Plan Süreci: Çalışan bir SafeBox oturumu yok")
            
            # Sonuç
            if tests_total > 0:
                percentage = int((tests_passed / tests_total) * 100)
                self.append_log(f"\n[SONUÇ] {tests_passed}/{tests_total} test geçti")
            else:
                self.append_log("\n[SONUÇ] Test yapılamadı.")
        else:
            if self.dev_mode:
                # Güvenlik: Whitelist kontrol
                cmd_parts = shlex.split(raw_cmd)
                base_cmd = cmd_parts[0] if cmd_parts else ""
                
                if base_cmd not in ALLOWED_DEV_CMDS:
                    self.append_log(f"[HATA] '{base_cmd}' komutuna izin yok!")
                    self.append_log(f"İzin verilen komutlar: {', '.join(ALLOWED_DEV_CMDS)}")
                    return
                
                try:
                    # Shell=False ile argümanları Array olarak geç (GÜVENLI)
                    res = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=5)
                    if res.stdout:
                        self.append_log(res.stdout.strip())
                    if res.stderr:
                        self.append_log(f"[STDERR] {res.stderr.strip()}")
                    if res.returncode != 0:
                        self.append_log(f"[UYARI] Çıkış kodu: {res.returncode}")
                except subprocess.TimeoutExpired:
                    self.append_log("[HATA] Komut zaman aşımına uğradı (5s)")
                except Exception as e:
                    self.append_log(f"[HATA] {e}")
            else:
                self.append_log("Geçersiz komut. (İzin verilenler: developer, doctor, sysinfo, purge, clear)")

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
            
            cmd = [engine_path, ram, cpu, res, share, audio, net]
            proc = subprocess.run(cmd)
            GLib.idle_add(self.on_sandbox_finished, proc.returncode)

        threading.Thread(target=run_thread, daemon=True).start()

    def on_sandbox_finished(self, returncode):
        self.btn_start.set_sensitive(True)
        if returncode == 0:
            self.append_log("[KAPANDI] Sanal alan sonlandırıldı.")
        elif returncode == 105:
            self.append_log("[HATA] RootFS eksik. Kurulum gerekiyor.")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text="SafeBox RootFS Eksik"
            )
            dialog.format_secondary_text(
                "Sanal alanın çalışması için temel dosya sistemi (RootFS) kurulu değil.\n"
                "Otomatik kurulumu başlatmak ister misiniz? (Root yetkisi gerektirebilir)"
            )
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                self.append_log("[BİLGİ] RootFS kurulumu başlatılıyor...")
                def setup_thread():
                    setup_cmd = ["pkexec", "/usr/bin/safebox-setup"]
                    if not os.path.exists("/usr/bin/safebox-setup"):
                        setup_cmd = ["pkexec", os.path.expanduser("~/safebox/usr/bin/safebox-setup")]
                    s_proc = subprocess.run(setup_cmd)
                    if s_proc.returncode == 0:
                        GLib.idle_add(self.append_log, "[BİLGİ] Kurulum başarıyla tamamlandı. Yeniden başlatabilirsiniz.")
                    else:
                        GLib.idle_add(self.append_log, f"[HATA] Kurulum başarısız oldu (Hata kodu: {s_proc.returncode}).")
                threading.Thread(target=setup_thread, daemon=True).start()
        else:
            self.append_log(f"[HATA] Hata kodu: {returncode}")

def main():
    app = SafeBoxGUI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
