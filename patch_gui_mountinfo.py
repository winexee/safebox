import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_mount = """                            leaks = [f"/home/{current_user}", "/root", "/mnt", "/media"]
                            leak_found = False
                            for leak in leaks:
                                if f" {leak} " in mountinfo or f" {leak}/" in mountinfo:
                                    leak_found = True
                                    self.append_log(f"  ✗ Mountinfo: Host {leak} dizini SIZMIŞ!")
                                    errors.append(f"Host {leak} sızıntısı!")"""

new_mount = """                            leaks = [f"/home/{current_user}", "/root", "/mnt", "/media"]
                            leak_found = False
                            for line in mountinfo.split("\\n"):
                                parts = line.split()
                                if len(parts) >= 5:
                                    root_path = parts[3]
                                    for leak in leaks:
                                        if root_path == leak or root_path == f"{leak}/":
                                            leak_found = True
                                            self.append_log(f"  ✗ Mountinfo: Host {leak} dizini SIZMIŞ! ({root_path})")
                                            errors.append(f"Host {leak} sızıntısı!")
                            """

content = content.replace(old_mount, new_mount)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
