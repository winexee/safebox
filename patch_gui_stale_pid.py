import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_pid = """                                if os.path.exists(f"/proc/{pid_candidate}"):
                                    sandbox_pid = pid_candidate
                                    break"""

new_pid = """                                if os.path.exists(f"/proc/{pid_candidate}"):
                                    try:
                                        with open(f"/proc/{pid_candidate}/cgroup", "r") as cgf:
                                            if "safebox-app.scope" in cgf.read():
                                                sandbox_pid = pid_candidate
                                                break
                                    except:
                                        pass"""

content = content.replace(old_pid, new_pid)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
