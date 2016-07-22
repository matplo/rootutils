#!/usr/bin/env python

import os
import sys

def try_importing_root():
	try:
		import ROOT
	except:
		print '[w] tried importing root and failed... adding path...'
		rsyspath = './'
		with open ('rootsys.conf', 'r') as f:
			clines = f.readlines()
		for l in clines:
			sdir = l.strip()
			if os.path.isdir(sdir):
				srpy = os.path.join(sdir, 'lib', 'ROOT.py')
				print '[i] trying with',srpy
				if os.path.isfile(srpy):
					rsyspath = os.path.join(sdir, 'lib')
		print '[i] using',rsyspath
		sys.path.append(rsyspath)
		#sys.path.append('/Users/ploskon/devel/hepsoft/root/v5-34-34/lib/')
	try:
		import ROOT
	except:
		return False
	return True
