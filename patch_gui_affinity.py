with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_affinity = """                                    if cpus_allowed:
                                        self.append_log(f"  ✓ CPU Affinity: Çalışabilir CPU'lar izole ({cpus_allowed[0]})")
                                        tests_passed += 1
                                    else:"""

new_affinity = """                                    if cpus_allowed:
                                        # Calculate expected affinity
                                        selected_cpu_cores = int(self.cpu_combo.get_active_text().split()[0])
                                        expected_affinity = f"0-{selected_cpu_cores - 1}" if selected_cpu_cores > 1 else "0"
                                        if cpus_allowed[0] == expected_affinity:
                                            self.append_log(f"  ✓ CPU Affinity: Çalışabilir CPU'lar tam doğrulandı ({cpus_allowed[0]})")
                                            tests_passed += 1
                                        else:
                                            self.append_log(f"  ✗ CPU Affinity Sızıntısı: Beklenen: {expected_affinity}, Bulunan: {cpus_allowed[0]}")
                                            errors.append(f"CPU Affinity Yanlış: Beklenen {expected_affinity}, Bulunan {cpus_allowed[0]}")
                                    else:"""

content = content.replace(old_affinity, new_affinity)

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
