#!/bin/bash

date > rootsys.conf
echo $ROOTSYS >> rootsys.conf

for pys in meta_draw.py tutils.py pyutils.py dlist.py draw_utils.py pcanvas.py dbgu gui_draw_select.py eval_string.py
do
	cp -rv ../$pys .	
done

py2applet --make-setup gdraw.py compare_pp_pPb_L2K_pt_draw__list_canvas.icns rootsys.conf
rm -rf build dist
#in-place
python setup.py py2app -A

#for deployment
#python setup.py py2app

#python setup.py build
