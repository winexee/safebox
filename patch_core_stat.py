with open("usr/bin/safebox-core", "r") as f:
    content = f.read()

old_stat = """rm -f "${PROC_MOCK_DIR}/cpuinfo" "${PROC_MOCK_DIR}/stat"
echo "cpu  2000 0 2000 20000 0 0 0 0 0 0" > "${PROC_MOCK_DIR}/stat"

for ((i=0; i<CPU_CORES; i++)); do"""

new_stat = """rm -f "${PROC_MOCK_DIR}/cpuinfo" "${PROC_MOCK_DIR}/stat"
echo "cpu  2000 0 2000 20000 0 0 0 0 0 0" > "${PROC_MOCK_DIR}/stat"

for ((i=0; i<CPU_CORES; i++)); do"""

# We'll just replace the closing brace of the loop to add btime
old_loop_end = """    echo "cpu$i 1000 0 1000 10000 0 0 0 0 0 0" >> "${PROC_MOCK_DIR}/stat"
done"""

new_loop_end = """    echo "cpu$i 1000 0 1000 10000 0 0 0 0 0 0" >> "${PROC_MOCK_DIR}/stat"
done
echo "btime $(date +%s)" >> "${PROC_MOCK_DIR}/stat"
echo "processes 1000" >> "${PROC_MOCK_DIR}/stat"
echo "procs_running 1" >> "${PROC_MOCK_DIR}/stat"
echo "procs_blocked 0" >> "${PROC_MOCK_DIR}/stat"
"""

content = content.replace(old_loop_end, new_loop_end)

with open("usr/bin/safebox-core", "w") as f:
    f.write(content)
