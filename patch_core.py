import re

with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

# 1. Add info-fd for bwrap
content = content.replace(
    'BWRAP_ARGS+=(--bind "/tmp/.X11-unix/X${TARGET_DISP#:}" "/tmp/.X11-unix/X${TARGET_DISP#:}")',
    '''BWRAP_ARGS+=(--bind "/tmp/.X11-unix/X${TARGET_DISP#:}" "/tmp/.X11-unix/X${TARGET_DISP#:}")
BWRAP_ARGS+=(--info-fd 8)
exec 8> /tmp/safebox-bwrap.json'''
)

# 2. Remove double dbus-run-session
content = content.replace(
    'bwrap "${BWRAP_ARGS[@]}" dbus-run-session -- /home/safebox/.local/bin/guest-init',
    'bwrap "${BWRAP_ARGS[@]}" /home/safebox/.local/bin/guest-init'
)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
