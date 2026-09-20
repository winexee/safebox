with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

content = content.replace(
    'taskset -c "$CPU_AFFINITY" "${CMD_SYSTEMD[@]}" >> "$ENGINE_LOG" 2>&1\n    RET=$?',
    'set +e\n    taskset -c "$CPU_AFFINITY" "${CMD_SYSTEMD[@]}" >> "$ENGINE_LOG" 2>&1\n    RET=$?\n    set -e'
)

content = content.replace(
    'taskset -c "$CPU_AFFINITY" "${CMD_BWRAP[@]}" >> "$ENGINE_LOG" 2>&1\n    RET=$?',
    'set +e\n    taskset -c "$CPU_AFFINITY" "${CMD_BWRAP[@]}" >> "$ENGINE_LOG" 2>&1\n    RET=$?\n    set -e'
)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
