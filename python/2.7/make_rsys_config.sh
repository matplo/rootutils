#!/bin/bash

function abspath()
{
  case "${1}" in
    [./]*)
    echo "$(cd ${1%/*}; pwd)/${1##*/}"
    ;;
    *)
    echo "${PWD}/${1}"
    ;;
  esac
}

savedir=$PWD

THISFILE=`abspath $BASH_SOURCE`
XDIR=`dirname $THISFILE`
if [ -L ${THISFILE} ];
then
    target=`readlink $THISFILE`
    XDIR=`dirname $target`
fi

THISDIR=$XDIR

rconfig=`which root-config`
[ -e "$rconfig" ] && RSYS=`$rconfig --prefix`
if [ -d "$RSYS" ]; then 
	rootpy=`find $RSYS -name "ROOT.py"`
	if [ -f "$rootpy" ]; then
		echo "[i] rootpy is: [$rootpy]"
		dir_rootpy=`dirname $rootpy`
		if [ -d "$dir_rootpy" ] ; then

			echo "[i] using $dir_rootpy"
			testr=`$THISDIR/test_root.py`
			if [ $testr == "success" ]; then
				echo "[i] test .py program responded with: $testr"
				date > rootsys.conf
				echo $dir_rootpy >> rootsys.conf
			else
				echo "[e] something is wrong with root setup and/or environment to use with python..."
				echo "    test .py program responded with: $testr"
				echo "    this will not work..."
			fi
		else
			echo "[e] dir for ROOT.py not found..."
		fi
	else
		echo "[e] ROOT.py not found."
	fi
else
	echo "[e] root-config not found in path."
fi

#if built for deployment (not in-place) it is safe to:
# remove_ignored dist rootsys.conf