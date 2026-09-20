import re

with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

# We need to find the run_success block and remove the fallback
# Currently it is:
# if [ $run_success -eq 0 ]; then
#     echo "[BİLGİ] Doğrudan bwrap ile deneniyor..." >> "$ENGINE_LOG"
#     exec 8> /tmp/safebox-bwrap.json
#     set +e
#     taskset -c "$CPU_AFFINITY" "${CMD_BWRAP[@]}" >> "$ENGINE_LOG" 2>&1
#     RET=$?
#     set -e
#     if [ $RET -ne 0 ]; then
#         echo "[HATA] bwrap başarısız oldu (Hata Kodu: $RET)" >> "$ENGINE_LOG"
#         exit 107
#     fi
# fi

fallback_regex = re.compile(r'if \[ \$run_success -eq 0 \]; then\s+echo "\[BİLGİ\] Doğrudan bwrap ile deneniyor.*?fi\nfi', re.DOTALL)

def replace_fallback(match):
    return """if [ $run_success -eq 0 ]; then
    echo "[HATA] Güvenlik politikası (Cgroup/systemd-run) uygulanamadığı için başlatma iptal edildi." >> "$ENGINE_LOG"
    exit 107
fi"""

content = fallback_regex.sub(replace_fallback, content)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
