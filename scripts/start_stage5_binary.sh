ls
tree /
cd /bin
ls
wc ib.bin
cd ib.bin
echo ERROR_CHECK: cd to file should have failed
cd ..
cp /bin/ib.bin /raw/ib_copy.bin
ls /raw
cp /bin /bin_copy
ls /
cp /nope /tmp
exit