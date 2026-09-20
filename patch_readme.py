with open("README.md", "r") as f:
    content = f.read()

# Fix GPU section
old_gpu = "4. GPU cihazları hosttan aktarılıyor."
new_gpu = "4. Software Rendering kullanılıyor."
content = content.replace(old_gpu, new_gpu)

old_gpu_reason = "Neden: `/dev/dri` ve NVIDIA cihazları sandbox'a bind ediliyor."
new_gpu_reason = "Neden: İzolasyonu ve kararlılığı artırmak için GPU passthrough kaldırılmış, saf yazılım (software) rendering'e geçilmiştir."
content = content.replace(old_gpu_reason, new_gpu_reason)

# Explicit Seccomp note: Seccomp filtrelemesi yok
if "Seccomp filtrelemesi yok." not in content:
    seccomp_note = """
### Sistem Sınırları (Seccomp)
SafeBox güçlü bir namespace izolasyonu sunar (Mount, PID, UTS, IPC, vb.), ancak şu an için **Seccomp (Secure Computing Mode) BPF filtrelemesi uygulamamaktadır**. Sandbox içerisindeki süreçler ana bilgisayar (host) kernel'ine doğrudan sistem çağrısı yapabilir. VM seviyesinde bir izolasyon hedeflenmemektedir.
"""
    content += seccomp_note

with open("README.md", "w") as f:
    f.write(content)
