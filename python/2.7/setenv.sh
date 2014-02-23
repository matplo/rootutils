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

THISFILE=`abspath $BASH_SOURCE`
XDIR=`dirname $THISFILE`

if [ -L ${THISFILE} ];
then
    target=`readlink $THISFILE`
    XDIR=`dirname $target`
fi

export PYROOTUTILS=$XDIR

if [ -z "$PATH" ];
then
    export PATH=$PYROOTUTILS
else
    export PATH=$PYROOTUTILS:$PATH
fi

if [ -z "$PYTHONPATH" ];
then
    export PYTHONPATH=$PYROOTUTILS
else
    export PYTHONPATH=$PYROOTUTILS:$PYTHONPATH
fi

function exec_carver()
{
    echo "[i] loading modules for carver"
    module unload pgi/12.9
    module load gcc
    module load cmake
    module use /project/projectdirs/alice/software/modulefiles
    module load alice/root
}

function exec_pdsf()
{
    echo "[i] loading modules for pdsf"

    #this is needed - relying that your account has the defaults
    . $HOME/.profile
    . $HOME/.bash_profile

    #module load gcc/4.3.2
    module load gcc/4.6.2_64bit
    module load cmake
    module use /project/projectdirs/alice/software/modulefiles
    module load alice/root
}

function exec_default()
{
    # nothing
    echo "[i] loading modules for default"
    module load root
}

function exec_darwin()
{
    # nothing
    echo "[i] loading modules for darwin"
    module load alice/root
}

date
hostid=`uname -a`
case $hostid in
    *.nersc*)
	[ "$NERSC_HOST" == "pdsf" ] && exec_pdsf
	[ "$NERSC_HOST" == "carver" ] && exec_carver
	hostn=`uname -n`
	case $hostn in
	    pc*)
		exec_pdsf
		;;
	esac
        ;;
    *Darwin*)
	exec_darwin
	;;
    *)
        exec_default
        ;;
esac

module list 2>&1
