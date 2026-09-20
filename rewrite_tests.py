import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

# I will find the exact boundaries of the block we want to replace
start_str = "                # Gerçek Sandbox Sürecini Bulma (bwrap info-fd json)"
end_str = "            # Sonuç"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx == -1 or end_idx == -1:
    print("Could not find boundaries!")
    exit(1)

new_block = """                # Gerçek Sandbox Sürecini Bulma (bwrap info-fd json)
                import json
                import time
                import getpass
                current_user = getpass.getuser()
                sandbox_pid = None
                
                # Retry loop to avoid race condition when bwrap starts
                for _ in range(10):
                    try:
                        with open("/tmp/safebox-bwrap.json", "r") as jf:
                            bwrap_info = json.load(jf)
                            pid_candidate = str(bwrap_info.get("child-pid", ""))
                            if pid_candidate:
                                # Verify it's actually alive
                                if os.path.exists(f"/proc/{pid_candidate}"):
                                    sandbox_pid = pid_candidate
                                    break
                    except Exception:
                        pass
                    time.sleep(0.1)
                
                if sandbox_pid and sandbox_pid != "0":
                    self.append_log(f"✓ Arka Plan Süreci: Aktif (PID: {sandbox_pid})")
                    tests_passed += 1
                    
                    # Test 3: Cgroup Limiti
                    tests_total += 1
                    try:
                        cgroup_path = subprocess.run(["cat", f"/proc/{sandbox_pid}/cgroup"], capture_output=True, text=True, timeout=2).stdout
                        if "safebox-app.scope" in cgroup_path:
                            self.append_log("✓ Kaynak Sınırları: Süreç izole edilmiş Cgroup içinde.")
                            tests_passed += 1
                            
                            # Gerçek Limit Kontrolü (Sadece Ultra)
                            if is_ultra:
                                tests_total += 2
                                try:
                                    cg_path_str = cgroup_path.strip().split("\\n")[0]
                                    if cg_path_str.startswith("0::"):
                                        real_cgroup = "/sys/fs/cgroup" + cg_path_str[3:]
                                    else:
                                        real_cgroup = "/sys/fs/cgroup/unified" + cg_path_str.split(":", 2)[-1]
                                    
                                    with open(f"{real_cgroup}/memory.max", "r") as mf:
                                        actual_mem = mf.read().strip()
                                        
                                    with open(f"{real_cgroup}/cpu.max", "r") as cf:
                                        actual_cpu = cf.read().strip().split()[0]
                                        
                                    expected_ram = str(int(self.ram_combo.get_active_text().split()[0]) * 1024**3)
                                    expected_cpu = str(int(self.cpu_combo.get_active_text().split()[0]) * 100000)
                                    
                                    if actual_mem == expected_ram or actual_mem == "max" and expected_ram == "0":
                                        self.append_log(f"  ✓ Cgroup RAM: Seçilen değer uygulandı (memory.max={actual_mem})")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Cgroup RAM: HATALI! Beklenen: {expected_ram}, Uygulanan: {actual_mem}")
                                        errors.append("Cgroup RAM limiti hatalı.")
                                        
                                    if actual_cpu == expected_cpu or actual_cpu == "max" and expected_cpu == "0":
                                        self.append_log(f"  ✓ Cgroup CPU: Seçilen değer uygulandı (cpu.max={actual_cpu})")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Cgroup CPU: HATALI! Beklenen: {expected_cpu}, Uygulanan: {actual_cpu}")
                                        errors.append("Cgroup CPU limiti hatalı.")
                                        
                                except Exception as e:
                                    self.append_log(f"  ⚠ Cgroup Limitleri doğrulanamadı: {e}")
                                    tests_unknown += 2
                                    errors.append("Cgroup doğrulama hatası.")
                                    
                                tests_total += 1
                                try:
                                    with open(f"/proc/{sandbox_pid}/status", "r") as sf:
                                        status_lines = sf.readlines()
                                    cpus_allowed = [line.split(":")[1].strip() for line in status_lines if line.startswith("Cpus_allowed_list")]
                                    if cpus_allowed:
                                        self.append_log(f"  ✓ CPU Affinity: Çalışabilir CPU'lar izole ({cpus_allowed[0]})")
                                        tests_passed += 1
                                    else:
                                        self.append_log("  ⚠ CPU Affinity: Cpus_allowed_list bulunamadı.")
                                        tests_unknown += 1
                                except Exception as e:
                                    self.append_log(f"  ⚠ CPU Affinity okunamadı: {e}")
                                    tests_unknown += 1
                        else:
                            msg = f"✗ Kaynak Sınırları: Süreç varsayılan Cgroup'ta! ({cgroup_path.strip()})"
                            self.append_log(msg)
                            errors.append(msg)
                    except Exception as e:
                        msg = f"⚠ Kaynak Sınırları: Cgroup doğrulanamadı ({e})"
                        if is_ultra: self.append_log(msg)
                        errors.append(msg)
                        tests_unknown += 1
                        
                    # Namespace ve Filesystem Testleri (Sadece Ultra)
                    if is_ultra:
                        # 1. Namespaces
                        for ns, name in [('mnt', 'Mount'), ('pid', 'PID'), ('uts', 'UTS'), ('ipc', 'IPC'), ('user', 'USER'), ('net', 'Network')]:
                            tests_total += 1
                            try:
                                h = os.readlink(f'/proc/self/ns/{ns}')
                                g = subprocess.run(["readlink", f"/proc/{sandbox_pid}/ns/{ns}"], capture_output=True, text=True).stdout.strip()
                                
                                if not g:
                                    self.append_log(f"  ⚠ {name} Namespace: Okunamadı!")
                                    tests_unknown += 1
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
                                    self.append_log(f"  ✓ {name} Namespace: PASS - Ağ bilerek paylaşıldı (NET=1).")
                                    tests_passed += 1
                                else:
                                    if h != g:
                                        self.append_log(f"  ✓ {name} Namespace: İzole (Guest: {g.split(':')[-1][:-1]})")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ {name} Namespace: HOST İLE PAYLAŞILMIŞ!")
                                        errors.append(f"{name} Namespace izole edilmemiş!")
                            except Exception as e:
                                self.append_log(f"  ⚠ {name} Namespace: Kontrol Hatası! ({e})")
                                tests_unknown += 1
                                errors.append(f"{name} Namespace hata: {e}")
                                
                        # 2. Filesystem Mountinfo (RootFS ve sızıntı kontrolü)
                        tests_total += 1
                        try:
                            with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                mountinfo = mf.read()
                                
                            leaks = [f"/home/{current_user}", "/root", "/mnt", "/media"]
                            leak_found = False
                            for leak in leaks:
                                if f" {leak} " in mountinfo or f" {leak}/" in mountinfo:
                                    leak_found = True
                                    self.append_log(f"  ✗ Mountinfo: Host {leak} dizini SIZMIŞ!")
                                    errors.append(f"Host {leak} sızıntısı!")
                            
                            if not leak_found:
                                self.append_log("  ✓ Mountinfo: Host özel dizinleri (/home, /root, vb.) izole.")
                                tests_passed += 1
                        except Exception as e:
                            self.append_log(f"  ⚠ Mountinfo İzolasyon: Kontrol edilemedi ({e})")
                            tests_unknown += 1
                            errors.append(f"Mountinfo testi hata: {e}")
                            
                        tests_total += 1
                        try:
                            with open(f"/proc/{sandbox_pid}/mountinfo", "r") as mf:
                                mounts = mf.readlines()
                            
                            root_mount = [m for m in mounts if " / " in m]
                            if root_mount and "/var/lib/safebox/rootfs" in root_mount[0]:
                                self.append_log("  ✓ RootFS Mount: Root (/) mount tablosu doğrulandı.")
                                tests_passed += 1
                            else:
                                self.append_log("  ✗ RootFS Mount: Hatalı izolasyon veya sızıntı var!")
                                errors.append("Root mount izolasyonu başarısız.")
                        except Exception as e:
                            self.append_log(f"  ⚠ RootFS Mount: Kontrol edilemedi ({e})")
                            tests_unknown += 1
                            errors.append(f"Root mount testi hata: {e}")
                            
                        # 3. Gerçek Dosya Erişimi (Host /home ve Cihaz sızıntı testi)
                        tests_total += 1
                        try:
                            home_access = subprocess.run(["nsenter", "-m", "-U", "-t", str(sandbox_pid), "ls", f"/home/{current_user}"], capture_output=True, text=True)
                            if home_access.returncode != 0:
                                self.append_log(f"  ✓ Filesystem: Guest içinden /home/{current_user} erişilemez durumda.")
                                tests_passed += 1
                            else:
                                self.append_log(f"  ✗ Filesystem: Guest içinden /home/{current_user} okunabiliyor!")
                                errors.append(f"Gerçek /home erişim sızıntısı!")
                        except Exception as e:
                            self.append_log(f"  ⚠ Filesystem /home: Gerçek erişim testi yapılamadı ({e})")
                            tests_unknown += 1
                            
                        tests_total += 1
                        try:
                            dev_access = subprocess.run(["nsenter", "-m", "-U", "-t", str(sandbox_pid), "ls", "/dev"], capture_output=True, text=True).stdout
                            host_devs = ["sda", "nvme0n1", "dri", "nvidia"]
                            dev_leak = False
                            for hd in host_devs:
                                if hd in dev_access:
                                    dev_leak = True
                                    break
                            if dev_leak:
                                self.append_log("  ✗ Filesystem: /dev altında host donanımları (disk/gpu) okunabiliyor!")
                                errors.append("/dev gerçek erişim izolasyonu başarısız!")
                            else:
                                self.append_log("  ✓ Filesystem: /dev izole; host disk/gpu cihazları görünmüyor.")
                                tests_passed += 1
                        except Exception as e:
                            self.append_log(f"  ⚠ Filesystem /dev: Gerçek erişim testi yapılamadı ({e})")
                            tests_unknown += 1
                            
                        # 4. Hostname
                        tests_total += 1
                        try:
                            hostname_check = subprocess.run(["nsenter", "-m", "-u", "-U", "-t", str(sandbox_pid), "hostname"], capture_output=True, text=True).stdout.strip()
                            if hostname_check == "safebox-sandbox":
                                self.append_log("  ✓ UTS: Hostname 'safebox-sandbox' olarak doğrulandı.")
                                tests_passed += 1
                            else:
                                self.append_log(f"  ✗ UTS: Hostname sızıntısı! Beklenen: safebox-sandbox, Bulunan: '{hostname_check}'")
                                errors.append(f"Hostname sızıntısı: {hostname_check}")
                        except Exception as e:
                            self.append_log(f"  ⚠ UTS: Hostname kontrol edilemedi ({e})")
                            tests_unknown += 1
                else:
                    self.append_log("ℹ Arka Plan Süreci: Çalışan bir oturum yok")
            except Exception as e:
                msg = f"✗ Arka Plan Kontrolü hatası: {e}"
                if is_ultra: self.append_log(msg)
                errors.append(msg)
                tests_unknown += 1
            
"""
content = content[:start_idx] + new_block + content[end_idx:]

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
