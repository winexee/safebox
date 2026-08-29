#!/usr/bin/env python3
import gi
import os
import subprocess
import threading
import multiprocessing
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

LOG_DIR = os.path.expanduser("~/.local/share/safebox")
LOG_FILE = os.path.join(LOG_DIR, "safebox.log")
os.makedirs(LOG_DIR, exist_ok=True)
os.chmod(LOG_DIR, 0o700)

class SafeBoxApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="SafeBox Kontrol Merkezi")
        self.set_default_size(720, 560)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(16)

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
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(vbox)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        icon = Gtk.Image.new_from_icon_name("security-high", Gtk.IconSize.DIALOG)
        header.pack_start(icon, False, False, 0)

        tbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_title = Gtk.Label()
        lbl_title.set_markup("<span size='x-large' weight='bold' foreground='#E95420'>SafeBox Güvenli Alan</span>")
        lbl_title.set_halign(Gtk.Align.START)
        lbl_sub = Gtk.Label(label="Tam izole, modern MATE sanal masaüstü ve güvenlik denetimi")
        lbl_sub.set_halign(Gtk.Align.START)
        tbox.pack_start(lbl_title, False, False, 0)
        tbox.pack_start(lbl_sub, False, False, 0)
        header.pack_start(tbox, True, True, 0)
        vbox.pack_start(header, False, False, 0)

        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        notebook = Gtk.Notebook()
        vbox.pack_start(notebook, True, True, 0)

        # SEKME 1: Genel Bakış
        tab1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tab1.set_border_width(12)
        info_frame = Gtk.Frame(label=" İzolasyon Güvenlik Modeli ")
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        info_box.set_border_width(12)
        info_frame.add(info_box)

        items = [
            ("<b>Kişisel Gizlilik:</b>", "Ana ev dizininiz gizlenir, 'safebox' izole kimliği atanır."),
            ("<b>Modern MATE Arayüzü:</b>", "Yaru teması ve hafifletilmiş masaüstü deneyimi."),
            ("<b>Geçici RAM Alanı:</b>", "İndirilen tüm veriler oturum kapandığında tamamen silinir."),
            ("<b>Donanım Hızlandırma:</b>", "NVIDIA/DRI desteği ile 3D grafik performansı."),
            ("<b>Sıfır Kalıntı:</b>", "Sistem dosyaları salt okunur (read-only) bağlanır.")
        ]
        for t, d in items:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            img = Gtk.Image.new_from_icon_name("emblem-default", Gtk.IconSize.MENU)
            l = Gtk.Label()
            l.set_markup(f"{t} {d}")
            l.set_halign(Gtk.Align.START)
            row.pack_start(img, False, False, 0)
            row.pack_start(l, True, True, 0)
            info_box.pack_start(row, False, False, 0)
        tab1.pack_start(info_frame, True, True, 0)
        notebook.append_page(tab1, Gtk.Label(label="Genel Bakış"))

        # SEKME 2: Donanım ve Kaynak Limitleri
        tab2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        tab2.set_border_width(14)

        ram_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        lbl_ram = Gtk.Label()
        lbl_ram.set_markup("<b>Maksimum RAM Sınırı (GB):</b>")
        lbl_ram.set_halign(Gtk.Align.START)
        ram_box.pack_start(lbl_ram, False, False, 0)
        self.ram_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 16, 1)
        self.ram_scale.set_value(4)
        self.ram_scale.set_digits(0)
        ram_box.pack_start(self.ram_scale, False, False, 0)
        tab2.pack_start(ram_box, False, False, 0)

        cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        lbl_cpu = Gtk.Label()
        lbl_cpu.set_markup("<b>Kullanılabilir Mantıksal Çekirdek (Thread):</b>")
        lbl_cpu.set_halign(Gtk.Align.START)
        cpu_box.pack_start(lbl_cpu, False, False, 0)
        total_cpus = multiprocessing.cpu_count()
        self.cpu_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, total_cpus, 1)
        self.cpu_scale.set_value(min(6, total_cpus))
        self.cpu_scale.set_digits(0)
        cpu_box.pack_start(self.cpu_scale, False, False, 0)
        tab2.pack_start(cpu_box, False, False, 0)

        res_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_res = Gtk.Label()
        lbl_res.set_markup("<b>Ekran Çözünürlüğü:</b>")
        self.res_combo = Gtk.ComboBoxText()
        self.res_combo.append_text("1280x720 (HD)")
        self.res_combo.append_text("1366x768 (Standart)")
        self.res_combo.append_text("1600x900 (HD+)")
        self.res_combo.append_text("1920x1010 (Tam Ekran Sığdır)")
        self.res_combo.set_active(1)
        res_box.pack_start(lbl_res, False, False, 0)
        res_box.pack_start(self.res_combo, True, True, 0)
        tab2.pack_start(res_box, False, False, 0)
        notebook.append_page(tab2, Gtk.Label(label="Kaynak ve Ekran"))

        # SEKME 3: Paylaşım ve İzinler
        tab3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        tab3.set_border_width(14)
        self.chk_share_folder = Gtk.CheckButton(label="Ortak Klasör Köprüsü (~/SafeBox-Paylasim)")
        self.chk_share_folder.set_active(True)
        tab3.pack_start(self.chk_share_folder, False, False, 0)

        self.chk_clipboard = Gtk.CheckButton(label="Çift Yönlü Pano Paylaşımı")
        self.chk_clipboard.set_active(True)
        tab3.pack_start(self.chk_clipboard, False, False, 0)

        self.chk_audio = Gtk.CheckButton(label="Ses Desteği (PulseAudio / PipeWire)")
        self.chk_audio.set_active(True)
        tab3.pack_start(self.chk_audio, False, False, 0)

        self.chk_net = Gtk.CheckButton(label="İnternet Erişimi")
        self.chk_net.set_active(True)
        tab3.pack_start(self.chk_net, False, False, 0)
        notebook.append_page(tab3, Gtk.Label(label="İzinler ve Paylaşım"))

        # SEKME 4: Canlı Güvenlik Günlüğü (Log)
        tab_log = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_log.set_border_width(12)

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

        log_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_refresh_log = Gtk.Button(label="Yenile")
        btn_refresh_log.connect("clicked", self.load_log)
        btn_export_log = Gtk.Button(label="Dışa Aktar (.txt)")
        btn_export_log.connect("clicked", self.export_log)
        btn_clear_log = Gtk.Button(label="Günlüğü Temizle")
        btn_clear_log.connect("clicked", self.clear_log)

        log_btn_box.pack_start(btn_refresh_log, False, False, 0)
        log_btn_box.pack_start(btn_export_log, False, False, 0)
        log_btn_box.pack_start(btn_clear_log, False, False, 0)
        tab_log.pack_start(log_btn_box, False, False, 0)

        notebook.append_page(tab_log, Gtk.Label(label="Güvenlik Günlüğü"))
        self.load_log()

        # Alt Butonlar
        btn_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_quit = Gtk.Button(label="Kapat")
        btn_quit.connect("clicked", Gtk.main_quit)
        btn_bar.pack_start(btn_quit, False, False, 0)

        self.btn_run = Gtk.Button()
        b_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        p_icon = Gtk.Image.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        p_lbl = Gtk.Label(label="Sanal Alanı Başlat")
        b_content.pack_start(p_icon, False, False, 0)
        b_content.pack_start(p_lbl, False, False, 0)
        self.btn_run.add(b_content)
        self.btn_run.get_style_context().add_class("suggested-action")
        self.btn_run.connect("clicked", self.launch_sandbox)
        btn_bar.pack_end(self.btn_run, False, False, 0)
        vbox.pack_end(btn_bar, False, False, 0)

    def load_log(self, widget=None):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log_buffer.set_text(content)
            except Exception as e:
                self.log_buffer.set_text(f"[HATA] Log okunamadı: {str(e)}\n")
        else:
            self.log_buffer.set_text("[BILGI] Henüz güvenlik günlüğü oluşmadı.\n")

    def export_log(self, widget=None):
        dialog = Gtk.FileChooserDialog(
            title="Güvenlik Günlüğünü Kaydet",
            parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_current_name("safebox_guvenlik_gunlugu.txt")
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
                self._show_error("Hata", f"Dışa aktarma hatası: {str(e)}")
        dialog.destroy()

    def clear_log(self, widget=None):
        dialog = Gtk.MessageDialog(
            self,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            "Günlüğü temizlemek istediğinize emin misiniz?"
        )
        if dialog.run() == Gtk.ResponseType.YES:
            try:
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Güvenlik günlüğü sıfırlandı.\n")
                self.load_log()
            except Exception as e:
                self._show_error("Hata", f"Günlük temizlenemedi: {str(e)}")
        dialog.destroy()

    def _show_error(self, title, message):
        dialog = Gtk.MessageDialog(
            self,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            title
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

        cmd = ["/usr/bin/safebox-core", str(ram), str(cpus), res, share, clip, audio, net]
        threading.Thread(target=self._run_backend, args=(cmd,), daemon=True).start()

    def _run_backend(self, cmd):
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            GLib.idle_add(self._show_error, "Sanal Alan Hatası", 
                          f"SafeBox çalıştırılırken hata oluştu.\nÇıkış kodu: {e.returncode}")
        except FileNotFoundError:
            GLib.idle_add(self._show_error, "Hata", "/usr/bin/safebox-core bulunamadı!")
        except Exception as e:
            GLib.idle_add(self._show_error, "Hata", str(e))
        finally:
            GLib.idle_add(Gtk.main_quit)

win = SafeBoxApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
