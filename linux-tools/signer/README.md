# Linux file signer
This tool signs Linux file with digital signature using bsign utility

## Requirments
+ bsign
+ gnupg
+ grep

This utility was used and tested under Astra Linux and other Debian-like systems in real case

## Usage
0. Install required utilities
1. Create your own public-private key pair and put them to `pub.key` and `secret.gpg` accordingly. Put password of private key to `password.txt`. Put these 3 files to some directory (further `KEY_DIR`)
2. Prepare directory with files you want to sign. Files can be ELF, archives, packages or any other type. Signing of nested archives is also available. Further this directory will be `REPO_DIR`
3. Use files `prepare.sh` and `sign.sh` - run next shell commands as root:
   ```
   # wget https://github.com/spbupos/projects-database/raw/main/linux-tools/signer/prepare.sh
   # wget https://github.com/spbupos/projects-database/raw/main/linux-tools/signer/sign.sh
   # chmod 0755 prepare.sh
   # ./prepare.sh KEY_DIR REPO_DIR sign.sh
   ```
   `prepare.sh` will create user `signer` with home directory in 0700 mode, add public key to the system and copy your repo and `sign.sh` file in 0755 mode into this temporary user
4. Switch to `signer` user and run the signer:
   ```
   # su signer
   $ cd
   $ ./sign.sh
   ```
   Script will automatically sign every file in directory using your private key, and also unpack *.tar.gz and *.deb files and sign everything inside them
5. Exit from `signer`, copy signed packages and clean up:
   ```
   $ exit
   # cp -a /home/signer/repository /path/to/signed_packages
   # userdel signer
   # rm -rf /home/signer
   ```

## Tips
+ ELF files signing using their headers and won't lose their signature in any case. Supported x86(-64) and ARM(64) ELFs
+ not-ELF files are signed using xattrs. To keep them when transfering your repository to another machines, you should pack and unpack repository in *.tar(.gz) file with `--xattrs` flag:
  ```
  (machine-1)# tar --xattrs -pczf /path/to/signed_repo.tar.gz /path/to/signer_repo
  ...
  (machine-2)# tar --xattrs -pxzf /path/to/signed_repo.tar.gz /path/to/signer_repo
  ```
+ If your repo contains *.tar.gz files, they will be unpacked, recursivelly signed inside, and repacked with automatically using `--xattrs` flag. Please don't forget it on unpacking
+ non-tar archives (*.zip, *.rar) signing as common non-ELF files (not unpacking) due to they can't keep xattrs

## Issues
+ *.deb packages don't keep their xattrs on unpacking due to `dpkg-deb` has built-in tar unpacker, which does not support xattrs

#### New realization for specific Astra Linux case, with signing ELFs inside wheels and JARs, placed in `new-astra-realization` directory
#### If your system doesn't have `bsign` in repos, you can use static 20-years old build: `cd bsign-root; sudo chown -R root:root .; sudo cp -a . /`
