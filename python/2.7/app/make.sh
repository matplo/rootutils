#!/bin/bash

function remove_ignored()
{
	if [ -e .gitignore ]; then
		toremove=`cat .gitignore`
		echo "[i] removing stuff..."
		for fn in $toremove
		do
			if [ "$1" == "$fn" ]; then
				echo "[i] ignoring " $fn
			else
				rm -rfv $fn
			fi
		done
		echo "[i] done."
	fi
}

remove_ignored

date > rootsys.conf
#echo $ROOTSYS >> rootsys.conf
rconfig=`which root-config`
[ -e "$rconfig" ] && RSYS=`$rconfig --prefix`
if [ -d "$RSYS" ]; then 
	rootpy=`find $RSYS -name "ROOT.py"`
	if [ -f "$rootpy" ]; then
		echo "[i] rootpy is: [$rootpy]"
		dir_rootpy=`dirname $rootpy`
		if [ -d "$dir_rootpy" ] ; then

			echo $dir_rootpy >> rootsys.conf
			echo "[i] using $dir_rootpy"
			for pys in meta_draw.py tutils.py pyutils.py dlist.py draw_utils.py pcanvas.py dbgu gui_draw_select.py eval_string.py data
			do
				cp -rv ../$pys .	
			done
			testr=`./test_root.py`
			if [ $testr == "success" ]; then
				echo "[i] test .py program responded with: $testr"
				cp ./compare_pp_pPb_L2K_pt_draw__list_canvas.icns ./data
				py2applet --make-setup gdraw.py ./data/compare_pp_pPb_L2K_pt_draw__list_canvas.icns rootsys.conf data
				rm -rf build dist
				#in-place
				python setup.py py2app -A
				#for deployment
				#python setup.py py2app
				#python setup.py build
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