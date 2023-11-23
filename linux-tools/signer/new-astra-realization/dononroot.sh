#!/bin/bash

# allow stop script with Ctrl-C
trap "rm -rf $TMP_DIR $HOME/signtmp; exit" INT

# timeout for killing bsign function on bugs with ELF file
BSIGN_TIMEOUT=20

# function for sign ELF files by key ID and them absolute path
sign_astra() {
	echo "[sign_astra] passed args $1, $2, $3"
	PGOPTS="--batch --pinentry-mode=loopback --passphrase-file=$HOME/astra_rtk_keys/OOO_RTK_password.txt --default-key=$1"
	if [[ $3 -eq 0 ]]; then # here inverted - 0 is true, 1 is false
		timeout -s 9 $BSIGN_TIMEOUT bsign -GNs -E --pgoptions="$PGOPTS" $2 1>&2
	else
		timeout -s 9 $BSIGN_TIMEOUT bsign -GNs -X --pgoptions="$PGOPTS" $2 1>&2
	fi
	return $?
}

# imported from Astra repos: sign for deb packages
sign_deb() {
	#---------------------
	local key_id="$3"
	local pass_file="$HOME/keys/password.txt"
	local DIR_BIN=$1
	local DIR_SIGNED=$2
	#---------------------
	local TMP_DIR=$DIR_SIGNED/tmp$$
	#echo "key_id=$key_id"

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

	local list_of_packages=`find $DIR_BIN -type f -name "*.deb"`
	local list_of_udebs=`find $DIR_BIN -type f -name "*.udeb"`

	for i in $list_of_packages ; do
		local pack_name=`echo $i | awk '{sub(/^.+\//,"",$0) ; a=$0; print a}'`

		echo "Unpacking $pack_name"
		mkdir -p $TMP_DIR/{control,data}

		cp $i $TMP_DIR
		pushd $TMP_DIR &>/dev/null

		fakeroot ar x $pack_name
		local SIGN_LOG=${DIR_SIGNED}/${pack_name}.log

		# Defining archives type
		local data_arch_type=`ls data.tar* | cut -d'.' -f3`
		local control_arch_type=`ls control.tar* | cut -d'.' -f3`
		popd &>/dev/null

		# Unpack data archive
		pushd $TMP_DIR/data &>/dev/null
		case $data_arch_type in
			gz)
			fakeroot tar --same-permissions --same-owner -xzf ../data.tar.gz
			;;
			bz2)
			fakeroot tar --same-permissions --same-owner -xjf ../data.tar.bz2
			;;
			lzma)
			fakeroot tar --same-permissions --same-owner --lzma -xf ../data.tar.lzma
			;;
			xz)
			fakeroot tar --same-permissions --same-owner -xJf ../data.tar.xz
			;;
		esac
		popd &>/dev/null

		# Unpack control archive
		pushd $TMP_DIR/control &>/dev/null
		case $control_arch_type in
			gz)
			fakeroot tar --same-permissions --same-owner -xzf ../control.tar.gz
			;;
			bz2)
			fakeroot tar --same-permissions --same-owner -xjf ../control.tar.bz2
			;;
			lzma)
			fakeroot tar --same-permissions --same-owner --lzma -xf ../control.tar.lzma
			;;
			xz)
			fakeroot tar --same-permissions --same-owner -xJf ../control.tar.xz
			;;
		esac
		popd &>/dev/null

		# Sign files
		super_signer $TMP_DIR/data $key_id 1 0

		# Counting md5sums
		pushd $TMP_DIR/control &>/dev/null
		if [ -e ./md5sums ] ; then
			local filenames=`cat md5sums | awk -F'  ' '{print $2}'`
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
			fakeroot tar --same-permissions --same-owner -czf ../data.tar.gz .
			;;
			bz2)
			fakeroot tar --same-permissions --same-owner -cjf ../data.tar.bz2 .
			;;
			lzma)
			fakeroot tar --same-permissions --same-owner --lzma -cf ../data.tar.lzma .
			;;
			xz)
			fakeroot tar --same-permissions --same-owner -cJf ../data.tar.xz .
			;;
		esac
		popd &> /dev/null

		pushd $TMP_DIR/control &> /dev/null
		case $control_arch_type in
			gz)
			fakeroot tar --same-permissions --same-owner -czvf ../control.tar.gz .
			;;
			bz2)
			fakeroot tar --same-permissions --same-owner -cjvf ../control.tar.bz2 .
			;;
			lzma)
			fakeroot tar --same-permissions --same-owner --lzma -cvf ../control.tar.lzma .
			;;
			xz)
			fakeroot tar --same-permissions --same-owner -cJvf ../control.tar.xz .
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

	local j
	for j in $list_of_udebs; do
		cp $j $DIR_SIGNED
	done
}

