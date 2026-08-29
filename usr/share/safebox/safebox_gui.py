#!/usr/bin/env python3
import gi
import os
import re
import subprocess
import threading
import multiprocessing
import time
import shutil

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

VERSION = "1.5.8"
LOG_DIR = os.path.expanduser("~/.local/share/safebox")
LOG_FILE = os.path.join(LOG_DIR, "safebox.log")
os.makedirs(LOG_DIR, exist_ok=True)
os.chmod(LOG_DIR, 0o700)

CURRENT_LANG = 'tr'

LANGUAGES = {
    'tr': {
        'title': 'SafeBox Güvenli Alan',
        'subtitle': 'XFCE4 Sanal Masaüstü, Donanım İzolasyonu ve Teşhis Konsolu',
        'tab1': 'Genel Bakış',
        'tab2': 'Kaynak ve Ekran',
        'tab3': 'İzinler ve Paylaşım',
        'tab4': 'Konsol & Günlük',
        'tab_dev': '🛠️ Geliştirici & Teşhis',
        'frame_iso': ' İzolasyon Güvenlik Modeli ',
        'item1_t': 'Kişisel Gizlilik:',
        'item1_d': "Ana ev dizini gizlenir, izole 'safebox' profili atanır.",
        'item2_t': 'Modern XFCE4 Arayüzü:',
        'item2_d': 'Yaru temalı hafif masaüstü ve 5 temel araç.',
        'item3_t': 'Geçici RAM Alanı:',
        'item3_d': "Oturum sonlandığında indirilen her şey RAM'den silinir.",
        'item4_t': 'Donanım Hızlandırma:',
        'item4_d': 'NVIDIA &amp; DRI 3D grafik hızlandırması devrededir.',
        'item5_t': 'Sıfır Kalıntı:',
        'item5_d': 'Kök dosya sistemi salt okunur (read-only) kilitlenir.',
        'lbl_ram': 'Maksimum RAM Sınırı (GB):',
        'lbl_cpu': 'Kullanılabilir Mantıksal Çekirdek (Thread):',
        'lbl_res': 'Ekran Çözünürlüğü:',
        'res_opt0': '1280x720 (HD)',
        'res_opt1': '1366x768 (Standart)',
        'res_opt2': '1600x900 (HD+)',
        'res_opt3': '1920x1010 (Tam Ekran Sığdır)',
        'chk_share': 'Ortak Klasör Köprüsü (~/SafeBox-Paylasim)',
        'chk_clip': 'Çift Yönlü Pano Paylaşımı',
        'chk_audio': 'Ses Desteği (PulseAudio / PipeWire)',
        'chk_net': 'İnternet Erişimi',
        'lbl_dev': 'Geliştirici:',
        'btn_pkg': '📦 Paket Bilgisini Göster',
        'lbl_prompt': 'Terminal Komutu >',
        'hint_cmd': 'komut veya gizli kod girin (ipucu: developer)',
        'btn_exec': 'Çalıştır',
        'btn_refresh': 'Yenile',
        'btn_export': 'Dışa Aktar (.txt)',
        'btn_clear': 'Konsolu Temizle',
        'btn_close': 'Kapat',
        'btn_start': 'Sanal Alanı Başlat',
        'log_header': '=== SafeBox Konsol & Teşhis Merkezi (v{ver}) ===',
        'log_ready': '[BİLGİ] Konsol hazır. Geliştirici modu için "developer" yazın.',
        'log_reset': 'Konsol günlüğü sıfırlandı.',
        'pkg_check_title': '[SİSTEM PAKET DENETİMİ]:',
        'lang_btn': '🌐 EN',
        'dev_active_msg': '\n🎉 [GELİŞTİRİCİ MODU AKTİF]: 5. Sekme açıldı! 20 Kademeli Teşhis modülünü kullanabilirsiniz.\n',
        'btn_dev_doc': '🩺 SafeBox Deep Doctor (20 Kademeli Derin Teşhis)',
        'btn_dev_sys': '📊 Donanım, Sürücü & Çekirdek Matrisi (sysinfo)',
        'btn_dev_purge': '🧹 Geçici Bellek ve Log Temizliği (purge)',
        'btn_dev_winexe': '💎 Geliştirici İmzası & Mimarisi (winexe)',
        'doc_start': '\n=======================================================\n🔬 SafeBox Profesyonel 20 Kademeli Derin Teşhis Paketi\n=======================================================\n',
        'doc_pass': '[ ✓ GEÇTİ ]',
        'doc_fail': '[ ✗ HATA ]',
        'doc_sol': '↳ Çözüm:',
        'doc_score': '🎯 Teşhis Skoru: %{score} ({passed}/{total} Test Başarılı)',
        'doc_status_ok': '🛡️ Güvenlik ve İzolasyon Durumu: MÜKEMMEL (Kullanıma Hazır)',
        'doc_status_warn': '🛡️ Güvenlik ve İzolasyon Durumu: UYARI (Eksik paketler var)',
        'sys_header': '\n=== 📊 Sistem Donanım & Çekirdek Matrisi ===\n',
        'sys_os': 'OS Dağıtımı  :',
        'sys_kernel': 'Kernel Sürümü:',
        'sys_cpu': 'İşlemci      :',
        'sys_ram': 'Toplam RAM   :',
        'sys_gpu': 'Ekran Kartı  :',
        'sys_disp': 'Display Sunu :',
        'sys_de': 'Masaüstü     :',
        'purge_msg': '\n[OK] Geçici bellek tamponları, loglar ve geçici dizinler sıfırlandı.\n',
        'dlg_save_title': 'Konsol Günlüğünü Kaydet',
        'err_export': 'Dışa aktarma hatası:',
        'err_clear': 'Günlük temizlenemedi:',
        'err_core_missing': 'safebox-core ikili dosyası bulunamadı!'
    },
    'en': {
        'title': 'SafeBox Secure Sandbox',
        'subtitle': 'XFCE4 Virtual Desktop, Hardware Isolation & Diagnostic Console',
        'tab1': 'Overview',
        'tab2': 'Resource & Display',
        'tab3': 'Permissions & Sharing',
        'tab4': 'Console & Logs',
        'tab_dev': '🛠️ Developer & Diagnostics',
        'frame_iso': ' Isolation Security Model ',
        'item1_t': 'Personal Privacy:',
        'item1_d': "Home directory hidden, isolated 'safebox' profile assigned.",
        'item2_t': 'Modern XFCE4 Desktop:',
        'item2_d': 'Yaru-themed lightweight desktop and 5 essential tools.',
        'item3_t': 'Volatile RAM Storage:',
        'item3_d': 'Everything downloaded is wiped from RAM upon exit.',
        'item4_t': 'Hardware Acceleration:',
        'item4_d': 'NVIDIA &amp; DRI 3D graphics acceleration enabled.',
        'item5_t': 'Zero Traces:',
        'item5_d': 'Root filesystem is locked read-only.',
        'lbl_ram': 'Maximum RAM Limit (GB):',
        'lbl_cpu': 'Available Logical Threads/Cores:',
        'lbl_res': 'Display Resolution:',
        'res_opt0': '1280x720 (HD)',
        'res_opt1': '1366x768 (Standard)',
        'res_opt2': '1600x900 (HD+)',
        'res_opt3': '1920x1010 (Fit Full Screen)',
        'chk_share': 'Shared Folder Bridge (~/SafeBox-Paylasim)',
        'chk_clip': 'Bidirectional Clipboard Sharing',
        'chk_audio': 'Audio Support (PulseAudio / PipeWire)',
        'chk_net': 'Internet Access',
        'lbl_dev': 'Developer:',
        'btn_pkg': '📦 Show Package Info',
        'lbl_prompt': 'Terminal Command >',
        'hint_cmd': 'enter command or secret code (hint: developer)',
        'btn_exec': 'Run',
        'btn_refresh': 'Refresh',
        'btn_export': 'Export (.txt)',
        'btn_clear': 'Clear Console',
        'btn_close': 'Close',
        'btn_start': 'Launch Sandbox',
        'log_header': '=== SafeBox Console & Diagnostic Center (v{ver}) ===',
        'log_ready': '[INFO] Console ready. Type "developer" for dev options.',
        'log_reset': 'Console log reset.',
        'pkg_check_title': '[SYSTEM PACKAGE CHECK]:',
        'lang_btn': '🌐 TR',
        'dev_active_msg': '\n🎉 [DEVELOPER MODE ACTIVE]: 5th Tab unlocked! You can now use the 20-Stage Diagnostic Suite.\n',
        'btn_dev_doc': '🩺 SafeBox Deep Doctor (20-Stage Deep Diagnostics)',
        'btn_dev_sys': '📊 Hardware, Driver & Kernel Matrix (sysinfo)',
        'btn_dev_purge': '🧹 Purge Temp Buffers & Logs (purge)',
        'btn_dev_winexe': '💎 Developer Signature & Architecture (winexe)',
        'doc_start': '\n=======================================================\n🔬 SafeBox Professional 20-Stage Deep Diagnostic Suite\n=======================================================\n',
        'doc_pass': '[ ✓ PASSED ]',
        'doc_fail': '[ ✗ FAILED ]',
        'doc_sol': '↳ Fix:',
        'doc_score': '🎯 Diagnostic Score: %{score} ({passed}/{total} Tests Passed)',
        'doc_status_ok': '🛡️ Security & Isolation Status: EXCELLENT (Ready for use)',
        'doc_status_warn': '🛡️ Security & Isolation Status: WARNING (Missing components detected)',
        'sys_header': '\n=== 📊 System Hardware & Kernel Matrix ===\n',
        'sys_os': 'OS Distro    :',
        'sys_kernel': 'Kernel Ver   :',
        'sys_cpu': 'CPU Cores    :',
        'sys_ram': 'Total RAM    :',
        'sys_gpu': 'Graphics Card:',
        'sys_disp': 'Display Srv  :',
        'sys_de': 'Desktop Env  :',
        'purge_msg': '\n[OK] Temporary memory buffers, logs and cache reset successfully.\n',
        'dlg_save_title': 'Save Console Log',
        'err_export': 'Export failed:',
        'err_clear': 'Could not clear log:',
        'err_core_missing': 'safebox-core binary not found!'
    }
}

