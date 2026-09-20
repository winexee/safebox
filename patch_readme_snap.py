with open("README.md", "r") as f:
    content = f.read()

snap_note = """
### Snap Confinement Notu
SafeBox Snap paketi olarak dağıtıldığında `confinement: classic` (klasik izolasyon) kullanır. Snap'in kendi strict izolasyon (apparmor) katmanı SafeBox'ın bwrap yeteneklerini engellememesi için kasıtlı olarak classic yapılmıştır. Gerçek güvenlik ve izolasyon sınırı Snap tarafından değil, SafeBox'ın çalıştırdığı Bubblewrap ve namespace mimarisi tarafından sağlanmaktadır.
"""
if "Snap Confinement Notu" not in content:
    content += snap_note

with open("README.md", "w") as f:
    f.write(content)
