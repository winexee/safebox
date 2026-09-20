with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

content = content.replace("--ro-bind /usr/share/safebox/guest-apps /opt/guest-apps", "--ro-bind /usr/share/safebox/guest-apps /tmp/guest-apps")

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
