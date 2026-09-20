with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

content = content.replace("tests_total = 0\\n            tests_unknown = 0", "tests_total = 0\\n            tests_unknown = 0")

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
