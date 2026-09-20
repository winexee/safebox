with open("usr/share/safebox/safebox_gui.py", "r") as f:
    lines = f.readlines()

new_lines = []
in_namespace_block = False
for line in lines:
    if "# Filesystem & Namespace İzolasyon Kontrolü" in line:
        in_namespace_block = True
    
    if in_namespace_block:
        if line.startswith("                                "):  # 32 spaces
            # Unindent by 12 spaces (so it aligns with `if is_ultra:`)
            new_lines.append(line[12:])
        else:
            new_lines.append(line)
            if not line.strip() or line.strip() == "else:":
                pass
            elif line.startswith("                        else:"):
                # Oh wait, there is an `else` block for cgroup check
                in_namespace_block = False
    else:
        new_lines.append(line)

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.writelines(new_lines)
