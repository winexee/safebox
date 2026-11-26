# SafeBox Architecture & Developer Guide

## 1. Component Overview

- **`usr/bin/safebox`**: Wrapper launcher setting `NO_AT_BRIDGE=1` and resolving `usr/share/safebox/safebox_gui.py` across Snap (`$SNAP`), local repository checkouts, and `/usr/share/safebox`.
- **`usr/share/safebox/safebox_gui.py`**: GTK3 Control Center (`SafeBoxGUI`). Manages resource settings, permissions (`Seccomp`, `Net`, `Audio`, `Share`), console commands (`help`, `status`, `sysinfo`, `purge`, `developer`, `test`, `test ultra`), and invokes `safebox-core` / `pkexec safebox-setup`.
- **`usr/bin/safebox-core`**: Bash runtime engine. Validates inputs, checks RootFS completeness (`exit 105`), acquires an exclusive per-user `flock` (`exit 106`), spawns an isolated `Xephyr -nolisten tcp` server, generates mock `/proc` & `/etc` identity files and Seccomp BPF bytecode, and launches `bwrap` inside `systemd-run --user --scope` (`fail-closed`: `exit 107` if cgroup scope fails, `exit 109` if seccomp filter fails).
- **`usr/share/safebox/seccomp_filter.py`**: Generates classic BPF (`struct sock_filter[]`) for `bwrap --seccomp FD`. Uses `libseccomp.so.2` via `ctypes` when available, with a pure-Python cBPF fallback for `x86_64` and `aarch64`. Denies high-risk syscalls with `-EPERM`.
- **`usr/share/safebox/guest-init`**: Entrypoint executed inside `bwrap` as UID/GID `1000` (`safebox`). Sets up ephemeral `/home/safebox`, desktop `.desktop` launchers, GTK2/3 themes, a mock system D-Bus daemon (`--fork`), applies `dconf` settings inside `dbus-run-session`, and runs `cinnamon-session --session cinnamon2d`.
- **`usr/bin/safebox-setup`**: Root-only atomic RootFS builder (`debootstrap` Ubuntu 24.04 `noble` + Cinnamon desktop packages). Unmounts any stale bind mounts safely before cleanup and restores `.old` backups on failure.
- **`usr/share/safebox/safebox-guest-blocker`**: Bind-mounted over `/home/safebox/.local/bin/safebox` inside the guest to prevent re-invoking `safebox` inside the sandbox.

---

## 2. Execution Flow

```
safebox
  └─> safebox_gui.py
        ├─ (if RootFS missing: exit 105) ─> pkexec safebox-setup ─> /var/lib/safebox/rootfs
        └─> safebox-core <RAM_GB> <CPU_CORES> <RES> <SHARE> <AUDIO> <NET> [SECCOMP]
              ├─ Per-user runtime dir ($XDG_RUNTIME_DIR/safebox): lock, pid, bwrap.json, seccomp.bpf
              ├─ Xephyr :<d> -nolisten tcp -screen <RES> -extension MIT-SHM
              ├─ seccomp_filter.py ─> safebox-seccomp.bpf
              └─ taskset -c 0-<N> systemd-run --user --scope --unit=safebox-app.scope
                   └─ bwrap (user,pid,uts,ipc,cgroup[,net]) --ro-bind rootfs / --seccomp 7 --info-fd 8
                        └─ guest-init ─> mock system dbus ─> dbus-run-session ─> cinnamon2d
```

---

## 3. Exit Codes (`safebox-core`)

| Code | Meaning |
|------|---------|
| `0` | Normal shutdown (including closing the Xephyr window cleanly) |
| `101` | No free X11 display (`:10`–`:99`) available |
| `102` | `Xephyr` or `bwrap` binary missing, or Xephyr failed/timed out on startup |
| `103` | Required file/directory missing under `SHARE_DIR` |
| `104` | Required file missing under `guest-etc/` |
| `105` | RootFS missing or incomplete (`/var/lib/safebox/rootfs/.safebox-rootfs-complete`) |
| `106` | Another SafeBox session already holds `safebox.lock` |
| `107` | Cgroup v2 / `systemd-run` enforcement failed (fail-closed) |
| `108` | Invalid CLI argument (RAM, CPU, resolution, or flag) |
| `109` | Seccomp BPF filter generation failed while `SECCOMP=1` |

---

## 4. Automated Testing

Run the unit and sandbox-enforcement test suite:

```bash
python3 -m unittest discover -s tests -v
```
