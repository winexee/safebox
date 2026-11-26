# 🛡️ SafeBox - Isolated Container Desktop (Cinnamon)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20LTS-orange.svg)](https://ubuntu.com/)
[![Release](https://img.shields.io/badge/Release-v1.7.30-brightgreen.svg)](https://github.com/winexee/safebox/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Bash](https://img.shields.io/badge/Bash-5.0+-red.svg)](https://www.gnu.org/software/bash/)

🇹🇷 **[Türkçe Dokümantasyon (README.md)](README.md)** | 🏗️ **[Architecture & Developer Guide (docs/ARCHITECTURE.md)](docs/ARCHITECTURE.md)**

SafeBox is a **Bubblewrap**-based Linux **container (namespace)** desktop workspace designed to inspect untrusted files, browse in an ephemeral environment, and keep the host filesystem protected.

> ⚠️ **WARNING - Isolation Boundaries:** SafeBox is **NOT** a Virtual Machine (VM). It shares the host Linux kernel and does not provide hardware virtualization. GPU device nodes (`/dev/dri`, NVIDIA) are not passed through; instead, Cinnamon 2D runs with software rendering (`CINNAMON_SOFTWARE_RENDERING=1`) inside an isolated Xephyr (`-nolisten tcp`) nested X server.

---

## ✨ Key Features

- **Namespace Isolation:** Separates User, PID, UTS, IPC, and Mount namespaces via Bubblewrap (`bwrap`).
- **Seccomp BPF Filtering:** Enabled by default via `seccomp_filter.py`; denies high-risk syscalls (`unshare`, `setns`, `mount`, `bpf`, `userfaultfd`, `io_uring_*`, `kexec_load`, `keyctl`, `ptrace`, etc.) with `-EPERM`.
- **Fail-Closed Resource Limits:** Enforces Cgroup v2 `MemoryMax`, `CPUQuota`, and CPU affinity (`taskset`) through `systemd-run --user --scope`. Refuses to launch without cgroup enforcement.
- **Optional Air-Gapped Networking:** Toggle between shared host networking and `--unshare-net` full network isolation.
- **Read-Only Isolated RootFS:** Uses a dedicated `debootstrap` Ubuntu 24.04 (`noble`) rootfs mounted read-only, with ephemeral RAM (`tmpfs`) overlays for `/tmp`, `/var`, `/run`, and `/home`.

---

## 🚀 Installation

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install bubblewrap libseccomp2 xserver-xephyr dbus-x11 python3 python3-gi gir1.2-gtk-3.0 debootstrap pkexec x11-utils
```

### 2. Install SafeBox

```bash
git clone https://github.com/winexee/safebox.git
cd safebox
sudo cp usr/bin/safebox-core /usr/bin/
sudo cp usr/bin/safebox-setup /usr/bin/
sudo cp -r usr/share/safebox /usr/share/
sudo cp usr/bin/safebox /usr/bin/
```

### 3. Build the Guest RootFS

```bash
sudo safebox-setup
```

---

## 💻 Usage & Diagnostics

Launch the GTK3 control center:

```bash
safebox
```

In the **Console & Logs** tab, run `developer` followed by `test` or `test ultra` while a session is active to verify RootFS integrity, cgroup v2 `MemoryMax`/`CPUQuota`, CPU affinity, namespaces, `mountinfo`, `/dev`, UTS hostname, `NoNewPrivs=1`, and `Seccomp=2`.

Run the automated test suite locally:

```bash
python3 -m unittest discover -s tests -v
```

---

## 🛡️ Security Threat Model & Trade-offs

- **Shared Kernel:** Kernel exploits bypass container boundaries.
- **Seccomp Denylist:** Blocks dangerous kernel/namespace/debug syscalls by default while keeping desktop apps working; it does not replace VM isolation.
- **X11 / Xephyr:** Host `:0` X11 socket is not bound into the container; only the isolated Xephyr (`-nolisten tcp`) socket is mounted. Still, Xephyr runs as a host X11 client.
- **Audio Sockets:** When enabled (`Audio=1`), host PulseAudio or PipeWire sockets are bind-mounted, exposing host audio/microphone access surface.
- **Snap Confinement:** Uses `confinement: classic` intentionally so Bubblewrap, `systemd-run`, and `pkexec` can manage namespaces and `/var/lib/safebox/rootfs`.

---

## 📞 License

Released under the **MIT License**. Author: Mehmet Akif Şahin ([winexee](https://github.com/winexee/safebox)).
