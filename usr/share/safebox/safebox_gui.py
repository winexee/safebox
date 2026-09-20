#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Control Center - v1.7.20
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

VERSION = "1.7.20"

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
        self.cmd_entry.set_placeholder_text("Komut girmek için buraya yazın (yardım için: help)")
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
        self.append_log("Komut listesini görmek için 'help' yazabilirsiniz.")

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
        
        if cmd == "help":
            self.append_log(f"SafeBox Sürüm: {VERSION}")
            self.append_log("--- Kullanılabilir Komutlar ---")
            self.append_log("help    : Bu yardım menüsünü gösterir")
            self.append_log("status  : SafeBox durumunu gösterir")
            self.append_log("sysinfo : Sistem bilgilerini gösterir")
            self.append_log("purge   : Önbelleği temizler")
            self.append_log("clear   : Konsol ekranını temizler")
        elif cmd == "clear":
            self.console_view.get_buffer().set_text("")
        elif cmd == "developer":
            self.dev_mode = not self.dev_mode
            st = "AÇIK" if self.dev_mode else "KAPALI"
            self.append_log(f"Geliştirici Modu: {st}")
            self.append_log("Geliştirici komutları aktif. (test, test ultra ve sistem komutları: uname, vb.)")
        elif cmd == "status":
            self.append_log("SafeBox Durumu: Hazır\nMasaüstü: Cinnamon")
        elif cmd == "sysinfo":
            self.append_log(f"SafeBox Sürüm: {VERSION}\nMasaüstü: Cinnamon")
        elif cmd == "purge":
            try:
                import glob
                targets = glob.glob(os.path.expanduser("~/.local/share/safebox/mock_*"))
                for target in targets:
                    subprocess.run(["rm", "-rf", "--", target], capture_output=True, text=True, timeout=5, check=False)
                self.append_log(f"Önbellek temizlendi. Öğeler: {len(targets)}")
            except Exception as e:
                self.append_log(f"[HATA] Purge başarısız: {e}")
        elif cmd == "test" or cmd == "test ultra":
            if not self.dev_mode:
                self.append_log("Bu komutu kullanabilmek için Geliştirici Modu (developer) aktif olmalıdır.")
                return
            
            is_ultra = (cmd == "test ultra")
            self.append_log("[🔍 SİSTEM TESTİ BAŞLANIYOR]")
            tests_passed = 0
            tests_total = 0
            errors = []
            
            # Test 1: RootFS kontrolü
            tests_total += 1
            if os.path.exists("/var/lib/safebox/rootfs/.safebox-rootfs-complete") and os.path.exists("/var/lib/safebox/rootfs/usr/bin/cinnamon") and os.path.exists("/var/lib/safebox/rootfs/usr/bin/nemo"):
                self.append_log("✓ RootFS: Tam ve eksiksiz kurulu.")
                tests_passed += 1
            else:
                msg = "✗ RootFS: Eksik veya hatalı kurulum (sudo safebox-setup gerekli)"
                self.append_log(msg)
                errors.append(msg)
            
            # Test 2: SafeBox-Core Çalışıyor mu?
            tests_total += 1
            try:
                import subprocess
                sandbox_pid = None
                
                # Gerçek Sandbox Sürecini Bulma (bwrap info-fd json)
                import json
                try:
                    with open("/tmp/safebox-bwrap.json", "r") as jf:
                        bwrap_info = json.load(jf)
                        sandbox_pid = str(bwrap_info.get("child-pid", ""))
                except Exception:
                    # Fallback
                    bwrap_res = subprocess.run(["pgrep", "-f", "bwrap.*guest-init"], capture_output=True, text=True)
                    for bpid in bwrap_res.stdout.split():
                        child_res = subprocess.run(["pgrep", "-P", bpid.strip()], capture_output=True, text=True)
                        if child_res.stdout.strip():
                            sandbox_pid = child_res.stdout.strip().split()[0]
                            break
                        
                if sandbox_pid and sandbox_pid != "0":
                    self.append_log(f"✓ Arka Plan Süreci: Aktif (PID: {sandbox_pid})")
                    tests_passed += 1
                    
                    # Test 3: Cgroup Limiti
                    tests_total += 1
                    try:
                        cgroup_path = subprocess.run(["cat", f"/proc/{sandbox_pid}/cgroup"], capture_output=True, text=True, timeout=2).stdout
                        if "safebox-app.scope" in cgroup_path:
                            self.append_log("✓ Kaynak Sınırları: Süreç izole edilmiş Cgroup içinde.")
                            tests_passed += 1
                            
                            # Gerçek Limit Kontrolü (Sadece Ultra)
                            if is_ultra:
                                tests_total += 2
                                try:
                                    limit_res = subprocess.run(["systemctl", "--user", "show", "safebox-app.scope", "--property=MemoryMax,CPUQuotaPerSecUSec"], capture_output=True, text=True, timeout=2).stdout
                                    parsed_limits = {}
                                    for line in limit_res.strip().split("\n"):
                                        if "=" in line:
                                            k, v = line.split("=", 1)
                                            parsed_limits[k] = v.strip()
                                            
                                    expected_ram = str(int(self.ram_combo.get_active_text().split()[0]) * 1024**3)
                                    expected_cpu = str(int(self.cpu_combo.get_active_text().split()[0]) * 100000)
                                    
                                    actual_mem = parsed_limits.get("MemoryMax", "")
                                    actual_cpu = parsed_limits.get("CPUQuotaPerSecUSec", "")
                                    
                                    if actual_mem == expected_ram or actual_mem == "[not set]" and expected_ram == "0":
                                        self.append_log(f"  ✓ Cgroup RAM: Seçilen değer uygulandı (MemoryMax={actual_mem})")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Cgroup RAM: HATALI! Beklenen: {expected_ram}, Uygulanan: {actual_mem}")
                                        errors.append("Cgroup RAM limiti hatalı.")
                                        
                                    if actual_cpu == expected_cpu or actual_cpu == "[not set]" and expected_cpu == "0":
                                        self.append_log(f"  ✓ Cgroup CPU: Seçilen değer uygulandı (CPUQuota={actual_cpu})")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Cgroup CPU: HATALI! Beklenen: {expected_cpu}, Uygulanan: {actual_cpu}")
                                        errors.append("Cgroup CPU limiti hatalı.")
                                        
                                except Exception as e:
                                    self.append_log(f"  ⚠ Cgroup Limitleri doğrulanamadı: {e}")
                                    errors.append("Cgroup doğrulama hatası.")
                                    # Fallback for systems without systemd-run but we won't count tests_total
                                    tests_total -= 2
                                
                                # Filesystem & Namespace İzolasyon Kontrolü
                                try:
                                    # Mnt Namespace kontrolü
                                    for ns, name in [('mnt', 'Mount'), ('pid', 'PID'), ('uts', 'UTS'), ('ipc', 'IPC'), ('user', 'USER'), ('net', 'Network')]:
                                        tests_total += 1
                                        try:
                                            h = os.readlink(f'/proc/self/ns/{ns}')
                                            g = subprocess.run(["readlink", f"/proc/{sandbox_pid}/ns/{ns}"], capture_output=True, text=True).stdout.strip()
                                            
                                            if not g:
                                                self.append_log(f"  ✗ {name} Namespace: Okunamadı!")
                                                errors.append(f"{name} Namespace okunamadı.")
                                                continue
                                                
                                            if ns == 'net' and not self.chk_net.get_active():
                                                if h != g:
                                                    self.append_log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                                    tests_passed += 1
                                                else:
                                                    self.append_log(f"  ✗ {name} Namespace: HOST İLE PAYLAŞILMIŞ! (KAPALI OLMASINA RAĞMEN)")
                                                    errors.append(f"{name} Namespace izole edilmemiş!")
                                            elif ns == 'net' and self.chk_net.get_active():
                                                self.append_log(f"  ✓ {name} Namespace: Ağ isteyerek host ile paylaşıldı (NET=1).")
                                                tests_passed += 1
                                            else:
                                                if h != g:
                                                    self.append_log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                                    tests_passed += 1
                                                else:
                                                    self.append_log(f"  ✗ {name} Namespace: HOST İLE PAYLAŞILMIŞ!")
                                                    errors.append(f"{name} Namespace izole edilmemiş!")
                                        except Exception as e:
                                            self.append_log(f"  ✗ {name} Namespace: Kontrol Hatası! ({e})")
                                            errors.append(f"{name} Namespace hata: {e}")
                                            
                                    import getpass
                                    current_user = getpass.getuser()
                                    
                                    # Filesystem Kontrolleri (Doğrudan /proc/PID/mountinfo üzerinden - nsenter olmadan)
                                    tests_total += 1
                                    try:
                                        with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                            mountinfo = mf.read()
                                            
                                        # Root sızıntı kontrolü
                                        leaks = [f"/home/{current_user}", "/root", "/mnt", "/media"]
                                        leak_found = False
                                        for leak in leaks:
                                            if f" {leak} " in mountinfo or f" {leak}/" in mountinfo:
                                                leak_found = True
                                                self.append_log(f"  ✗ Filesystem: Host {leak} dizini SIZMIŞ!")
                                                errors.append(f"Host {leak} sızıntısı!")
                                        
                                        if not leak_found:
                                            self.append_log("  ✓ Filesystem: Host özel dizinleri (/home, /root, vb.) izole.")
                                            tests_passed += 1
                                    except Exception as e:
                                        self.append_log(f"  ⚠ Filesystem: İzolasyon kontrol edilemedi: {e}")
                                        errors.append(f"Filesystem testi hata: {e}")
                                        
                                    tests_total += 1
                                    try:
                                        with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                            mounts = mf.readlines()
                                        
                                        root_mount = [m for m in mounts if " / " in m]
                                        if root_mount and "/var/lib/safebox/rootfs" in root_mount[0]:
                                            self.append_log("  ✓ Filesystem: Root (/) mount tablosu doğrulanıyor (gerçek RootFS).")
                                            tests_passed += 1
                                        else:
                                            self.append_log("  ✗ Filesystem: Root (/) mount izolasyonu hatalı veya host sızıntısı var!")
                                            errors.append("Root mount izolasyonu başarısız.")
                                    except Exception as e:
                                        self.append_log(f"  ⚠ Filesystem Root: İzolasyon kontrol edilemedi: {e}")
                                        errors.append(f"Root mount testi hata: {e}")
                                        
                                    tests_total += 1
                                    try:
                                        with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                            mounts = mf.readlines()
                                        dev_leak = False
                                        for m in mounts:
                                            if " /dev " in m and ("udev" in m or "devtmpfs" in m):
                                                dev_leak = True
                                        if dev_leak:
                                            self.append_log("  ✗ Filesystem: /dev host ile direkt paylaşımlı!")
                                            errors.append("/dev izolasyonu başarısız!")
                                        else:
                                            self.append_log("  ✓ Filesystem: /dev (Cihazlar) izole tmpfs/devtmpfs kullanıyor.")
                                            tests_passed += 1
                                    except Exception as e:
                                        self.append_log(f"  ⚠ /dev: Kontrol edilemedi: {e}")
                                        errors.append(f"/dev testi hata: {e}")
                                        
                                    tests_total += 1
                                    try:
                                        # Hostname doğrudan UTS namespace içinden okunacak, bunu /proc/sys/kernel/hostname den okuyabiliriz (ama kernel proc u namespace'e duyarlıdır)
                                        # Yada basitçe Python ile setns yapamayacağımıza göre, subprocess nsenter'ı unprivileged şekilde deneriz:
                                        hostname_check = subprocess.run(["nsenter", "-m", "-u", "-U", "-t", str(sandbox_pid), "hostname"], capture_output=True, text=True).stdout.strip()
                                        if hostname_check == "safebox-sandbox":
                                            self.append_log("  ✓ UTS: Hostname 'safebox-sandbox' olarak doğrulanıyor.")
                                            tests_passed += 1
                                        else:
                                            self.append_log(f"  ✗ UTS: Hostname sızıntısı! Beklenmeyen hostname '{hostname_check}'")
                                            errors.append(f"Hostname sızıntısı: {hostname_check}")
                                    except Exception as e:
                                        self.append_log(f"  ⚠ UTS: Hostname kontrol edilemedi: {e}")
                                        errors.append(f"UTS testi hata: {e}")
                                        
                                except Exception as e:
                                    self.append_log(f"  ⚠ Filesystem/Namespace İzolasyonu kontrol edilemedi: {e}")
                        else:
                            msg = f"⚠ Kaynak Sınırları: Süreç varsayılan Cgroup'ta! ({cgroup_path.strip()})"
                            self.append_log(msg)
                            errors.append(msg)
                    except Exception as e:
                        msg = f"⚠ Kaynak Sınırları: Cgroup doğrulanamadı ({e})"
                        if is_ultra: self.append_log(msg)
                        errors.append(msg)
                else:
                    self.append_log("ℹ Arka Plan Süreci: Çalışan bir oturum yok")
            except Exception as e:
                msg = f"✗ Arka Plan Kontrolü hatası: {e}"
                if is_ultra: self.append_log(msg)
                errors.append(msg)
            
            # Sonuç
            if tests_total > 0:
                self.append_log(f"\n[SONUÇ] {tests_passed}/{tests_total} test geçti.")
                if is_ultra and errors:
                    self.append_log("--- Ultra Detaylı Hata Listesi ---")
                    for err in errors:
                        self.append_log(err)
                    self.append_log("----------------------------------")
            else:
                self.append_log("\n[SONUÇ] Test yapılamadı.")
        else:
            if self.dev_mode:
                # Güvenlik: Whitelist kontrol
                cmd_parts = shlex.split(raw_cmd)
                base_cmd = cmd_parts[0] if cmd_parts else ""
                
                if base_cmd not in ALLOWED_DEV_CMDS:
                    self.append_log(f"[HATA] '{base_cmd}' komutuna izin yok!")
                    self.append_log(f"İzin verilen sistem komutları: {', '.join(ALLOWED_DEV_CMDS)}")
                    return
                
                try:
                    res = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=5)
                    if res.stdout: self.append_log(res.stdout.strip())
                    if res.stderr: self.append_log(f"[STDERR] {res.stderr.strip()}")
                    if res.returncode != 0: self.append_log(f"[UYARI] Çıkış kodu: {res.returncode}")
                except Exception as e:
                    self.append_log(f"[HATA] {e}")
            else:
                self.append_log("Geçersiz komut. Komutları görmek için 'help' yazın.")

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
            self.append_log(f"[HATA] Beklenmeyen kapanış (Hata kodu: {returncode})")
            
            # Hata detaylarını engine logundan çıkar
            log_path = os.path.expanduser("~/.local/share/safebox/safebox-engine.log")
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Hata olabilecek satırları yakala
                        error_lines = [line.strip() for line in lines if "bwrap:" in line or "failed to exec" in line or "[HATA]" in line]
                        if error_lines:
                            self.append_log("--- Hata Detayı ---")
                            # Sadece en son 3 hatayı göster
                            for el in error_lines[-3:]:
                                self.append_log(el)
                            self.append_log("-------------------")
                except Exception:
                    pass

def main():
    app = SafeBoxGUI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
