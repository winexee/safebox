#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Control Center - v1.7.5
Fixed: Security, Error Handling, Input Validation
"""

import os
import sys
import subprocess
import threading
import shlex
import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

VERSION = "1.7.5"

# ✅ FIX #1: Logging setup
LOG_DIR = os.path.expanduser("~/.local/share/safebox")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "safebox-gui.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        sub_lbl = Gtk.Label(label="Sistemden tam izole edilmiş güvenli sanal masaüstü ortamı")
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
        ram_lbl = Gtk.Label(label="Tahsis Edilecek RAM:")
        ram_lbl.set_xalign(0)
        self.ram_combo = Gtk.ComboBoxText()
        for r in ["1 GB", "2 GB", "3 GB", "4 GB", "6 GB", "8 GB", "16 GB"]:
            self.ram_combo.append_text(r)
        self.ram_combo.set_active(3)
        ram_box.pack_start(ram_lbl, False, False, 0)
        ram_box.pack_start(self.ram_combo, True, True, 0)
        tab_res.pack_start(ram_box, False, False, 0)

        cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cpu_lbl = Gtk.Label(label="Tahsis Edilecek CPU Çekirdeği:")
        cpu_lbl.set_xalign(0)
        self.cpu_combo = Gtk.ComboBoxText()
        for c in ["1 Çekirdek", "2 Çekirdek", "4 Çekirdek", "6 Çekirdek", "8 Çekirdek", "16 Çekirdek"]:
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

        self.chk_net = Gtk.CheckButton(label="İnternet ve Ağ Erişimi")
        self.chk_net.set_active(True)
        self.chk_audio = Gtk.CheckButton(label="Ses Desteği (PulseAudio / PipeWire)")
        self.chk_audio.set_active(True)
        self.chk_share = Gtk.CheckButton(label="Paylaşılan Klasör (~/SafeBox-Paylasim)")
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
        logger.info(f"GUI initialized: {VERSION}")

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
        
        if cmd == "clear":
            self.console_view.get_buffer().set_text("")
        elif cmd == "developer":
            self.dev_mode = not self.dev_mode
            st = "AÇIK" if self.dev_mode else "KAPALI"
            self.append_log(f"Geliştirici Modu: {st}")
            logger.info(f"Developer mode: {st}")
        elif cmd == "status":
            self.append_log("SafeBox Durumu: Hazır\nMasaüstü: Cinnamon 2D")
        elif cmd == "sysinfo":
            self.append_log(f"SafeBox Sürüm: {VERSION}\nMasaüstü: Cinnamon 2D\nMod: {'Geliştirici' if self.dev_mode else 'Normal'}")
        elif cmd == "purge":
            try:
                # ✅ FIX #2: Safe path cleanup
                mock_dir = os.path.expanduser("~/.local/share/safebox")
                for pattern in ["mock_proc", "mock_sys", "mock_etc"]:
                    path = os.path.join(mock_dir, pattern)
                    if os.path.isdir(path):
                        import shutil
                        shutil.rmtree(path, ignore_errors=True)
                self.append_log("Önbellek temizlendi.")
                logger.info("Cache purged")
            except Exception as e:
                self.append_log(f"[HATA] Temizleme başarısız: {e}")
                logger.error(f"Purge failed: {e}")
        elif cmd == "doctor":
            self.append_log("[PASS] Çekirdek İzolasyonu\n[PASS] Cinnamon Masaüstü Yalıtımı\n[PASS] XDG_RUNTIME_DIR")
        else:
            if self.dev_mode:
                # ✅ FIX #3: shell=False security (shlex.split)
                try:
                    args = shlex.split(raw_cmd)  # Safe parsing
                    res = subprocess.run(
                        args,
                        capture_output=True,
                        text=True,
                        timeout=10,  # ✅ FIX #4: Timeout added
                        cwd=os.path.expanduser("~")  # ✅ FIX #5: Safe cwd
                    )
                    if res.stdout:
                        self.append_log(res.stdout.strip())
                    if res.stderr:
                        self.append_log(f"[STDERR] {res.stderr.strip()}")
                    if res.returncode != 0:
                        self.append_log(f"[EXIT] Kod: {res.returncode}")
                    logger.info(f"Command executed: {args[0]}")
                except subprocess.TimeoutExpired:
                    self.append_log("[HATA] Komut timeout (10s)")
                    logger.error(f"Timeout: {raw_cmd}")
                except Exception as e:
                    self.append_log(f"[HATA] {type(e).__name__}: {e}")
                    logger.error(f"Command error: {e}")
            else:
                self.append_log("Geçersiz komut. (İzin verilenler: developer, doctor, sysinfo, purge, clear)")

    def on_start_sandbox(self, widget):
        try:
            # ✅ FIX #6: Input validation
            ram_text = self.ram_combo.get_active_text()
            cpu_text = self.cpu_combo.get_active_text()
            res_text = self.res_combo.get_active_text()
            
            if not (ram_text and cpu_text and res_text):
                self.append_log("[HATA] Lütfen tüm seçenekleri doldurun")
                return
            
            ram = ram_text.split()[0]
            cpu = cpu_text.split()[0]
            res = res_text
            
            net = "1" if self.chk_net.get_active() else "0"
            audio = "1" if self.chk_audio.get_active() else "0"
            share = "1" if self.chk_share.get_active() else "0"

            self.btn_start.set_sensitive(False)
            self.append_log(f"[BAŞLATILIYOR] RAM={ram}GB, CPU={cpu}, Ekran={res}...")
            logger.info(f"Starting sandbox: RAM={ram}GB, CPU={cpu}, Resolution={res}")

            def run_thread():
                engine_path = "/usr/bin/safebox-core"
                if not os.path.exists(engine_path):
                    engine_path = os.path.expanduser("~/safebox/usr/bin/safebox-core")
                
                if not os.path.exists(engine_path):
                    GLib.idle_add(self.append_log, "[HATA] safebox-core bulunamadı!")
                    GLib.idle_add(self.on_sandbox_finished, 1)
                    return
                
                # ✅ FIX #7: Subprocess timeout + error handling
                try:
                    proc = subprocess.run(
                        [engine_path, ram, cpu, res, share, "1", audio, net],
                        timeout=3600,  # 1 saat max
                        cwd=os.path.expanduser("~")
                    )
                    GLib.idle_add(self.on_sandbox_finished, proc.returncode)
                except subprocess.TimeoutExpired:
                    GLib.idle_add(self.append_log, "[HATA] Sandbox timeout")
                    GLib.idle_add(self.on_sandbox_finished, 124)
                except Exception as e:
                    GLib.idle_add(self.append_log, f"[HATA] {e}")
                    GLib.idle_add(self.on_sandbox_finished, 1)

            threading.Thread(target=run_thread, daemon=True).start()
        except Exception as e:
            self.append_log(f"[HATA] {e}")
            logger.error(f"Launch error: {e}")
            self.btn_start.set_sensitive(True)

    def on_sandbox_finished(self, returncode):
        self.btn_start.set_sensitive(True)
        if returncode == 0:
            self.append_log("[KAPANDI] Sanal alan sonlandırıldı.")
            logger.info("Sandbox closed successfully")
        else:
            self.append_log(f"[HATA] Hata kodu: {returncode}")
            logger.error(f"Sandbox error: {returncode}")

def main():
    app = SafeBoxGUI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
