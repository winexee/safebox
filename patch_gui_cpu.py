with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

old_cpu = """        self.cpu_combo = Gtk.ComboBoxText()
        for c in ["1 Çekirdek", "2 Çekirdek", "4 Çekirdek", "6 Çekirdek", "8 Çekirdek"]:
            self.cpu_combo.append_text(c)
        self.cpu_combo.set_active(2)"""

new_cpu = """        import multiprocessing
        self.cpu_combo = Gtk.ComboBoxText()
        cpu_count = multiprocessing.cpu_count()
        valid_cores = [1, 2, 4, 6, 8, 12, 16, 24, 32, 64]
        if cpu_count not in valid_cores:
            valid_cores.append(cpu_count)
        valid_cores = sorted(list(set([c for c in valid_cores if c <= cpu_count])))
        if not valid_cores: valid_cores = [1]
        
        for c in valid_cores:
            self.cpu_combo.append_text(f"{c} Çekirdek")
        
        # Set default to roughly half cores or fallback
        default_idx = len(valid_cores) - 1
        for i, c in enumerate(valid_cores):
            if c >= cpu_count // 2:
                default_idx = i
                break
        self.cpu_combo.set_active(default_idx)"""

content = content.replace(old_cpu, new_cpu)
with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
