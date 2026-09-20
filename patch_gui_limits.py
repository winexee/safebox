import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_limits = """                            # Gerçek Limit Kontrolü (Sadece Ultra)
                            if is_ultra:
                                limit_res = subprocess.run(["systemctl", "--user", "show", "safebox-app.scope", "--property=MemoryMax,CPUQuotaPerSecUSec"], capture_output=True, text=True, timeout=2).stdout
                                self.append_log("  - Uygulanan Cgroup Limitleri:")
                                for line in limit_res.strip().split("\\n"):
                                    self.append_log(f"    {line}")"""

new_limits = """                            # Gerçek Limit Kontrolü (Sadece Ultra)
                            if is_ultra:
                                tests_total += 2
                                try:
                                    limit_res = subprocess.run(["systemctl", "--user", "show", "safebox-app.scope", "--property=MemoryMax,CPUQuotaPerSecUSec"], capture_output=True, text=True, timeout=2).stdout
                                    parsed_limits = {}
                                    for line in limit_res.strip().split("\\n"):
                                        if "=" in line:
                                            k, v = line.split("=", 1)
                                            parsed_limits[k] = v.strip()
                                            
                                    expected_ram = str(int(self.ram_combo.get_active_id().replace("GB","")) * 1024**3)
                                    expected_cpu = str(int(self.cpu_combo.get_active_id()) * 100000)
                                    
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

content = content.replace(old_limits, new_limits)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
