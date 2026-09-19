#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SafeBox Hoş Geldiniz Ekranı
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class WelcomeWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="SafeBox Sanal Alan")
        self.set_border_width(20)
        self.set_default_size(500, 320)
        self.set_position(Gtk.WindowPosition.CENTER)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.add(vbox)

        # Başlık
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold' foreground='#3584e4'>SafeBox Güvenli Alan</span>")
        vbox.pack_start(title, False, False, 0)

        # Bilgilendirme Metni
        desc = Gtk.Label()
        desc.set_markup(
            "Bu sanal masaüstünde yaptığınız hiçbir işlem ana sisteminizi etkilemez.\n\n"
            "• <b>Dosya Güvenliği:</b> Kişisel verileriniz tamamen gizlenmiştir.\n"
            "• <b>Geçici Hafıza:</b> Pencere kapandığında tüm değişiklikler silinir.\n"
            "• <b>Tam İzolasyon:</b> Şüpheli dosyaları güvenle açabilirsiniz."
        )
        desc.set_line_wrap(True)
        vbox.pack_start(desc, True, True, 0)

        # Buton
        btn = Gtk.Button(label="Kullanmaya Başla")
        btn.connect("clicked", lambda x: Gtk.main_quit())
        vbox.pack_end(btn, False, False, 0)

if __name__ == "__main__":
    win = WelcomeWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
