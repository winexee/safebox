with open("usr/share/safebox/guest-init", "r") as f:
    content = f.read()

import re
content = re.sub(r'export XDG_SESSION_TYPE=x11\n?', '', content)
content = content.replace("export DESKTOP_SESSION=cinnamon", "export DESKTOP_SESSION=cinnamon\nexport XDG_SESSION_TYPE=x11")

with open("usr/share/safebox/guest-init", "w") as f:
    f.write(content)
