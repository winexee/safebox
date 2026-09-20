with open("usr/share/safebox/guest-init", "r") as f:
    content = f.read()

gsettings = """
# Masaüstü ve Tema ayarları (GSettings)
dconf write /org/cinnamon/desktop/background/picture-uri "'none'" || true
dconf write /org/cinnamon/desktop/background/primary-color "'#2b2b2b'" || true
dconf write /org/cinnamon/desktop/background/color-shading-type "'solid'" || true
dconf write /org/cinnamon/desktop/interface/cursor-theme "'DMZ-White'" || true
dconf write /org/cinnamon/desktop/interface/gtk-theme "'Adwaita'" || true
dconf write /org/cinnamon/desktop/interface/icon-theme "'Adwaita'" || true

# Temel masaüstü bileşenlerini başlat (Cinnamon'un DBus oturumu ile başlaması gerekir)
"""

content = content.replace("# Temel masaüstü bileşenlerini başlat (Cinnamon'un DBus oturumu ile başlaması gerekir)", gsettings)

with open("usr/share/safebox/guest-init", "w") as f:
    f.write(content)
