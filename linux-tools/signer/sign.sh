#!/bin/bash

# function for sign ELF files by key ID and them absolute path
sign_astra() {
	PGOPTS="--batch --pinentry-mode=loopback --passphrase-file=$HOME/keys/password.txt --default-key=$1"
	if [[ $3 -eq 0 ]]; then
		timeout -s 9 10 bsign -N -s --pgoptions="$PGOPTS" $2
	else
		timeout -s 9 10 bsign -N -s --xattr --pgoptions="$PGOPTS" $2
	fi
	return $?
}

# imported from Astra repos: sign for deb packages
sign_deb() {
	#---------------------
	key_id="$3"
	pass_file="$HOME/keys/password.txt"
	DIR_BIN=$1
	DIR_SIGNED=$2
	#---------------------
	TMP_DIR=$DIR_SIGNED/tmp$$

	if [ -z $DIR_BIN ] ; then
		echo "Specify original directory as first argument."
		exit 1
	fi

	if [ -z $DIR_SIGNED ] ; then
		echo "Specify destination directory as second argument."
		exit 1
	fi

	if [ ! -e $DIR_BIN ] ; then
		echo "Original directory $DIR_BIN doesn't exist."
		exit 1
	fi

	list_of_packages=`find $DIR_BIN -type f -name "*.deb"`
	list_of_udebs=`find $DIR_BIN -type f -name "*.udeb"`

	for i in $list_of_packages ; do
		pack_name=`echo $i | awk '{sub(/^.+\//,"",$0) ; a=$0; print a}'`
		echo "Unpacking $pack_name"
		mkdir -p $TMP_DIR/{control,data}
		cp $i $TMP_DIR
		pushd $TMP_DIR &>/dev/null
		fakeroot ar x $pack_name
		SIGN_LOG=${DIR_SIGNED}/${pack_name}.log

		# Defining archives type
		data_arch_type=`ls data.tar* | cut -d'.' -f3`
		control_arch_type=`ls control.tar* | cut -d'.' -f3`
		popd &>/dev/null

		# Unpack data archive
		pushd $TMP_DIR/data &>/dev/null
		case $data_arch_type in
			gz)
			fakeroot tar --xattrs --same-permissions --same-owner -xzf ../data.tar.gz
			;;
			bz2)
			fakeroot tar --xattrs --same-permissions --same-owner -xjf ../data.tar.bz2
			;;
			lzma)
			fakeroot tar --xattrs --same-permissions --same-owner --lzma -xf ../data.tar.lzma
			;;
			xz)
			fakeroot tar --xattrs --same-permissions --same-owner -xJf ../data.tar.xz
			;;
		esac
		popd &>/dev/null

		# Unpack control archive
		pushd $TMP_DIR/control &>/dev/null
		case $control_arch_type in
			gz)
			fakeroot tar --xattrs --same-permissions --same-owner -xzf ../control.tar.gz
			;;
			bz2)
			fakeroot tar --xattrs --same-permissions --same-owner -xjf ../control.tar.bz2
			;;
			lzma)
			fakeroot tar --xattrs --same-permissions --same-owner --lzma -xf ../control.tar.lzma
			;;
			xz)
			fakeroot tar --xattrs --same-permissions --same-owner -xJf ../control.tar.xz
			;;
		esac
		popd &>/dev/null

		# Sign files
		pushd $TMP_DIR/data &> /dev/null
		list=`find . -type f`
		for file in $list ; do
			info=$(file "$file")
			oldstat=`stat -c %a $file`

			# WARNING: we can sign file inside deb package only if it is ELF for x86
			if grep -E '(.*)ELF(.*)(x86|386)(.*)' <<< $info; then
				sign_astra $key_id $file 0
			fi

			newstat=`stat -c %a $file`
			[ $newstat != $oldstat ] && echo "BSIGN_CHMOD_ERROR in $file" >> ${SIGN_LOG} 2>&1
		done
		popd &> /dev/null

		# Counting md5sums
		pushd $TMP_DIR/control &>/dev/null
		if [ -e ./md5sums ] ; then
			filenames=`cat md5sums | awk -F'  ' '{print $2}'`
			popd &>/dev/null
			pushd $TMP_DIR/data &> /dev/null
			for j in $filenames; do
				echo `md5sum $j` >> $TMP_DIR/control/md5sums.new
			done
			sed -e 's/\ /\ \ /g' $TMP_DIR/control/md5sums.new > $TMP_DIR/control/md5sums.new_mod
			popd &> /dev/null
			mv -f $TMP_DIR/control/md5sums.new_mod $TMP_DIR/control/md5sums &> /dev/null
			rm -f $TMP_DIR/control/md5sums.new &> /dev/null
		fi

		# Packing back in deb
		pushd $TMP_DIR/data &> /dev/null
		case $data_arch_type in
			gz)
			fakeroot tar --xattrs --same-permissions --same-owner -czf ../data.tar.gz .
			;;
			bz2)
			fakeroot tar --xattrs --same-permissions --same-owner -cjf ../data.tar.bz2 .
			;;
			lzma)
			fakeroot tar --xattrs --same-permissions --same-owner --lzma -cf ../data.tar.lzma .
			;;
			xz)
			fakeroot tar --xattrs --same-permissions --same-owner -cJf ../data.tar.xz .
			;;
		esac
		popd &> /dev/null

		pushd $TMP_DIR/control &> /dev/null
		case $control_arch_type in
			gz)
			fakeroot tar --xattrs --same-permissions --same-owner -czvf ../control.tar.gz .
			;;
			bz2)
			fakeroot tar --xattrs --same-permissions --same-owner -cjvf ../control.tar.bz2 .
			;;
			lzma)
			fakeroot tar --xattrs --same-permissions --same-owner --lzma -cvf ../control.tar.lzma .
			;;
			xz)
			fakeroot tar --xattrs --same-permissions --same-owner -cJvf ../control.tar.xz .
			;;
		esac
		popd &> /dev/null
		pushd $TMP_DIR &> /dev/null
		fakeroot ar rcs $TMP_DIR/$pack_name debian-binary control.tar.$control_arch_type data.tar.$data_arch_type &> /dev/null
		cp ${pack_name}  $DIR_SIGNED/${pack_name%.deb}_signed.deb &> /dev/null
		echo "Creating $DIR_SIGNED/${pack_name%.deb}_signed.deb"
		popd &> /dev/null
		rm -rf $TMP_DIR  &> /dev/null
	done

	for j in $list_of_udebs; do
		cp $j $DIR_SIGNED
	done
}

