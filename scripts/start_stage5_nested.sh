ls
tree /
cd /etc/conf
wc settings.ini
cd settings.ini
echo ERROR_CHECK: cd to file should have failed
cd /home/user
echo NewNote > new.txt
wc new.txt
cp /etc /home/user/notes.txt
exit