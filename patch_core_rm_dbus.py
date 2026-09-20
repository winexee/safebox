import re

with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

content = content.replace("    --ro-bind-try /run/dbus/system_bus_socket /run/dbus/system_bus_socket\\n", "")

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
