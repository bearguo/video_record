#!/bin/bash
DEPLOY_DIR="deploy/home/share/video_record"
INIT_SCRIPT="record"
if [ -z "$1" ];then
	echo "Please enter one parameter:<version>"
	echo -e "Example:Build with version 1.1\n./build 1.1"
	echo -e "Example:If the version file exsits.Use f as the second parameter to overwrite it\n./build 1.1 f"
	exit
fi
VERSION=$1
echo $VERSION
copy_files() {
	mkdir -p $DEPLOY_DIR
	cp libUDP2HLS.so.* $DEPLOY_DIR
	cp dist/tsserver $DEPLOY_DIR
	cp replay.conf $DEPLOY_DIR
}
pack() {
	case "$1" in
		f | force )
		  FORCE="-f"
			;;
		*)
			FORCE=""
	esac
	fpm -s dir -t deb --verbose --deb-init $INIT_SCRIPT -n video_record -C deploy $FORCE -v $VERSION  .
}
copy_files
pack $2
