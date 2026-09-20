import re

with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

content = content.replace("    --tmpfs /usr/share/applications\\n", "")
content = content.replace("    --ro-bind /usr/share/safebox/guest-apps /usr/share/applications\\n", "")

# We need to make sure guest-apps are accessible
# Since we removed them, let's bind them to /opt/guest-apps
content = content.replace("    --ro-bind /usr/share/safebox/guest-apps /usr/share/applications", "    --ro-bind /usr/share/safebox/guest-apps /opt/guest-apps")

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
