#!/bin/bash

py2applet compare_pp_pPb_L2K_pt_draw__list_canvas.icns --make-setup MyApplication.py
rm -rf build dist
#in-place
python setup.py py2app -A

#for deployment
# python setup.py py2app