# functions for sign every file in directory by it path and key ID
super_signer() {
	# start variables
	local REPO=$1
	local KEY=$2
	local ONLYELFS=$3
	local REMOVE_NON_X86_ELFS=$4
	#echo "KEY=$KEY"

	# create temp dir if not exists
	mkdir -p $HOME/signtmp

	# list all files in repo
	local REPOSITORY_LIST=$(find $REPO -type f)
	local file
	for file in $REPOSITORY_LIST; do
		# get file info
		local info=$(file -b $file)
		local filename=$(basename -- $file)

		# recursivelly sign everything inside tar archives with any compression
		if tar -tf $file > /dev/null; then
			# create unique name for all temp dirs
			local arc_temp_dir="$HOME/signtmp/archive_$(date +%s%N)"
			mkdir $arc_temp_dir

			# unpack
			fakeroot tar -pxf $file -C $arc_temp_dir

			# sign everything inside archive
			super_signer $arc_temp_dir $KEY $ONLYELFS $REMOVE_NON_X86_ELFS

			# hook for TAR packing
			pushd $arc_temp_dir &>/dev/null

			# repack. IMPORTANT: (un)pack with --xattrs flag or you'll lose digital signs!
			fakeroot tar --xattrs -pcf $file .

			# clean up temp
			popd &>/dev/null
			rm -r $arc_temp_dir

		# recursivelly sign elfs inside jar files
		elif [[ "${filename##*.}" = "jar" ]]; then
			# create unique name for all temp dirs
			local arc_temp_dir="$HOME/signtmp/archive_$(date +%s%N)"
			mkdir $arc_temp_dir

			# hook for jar (re)packing
			pushd $arc_temp_dir &>/dev/null

			# unpack
			jar xf $file 1>&2

			# sign only x86 elfs inside jar, remove non-x86
			super_signer $arc_temp_dir $KEY 1 1

			# repack
			rm $file
			# if jar is special only-includable, it doesn't have manifest
			if [[ -f META-INF/MANIFEST.MF ]]; then
				jar 0cmf META-INF/MANIFEST.MF $file . 1>&2
			else
				jar 0cf $file . 1>&2
			fi

			# clean up temp
			popd &>/dev/null
			rm -r $arc_temp_dir

			if [[ ! -f $file ]]; then
				echo "File $file disappeared after proccessing. Maybe you have error in script"
				exit 1
			fi

		# sign everything inside deb archives
		elif grep -q Debian <<< $info; then
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

		# sign only elfs inside wheel packages
		elif grep -q Zip <<< $info; then
			# create unique name for all temp dirs
			local arc_temp_dir="$HOME/signtmp/archive_$(date +%s%N)"
			mkdir $arc_temp_dir

			local ZIP_IS_WHEEL=1

			# try to unpack using wheel. if error, use zip
			if ! python3 -m wheel unpack --dest $arc_temp_dir $file 1>&2; then
				echo "DEBUG: file $file is common zip"
				ZIP_IS_WHEEL=0
				unzip -q $file -d $arc_temp_dir
			fi

			# sign elfs inside archive
			super_signer $arc_temp_dir $KEY 1 $REMOVE_NON_X86_ELFS

			# hook for TAR packing
			pushd $arc_temp_dir &>/dev/null
			# HOOK: cd to single directory inside temporary directory
			if [[ $ZIP_IS_WHEEL -eq 1 ]]; then
				cd *
			fi

			# repack to zip or wheel
			rm -f $file
			if [[ $ZIP_IS_WHEEL -eq 1 ]]; then
				python3 -m wheel pack --dest-dir `dirname $(realpath $file)` . 1>&2
			else
				zip -qr $file .
			fi

			# clean up temp
			popd &>/dev/null
			rm -r $arc_temp_dir

			if [[ ! -f $file ]]; then
				echo "File $file disappeared after proccessing. Maybe you have error in script"
				exit 1
			fi

		# sign another single file
		else
			# HOOK: check if file is ELF and pass return value to sign function
			grep -q ELF <<< $info
			local IS_ELF=$?
			grep -qE '(.*)ELF(.*)(x86|386)(.*)' <<< $info
			local IS_X86_ELF=$?

			# remove file if it's in blacklist
			local BAD_FLAG=0
			local blfile
			for blfile in `cat $HOME/bad.txt`; do
				if grep -q  $blfile <<< $file; then
					BAD_FLAG=1
				fi
			done

			# signer itself
			if [[ $BAD_FLAG -eq 1 || ( $IS_ELF -eq 0 && $IS_X86_ELF -ne 0 && $REMOVE_NON_X86_ELFS -eq 1 ) ]]; then
				rm $file # Remove file if it's non-x86 ELF and remove required, or it's blacklisted
			elif [[ $ONLYELFS -eq 0 || ( $ONLYELFS -eq 1 && $IS_X86_ELF -eq 0 ) ]]; then
				sign_astra $KEY $file $IS_X86_ELF
			fi
		fi
	done
} 2>>$HOME/signer_errors.log

# import secret keys
gpg --import --pinentry-mode=loopback --passphrase-file=$HOME/astra_rtk_keys/OOO_RTK_password.txt $HOME/astra_rtk_keys/OOO_RTK_secret.gpg

# get secret key ID
SECRET_ID=$(gpg --list-secret-keys | grep -E '[A-F0-9]{40}' | awk '{print $1}')

# sign everything in repository
super_signer $HOME/repository $SECRET_ID 1 0

exit 0
