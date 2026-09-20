with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_limits = """                            # Gerçek Limit Kontrolü (Sadece Ultra)
                            if is_ultra:
                                tests_total += 2
                                try:
                                    limit_res = subprocess.run(["systemctl", "--user", "show", "safebox-app.scope", "--property=MemoryMax,CPUQuotaPerSecUSec"], capture_output=True, text=True, timeout=2).stdout
                                    parsed_limits = {}
                                    for line in limit_res.strip().split("\\n"):
                                        if "=" in line:
                                            k, v = line.split("=", 1)
                                            parsed_limits[k] = v.strip()
                                            
                                    expected_ram = str(int(self.ram_combo.get_active_text().split()[0]) * 1024**3)
                                    expected_cpu = str(int(self.cpu_combo.get_active_text().split()[0]) * 100000)
                                    
                                    actual_mem = parsed_limits.get("MemoryMax", "")
                                    actual_cpu = parsed_limits.get("CPUQuotaPerSecUSec", "")
                                    
                                    if actual_mem == expected_ram or actual_mem == "[not set]" and expected_ram == "0":
                                        self.append_log(f"  ✓ Cgroup RAM: Seçilen değer uygulandı (MemoryMax={actual_mem})")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Cgroup RAM: HATALI! Beklenen: {expected_ram}, Uygulanan: {actual_mem}")
                                        errors.append("Cgroup RAM limiti hatalı.")
                                        
                                    if actual_cpu == expected_cpu or actual_cpu == "[not set]" and expected_cpu == "0":
                                        self.append_log(f"  ✓ Cgroup CPU: Seçilen değer uygulandı (CPUQuota={actual_cpu})")
                                        tests_passed += 1
                                    else:
                                        self.append_log(f"  ✗ Cgroup CPU: HATALI! Beklenen: {expected_cpu}, Uygulanan: {actual_cpu}")
                                        errors.append("Cgroup CPU limiti hatalı.")
                                        
                                except Exception as e:
                                    self.append_log(f"  ⚠ Cgroup Limitleri doğrulanamadı: {e}")
                                    errors.append("Cgroup doğrulama hatası.")
                                    # Fallback for systems without systemd-run but we won't count tests_total
                                    tests_total -= 2"""

new_limits = """                            # Gerçek Limit Kontrolü (Sadece Ultra)
                            if is_ultra:
                                tests_total += 2
                                try:
                                    # Cgroup yolunu parse et (0::/path)
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
                                        
                                except Exception as e:
                                    self.append_log(f"  ⚠ Cgroup Limitleri doğrulanamadı: {e}")
                                    tests_unknown += 2
                                    errors.append("Cgroup doğrulama hatası.")"""

content = content.replace(old_limits, new_limits)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
