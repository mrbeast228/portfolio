#!/bin/sh

# clean up previous user if exists
userdel signer 2>/dev/null
rm -rf /home/signer

# create secured user for signing
adduser --disabled-password --gecos "" signer
chmod 0700 /home/signer

# install signing utils
apt install bsign binutils gzip lzma bzip2 gnupg p7zip-full -y

# move keys to signer
cp -ar "$1" /home/signer/keys

# move repo to signer
cp -ar "$2" /home/signer/repository

# move dononroot.sh to signer
cp -a "$3" /home/signer/sign.sh

# fix owner of everythin under signer
chown -R signer:signer /home/signer

# fix access rules of dononroot.sh
chmod 0755 /home/signer/sign.sh

# add public key to digsig keys
cp /home/signer/keys/pub.key /etc/digsig/xattr_keys/
cp /home/signer/keys/pub.key /etc/digsig/keys/

exit 0
