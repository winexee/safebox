import re

with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

old_run = """if which systemd-run >/dev/null 2>&1; then
    taskset -c "$CPU_AFFINITY" systemd-run --user --scope --unit=safebox-app.scope -p "MemoryMax=${RAM_GB}G" -p "CPUQuota=${CPU_QUOTA_VAL}%" bwrap "${BWRAP_ARGS[@]}" /home/safebox/.local/bin/guest-init >> "$ENGINE_LOG" 2>&1 || {
        echo "[HATA] Sandbox başlatılamadı! systemd-run veya bwrap hatası." >> "$ENGINE_LOG"
        exit 107
    }
else
    taskset -c "$CPU_AFFINITY" bwrap "${BWRAP_ARGS[@]}" /home/safebox/.local/bin/guest-init >> "$ENGINE_LOG" 2>&1 || {
        echo "[HATA] Sandbox başlatılamadı! bwrap hatası." >> "$ENGINE_LOG"
        exit 107
    }
fi"""

new_run = """# Gerçek Hata Ayıklama (Debug) İçin Loglama
echo "[BİLGİ] Çalıştırma zinciri başlatılıyor..." >> "$ENGINE_LOG"
# systemd-run FD miras almayabileceği için bwrap doğrudan bash ile sarmalanır ve info-fd 8 aktarımı bash içerisinde yapılır
# veya info-fd doğrudan kullanılacaksa systemd-run sorun çıkarırsa diye doğrudan bwrap'i fallback yaparız.
# Ancak bwrap komutunu loglamak çok önemli.
CMD_BWRAP=(bwrap "${BWRAP_ARGS[@]}" /home/safebox/.local/bin/guest-init)

run_success=0
if which systemd-run >/dev/null 2>&1; then
    # systemd-run --scope fd 8'i kapatabileceği için --info-fd'yi bash içinden açıyoruz
    CMD_SYSTEMD=(systemd-run --user --scope --unit=safebox-app.scope -p "MemoryMax=${RAM_GB}G" -p "CPUQuota=${CPU_QUOTA_VAL}%" bash -c 'exec 8> /tmp/safebox-bwrap.json && exec "$@"' _ "${CMD_BWRAP[@]}")
    
    echo "[BİLGİ] systemd-run ile deneniyor..." >> "$ENGINE_LOG"
    taskset -c "$CPU_AFFINITY" "${CMD_SYSTEMD[@]}" >> "$ENGINE_LOG" 2>&1
    RET=$?
    if [ $RET -eq 0 ]; then
        run_success=1
    else
        echo "[HATA] systemd-run başarısız oldu (Hata Kodu: $RET)" >> "$ENGINE_LOG"
        echo "[BİLGİ] Fallback: Doğrudan bwrap deneniyor..." >> "$ENGINE_LOG"
    fi
fi

if [ $run_success -eq 0 ]; then
    echo "[BİLGİ] Doğrudan bwrap ile deneniyor..." >> "$ENGINE_LOG"
    exec 8> /tmp/safebox-bwrap.json
    taskset -c "$CPU_AFFINITY" "${CMD_BWRAP[@]}" >> "$ENGINE_LOG" 2>&1
    RET=$?
    if [ $RET -ne 0 ]; then
        echo "[HATA] bwrap başarısız oldu (Hata Kodu: $RET)" >> "$ENGINE_LOG"
        exit 107
    fi
fi"""

content = content.replace("BWRAP_ARGS+=(--info-fd 8)\\nexec 8> /tmp/safebox-bwrap.json", "BWRAP_ARGS+=(--info-fd 8)")
content = content.replace(old_run, new_run)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
