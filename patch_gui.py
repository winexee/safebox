import re
import os

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

# Fix network_switch to chk_net
content = content.replace("self.network_switch.get_active()", "self.chk_net.get_active()")

# Replace PID detection logic
old_pid_logic = """                # Gerçek Sandbox Sürecini Bulma (bwrap child process)
                bwrap_res = subprocess.run(["pgrep", "-f", "bwrap.*guest-init"], capture_output=True, text=True)
                for bpid in bwrap_res.stdout.split():
                    child_res = subprocess.run(["pgrep", "-P", bpid.strip()], capture_output=True, text=True)
                    if child_res.stdout.strip():
                        sandbox_pid = child_res.stdout.strip().split()[0]
                        break"""

new_pid_logic = """                # Gerçek Sandbox Sürecini Bulma (bwrap info-fd json)
                import json
                try:
                    with open("/tmp/safebox-bwrap.json", "r") as jf:
                        bwrap_info = json.load(jf)
                        sandbox_pid = str(bwrap_info.get("child-pid", ""))
                except Exception:
                    # Fallback
                    bwrap_res = subprocess.run(["pgrep", "-f", "bwrap.*guest-init"], capture_output=True, text=True)
                    for bpid in bwrap_res.stdout.split():
                        child_res = subprocess.run(["pgrep", "-P", bpid.strip()], capture_output=True, text=True)
                        if child_res.stdout.strip():
                            sandbox_pid = child_res.stdout.strip().split()[0]
                            break"""
content = content.replace(old_pid_logic, new_pid_logic)

# Replace namespace/filesystem blocks to be completely independent and not use nsenter for filesystem
# I will use regex to find the block from `# Mnt Namespace kontrolü` to the end of UTS check.

start_marker = "# Mnt Namespace kontrolü"
end_marker = 'errors.append(f"Hostname sızıntısı: {hostname_check}")'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker) + len(end_marker)

if start_idx != -1 and end_idx != -1:
    new_checks = """# Mnt Namespace kontrolü
                                    for ns, name in [('mnt', 'Mount'), ('pid', 'PID'), ('uts', 'UTS'), ('ipc', 'IPC'), ('user', 'USER'), ('net', 'Network')]:
                                        tests_total += 1
                                        try:
                                            h = os.readlink(f'/proc/self/ns/{ns}')
                                            g = subprocess.run(["readlink", f"/proc/{sandbox_pid}/ns/{ns}"], capture_output=True, text=True).stdout.strip()
                                            
                                            if not g:
                                                self.append_log(f"  ✗ {name} Namespace: Okunamadı!")
                                                errors.append(f"{name} Namespace okunamadı.")
                                                continue
                                                
                                            if ns == 'net' and not self.chk_net.get_active():
                                                if h != g:
                                                    self.append_log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                                    tests_passed += 1
                                                else:
                                                    self.append_log(f"  ✗ {name} Namespace: HOST İLE PAYLAŞILMIŞ! (KAPALI OLMASINA RAĞMEN)")
                                                    errors.append(f"{name} Namespace izole edilmemiş!")
                                            elif ns == 'net' and self.chk_net.get_active():
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
                                    
                                    # Filesystem Kontrolleri (Doğrudan /proc/PID/mountinfo üzerinden - nsenter olmadan)
                                    tests_total += 1
                                    try:
                                        with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                            mountinfo = mf.read()
                                            
                                        # Root sızıntı kontrolü
                                        leaks = [f"/home/{current_user}", "/root", "/mnt", "/media"]
                                        leak_found = False
                                        for leak in leaks:
                                            if f" {leak} " in mountinfo or f" {leak}/" in mountinfo:
                                                leak_found = True
                                                self.append_log(f"  ✗ Filesystem: Host {leak} dizini SIZMIŞ!")
                                                errors.append(f"Host {leak} sızıntısı!")
                                        
                                        if not leak_found:
                                            self.append_log("  ✓ Filesystem: Host özel dizinleri (/home, /root, vb.) izole.")
                                            tests_passed += 1
                                    except Exception as e:
                                        self.append_log(f"  ⚠ Filesystem: İzolasyon kontrol edilemedi: {e}")
                                        errors.append(f"Filesystem testi hata: {e}")
                                        
                                    tests_total += 1
                                    try:
                                        with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                            mounts = mf.readlines()
                                        
                                        root_mount = [m for m in mounts if " / " in m]
                                        if root_mount and "/var/lib/safebox/rootfs" in root_mount[0]:
                                            self.append_log("  ✓ Filesystem: Root (/) mount tablosu doğrulanıyor (gerçek RootFS).")
                                            tests_passed += 1
                                        else:
                                            self.append_log("  ✗ Filesystem: Root (/) mount izolasyonu hatalı veya host sızıntısı var!")
                                            errors.append("Root mount izolasyonu başarısız.")
                                    except Exception as e:
                                        self.append_log(f"  ⚠ Filesystem Root: İzolasyon kontrol edilemedi: {e}")
                                        errors.append(f"Root mount testi hata: {e}")
                                        
                                    tests_total += 1
                                    try:
                                        with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                            mounts = mf.readlines()
                                        dev_leak = False
                                        for m in mounts:
                                            if " /dev " in m and ("udev" in m or "devtmpfs" in m):
                                                dev_leak = True
                                        if dev_leak:
                                            self.append_log("  ✗ Filesystem: /dev host ile direkt paylaşımlı!")
                                            errors.append("/dev izolasyonu başarısız!")
                                        else:
                                            self.append_log("  ✓ Filesystem: /dev (Cihazlar) izole tmpfs/devtmpfs kullanıyor.")
                                            tests_passed += 1
                                    except Exception as e:
                                        self.append_log(f"  ⚠ /dev: Kontrol edilemedi: {e}")
                                        errors.append(f"/dev testi hata: {e}")
                                        
                                    tests_total += 1
                                    try:
                                        # Hostname doğrudan UTS namespace içinden okunacak, bunu /proc/sys/kernel/hostname den okuyabiliriz (ama kernel proc u namespace'e duyarlıdır)
                                        # Yada basitçe Python ile setns yapamayacağımıza göre, subprocess nsenter'ı unprivileged şekilde deneriz:
                                        hostname_check = subprocess.run(["nsenter", "-m", "-u", "-U", "-t", str(sandbox_pid), "hostname"], capture_output=True, text=True).stdout.strip()
                                        if hostname_check == "safebox-sandbox":
                                            self.append_log("  ✓ UTS: Hostname 'safebox-sandbox' olarak doğrulanıyor.")
                                            tests_passed += 1
                                        else:
                                            self.append_log(f"  ✗ UTS: Hostname sızıntısı! Beklenmeyen hostname '{hostname_check}'")
                                            errors.append(f"Hostname sızıntısı: {hostname_check}")
                                    except Exception as e:
                                        self.append_log(f"  ⚠ UTS: Hostname kontrol edilemedi: {e}")
                                        errors.append(f"UTS testi hata: {e}")"""
    content = content[:start_idx] + new_checks + content[end_idx:]

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
