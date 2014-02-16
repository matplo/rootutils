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

if [ -z "$PATH" ];
then
    export PATH=$XDIR
else
    export PATH=$XDIR:$PATH
fi

if [ -z "$PYTHONPATH" ];
then
    export PYTHONPATH=$XDIR
else
    export PYTHONPATH=$XDIR:$PYTHONPATH
fi

export PYROOTUTILS=$XDIR
