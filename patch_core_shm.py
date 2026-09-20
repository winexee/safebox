import re

with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

content = content.replace(
    'Xephyr "$TARGET_DISP" -screen "$RESOLUTION" -title "SafeBox Secure Workspace ($TARGET_DISP)" -resizeable',
    'Xephyr "$TARGET_DISP" -screen "$RESOLUTION" -title "SafeBox Secure Workspace ($TARGET_DISP)" -resizeable -extension MIT-SHM'
)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
