#!/bin/bash

# make possible exit on Ctrl-C
trap "cp /home/signer/signer_errors.log signer_errors.log; rm -rf /home/signer; userdel signer; chown $(stat -c '%U' $0):$(stat -c '%G' $0) signer_errors.log; exit" INT

if [[ -e /home/signer ]]; then
	echo "ERROR: user 'signer' already exists in system, please delete it before running script!"
	exit 1
fi

# create secured user for signing
adduser --disabled-password --gecos "" signer
chmod 0700 /home/signer

# install signing utils
apt install bsign binutils gzip lzma bzip2 gnupg p7zip-full -y

# move keys to signer
cp -ar "$1" /home/signer/astra_rtk_keys

# move repo to signer
cp -ar "$2" /home/signer/repository

# move dononroot.sh to signer
cp -a "$3" /home/signer/dononroot.sh

# move bad.txt to signer
if [[ -e "$4" ]]; then
	cp -a "$4" /home/signer/bad.txt
else
	echo "WARNING: bad.txt doesn't exists, no files will blacklisted!"
	echo > /home/signer/bad.txt
fi

# fix owner of everythin under signer
chown -R signer:signer /home/signer

# fix access rules of dononroot.sh
chmod 0755 /home/signer/dononroot.sh

# add public key to digsig keys
cp /home/signer/astra_rtk_keys/OOO_RTK_pub.key /etc/digsig/xattr_keys/

# run signer
su signer -c 'cd ~; ./dononroot.sh'

# return signed
cp -ar /home/signer/repository $5

# copy logs
cp /home/signer/signer_errors.log signer_errors.log

# fix rights
chown -R `stat -c "%U" $0`:`stat -c "%G" $0` $5 signer_errors.log

# remove signer data
rm -rf /home/signer
userdel -f signer

exit 0
