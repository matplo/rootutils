#!/usr/bin/env python

import import_root

import sys
if import_root.try_importing_root():
	print '[i] import root ok...'
else:
	print '[e] no root no fun...'
	sys.exit(0)

import gui_draw_select as gui
gui.main()


