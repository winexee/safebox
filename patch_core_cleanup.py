with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

old_cleanup = """cleanup() {
    echo "[BİLGİ] Oturum kapatılıyor..." >> "$ENGINE_LOG"
    kill -9 "$XEPHYR_PID" 2>/dev/null || true
    rm -f "/tmp/.X${TARGET_DISP#:}-lock" 2>/dev/null || true
    rm -rf "/tmp/.X11-unix/X${TARGET_DISP#:}" 2>/dev/null || true
    rm -f "/tmp/safebox-core.pid" 2>/dev/null || true

    echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Oturum Kapatıldı ===" >> "$ENGINE_LOG"
}"""

new_cleanup = """cleanup() {
    echo "[BİLGİ] Oturum kapatılıyor..." >> "$ENGINE_LOG"
    systemctl --user stop safebox-app.scope 2>/dev/null || true
    kill -9 "$XEPHYR_PID" 2>/dev/null || true
    rm -f "/tmp/.X${TARGET_DISP#:}-lock" 2>/dev/null || true
    rm -rf "/tmp/.X11-unix/X${TARGET_DISP#:}" 2>/dev/null || true
    rm -f "/tmp/safebox-core.pid" 2>/dev/null || true
    rm -f "/tmp/safebox.lock" 2>/dev/null || true

    echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Oturum Kapatıldı ===" >> "$ENGINE_LOG"
}

# Xephyr penceresi kapandığında (kullanıcı kapattığında) Sandbox'ı otomatik sonlandır
(
    while kill -0 "$XEPHYR_PID" 2>/dev/null; do
        sleep 1
    done
    echo "[BİLGİ] Xephyr kapandı. Sandbox durduruluyor..." >> "$ENGINE_LOG"
    kill -TERM $$ 2>/dev/null || true
) &
"""

content = content.replace(old_cleanup, new_cleanup)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
