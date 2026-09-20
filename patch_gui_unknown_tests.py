with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_else = """                else:
                    self.append_log("✗ Sandbox Runtime: FAIL (Çalışan bir oturum yok)")
            except Exception as e:"""

new_else = """                else:
                    self.append_log("✗ Sandbox Runtime: FAIL (Çalışan bir oturum yok)")
                    errors.append("Sandbox başlatılamadı.")
                    if is_ultra:
                        self.append_log("  ⚠ Cgroup: UNKNOWN")
                        self.append_log("  ⚠ Namespace: UNKNOWN")
                        self.append_log("  ⚠ Filesystem: UNKNOWN")
                        self.append_log("  ⚠ Hostname: UNKNOWN")
                        tests_unknown += 12 # 2 limit + 1 affinity + 6 ns + 1 mount + 1 dev + 1 uts
            except Exception as e:"""

content = content.replace(old_else, new_else)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
