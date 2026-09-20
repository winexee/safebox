with open("usr/share/safebox/guest-init", "r") as f:
    content = f.read()

mock_dbus = """
# Host izolasyonunu sağlamak için sahte (mock) bir System DBus başlat (Cinnamon çökmesini engeller)
mkdir -p /run/dbus
dbus-daemon --session --address=unix:path=/run/dbus/system_bus_socket --nopidfile --syslog-only &
"""

# add it before exec dbus-run-session
content = content.replace("# Temel masaüstü bileşenlerini başlat", mock_dbus + "\\n# Temel masaüstü bileşenlerini başlat")

with open("usr/share/safebox/guest-init", "w") as f:
    f.write(content)
