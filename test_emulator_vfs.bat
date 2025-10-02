@echo off
REM Тест разных вариантов VFS

echo "--- Testing Minimal VFS ---"
python conf_prac1.py --vfs "VFS_minimal.csv" --log "log_vfs_minimal.csv" --script "start_script_vfs.sh"

echo "--- Testing Nested VFS ---"
python conf_prac1.py --vfs "VFS_nested.csv" --log "log_vfs_nested.csv" --script "start_script_vfs.sh"

echo "--- Testing Binary VFS ---"
python conf_prac1.py --vfs "VFS_binary.csv" --log "log_vfs_binary.csv" --script "start_script_vfs.sh"


