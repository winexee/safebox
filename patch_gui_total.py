import re

with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

content = content.replace(
    'tests_unknown += 12 # 2 limit + 1 affinity + 6 ns + 1 mount + 1 dev + 1 uts',
    'tests_total += 12\n                        tests_unknown += 12'
)

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