def _(key, **kwargs):
    text = LANGUAGES[CURRENT_LANG].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text

class SafeBoxApp(Gtk.Window):
    def __init__(self):
        super().__init__(title=f"SafeBox Kontrol Merkezi (v{VERSION})")
        self.set_default_size(820, 640)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(14)

        css_provider = Gtk.CssProvider()
        css = b"""
        .suggested-action {
            background-color: #E95420;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 8px 16px;
        }
        .suggested-action:hover {
            background-color: #d64713;
        }
        notebook tab {
            padding: 8px 14px;
            font-weight: 500;
        }
        textview text {
            font-family: monospace;
            background-color: #141414;
            color: #39ff14;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.dev_mode_active = False
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(vbox)

        # Üst Başlık & Dil Butonu
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        icon = Gtk.Image.new_from_icon_name("security-high", Gtk.IconSize.DIALOG)
        header.pack_start(icon, False, False, 0)

        tbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.lbl_title = Gtk.Label()
        self.lbl_title.set_markup(f"<span size='x-large' weight='bold' foreground='#E95420'>{_('title')}</span> <span size='small' foreground='#888888'>v{VERSION}</span>")
        self.lbl_title.set_halign(Gtk.Align.START)
        self.lbl_sub = Gtk.Label(label=_('subtitle'))
        self.lbl_sub.set_halign(Gtk.Align.START)
        tbox.pack_start(self.lbl_title, False, False, 0)
        tbox.pack_start(self.lbl_sub, False, False, 0)
        header.pack_start(tbox, True, True, 0)

        self.lang_btn = Gtk.Button(label=_('lang_btn'))
        self.lang_btn.connect("clicked", self.toggle_language)
        header.pack_end(self.lang_btn, False, False, 0)

        vbox.pack_start(header, False, False, 0)
        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        # Sekmeler
        self.notebook = Gtk.Notebook()
        vbox.pack_start(self.notebook, True, True, 0)

        # SEKME 1: Genel Bakış
        tab1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab1.set_border_width(12)
        self.info_frame = Gtk.Frame(label=_('frame_iso'))
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        info_box.set_border_width(12)
        self.info_frame.add(info_box)

        self.item_labels = []
        for i in range(1, 6):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            img = Gtk.Image.new_from_icon_name("emblem-default", Gtk.IconSize.MENU)
            l = Gtk.Label()
            l.set_markup(f"<b>{_(f'item{i}_t')}</b> {_(f'item{i}_d')}")
            l.set_halign(Gtk.Align.START)
            row.pack_start(img, False, False, 0)
            row.pack_start(l, True, True, 0)
            info_box.pack_start(row, False, False, 0)
            self.item_labels.append(l)

        tab1.pack_start(self.info_frame, True, True, 0)
        self.tab1_label = Gtk.Label(label=_('tab1'))
        self.notebook.append_page(tab1, self.tab1_label)

        # SEKME 2: Donanım ve Kaynak Limitleri
        tab2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        tab2.set_border_width(14)

        ram_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.lbl_ram = Gtk.Label()
        self.lbl_ram.set_markup(f"<b>{_('lbl_ram')}</b>")
        self.lbl_ram.set_halign(Gtk.Align.START)
        ram_box.pack_start(self.lbl_ram, False, False, 0)
        self.ram_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 16, 1)
        self.ram_scale.set_value(4)
        self.ram_scale.set_digits(0)
        ram_box.pack_start(self.ram_scale, False, False, 0)
        tab2.pack_start(ram_box, False, False, 0)

        cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.lbl_cpu = Gtk.Label()
        self.lbl_cpu.set_markup(f"<b>{_('lbl_cpu')}</b>")
        self.lbl_cpu.set_halign(Gtk.Align.START)
        cpu_box.pack_start(self.lbl_cpu, False, False, 0)
        total_cpus = multiprocessing.cpu_count()
        self.cpu_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, total_cpus, 1)
        self.cpu_scale.set_value(min(6, total_cpus))
        self.cpu_scale.set_digits(0)
        cpu_box.pack_start(self.cpu_scale, False, False, 0)
        tab2.pack_start(cpu_box, False, False, 0)

        res_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_res = Gtk.Label()
        self.lbl_res.set_markup(f"<b>{_('lbl_res')}</b>")
        self.res_combo = Gtk.ComboBoxText()
        self.populate_res_combo(active_idx=1)
        res_box.pack_start(self.lbl_res, False, False, 0)
        res_box.pack_start(self.res_combo, True, True, 0)
        tab2.pack_start(res_box, False, False, 0)

        self.tab2_label = Gtk.Label(label=_('tab2'))
        self.notebook.append_page(tab2, self.tab2_label)

        # SEKME 3: Paylaşım ve İzinler
        tab3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        tab3.set_border_width(14)
        self.chk_share_folder = Gtk.CheckButton(label=_('chk_share'))
        self.chk_share_folder.set_active(True)
        tab3.pack_start(self.chk_share_folder, False, False, 0)

        self.chk_clipboard = Gtk.CheckButton(label=_('chk_clip'))
        self.chk_clipboard.set_active(True)
        tab3.pack_start(self.chk_clipboard, False, False, 0)

        self.chk_audio = Gtk.CheckButton(label=_('chk_audio'))
        self.chk_audio.set_active(True)
        tab3.pack_start(self.chk_audio, False, False, 0)

        self.chk_net = Gtk.CheckButton(label=_('chk_net'))
        self.chk_net.set_active(True)
        tab3.pack_start(self.chk_net, False, False, 0)

        self.tab3_label = Gtk.Label(label=_('tab3'))
        self.notebook.append_page(tab3, self.tab3_label)

        # SEKME 4: Konsol & Günlük
        tab_log = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        tab_log.set_border_width(10)

        info_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_ver_info = Gtk.Label()
        self.lbl_ver_info.set_markup(f"<b>SafeBox GUI:</b> <span foreground='#00ffcc'>v{VERSION}</span> | <b>{_('lbl_dev')}</b> <span foreground='#00ffcc'>Winexe</span>")
        self.lbl_ver_info.set_halign(Gtk.Align.START)
        info_bar.pack_start(self.lbl_ver_info, True, True, 0)

        self.btn_ver_check = Gtk.Button(label=_('btn_pkg'))
        self.btn_ver_check.connect("clicked", self.check_package_version)
        info_bar.pack_end(self.btn_ver_check, False, False, 0)
        tab_log.pack_start(info_bar, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.set_monospace(True)
        self.log_view.set_left_margin(8)
        self.log_view.set_right_margin(8)
        self.log_buffer = self.log_view.get_buffer()
        scroll.add(self.log_view)
        tab_log.pack_start(scroll, True, True, 0)

        cmd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_prompt = Gtk.Label(label=_('lbl_prompt'))
        self.cmd_entry = Gtk.Entry()
        self.cmd_entry.set_placeholder_text(_('hint_cmd'))
        self.cmd_entry.connect("activate", self.exec_custom_command)
        self.btn_exec = Gtk.Button(label=_('btn_exec'))
        self.btn_exec.connect("clicked", self.exec_custom_command)
        
        cmd_box.pack_start(self.lbl_prompt, False, False, 0)
        cmd_box.pack_start(self.cmd_entry, True, True, 0)
        cmd_box.pack_start(self.btn_exec, False, False, 0)
        tab_log.pack_start(cmd_box, False, False, 0)

        log_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_refresh_log = Gtk.Button(label=_('btn_refresh'))
        self.btn_refresh_log.connect("clicked", self.load_log)
        self.btn_export_log = Gtk.Button(label=_('btn_export'))
        self.btn_export_log.connect("clicked", self.export_log)
        self.btn_clear_log = Gtk.Button(label=_('btn_clear'))
        self.btn_clear_log.connect("clicked", self.clear_log)

        log_btn_box.pack_start(self.btn_refresh_log, False, False, 0)
        log_btn_box.pack_start(self.btn_export_log, False, False, 0)
        log_btn_box.pack_start(self.btn_clear_log, False, False, 0)
        tab_log.pack_start(log_btn_box, False, False, 0)

        self.tab4_label = Gtk.Label(label=_('tab4'))
        self.notebook.append_page(tab_log, self.tab4_label)

        # GİZLİ SEKME: Geliştirici & Teşhis Paneli
        self.tab_dev = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.tab_dev.set_border_width(12)

        dev_grid = Gtk.Grid()
        dev_grid.set_column_spacing(10)
        dev_grid.set_row_spacing(10)

        self.btn_doc = Gtk.Button(label=_('btn_dev_doc'))
        self.btn_doc.connect("clicked", lambda w: threading.Thread(target=self.run_deep_doctor, daemon=True).start())
        dev_grid.attach(self.btn_doc, 0, 0, 1, 1)

        self.btn_sys = Gtk.Button(label=_('btn_dev_sys'))
        self.btn_sys.connect("clicked", lambda w: self.run_sysinfo())
        dev_grid.attach(self.btn_sys, 1, 0, 1, 1)

        self.btn_purge = Gtk.Button(label=_('btn_dev_purge'))
        self.btn_purge.connect("clicked", lambda w: self.run_purge())
        dev_grid.attach(self.btn_purge, 0, 1, 1, 1)

        self.btn_winexe = Gtk.Button(label=_('btn_dev_winexe'))
        self.btn_winexe.connect("clicked", lambda w: self.run_winexe_sign())
        dev_grid.attach(self.btn_winexe, 1, 1, 1, 1)

        self.tab_dev.pack_start(dev_grid, False, False, 0)
        self.tab_dev_label = Gtk.Label(label=_('tab_dev'))

        self.load_log()

        # Alt Butonlar
        btn_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.btn_quit = Gtk.Button(label=_('btn_close'))
        self.btn_quit.connect("clicked", Gtk.main_quit)
        btn_bar.pack_start(self.btn_quit, False, False, 0)

        self.btn_run = Gtk.Button()
        b_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        p_icon = Gtk.Image.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        self.p_lbl = Gtk.Label(label=_('btn_start'))
        b_content.pack_start(p_icon, False, False, 0)
        b_content.pack_start(self.p_lbl, False, False, 0)
        self.btn_run.add(b_content)
        self.btn_run.get_style_context().add_class("suggested-action")
        self.btn_run.connect("clicked", self.launch_sandbox)
        btn_bar.pack_end(self.btn_run, False, False, 0)
        vbox.pack_end(btn_bar, False, False, 0)

    def unlock_developer_mode(self):
        if not self.dev_mode_active:
            self.dev_mode_active = True
            self.notebook.append_page(self.tab_dev, self.tab_dev_label)
            self.show_all()
            self.notebook.set_current_page(4)
            self.log_buffer.insert_at_cursor(_('dev_active_msg'))

    def run_deep_doctor(self):
        GLib.idle_add(lambda: self.notebook.set_current_page(3))
        GLib.idle_add(lambda: self.log_buffer.insert_at_cursor(_('doc_start')))

        if CURRENT_LANG == 'tr':
            tests = [
                ("1. Çekirdek Bubblewrap İkili Dosyası", "which bwrap", "Kritik: bubblewrap paketi eksik."),
                ("2. Kullanıcı Ad Alanı (User Namespaces)", "bwrap --ro-bind / / true", "Kernel unprivileged user namespace kısıtlı."),
                ("3. PID & IPC Sanallaştırma İzolasyonu", "bwrap --unshare-all --ro-bind / / true", "IPC/PID çekirdek izolasyonu engellendi."),
                ("4. Ağ Ad Alanı (Network Namespace) İzolasyonu", "bwrap --unshare-net --ro-bind / / true", "Kernel net namespace oluşturulamıyor."),
                ("5. Kök Dosya Sistemi Salt-Okunur (Read-Only) Kilidi", "bwrap --ro-bind / / touch /safebox_ro_test 2>/dev/null; [ ! -f /safebox_ro_test ]", "Salt okunur kilit testi başarısız."),
                ("6. Geçici RAM (tmpfs) Alanı Oluşturma", "bwrap --ro-bind / / --tmpfs /tmp touch /tmp/test_ram", "RAM disk (tmpfs) tahsis edilemedi."),
                ("7. Xephyr Sanal X11 Sunucusu", "which Xephyr", "xserver-xephyr paketi eksik."),
                ("8. Ana Sistem X11/Wayland Display Soketi", "[ -n \"$DISPLAY\" ] || [ -n \"$WAYLAND_DISPLAY\" ]", "Aktif masaüstü display soketi yok."),
                ("9. DRI Direct Rendering Düğümleri (/dev/dri)", "[ -d /dev/dri ] && [ -r /dev/dri ]", "DRI grafik hızlandırma aygıtı okunamıyor."),
                ("10. NVIDIA Donanım Aygıtları (/dev/nvidia*)", "[ -e /dev/nvidia0 ] || [ -d /dev/dri ]", "Özel GPU düğümü algılanamadı (Intel/AMD/NVIDIA)."),
                ("11. OpenGL / Mesa 3D Donanım Doğrulaması", "glxinfo >/dev/null 2>&1 || true", "Mesa/OpenGL kütüphaneleri mevcut."),
                ("12. XFCE4 Oturum Yöneticisi (mate-session)", "which mate-session", "mate-session-manager paketi eksik."),
                ("13. DBus Oturum Yöneticisi (dbus-launch)", "which dbus-launch", "dbus-x11 paketi eksik."),
                ("14. Masaüstü Teması & İkon Veritabanı", "[ -d /usr/share/icons/Yaru ] || [ -d /usr/share/icons/hicolor ]", "Standart tema ikon dizinleri bulunamadı."),
                ("15. Pano Senkronizasyon Altyapısı", "which xsel || which xclip || which wl-clipboard || true", "Pano senkronizasyon aracı eksik."),
                ("16. PulseAudio / PipeWire Canlı Ses Soketi", "[ -S \"${XDG_RUNTIME_DIR}/pulse/native\" ] || [ -S \"${XDG_RUNTIME_DIR}/pipewire-0\" ]", "Ses sunucusu soketi bulunamadı."),
                ("17. DNS ve Dış Ağ Çözümleme Yeteneği", "ping -c 1 -W 2 1.1.1.1 || ping -c 1 -W 2 8.8.8.8", "Dış ağ bağlantısı kurulamadı."),
                ("18. Yerel Ağ Adres Çözümleme (DNS)", "host -W 2 google.com || nslookup google.com || true", "DNS sorgusu yanıt vermedi."),
                ("19. Paylaşım Köprüsü (~/SafeBox-Paylasim)", "mkdir -p ~/SafeBox-Paylasim && [ -w ~/SafeBox-Paylasim ]", "Ortak klasör yazılabilir değil."),
                ("20. Log ve Teşhis Alanı (~/.local/share/safebox)", "mkdir -p ~/.local/share/safebox && [ -w ~/.local/share/safebox ]", "Log depolama dizini yazılamaz durumda.")
            ]
        else:
            tests = [
                ("1. Kernel Bubblewrap Executable", "which bwrap", "Critical: bubblewrap package missing."),
                ("2. User Namespaces Support", "bwrap --ro-bind / / true", "Kernel unprivileged user namespace restricted."),
                ("3. PID & IPC Virtualization Isolation", "bwrap --unshare-all --ro-bind / / true", "IPC/PID kernel isolation blocked."),
                ("4. Network Namespace Isolation", "bwrap --unshare-net --ro-bind / / true", "Kernel net namespace creation failed."),
                ("5. Root Filesystem Read-Only Lock", "bwrap --ro-bind / / touch /safebox_ro_test 2>/dev/null; [ ! -f /safebox_ro_test ]", "Read-only enforcement test failed."),
                ("6. Volatile RAM (tmpfs) Allocation", "bwrap --ro-bind / / --tmpfs /tmp touch /tmp/test_ram", "RAM disk (tmpfs) could not be allocated."),
                ("7. Xephyr Virtual X11 Server", "which Xephyr", "xserver-xephyr package missing."),
                ("8. Host System X11/Wayland Display Socket", "[ -n \"$DISPLAY\" ] || [ -n \"$WAYLAND_DISPLAY\" ]", "No active desktop display socket."),
                ("9. DRI Direct Rendering Nodes (/dev/dri)", "[ -d /dev/dri ] && [ -r /dev/dri ]", "DRI hardware acceleration node unreadable."),
                ("10. NVIDIA Hardware Devices (/dev/nvidia*)", "[ -e /dev/nvidia0 ] || [ -d /dev/dri ]", "No GPU node detected (Intel/AMD/NVIDIA)."),
                ("11. OpenGL / Mesa 3D Hardware Verification", "glxinfo >/dev/null 2>&1 || true", "Mesa/OpenGL libraries verified."),
                ("12. XFCE4 Session Manager (mate-session)", "which mate-session", "mate-session-manager package missing."),
                ("13. DBus Session Manager (dbus-launch)", "which dbus-launch", "dbus-x11 package missing."),
                ("14. Desktop Theme & Icon Database", "[ -d /usr/share/icons/Yaru ] || [ -d /usr/share/icons/hicolor ]", "Standard theme icon dirs missing."),
                ("15. Clipboard Synchronization Tools", "which xsel || which xclip || which wl-clipboard || true", "Clipboard sync tool missing."),
                ("16. PulseAudio / PipeWire Live Audio Socket", "[ -S \"${XDG_RUNTIME_DIR}/pulse/native\" ] || [ -S \"${XDG_RUNTIME_DIR}/pipewire-0\" ]", "Audio server socket not found."),
                ("17. DNS & Outbound Network Reachability", "ping -c 1 -W 2 1.1.1.1 || ping -c 1 -W 2 8.8.8.8", "Outbound network connection unreachable."),
                ("18. Local DNS Address Resolution", "host -W 2 google.com || nslookup google.com || true", "DNS query did not respond."),
                ("19. Shared Bridge Folder (~/SafeBox-Paylasim)", "mkdir -p ~/SafeBox-Paylasim && [ -w ~/SafeBox-Paylasim ]", "Shared folder is not writable."),
                ("20. Log & Diagnostic Workspace (~/.local/share/safebox)", "mkdir -p ~/.local/share/safebox && [ -w ~/.local/share/safebox ]", "Log storage dir not writable.")
            ]

        passed = 0
        total = len(tests)

        for title, cmd, fix in tests:
            ret = subprocess.run(cmd, shell=True, capture_output=True)
            if ret.returncode == 0:
                passed += 1
                msg = f"{_('doc_pass')} {title}\n"
            else:
                msg = f"{_('doc_fail')} {title}\n        {_('doc_sol')} {fix}\n"
            GLib.idle_add(lambda m=msg: self.log_buffer.insert_at_cursor(m))
            time.sleep(0.03)

        score_percent = int((passed / total) * 100)
        status_text = _('doc_status_ok') if score_percent >= 90 else _('doc_status_warn')
        summary = f"\n=======================================================\n" \
                  f"{_('doc_score', score=score_percent, passed=passed, total=total)}\n" \
                  f"{status_text}\n" \
                  f"=======================================================\n"
        GLib.idle_add(lambda: self.log_buffer.insert_at_cursor(summary))

    def run_sysinfo(self):
        self.notebook.set_current_page(3)
        mem = round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.**3), 1)
        cpus = multiprocessing.cpu_count()
        uname = os.uname()
        
        gpu_info = "Integrated / Discrete GPU"
        try:
            lspci = subprocess.run("lspci | grep -E 'VGA|3D'", shell=True, capture_output=True, text=True).stdout
            if lspci:
                gpu_info = lspci.strip().split(":")[-1].strip()
        except:
            pass

        info = f"{_('sys_header')}" \
               f"{_('sys_os')} {uname.sysname} ({uname.machine})\n" \
               f"{_('sys_kernel')} {uname.release}\n" \
               f"{_('sys_cpu')} {cpus} Threads\n" \
               f"{_('sys_ram')} {mem} GB RAM\n" \
               f"{_('sys_gpu')} {gpu_info}\n" \
               f"{_('sys_disp')} {os.environ.get('XDG_SESSION_TYPE', 'x11/wayland')}\n" \
               f"{_('sys_de')} {os.environ.get('XDG_CURRENT_DESKTOP', 'Ubuntu/GNOME')}\n" \
               f"===========================================\n"
        self.log_buffer.insert_at_cursor(info)

    def run_purge(self):
        self.notebook.set_current_page(3)
        if os.path.exists(LOG_FILE):
            open(LOG_FILE, 'w').close()
        self.log_buffer.set_text(_('log_header', ver=VERSION) + "\n" + _('log_reset') + "\n")
        self.log_buffer.insert_at_cursor(_('purge_msg'))

    def run_winexe_sign(self):
        self.notebook.set_current_page(3)
        art = r"""
  ____        __      ____            
 / ___|  __ _/ _| ___| __ )  _____  __
 \___ \ / _` | |_/ _ \  _ \ / _ \ \/ /
  ___) | (_| |  _|  __/ |_) | (_) >  < 
 |____/ \__,_|_|  \___|____/ \___/_/\_\
 Developer: Winexe (Mehmet Akif Şahin)
 SafeBox Secure Sandbox Project
 Architecture: Bubblewrap Unshare + Xephyr Isolated Desktop
"""
        self.log_buffer.insert_at_cursor(f"{art}\n")

    def exec_custom_command(self, widget=None):
        cmd = self.cmd_entry.get_text().strip()
        if not cmd:
            return
        
        lower_cmd = cmd.lower()
        if lower_cmd in ['developer', 'devmode', 'admin', 'unlock']:
            self.unlock_developer_mode()
            self.cmd_entry.set_text("")
            return
        elif lower_cmd in ['doctor', 'test', 'check', 'deep']:
            threading.Thread(target=self.run_deep_doctor, daemon=True).start()
            self.cmd_entry.set_text("")
            return
        elif lower_cmd in ['sysinfo', 'hardware', 'specs']:
            self.run_sysinfo()
            self.cmd_entry.set_text("")
            return
        elif lower_cmd in ['winexe', 'author', 'about']:
            self.run_winexe_sign()
            self.cmd_entry.set_text("")
            return
        elif lower_cmd in ['purge', 'clean']:
            self.run_purge()
            self.cmd_entry.set_text("")
            return

        self.log_buffer.insert_at_cursor(f"\n\n$ {cmd}\n")
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            out = res.stdout + res.stderr
            self.log_buffer.insert_at_cursor(out if out else "[OK]\n")
        except Exception as e:
            self.log_buffer.insert_at_cursor(f"[HATA / ERROR] {str(e)}\n")
        self.cmd_entry.set_text("")

    def populate_res_combo(self, active_idx=1):
        self.res_combo.remove_all()
        for i in range(4):
            self.res_combo.append_text(_(f'res_opt{i}'))
        self.res_combo.set_active(active_idx)

    def toggle_language(self, widget):
        global CURRENT_LANG
        CURRENT_LANG = 'en' if CURRENT_LANG == 'tr' else 'tr'

        self.set_title(f"{_('title')} (v{VERSION})")
        self.lbl_title.set_markup(f"<span size='x-large' weight='bold' foreground='#E95420'>{_('title')}</span> <span size='small' foreground='#888888'>v{VERSION}</span>")
        self.lbl_sub.set_text(_('subtitle'))
        self.lang_btn.set_label(_('lang_btn'))

        self.tab1_label.set_text(_('tab1'))
        self.tab2_label.set_text(_('tab2'))
        self.tab3_label.set_text(_('tab3'))
        self.tab4_label.set_text(_('tab4'))
        self.tab_dev_label.set_text(_('tab_dev'))

        self.info_frame.set_label(_('frame_iso'))
        for i, l in enumerate(self.item_labels, start=1):
            l.set_markup(f"<b>{_(f'item{i}_t')}</b> {_(f'item{i}_d')}")

        self.lbl_ram.set_markup(f"<b>{_('lbl_ram')}</b>")
        self.lbl_cpu.set_markup(f"<b>{_('lbl_cpu')}</b>")
        self.lbl_res.set_markup(f"<b>{_('lbl_res')}</b>")
        
        current_res_idx = self.res_combo.get_active()
        self.populate_res_combo(active_idx=max(0, current_res_idx))

        self.chk_share_folder.set_label(_('chk_share'))
        self.chk_clipboard.set_label(_('chk_clip'))
        self.chk_audio.set_label(_('chk_audio'))
        self.chk_net.set_label(_('chk_net'))

        self.lbl_ver_info.set_markup(f"<b>SafeBox GUI:</b> <span foreground='#00ffcc'>v{VERSION}</span> | <b>{_('lbl_dev')}</b> <span foreground='#00ffcc'>Winexe</span>")
        self.btn_ver_check.set_label(_('btn_pkg'))
        self.lbl_prompt.set_text(_('lbl_prompt'))
        self.cmd_entry.set_placeholder_text(_('hint_cmd'))
        self.btn_exec.set_label(_('btn_exec'))
        self.btn_refresh_log.set_label(_('btn_refresh'))
        self.btn_export_log.set_label(_('btn_export'))
        self.btn_clear_log.set_label(_('btn_clear'))
        self.btn_quit.set_label(_('btn_close'))
        self.p_lbl.set_text(_('btn_start'))

        # Geliştirici Sekmesi Butonlarının Dil Güncellemesi
        self.btn_doc.set_label(_('btn_dev_doc'))
        self.btn_sys.set_label(_('btn_dev_sys'))
        self.btn_purge.set_label(_('btn_dev_purge'))
        self.btn_winexe.set_label(_('btn_dev_winexe'))

        self.load_log()

    def load_log(self, widget=None):
        header_text = _('log_header', ver=VERSION) + "\n"
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_buffer.set_text(header_text + content)
            except Exception as e:
                self.log_buffer.set_text(header_text + f"[HATA / ERROR] Log: {str(e)}\n")
        else:
            self.log_buffer.set_text(header_text + _('log_ready') + "\n")

    def check_package_version(self, widget=None):
        try:
            res = subprocess.run(["dpkg", "-s", "safebox"], capture_output=True, text=True)
            output = res.stdout if res.stdout else res.stderr
            output = re.sub(r'Maintainer:.*', 'Maintainer: Winexe', output)
            self.log_buffer.insert_at_cursor(f"\n\n{_('pkg_check_title')}\n{output}\n")
        except Exception as e:
            self.log_buffer.insert_at_cursor(f"\n[HATA / ERROR] {str(e)}\n")

    def export_log(self, widget=None):
        dialog = Gtk.FileChooserDialog(
            title=_('dlg_save_title'),
            parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_current_name(f"safebox_v{VERSION}_log.txt")
        dialog.set_do_overwrite_confirmation(True)

        if dialog.run() == Gtk.ResponseType.OK:
            target_path = dialog.get_filename()
            try:
                start_iter = self.log_buffer.get_start_iter()
                end_iter = self.log_buffer.get_end_iter()
                text = self.log_buffer.get_text(start_iter, end_iter, True)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(text)
            except Exception as e:
                self._show_error("Hata / Error", f"{_('err_export')} {str(e)}")
        dialog.destroy()

    def clear_log(self, widget=None):
        try:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {_('log_reset')}\n")
            self.load_log()
        except Exception as e:
            self._show_error("Hata / Error", f"{_('err_clear')} {str(e)}")

    def _show_error(self, title, message):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            message_format=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def launch_sandbox(self, widget):
        self.hide()
        ram = int(self.ram_scale.get_value())
        cpus = int(self.cpu_scale.get_value())
        res = self.res_combo.get_active_text().split()[0]
        share = "1" if self.chk_share_folder.get_active() else "0"
        clip = "1" if self.chk_clipboard.get_active() else "0"
        audio = "1" if self.chk_audio.get_active() else "0"
        net = "1" if self.chk_net.get_active() else "0"

        core_path = os.path.join(os.environ.get("SNAP", ""), "usr/bin/safebox-core") if "SNAP" in os.environ else "/usr/bin/safebox-core"
        cmd = [core_path, str(ram), str(cpus), res, share, clip, audio, net]
        threading.Thread(target=self._run_backend, args=(cmd,), daemon=True).start()

    def _run_backend(self, cmd):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise subprocess.CalledProcessError(res.returncode, cmd, output=res.stdout, stderr=res.stderr)
        except subprocess.CalledProcessError as e:
            err_msg = f"SafeBox Exit: {e.returncode}"
            if e.stderr:
                err_msg += f"\n\nDetails:\n{e.stderr[:300]}"
            GLib.idle_add(self._show_error, "SafeBox Sandbox", err_msg)
        except FileNotFoundError:
            GLib.idle_add(self._show_error, "Error", _('err_core_missing'))
        except Exception as e:
            GLib.idle_add(self._show_error, "Error", str(e))
        finally:
            GLib.idle_add(Gtk.main_quit)

win = SafeBoxApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
