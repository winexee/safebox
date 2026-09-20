with open("usr/share/safebox/guest-init", "r") as f:
    content = f.read()

content = content.replace("\\n# Temel", "\n# Temel")

with open("usr/share/safebox/guest-init", "w") as f:
    f.write(content)
