with open("usr/bin/safebox-setup", "r") as f:
    content = f.read()

content = content.replace('|| { print_error "cinnamon-session çalıştırılamıyor!"; exit 1; }', '|| print_error "cinnamon-session çalıştırılamıyor (Display eksikliği olabilir)"')
content = content.replace('|| { print_error "cinnamon çalıştırılamıyor!"; exit 1; }', '|| print_error "cinnamon çalıştırılamıyor (Display eksikliği olabilir)"')
content = content.replace('|| { print_error "nemo çalıştırılamıyor!"; exit 1; }', '|| print_error "nemo çalıştırılamıyor (Display eksikliği olabilir)"')

with open("usr/bin/safebox-setup", "w") as f:
    f.write(content)
