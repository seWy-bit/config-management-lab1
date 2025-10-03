@echo off
REM Тест разных вариантов VFS

echo "--- Testing Minimal VFS ---"
python conf_prac1.py --vfs "vfs/VFS_minimal.csv" --log "logs/log_vfs_minimal.csv" --script "scripts/start_stage4_minimal.sh"

echo "--- Testing Nested VFS ---"
python conf_prac1.py --vfs "vfs/VFS_nested.csv" --log "logs/log_vfs_nested.csv" --script "scripts/start_stage4_nested.sh"

echo "--- Testing Binary VFS ---"
python conf_prac1.py --vfs "vfs/VFS_binary.csv" --log "logs/log_vfs_binary.csv" --script "scripts/start_stage4_binary.sh"
