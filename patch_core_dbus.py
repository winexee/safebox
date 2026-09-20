import re

with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

dbus_bind = """    --tmpfs /run
    --dir /run/dbus
    --ro-bind-try /run/dbus/system_bus_socket /run/dbus/system_bus_socket"""

content = content.replace("    --tmpfs /run", dbus_bind)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
