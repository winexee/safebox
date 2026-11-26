#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Control Center - v1.7.30
Original Classic UI & Cinnamon Integration
"""

import getpass
import glob
import json
import multiprocessing
import os
import shlex
import shutil
import subprocess
import threading
import time
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

VERSION = "1.7.30"


def get_runtime_dir():
    """Return the per-user runtime directory shared with safebox-core."""
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg and os.path.isdir(xdg) and os.access(xdg, os.W_OK):
        return os.path.join(xdg, "safebox")
    return os.path.expanduser("~/.local/share/safebox/run")


def resolve_bin(binary_name):
    """Resolve an executable across Snap, local repository checkout, or system /usr/bin."""
    snap_dir = os.environ.get("SNAP")
    candidates = []
    if snap_dir:
        candidates.append(os.path.join(snap_dir, "usr", "bin", binary_name))

    usr_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates.append(os.path.join(usr_root, "bin", binary_name))
    candidates.append(os.path.join("/usr/bin", binary_name))

    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return os.path.join("/usr/bin", binary_name)


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
        cpu_count = multiprocessing.cpu_count()
        valid_cores = [1, 2, 4, 6, 8, 12, 16, 24, 32, 64]
        if cpu_count not in valid_cores:
            valid_cores.append(cpu_count)
        valid_cores = sorted({c for c in valid_cores if c <= cpu_count})
        if not valid_cores:
            valid_cores = [1]

        for c in valid_cores:
            self.cpu_combo.append_text(f"{c} Çekirdek")

        # Set default to roughly half cores or fallback
        default_idx = len(valid_cores) - 1
        for i, c in enumerate(valid_cores):
            if c >= cpu_count // 2:
                default_idx = i
                break
        self.cpu_combo.set_active(default_idx)
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
        self.btn_run = Gtk.Button(label="Çalıştır")
        self.btn_run.connect("clicked", self.on_run_command)

        cmd_box.pack_start(cmd_lbl, False, False, 0)
        cmd_box.pack_start(self.cmd_entry, True, True, 0)
        cmd_box.pack_start(self.btn_run, False, False, 0)
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

    def _find_running_sandbox_pid(self, retries=1):
        bwrap_json = os.path.join(get_runtime_dir(), "safebox-bwrap.json")
        for attempt in range(retries):
            try:
                with open(bwrap_json, "r", encoding="utf-8") as jf:
                    bwrap_info = json.load(jf)
                pid_candidate = str(bwrap_info.get("child-pid", "")).strip()
                if pid_candidate.isdigit() and pid_candidate != "0" and os.path.exists(f"/proc/{pid_candidate}"):
                    with open(f"/proc/{pid_candidate}/cgroup", "r", encoding="utf-8") as cgf:
                        if "safebox-app.scope" in cgf.read():
                            return pid_candidate
            except Exception:
                pass
            if attempt + 1 < retries:
                time.sleep(0.1)
        return None

    def on_run_command(self, widget):
        raw_cmd = self.cmd_entry.get_text().strip()
        self.cmd_entry.set_text("")
        if not raw_cmd:
            return

        cmd = raw_cmd.lower()
        self.append_log(f"> {raw_cmd}")

        # İzin verilen komutlar (whitelist)
        ALLOWED_DEV_CMDS = {"uname", "whoami", "pwd", "ls", "echo", "date"}

        if cmd == "help":
            self.append_log(f"SafeBox Sürüm: {VERSION}")
            self.append_log("--- Kullanılabilir Komutlar ---")
            self.append_log("help      : Bu yardım menüsünü gösterir")
            self.append_log("status    : SafeBox durumunu gösterir")
            self.append_log("sysinfo   : Sistem bilgilerini gösterir")
            self.append_log("purge     : Önbelleği temizler")
            self.append_log("developer : Geliştirici modunu açar/kapatır")
            self.append_log("clear     : Konsol ekranını temizler")
        elif cmd == "clear":
            self.console_view.get_buffer().set_text("")
        elif cmd == "developer":
            self.dev_mode = not self.dev_mode
            st = "AÇIK" if self.dev_mode else "KAPALI"
            self.append_log(f"Geliştirici Modu: {st}")
            if self.dev_mode:
                self.append_log("Geliştirici komutları aktif. (test, test ultra ve sistem komutları: uname, vb.)")
        elif cmd == "status":
            pid = self._find_running_sandbox_pid(retries=1)
            if pid:
                self.append_log(f"SafeBox Durumu: Çalışıyor (PID: {pid})\nMasaüstü: Cinnamon 2D")
            else:
                self.append_log("SafeBox Durumu: Hazır (Çalışan oturum yok)\nMasaüstü: Cinnamon 2D")
        elif cmd == "sysinfo":
            self.append_log(f"SafeBox Sürüm: {VERSION}\nMasaüstü: Cinnamon 2D")
        elif cmd == "purge":
            if self._find_running_sandbox_pid(retries=1):
                self.append_log("[UYARI] SafeBox aktifken önbellek temizlenemez. Önce oturumu kapatın.")
                return
            try:
                targets = glob.glob(os.path.expanduser("~/.local/share/safebox/mock_*"))
                for target in targets:
                    if os.path.isdir(target):
                        shutil.rmtree(target)
                    else:
                        os.remove(target)
                self.append_log(f"Önbellek temizlendi. Öğeler: {len(targets)}")
            except Exception as e:
                self.append_log(f"[HATA] Purge başarısız: {e}")
        elif cmd in ("test", "test ultra"):
            if not self.dev_mode:
                self.append_log("Bu komutu kullanabilmek için Geliştirici Modu (developer) aktif olmalıdır.")
                return

            is_ultra = (cmd == "test ultra")
            ram_text = self.ram_combo.get_active_text() or "4 GB"
            cpu_text = self.cpu_combo.get_active_text() or "1 Çekirdek"
            expected_ram_gb = int(ram_text.split()[0])
            expected_cpu_cores = int(cpu_text.split()[0])
            net_shared = self.chk_net.get_active()

            self.cmd_entry.set_sensitive(False)
            self.btn_run.set_sensitive(False)
            self.append_log("[🔍 SİSTEM TESTİ BAŞLANIYOR]")

            threading.Thread(
                target=self._run_diagnostics_thread,
                args=(is_ultra, expected_ram_gb, expected_cpu_cores, net_shared),
                daemon=True,
            ).start()
        else:
            if self.dev_mode:
                try:
                    cmd_parts = shlex.split(raw_cmd)
                except ValueError as e:
                    self.append_log(f"[HATA] Geçersiz komut sözdizimi: {e}")
                    return

                base_cmd = cmd_parts[0] if cmd_parts else ""
                if base_cmd not in ALLOWED_DEV_CMDS:
                    self.append_log(f"[HATA] '{base_cmd}' komutuna izin yok!")
                    self.append_log(f"İzin verilen sistem komutları: {', '.join(sorted(ALLOWED_DEV_CMDS))}")
                    return

                try:
                    res = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=5)
                    if res.stdout:
                        self.append_log(res.stdout.strip())
                    if res.stderr:
                        self.append_log(f"[STDERR] {res.stderr.strip()}")
                    if res.returncode != 0:
                        self.append_log(f"[UYARI] Çıkış kodu: {res.returncode}")
                except Exception as e:
                    self.append_log(f"[HATA] {e}")
            else:
                self.append_log("Geçersiz komut. Komutları görmek için 'help' yazın.")

    def _run_diagnostics_thread(self, is_ultra, expected_ram_gb, expected_cpu_cores, net_shared):
        def log(msg):
            GLib.idle_add(self.append_log, msg)

        tests_passed = 0
        tests_total = 0
        tests_unknown = 0
        errors = []

        # Test 1: RootFS kontrolü
        tests_total += 1
        if (
            os.path.exists("/var/lib/safebox/rootfs/.safebox-rootfs-complete")
            and os.path.exists("/var/lib/safebox/rootfs/usr/bin/cinnamon")
            and os.path.exists("/var/lib/safebox/rootfs/usr/bin/nemo")
        ):
            log("✓ RootFS: Tam ve eksiksiz kurulu.")
            tests_passed += 1
        else:
            msg = "✗ RootFS: Eksik veya hatalı kurulum (sudo safebox-setup gerekli)"
            log(msg)
            errors.append(msg)

        # Test 2: SafeBox-Core Çalışıyor mu?
        tests_total += 1
        try:
            current_user = getpass.getuser()
            sandbox_pid = self._find_running_sandbox_pid(retries=10)

            if sandbox_pid:
                log(f"✓ Arka Plan Süreci: Aktif (PID: {sandbox_pid})")
                tests_passed += 1

                # Test 3: Cgroup Limiti
                tests_total += 1
                try:
                    with open(f"/proc/{sandbox_pid}/cgroup", "r", encoding="utf-8") as cgf:
                        cgroup_path = cgf.read()

                    if "safebox-app.scope" in cgroup_path:
                        log("✓ Kaynak Sınırları: Süreç izole edilmiş Cgroup içinde.")
                        tests_passed += 1

                        if is_ultra:
                            tests_total += 2
                            try:
                                cgroup_lines = [line.strip() for line in cgroup_path.splitlines() if line.strip()]
                                v2_lines = [line for line in cgroup_lines if line.startswith("0::")]
                                if v2_lines:
                                    real_cgroup = "/sys/fs/cgroup" + v2_lines[0][3:]
                                else:
                                    real_cgroup = "/sys/fs/cgroup/unified" + cgroup_lines[0].split(":", 2)[-1]

                                with open(f"{real_cgroup}/memory.max", "r", encoding="utf-8") as mf:
                                    actual_mem = mf.read().strip()

                                with open(f"{real_cgroup}/cpu.max", "r", encoding="utf-8") as cf:
                                    actual_cpu = cf.read().strip().split()[0]

                                expected_ram = str(expected_ram_gb * 1024**3)
                                host_cores = os.cpu_count() or expected_cpu_cores
                                capped_cores = min(expected_cpu_cores, host_cores)
                                expected_cpu = str(capped_cores * 100000)

                                if actual_mem == expected_ram or (actual_mem == "max" and expected_ram == "0"):
                                    log(f"  ✓ Cgroup RAM: Seçilen değer uygulandı (memory.max={actual_mem})")
                                    tests_passed += 1
                                else:
                                    log(f"  ✗ Cgroup RAM: HATALI! Beklenen: {expected_ram}, Uygulanan: {actual_mem}")
                                    errors.append("Cgroup RAM limiti hatalı.")

                                if actual_cpu == expected_cpu or (actual_cpu == "max" and expected_cpu == "0"):
                                    log(f"  ✓ Cgroup CPU: Seçilen değer uygulandı (cpu.max={actual_cpu})")
                                    tests_passed += 1
                                else:
                                    log(f"  ✗ Cgroup CPU: HATALI! Beklenen: {expected_cpu}, Uygulanan: {actual_cpu}")
                                    errors.append("Cgroup CPU limiti hatalı.")

                            except Exception as e:
                                log(f"  ⚠ Cgroup Limitleri doğrulanamadı: {e}")
                                tests_unknown += 2
                                errors.append("Cgroup doğrulama hatası.")

                            tests_total += 1
                            try:
                                with open(f"/proc/{sandbox_pid}/status", "r", encoding="utf-8") as sf:
                                    status_lines = sf.readlines()
                                cpus_allowed = [
                                    line.split(":")[1].strip()
                                    for line in status_lines
                                    if line.startswith("Cpus_allowed_list")
                                ]
                                if cpus_allowed:
                                    host_cores = os.cpu_count() or expected_cpu_cores
                                    capped_cores = min(expected_cpu_cores, host_cores)
                                    expected_affinity = f"0-{capped_cores - 1}" if capped_cores > 1 else "0"
                                    if cpus_allowed[0] == expected_affinity:
                                        log(f"  ✓ CPU Affinity: Çalışabilir CPU'lar tam doğrulandı ({cpus_allowed[0]})")
                                        tests_passed += 1
                                    else:
                                        log(f"  ✗ CPU Affinity Sızıntısı: Beklenen: {expected_affinity}, Bulunan: {cpus_allowed[0]}")
                                        errors.append(f"CPU Affinity Yanlış: Beklenen {expected_affinity}, Bulunan {cpus_allowed[0]}")
                                else:
                                    log("  ⚠ CPU Affinity: Cpus_allowed_list bulunamadı.")
                                    tests_unknown += 1
                            except Exception as e:
                                log(f"  ⚠ CPU Affinity okunamadı: {e}")
                                tests_unknown += 1
                    else:
                        msg = f"✗ Kaynak Sınırları: Süreç varsayılan Cgroup'ta! ({cgroup_path.strip()})"
                        log(msg)
                        errors.append(msg)
                except Exception as e:
                    msg = f"⚠ Kaynak Sınırları: Cgroup doğrulanamadı ({e})"
                    if is_ultra:
                        log(msg)
                    errors.append(msg)
                    tests_unknown += 1

                # Namespace ve Filesystem Testleri (Sadece Ultra)
                if is_ultra:
                    # 1. Namespaces
                    for ns, name in [("mnt", "Mount"), ("pid", "PID"), ("uts", "UTS"), ("ipc", "IPC"), ("user", "USER"), ("net", "Network")]:
                        tests_total += 1
                        try:
                            h = os.readlink(f"/proc/self/ns/{ns}")
                            g_proc = subprocess.run(["readlink", f"/proc/{sandbox_pid}/ns/{ns}"], capture_output=True, text=True, timeout=2)
                            g = g_proc.stdout.strip() if g_proc.returncode == 0 else ""

                            if not g:
                                log(f"  ⚠ {name} Namespace: Okunamadı!")
                                tests_unknown += 1
                                errors.append(f"{name} Namespace okunamadı.")
                                continue

                            if ns == "net" and net_shared:
                                log(f"  ✓ {name} Namespace: PASS - Ağ bilerek paylaşıldı (NET=1).")
                                tests_passed += 1
                            elif h != g:
                                log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                tests_passed += 1
                            else:
                                suffix = " (KAPALI OLMASINA RAĞMEN)" if ns == "net" else ""
                                log(f"  ✗ {name} Namespace: HOST İLE PAYLAŞILMIŞ!{suffix}")
                                errors.append(f"{name} Namespace izole edilmemiş!")
                        except Exception as e:
                            log(f"  ⚠ {name} Namespace: Kontrol Hatası! ({e})")
                            tests_unknown += 1
                            errors.append(f"{name} Namespace hata: {e}")

                    # 2. Filesystem Mountinfo (RootFS ve sızıntı kontrolü)
                    tests_total += 1
                    try:
                        with open(f"/proc/{sandbox_pid}/mountinfo", "r", encoding="utf-8") as mf:
                            mountinfo = mf.read()

                        leaks = [f"/home/{current_user}", "/root", "/mnt", "/media"]
                        leak_found = False
                        for line in mountinfo.splitlines():
                            parts = line.split()
                            if len(parts) >= 5:
                                root_path = parts[3]
                                mount_point = parts[4]
                                for leak in leaks:
                                    if root_path in (leak, f"{leak}/") or mount_point in (leak, f"{leak}/"):
                                        leak_found = True
                                        log(f"  ✗ Mountinfo: Host {leak} dizini SIZMIŞ! ({root_path} -> {mount_point})")
                                        errors.append(f"Host {leak} sızıntısı!")

                        if not leak_found:
                            log("  ✓ Mountinfo: Host özel dizinleri (/home, /root, vb.) izole.")
                            tests_passed += 1
                    except Exception as e:
                        log(f"  ⚠ Mountinfo İzolasyon: Kontrol edilemedi ({e})")
                        tests_unknown += 1
                        errors.append(f"Mountinfo testi hata: {e}")

                    tests_total += 1
                    try:
                        with open(f"/proc/{sandbox_pid}/mountinfo", "r", encoding="utf-8") as mf:
                            mounts = mf.readlines()

                        root_mounts = [m.split() for m in mounts if len(m.split()) >= 5 and m.split()[4] == "/"]
                        if root_mounts and "/var/lib/safebox/rootfs" in root_mounts[0][3]:
                            log("  ✓ RootFS Mount: Root (/) mount tablosu doğrulandı.")
                            tests_passed += 1
                        else:
                            log("  ✗ RootFS Mount: Hatalı izolasyon veya sızıntı var!")
                            errors.append("Root mount izolasyonu başarısız.")
                    except Exception as e:
                        log(f"  ⚠ RootFS Mount: Kontrol edilemedi ({e})")
                        tests_unknown += 1
                        errors.append(f"Root mount testi hata: {e}")

                    # 3. Gerçek Dosya Erişimi (Host /home ve Cihaz sızıntı testi)
                    tests_total += 1
                    try:
                        home_access = subprocess.run(
                            ["nsenter", "-m", "-U", "-t", str(sandbox_pid), "ls", f"/home/{current_user}"],
                            capture_output=True,
                            text=True,
                            timeout=3,
                        )
                        if "nsenter:" in home_access.stderr:
                            log(f"  ⚠ Filesystem /home: nsenter çalıştırılamadı ({home_access.stderr.strip()})")
                            tests_unknown += 1
                        elif home_access.returncode != 0:
                            log(f"  ✓ Filesystem: Guest içinden /home/{current_user} erişilemez durumda.")
                            tests_passed += 1
                        else:
                            log(f"  ✗ Filesystem: Guest içinden /home/{current_user} okunabiliyor!")
                            errors.append("Gerçek /home erişim sızıntısı!")
                    except Exception as e:
                        log(f"  ⚠ Filesystem /home: Gerçek erişim testi yapılamadı ({e})")
                        tests_unknown += 1

                    tests_total += 1
                    try:
                        dev_proc = subprocess.run(
                            ["nsenter", "-m", "-U", "-t", str(sandbox_pid), "ls", "/dev"],
                            capture_output=True,
                            text=True,
                            timeout=3,
                        )
                        if dev_proc.returncode != 0:
                            log(f"  ⚠ Filesystem /dev: okunamadı ({dev_proc.stderr.strip()})")
                            tests_unknown += 1
                        else:
                            dev_access = dev_proc.stdout
                            host_devs = []
                            for bd in glob.glob("/sys/block/*"):
                                bd_name = os.path.basename(bd)
                                if not bd_name.startswith("loop") and not bd_name.startswith("ram"):
                                    host_devs.append(bd_name)
                            if os.path.exists("/dev/dri"):
                                host_devs.append("dri")

                            dev_leak = any(hd in dev_access.split() for hd in host_devs)
                            if dev_leak:
                                log("  ✗ Filesystem: /dev altında host donanımları (disk/gpu) okunabiliyor!")
                                errors.append("/dev gerçek erişim izolasyonu başarısız!")
                            else:
                                log("  ✓ Filesystem: /dev izole; host disk/gpu cihazları görünmüyor.")
                                tests_passed += 1
                    except Exception as e:
                        log(f"  ⚠ Filesystem /dev: Gerçek erişim testi yapılamadı ({e})")
                        tests_unknown += 1

                    # 4. Hostname
                    tests_total += 1
                    try:
                        host_proc = subprocess.run(
                            ["nsenter", "-m", "-u", "-U", "-t", str(sandbox_pid), "cat", "/proc/sys/kernel/hostname"],
                            capture_output=True,
                            text=True,
                            timeout=3,
                        )
                        if host_proc.returncode != 0:
                            log(f"  ⚠ UTS: Hostname okunamadı ({host_proc.stderr.strip()})")
                            tests_unknown += 1
                        else:
                            hostname_check = host_proc.stdout.strip()
                            if hostname_check == "safebox-sandbox":
                                log("  ✓ UTS: Hostname 'safebox-sandbox' olarak doğrulandı.")
                                tests_passed += 1
                            else:
                                log(f"  ✗ UTS: Hostname sızıntısı! Beklenen: safebox-sandbox, Bulunan: '{hostname_check}'")
                                errors.append(f"Hostname sızıntısı: {hostname_check}")
                    except Exception as e:
                        log(f"  ⚠ UTS: Hostname kontrol edilemedi ({e})")
                        tests_unknown += 1
            else:
                log("✗ Sandbox Runtime: FAIL (Çalışan bir oturum yok)")
                errors.append("Sandbox başlatılamadı.")
                if is_ultra:
                    log("  ⚠ Cgroup: UNKNOWN")
                    log("  ⚠ Namespace: UNKNOWN")
                    log("  ⚠ Filesystem: UNKNOWN")
                    log("  ⚠ Hostname: UNKNOWN")
                    tests_total += 15
                    tests_unknown += 15
        except Exception as e:
            msg = f"✗ Arka Plan Kontrolü hatası: {e}"
            if is_ultra:
                log(msg)
            errors.append(msg)
            tests_unknown += 1

        # Sonuç
        if tests_total > 0:
            tests_failed = tests_total - tests_passed - tests_unknown
            log(f"\n[SONUÇ] PASS: {tests_passed} | FAIL: {tests_failed} | UNKNOWN: {tests_unknown} (Toplam: {tests_total} Test)")
            if is_ultra and errors:
                log("--- Ultra Detaylı Hata Listesi ---")
                for err in errors:
                    log(err)
                log("----------------------------------")
        else:
            log("\n[SONUÇ] Test yapılamadı.")

        def reenable_console():
            self.cmd_entry.set_sensitive(True)
            self.btn_run.set_sensitive(True)

        GLib.idle_add(reenable_console)

    def on_start_sandbox(self, widget):
        ram_text = self.ram_combo.get_active_text()
        cpu_text = self.cpu_combo.get_active_text()
        res = self.res_combo.get_active_text()
        if not ram_text or not cpu_text or not res:
            self.append_log("[HATA] Lütfen RAM, CPU ve çözünürlük seçin.")
            return

        ram = ram_text.split()[0]
        cpu = cpu_text.split()[0]
        net = "1" if self.chk_net.get_active() else "0"
        audio = "1" if self.chk_audio.get_active() else "0"
        share = "1" if self.chk_share.get_active() else "0"

        self.btn_start.set_sensitive(False)
        self.append_log(f"[BAŞLATILIYOR] RAM={ram}GB, CPU={cpu}, Ekran={res}...")

        def run_thread():
            engine_path = resolve_bin("safebox-core")
            cmd = [engine_path, ram, cpu, res, share, audio, net]
            try:
                proc = subprocess.run(cmd)
                rc = proc.returncode
            except Exception as e:
                GLib.idle_add(self.append_log, f"[HATA] Engine başlatılamadı: {e}")
                rc = 1
            GLib.idle_add(self.on_sandbox_finished, rc)

        threading.Thread(target=run_thread, daemon=True).start()

    def on_sandbox_finished(self, returncode):
        if returncode == 0:
            self.btn_start.set_sensitive(True)
            self.append_log("[KAPANDI] Sanal alan sonlandırıldı.")
            return

        if returncode == 106:
            self.btn_start.set_sensitive(True)
            self.append_log("[UYARI] SafeBox zaten çalışıyor. Aynı anda birden fazla oturum açılamaz.")
            return

        if returncode == 105:
            self.append_log("[HATA] RootFS eksik. Kurulum gerekiyor.")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.YES_NO,
                text="SafeBox RootFS Eksik",
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
                    setup_cmd = ["pkexec", resolve_bin("safebox-setup")]
                    try:
                        s_proc = subprocess.run(setup_cmd)
                        rc = s_proc.returncode
                    except Exception as e:
                        GLib.idle_add(self.append_log, f"[HATA] Kurulum başlatılamadı: {e}")
                        rc = 1

                    def on_setup_done():
                        self.btn_start.set_sensitive(True)
                        if rc == 0:
                            self.append_log("[BİLGİ] Kurulum başarıyla tamamlandı. Yeniden başlatabilirsiniz.")
                        else:
                            self.append_log(f"[HATA] Kurulum başarısız oldu (Hata kodu: {rc}).")

                    GLib.idle_add(on_setup_done)

                threading.Thread(target=setup_thread, daemon=True).start()
                return

            self.btn_start.set_sensitive(True)
            return

        self.btn_start.set_sensitive(True)
        self.append_log(f"[HATA] Beklenmeyen kapanış (Hata kodu: {returncode})")

        # Hata detaylarını yalnızca son oturum logundan çıkar
        log_path = os.path.expanduser("~/.local/share/safebox/safebox-engine.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                last_session_idx = 0
                for idx, line in enumerate(lines):
                    if line.startswith("=== ["):
                        last_session_idx = idx
                recent_lines = lines[last_session_idx:]
                error_lines = [
                    line.strip()
                    for line in recent_lines
                    if "bwrap:" in line or "failed to exec" in line or "[HATA]" in line
                ]
                if error_lines:
                    self.append_log("--- Hata Detayı ---")
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
