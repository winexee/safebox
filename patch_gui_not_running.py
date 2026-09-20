with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

content = content.replace('self.append_log("ℹ Arka Plan Süreci: Çalışan bir oturum yok")', 'self.append_log("✗ Sandbox Runtime: FAIL (Çalışan bir oturum yok)")')

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
