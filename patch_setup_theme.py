with open("usr/bin/safebox-setup", "r") as f:
    content = f.read()

# Add theme and cursor packages
old_pkg = "        epiphany-browser \\"
new_pkg = "        epiphany-browser \\\n        adwaita-icon-theme \\\n        dmz-cursor-theme \\\n        gnome-themes-extra \\\n        fonts-liberation \\"

content = content.replace(old_pkg, new_pkg)

with open("usr/bin/safebox-setup", "w") as f:
    f.write(content)
