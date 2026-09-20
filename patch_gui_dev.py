import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_dev = """                            dev_access = subprocess.run(["nsenter", "-m", "-U", "-t", str(sandbox_pid), "ls", "/dev"], capture_output=True, text=True).stdout
                            host_devs = ["sda", "nvme0n1", "dri", "nvidia"]
                            dev_leak = False
                            for hd in host_devs:
                                if hd in dev_access:
                                    dev_leak = True
                                    break"""

new_dev = """                            dev_access = subprocess.run(["nsenter", "-m", "-U", "-t", str(sandbox_pid), "ls", "/dev"], capture_output=True, text=True).stdout
                            import glob
                            host_devs = []
                            for bd in glob.glob("/sys/block/*"):
                                bd_name = os.path.basename(bd)
                                if not bd_name.startswith("loop") and not bd_name.startswith("ram"):
                                    host_devs.append(bd_name)
                            if os.path.exists("/dev/dri"): host_devs.append("dri")
                            
                            dev_leak = False
                            for hd in host_devs:
                                # /dev altinda tam kelime eslesmesi (regex ile sinirlari belirle veya split ile)
                                if hd in dev_access.split():
                                    dev_leak = True
                                    break"""

content = content.replace(old_dev, new_dev)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
