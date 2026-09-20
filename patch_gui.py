import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

replacement = """                                    # Mnt Namespace kontrolü
                                    for ns, name in [('mnt', 'Mount'), ('pid', 'PID'), ('uts', 'UTS'), ('ipc', 'IPC'), ('user', 'USER'), ('net', 'Network')]:
                                        try:
                                            h = os.readlink(f'/proc/self/ns/{ns}')
                                            g = subprocess.run(["readlink", f"/proc/{sandbox_pid}/ns/{ns}"], capture_output=True, text=True).stdout.strip()
                                            if not g: continue
                                            if h != g:
                                                self.append_log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                            else:
                                                self.append_log(f"  ⚠ {name} Namespace: HOST İLE PAYLAŞILMIŞ!")
                                        except:
                                            pass
                                            
                                    # Filesystem Kontrolleri
                                    host_home_check = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "ls", "/home"], capture_output=True, text=True).stdout
                                    if "safebox" in host_home_check and "mehmet-akif" not in host_home_check:
                                        self.append_log("  ✓ Filesystem: Host /home dizini görünmüyor, guest /home/safebox izole.")
                                    else:
                                        self.append_log("  ⚠ Filesystem: İzolasyon başarısız veya test edilemedi.")
                                        
                                    root_check = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "stat", "-c", "%i", "/"], capture_output=True, text=True).stdout.strip()
                                    if root_check and root_check == "2":
                                        self.append_log("  ✓ Filesystem: Root (/) mount edilmiş izole bir kök dosya sistemi.")
                                    else:
                                        self.append_log(f"  ⚠ Filesystem: Root (/) inode beklenmeyen değer: {root_check}")
                                        
                                    hostname_check = subprocess.run(["nsenter", "-U", "-u", "-t", str(sandbox_pid), "hostname"], capture_output=True, text=True).stdout.strip()
                                    if hostname_check == "safebox-sandbox":
                                        self.append_log("  ✓ UTS: Hostname 'safebox-sandbox' olarak doğrulanıyor.")
                                    elif hostname_check:
                                        self.append_log(f"  ⚠ UTS: Beklenmeyen hostname '{hostname_check}'")"""

old_block = """                                    # Mnt Namespace kontrolü
                                    mnt_host = os.readlink('/proc/self/ns/mnt')
                                    mnt_guest = subprocess.run(["sudo", "readlink", f"/proc/{sandbox_pid}/ns/mnt"], capture_output=True, text=True).stdout.strip()
                                    if not mnt_guest: # Sudo olmadan dene
                                        mnt_guest = subprocess.run(["readlink", f"/proc/{sandbox_pid}/ns/mnt"], capture_output=True, text=True).stdout.strip()

                                    if mnt_host != mnt_guest and mnt_guest:
                                        self.append_log(f"  ✓ MNT Namespace: İzole edilmiş (Host: {mnt_host}, Guest: {mnt_guest})")
                                    else:
                                        self.append_log(f"  ⚠ MNT Namespace: İZOLASYON ZAYIF! ({mnt_host} == {mnt_guest})")
                                    
                                    # Filesystem Kontrolleri
                                    host_home_check = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "ls", "/home"], capture_output=True, text=True).stdout
                                    if "mehmet-akif" not in host_home_check:
                                        self.append_log("  ✓ Filesystem: Host /home dizini sandbox içinde GÖRÜNMÜYOR.")
                                    else:
                                        self.append_log("  ⚠ Filesystem: Host /home dizini sandbox içine SIZMIŞ!")
                                        
                                    root_check = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "stat", "-c", "%i", "/"], capture_output=True, text=True).stdout.strip()
                                    if root_check and root_check == "2":
                                        self.append_log("  ✓ Filesystem: Root (/) mount edilmiş izole bir kök dosya sistemi.")
                                    else:
                                        self.append_log(f"  ✓ Filesystem: Root (/) inode: {root_check} (İzole olduğu varsayılıyor)")"""

content = content.replace(old_block, replacement)

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)

