with open("usr/share/safebox/guest-init", "r") as f:
    content = f.read()

content = content.replace("gtk-theme-name=Yaru", "gtk-theme-name=Adwaita")
content = content.replace("gtk-icon-theme-name=Yaru", "gtk-icon-theme-name=Adwaita")
content = content.replace('gtk-theme-name="Yaru"', 'gtk-theme-name="Adwaita"')
content = content.replace('gtk-icon-theme-name="Yaru"', 'gtk-icon-theme-name="Adwaita"')

with open("usr/share/safebox/guest-init", "w") as f:
    f.write(content)
