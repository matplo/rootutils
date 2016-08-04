#!/usr/bin/env python

import os
import sys

def atry(verbose = True):
	return try_importing_root(verbose)
	
def try_importing_root_nofind():
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

def try_importing_root(verbose = True):
	try:
		import ROOT
	except:
		if verbose: print '[w] tried importing root and failed... adding path...'
		rsyspath = './'
		with open ('rootsys.conf', 'r') as f:
			clines = f.readlines()
		for l in clines:
			sdir = l.strip()
			if os.path.isdir(sdir):
				import pyutils as ut
				candidates = ut.find_files(sdir, 'ROOT.py')
				if len(candidates) > 1:
					if verbose: print '[e] multiple ROOT.py found in',sdir,'this is not ok...'
				else:
					sdir = os.path.dirname(candidates[0])
					srpy = os.path.join(sdir, 'ROOT.py')
					if verbose: print '[i] trying with',srpy
					if os.path.isfile(srpy):
						rsyspath = sdir
		if verbose: print '[i] using',rsyspath
		sys.path.append(rsyspath)
		#sys.path.append('/Users/ploskon/devel/hepsoft/root/v5-34-34/lib/')
	try:
		import ROOT
	except:
		return False
	return True
