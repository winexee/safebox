with open("usr/share/safebox/safebox_gui.py", "r") as f:
    content = f.read()

content = content.replace("tests_passed = 0\\n            tests_total = 0\\n            errors = []", "tests_passed = 0\\n            tests_total = 0\\n            tests_unknown = 0\\n            errors = []")

old_result = """            # Sonuç
            if tests_total > 0:
                self.append_log(f"\\n[SONUÇ] {tests_passed}/{tests_total} test geçti.")"""

new_result = """            # Sonuç
            if tests_total > 0:
                tests_failed = tests_total - tests_passed - tests_unknown
                self.append_log(f"\\n[SONUÇ] PASS: {tests_passed} | FAIL: {tests_failed} | UNKNOWN: {tests_unknown} (Toplam: {tests_total} Test)")"""

content = content.replace(old_result, new_result)

with open("usr/share/safebox/safebox_gui.py", "w") as f:
    f.write(content)
