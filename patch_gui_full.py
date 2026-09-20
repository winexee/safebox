import re
import os

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

# Replace the PID detection logic and cgroup/namespace checks
old_pid_logic = """                unit_pid_res = subprocess.run(["systemctl", "--user", "show", "safebox-app.scope", "--property=MainPID"], capture_output=True, text=True, timeout=2)
                sandbox_pid = None
                if "MainPID=" in unit_pid_res.stdout:
                    sandbox_pid = unit_pid_res.stdout.split("=")[1].strip()
                
                if sandbox_pid and sandbox_pid != "0":"""

new_pid_logic = """                import subprocess
                sandbox_pid = None
                
                # Gerçek Sandbox Sürecini Bulma (bwrap child process)
                bwrap_res = subprocess.run(["pgrep", "-f", "bwrap.*guest-init"], capture_output=True, text=True)
                for bpid in bwrap_res.stdout.split():
                    child_res = subprocess.run(["pgrep", "-P", bpid.strip()], capture_output=True, text=True)
                    if child_res.stdout.strip():
                        sandbox_pid = child_res.stdout.strip().split()[0]
                        break
                        
                if sandbox_pid and sandbox_pid != "0":"""

content = content.replace(old_pid_logic, new_pid_logic)

# Replace the namespace check logic
old_ns_logic = """                                    # Mnt Namespace kontrolü
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

new_ns_logic = """                                    # Mnt Namespace kontrolü
                                    for ns, name in [('mnt', 'Mount'), ('pid', 'PID'), ('uts', 'UTS'), ('ipc', 'IPC'), ('user', 'USER'), ('net', 'Network')]:
                                        tests_total += 1
                                        try:
                                            h = os.readlink(f'/proc/self/ns/{ns}')
                                            g = subprocess.run(["readlink", f"/proc/{sandbox_pid}/ns/{ns}"], capture_output=True, text=True).stdout.strip()
                                            
                                            if not g:
                                                self.append_log(f"  ✗ {name} Namespace: Okunamadı!")
                                                errors.append(f"{name} Namespace okunamadı.")
                                                continue
                                                
                                            if ns == 'net' and not self.network_switch.get_active():
                                                # Ağ kapalıysa (NET=0) network namespace izole olmalı
                                                if h != g:
                                                    self.append_log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                                    tests_passed += 1
                                                else:
                                                    self.append_log(f"  ✗ {name} Namespace: HOST İLE PAYLAŞILMIŞ! (KAPALI OLMASINA RAĞMEN)")
                                                    errors.append(f"{name} Namespace izole edilmemiş!")
                                            elif ns == 'net' and self.network_switch.get_active():
                                                # Ağ açıksa (NET=1) host ile aynı olması normaldir
                                                self.append_log(f"  ✓ {name} Namespace: Ağ isteyerek host ile paylaşıldı (NET=1).")
                                                tests_passed += 1
                                            else:
                                                if h != g:
                                                    self.append_log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                                    tests_passed += 1
                                                else:
                                                    self.append_log(f"  ✗ {name} Namespace: HOST İLE PAYLAŞILMIŞ!")
                                                    errors.append(f"{name} Namespace izole edilmemiş!")
                                        except Exception as e:
                                            self.append_log(f"  ✗ {name} Namespace: Kontrol Hatası! ({e})")
                                            errors.append(f"{name} Namespace hata: {e}")
                                            
                                    import getpass
                                    current_user = getpass.getuser()
                                    
                                    # Filesystem Kontrolleri
                                    tests_total += 1
                                    host_home_check = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "ls", "/home"], capture_output=True, text=True).stdout
                                    if "safebox" in host_home_check and current_user not in host_home_check:
                                        self.append_log(f"  ✓ Filesystem: Host /home/{current_user} görünmüyor, guest izole.")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Filesystem: Host /home dizini SIZMIŞ!")
                                        errors.append("Host /home dizini sızıntısı!")
                                        
                                    tests_total += 1
                                    mountinfo = subprocess.run(["nsenter", "-U", "-m", "-t", str(sandbox_pid), "cat", "/proc/self/mountinfo"], capture_output=True, text=True).stdout
                                    if f" /home/{current_user} " not in mountinfo and "/var/lib/safebox/rootfs / " in mountinfo:
                                        self.append_log("  ✓ Filesystem: Root (/) mount tablosu doğrulanıyor.")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Filesystem: Mount tablosu zayıf veya / sızıntısı var!")
                                        errors.append("Root mount izolasyonu başarısız.")
                                        
                                    tests_total += 1
                                    hostname_check = subprocess.run(["nsenter", "-U", "-u", "-t", str(sandbox_pid), "hostname"], capture_output=True, text=True).stdout.strip()
                                    if hostname_check == "safebox-sandbox":
                                        self.append_log("  ✓ UTS: Hostname 'safebox-sandbox' olarak doğrulanıyor.")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ UTS: Hostname sızıntısı! Beklenmeyen hostname '{hostname_check}'")
                                        errors.append(f"Hostname sızıntısı: {hostname_check}")"""

content = content.replace(old_ns_logic, new_ns_logic)

# Replace 'mehmet-akif' in other places if exists
# No need, the new logic uses getpass.getuser()

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
