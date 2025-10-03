# Тестовый скрипт для VFS_nested
ls
cd /etc
ls
cd settings.ini
echo "ERROR_CHECK: cd to file should have failed"
cd ..
cd /home/user
echo New note > new.txt
ls
wc new.txt
cd /nope
echo "ERROR_CHECK: cd to /nope should have failed"
exit


