import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_affinity = """                                        if cpus_allowed:
                                            self.append_log(f"  ✓ CPU Affinity: Çalışabilir CPU'lar izole ({cpus_allowed[0]})")
                                            tests_passed += 1
                                        else:
                                            self.append_log("  ⚠ CPU Affinity: Cpus_allowed_list bulunamadı.")
                                            tests_unknown += 1"""

new_affinity = """                                        if cpus_allowed:
                                            expected_cores = int(self.cpu_combo.get_active_text().split()[0])
                                            # format: 0 for 1 core, 0-1 for 2, 0-3 for 4, etc.
                                            expected_affinity = "0" if expected_cores == 1 else f"0-{expected_cores-1}"
                                            actual_affinity = cpus_allowed[0]
                                            
                                            # some systems return 0,1 instead of 0-1.
                                            if actual_affinity == expected_affinity or (expected_cores == 2 and actual_affinity == "0,1"):
                                                self.append_log(f"  ✓ CPU Affinity: Çalışabilir CPU'lar izole ({actual_affinity})")
                                                tests_passed += 1
                                            else:
                                                self.append_log(f"  ✗ CPU Affinity: HATALI! Beklenen: {expected_affinity}, Gerçek: {actual_affinity}")
                                                errors.append("CPU Affinity izolasyonu hatalı.")
                                        else:
                                            self.append_log("  ⚠ CPU Affinity: Cpus_allowed_list bulunamadı.")
                                            tests_unknown += 1"""

content = content.replace(old_affinity, new_affinity)

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
