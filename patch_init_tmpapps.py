with open("usr/share/safebox/guest-init", "r") as f:
    content = f.read()

content = content.replace('app_file="/opt/guest-apps/${app}.desktop"', 'app_file="/tmp/guest-apps/${app}.desktop"')

with open("usr/share/safebox/guest-init", "w") as f:
    f.write(content)
