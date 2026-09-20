with open("usr/bin/safebox-core", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "--tmpfs /usr/share/applications" in line:
        continue
    if "--ro-bind /usr/share/safebox/guest-apps /usr/share/applications" in line:
        continue
    new_lines.append(line)

with open("usr/bin/safebox-core", "w") as f:
    f.writelines(new_lines)
