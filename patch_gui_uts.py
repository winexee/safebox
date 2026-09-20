import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_uts = 'hostname_check = subprocess.run(["nsenter", "-m", "-u", "-U", "-t", str(sandbox_pid), "hostname"], capture_output=True, text=True).stdout.strip()'
new_uts = 'hostname_check = subprocess.run(["nsenter", "-m", "-u", "-U", "-t", str(sandbox_pid), "cat", "/proc/sys/kernel/hostname"], capture_output=True, text=True).stdout.strip()'

content = content.replace(old_uts, new_uts)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
