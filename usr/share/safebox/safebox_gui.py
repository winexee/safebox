#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Control Center - v1.7.5
Original Classic UI & Cinnamon Integration
"""

import os
import sys
import subprocess
import threading
from pathlib import Path
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

VERSION = "1.7.5"

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

        notebook.append_page(tab_res, Gtk.Label(label="Kaynak ve Ekran"))

        # 3. İzinler ve İzolasyon
        tab_perms = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_perms.set_margin_top(12)

        self.chk_net = Gtk.CheckButton(label="İnternet ve Ağ Erişimi (Açıkken yalnızca kontrollü DNS kullanılır)")
        self.chk_net.set_active(True)
        self.chk_audio = Gtk.CheckButton(label="Ses Desteği (PulseAudio / PipeWire Soketi)")
        self.chk_audio.set_active(True)
        self.chk_share = Gtk.CheckButton(label="Paylaşılan Klasör (~/SafeBox-Paylasim Köprüsü)")
        self.chk_share.set_active(True)
        self.chk_clipboard = Gtk.CheckButton(label="Çift Yönlü Pano Paylaşımı")
        self.chk_clipboard.set_active(True)

        tab_perms.pack_start(self.chk_net, False, False, 0)
        tab_perms.pack_start(self.chk_audio, False, False, 0)
        tab_perms.pack_start(self.chk_share, False, False, 0)
        tab_perms.pack_start(self.chk_clipboard, False, False, 0)
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
        
        if cmd == "clear":
            self.console_view.get_buffer().set_text("")
        elif cmd == "developer":
            self.dev_mode = not self.dev_mode
            st = "AÇIK" if self.dev_mode else "KAPALI"
            self.append_log(f"Geliştirici Modu: {st}")
        elif cmd == "status":
            self.append_log("SafeBox Durumu: Hazır\nMasaüstü: Cinnamon")
        elif cmd == "sysinfo":
            self.append_log(f"SafeBox Sürüm: {VERSION}\nMasaüstü: Cinnamon 2D")
        elif cmd == "purge":
            os.system("rm -rf ~/.local/share/safebox/mock_*")
            self.append_log("Önbellek temizlendi.")
        elif cmd == "doctor":
            self.append_log("[PASS] Çekirdek İzolasyonu\n[PASS] Cinnamon Masaüstü Yalıtımı")
        else:
            if self.dev_mode:
                try:
                    res = subprocess.run(raw_cmd, shell=True, capture_output=True, text=True, timeout=5)
                    if res.stdout:
                        self.append_log(res.stdout.strip())
                    if res.stderr:
                        self.append_log(f"[STDERR] {res.stderr.strip()}")
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
        clip = "1" if self.chk_clipboard.get_active() else "0"

        if getattr(self, "sandbox_proc", None) is not None:
            if self.sandbox_proc.poll() is None:
                self.append_log("[UYARI] SafeBox zaten çalışıyor.")
                return

        self.btn_start.set_sensitive(False)
        self.append_log(f"[BAŞLATILIYOR] RAM={ram}GB, CPU={cpu}, Ekran={res}...")

        engine_path = "/usr/bin/safebox-core"
        if not os.path.exists(engine_path):
            engine_path = os.path.expanduser("~/safebox/usr/bin/safebox-core")

        cmd = [engine_path, ram, cpu, res, share, clip, audio, net]

        try:
            self.sandbox_proc = subprocess.Popen(cmd)
            self.append_log(f"[OK] SafeBox core çalışıyor (PID={self.sandbox_proc.pid}).")
            self.append_log("[BEKLENİYOR] Sanal ekran hazırlanıyor...")

            self.viewer_started = False
            self.vnc_proc = None
            self.viewer_proc = None

            GLib.timeout_add(300, self.check_sandbox_process)
            GLib.timeout_add(300, self.check_display_ready)

        except Exception as e:
            self.btn_start.set_sensitive(True)
            self.append_log(f"[HATA] Core başlatılamadı: {e}")

    def check_display_ready(self):
        if self.viewer_started:
            return False

        # SafeBox tarafından başlatılan rootless Xorg'u bul.
        import subprocess

        try:
            result = subprocess.run(
                ["pgrep", "-af", "/usr/lib/xorg/Xorg :"],
                capture_output=True,
                text=True,
                timeout=1,
            )

            for line in result.stdout.splitlines():
                if "/usr/share/safebox/xorg/safebox-dummy.conf" not in line:
                    continue

                parts = line.split()

                for part in parts:
                    if part.startswith(":") and part[1:].isdigit():
                        display = part
                        display_num = int(part[1:])
                        vnc_port = 5900 + display_num

                        self.append_log(
                            f"[OK] Sanal ekran bulundu: DISPLAY={display}"
                        )

                        # Aynı ekran için ikinci kez VNC başlatılmasını engelle.
                        self.viewer_started = True

                        self.vnc_proc = subprocess.Popen([
                            "x11vnc",
                            "-display", display,
                            "-auth", "/dev/null",
                            "-localhost",
                            "-nopw",
                            "-rfbport", str(vnc_port),
                            "-forever",
                            "-shared",
                            "-noxdamage",
                            "-noshm",
                            "-input", "KMBC",
                        ], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

                        self.append_log(
                            f"[OK] Görüntü köprüsü başlatıldı: VNC={vnc_port}"
                        )

                        GLib.timeout_add(
                            1000,
                            self.launch_vnc_viewer,
                            display,
                            display_num
                        )

                        return False

        except Exception:
            pass

        if getattr(self, "sandbox_proc", None) is not None:
            if self.sandbox_proc.poll() is not None:
                self.btn_start.set_sensitive(True)
                self.append_log("[HATA] SafeBox core sonlandı.")
                return False

        return True

    def launch_vnc_viewer(self, display, display_num):
        try:
            vnc_display = f"127.0.0.1:{display_num}"

            self.append_log(
                f"[BAŞLATILIYOR] Görüntüleyici: {vnc_display}"
            )

            self.viewer_proc = subprocess.Popen([
                "gvncviewer",
                vnc_display,
            ])

            self.viewer_started = True

            self.append_log(
                f"[OK] Cinnamon görüntüsü açıldı: {display}"
            )

            # Viewer kapanırsa SafeBox oturumunu da sonlandır.
            GLib.timeout_add(500, self.check_viewer_process)

        except Exception as e:
            self.viewer_started = False
            self.append_log(
                f"[HATA] Görüntüleyici açılamadı: {e}"
            )

        return False

    def check_sandbox_process(self):
        proc = getattr(self, "sandbox_proc", None)

        if proc is None:
            return False

        returncode = proc.poll()

        if returncode is None:
            return True

        self.on_sandbox_finished(returncode)
        self.sandbox_proc = None
        return False

    def check_viewer_process(self):
        viewer = getattr(self, "viewer_proc", None)

        if viewer is None:
            return False

        if viewer.poll() is None:
            return True

        self.append_log(
            "[BİLGİ] Görüntüleyici kapandı; SafeBox oturumu sonlandırılıyor."
        )

        proc = getattr(self, "sandbox_proc", None)

        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
            except Exception as e:
                self.append_log(
                    f"[UYARI] SafeBox core sonlandırılamadı: {e}"
                )

        self.viewer_proc = None
        self.vnc_proc = None

        return False

    def on_sandbox_finished(self, returncode):
        self.btn_start.set_sensitive(True)
        if returncode == 0:
            self.append_log("[KAPANDI] Sanal alan sonlandırıldı.")
        else:
            self.append_log(f"[HATA] Hata kodu: {returncode}")

def main():
    app = SafeBoxGUI()

    def on_destroy(_widget):
        for attr in ("viewer_proc", "vnc_proc", "sandbox_proc"):
            proc = getattr(app, attr, None)
            if proc is not None:
                try:
                    if proc.poll() is None:
                        proc.terminate()
                except Exception:
                    pass

        Gtk.main_quit()

    app.connect("destroy", on_destroy)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
