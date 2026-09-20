import datetime
with open("debian/changelog", "r") as f:
    content = f.read()

new_changelog = """safebox (1.7.24-1) stable; urgency=high

  * Complete sandbox architecture overhaul.
  * Fail-closed cgroups and dbus isolation.
  * Cinnamon rendering and theme fixes.

 -- Mehmet Akif Sahin <mehmet-akif@localhost>  """ + datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0300") + """

""" + content

with open("debian/changelog", "w") as f:
    f.write(new_changelog)
