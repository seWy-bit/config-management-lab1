# Тестовый скрипт для VFS_binary
ls
tree /
cd bin
ls
wc ib.bin
cd ib.bin
echo OOPS > note.txt
ls
wc note.txt
cd /nope
echo "ERROR_CHECK: cd /nope should have failed"
exit