# functions for sign every file in directory by it path and key ID
super_signer() {
	# start variables
	local REPO=$1
	local KEY=$2

	# create temp dir if not exists
	mkdir -p $HOME/signtmp

	# list all files in repo
	local REPOSITORY_LIST=$(find $REPO -type f)
	local file
	for file in $REPOSITORY_LIST; do
		# get file info
		local info=$(file $file)

		# recursivelly sign everything inside tar archives
		if grep -E '(.*)gzip(.*)data(.*)' <<< $info; then
			# create unique name for all temp dirs
			local arc_temp_dir="$HOME/signtmp/archive_$(date +%s%N)"
			mkdir $arc_temp_dir

			# unpack
			fakeroot tar -pxzf $file -C $arc_temp_dir

			# sign anything inside archive
			super_signer $arc_temp_dir $KEY

			# hook for TAR packing
			pushd $arc_temp_dir &>/dev/null

			# repack. IMPORTANT: (un)pack with --xattrs flag or you'll lose digital signs!
			fakeroot tar --xattrs -pczf $file .

			# clean up temp
			popd &>/dev/null
			rm -r $arc_temp_dir

		# sign everything inside deb archives
		elif grep Debian <<< $info; then
			# create temp dirs
			mkdir $HOME/signtmp/debs
			mkdir $HOME/signtmp/debs_signed

			# copy deb to temp
			cp $file $HOME/signtmp/debs/

			# sign deb with Astra script
			sign_deb $HOME/signtmp/debs $HOME/signtmp/debs_signed $KEY

			# move signed deb back
			cp $HOME/signtmp/debs_signed/*.deb $file

			# remove temp
			rm -rf $HOME/signtmp/debs*

		# sign another single file
		else
			# HOOK: check if file is ELF and pass return value to sign function
			grep -E '(.*)ELF(.*)(x86|386)(.*)' <<< $info
			ISELF=$?

			# signer itself
			sign_astra $KEY $file $ISELF
		fi
	done
} 2>$HOME/signer_errors.log

# import secret keys
gpg --import --pinentry-mode=loopback --passphrase-file=$HOME/keys/password.txt $HOME/keys/secret.gpg

# get secret key ID
SECRET_ID=$(gpg --list-secret-keys | grep -E '[A-F0-9]{40}' | awk '{print $1}')

# sign everything in repository
super_signer $HOME/repository $SECRET_ID

exit 0
