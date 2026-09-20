with open("usr/bin/safebox-setup", "r") as f:
    content = f.read()

content = content.replace("        fonts-liberation \\", "        fonts-liberation \\\n        dconf-cli \\")

with open("usr/bin/safebox-setup", "w") as f:
    f.write(content)
