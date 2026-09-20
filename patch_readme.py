with open("README.md", "r") as f:
    content = f.read()

# Replace GPU info
gpu_old = """*   **Donanım Hızlandırma:** GPU donanımı (NVIDIA/Intel) güvenli bir şekilde `bind` edilerek donanım hızlandırma desteği sağlanır."""
gpu_new = """*   **Yazılım Tabanlı İşleme:** GPU donanımı (NVIDIA/Intel) güvenliği zayıflatmamak adına Sandbox'a aktarılmaz. Güvenli izolasyon için %100 CPU tabanlı yazılım (Software Rendering) kullanılır."""

if gpu_old in content:
    content = content.replace(gpu_old, gpu_new)

with open("README.md", "w") as f:
    f.write(content)
