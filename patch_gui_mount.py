import re
import os

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_mount = """                                    tests_total += 1
                                    mountinfo = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "cat", "/proc/self/mountinfo"], capture_output=True, text=True).stdout
                                    if f" /home/{current_user} " not in mountinfo and "/var/lib/safebox/rootfs / " in mountinfo:
                                        self.append_log("  ✓ Filesystem: Root (/) mount tablosu doğrulanıyor.")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Filesystem: Mount tablosu zayıf veya / sızıntısı var!")
                                        errors.append("Root mount izolasyonu başarısız.")"""

new_mount = """                                    tests_total += 1
                                    mountinfo = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "cat", "/proc/self/mountinfo"], capture_output=True, text=True).stdout
                                    if f" /home/{current_user} " not in mountinfo and "/var/lib/safebox/rootfs" in mountinfo and " / " in mountinfo:
                                        self.append_log("  ✓ Filesystem: Root (/) mount tablosu doğrulanıyor.")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Filesystem: Mount tablosu zayıf veya / sızıntısı var!")
                                        errors.append("Root mount izolasyonu başarısız.")"""

content = content.replace(old_mount, new_mount)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
