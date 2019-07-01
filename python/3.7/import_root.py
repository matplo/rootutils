#!/usr/bin/env python

import IPython

def try_importing_root_no_config():
	try:
		import ROOT
	except:
		print('tried importing root and failed... adding path...')
		sys.path.append('/Users/ploskon/devel/hepsoft/root/v5-34-34/lib/')
	import ROOT

def exists(fname):
	retval = False
	try:
		f = open(fname, 'r')
		f.close()
		retval = True
	except:
		retval = False
	return retval

def get_config():
	fconfig = 'rootsys.conf'
	if exists(fconfig):
		return fconfig
	import os
	thisfiledir = os.path.dirname(os.path.abspath(__file__))
	fconfig = os.path.join(thisfiledir, fconfig)
	if exists(fconfig):
		return fconfig
	return None

def atry(do_exit=True, verbose = False):
	return try_importing_root(do_exit, verbose)

def try_importing_root(do_exit=True, verbose = False):
	try:
		if verbose: print('[i] importing root...')
		import ROOT
	except:
		if verbose: print('[w] failed. checking for config...')
		rsyspath = './'
		fconfig = get_config()
		if fconfig == None:
			if verbose: print('[i] config file not found...')
			if do_exit: raise SystemExit('ROOT not found.')
			return False
		if verbose: print('[i] found config file', fconfig)
		with open (fconfig, 'r') as f:
			clines = f.readlines()
		for l in clines:
			sdir = l.strip()
			import os
			if os.path.isdir(sdir):
				import pyutils as ut
				candidates = ut.find_files(sdir, 'ROOT.py')
				if len(candidates) > 1:
					if verbose: print('[e] multiple ROOT.py found in',sdir,'this is not ok...')
				else:
					sdir = os.path.dirname(candidates[0])
					srpy = os.path.join(sdir, 'ROOT.py')
					if verbose: print('[i] trying with',srpy)
					if os.path.isfile(srpy):
						rsyspath = sdir
		if verbose: print('[i] using',rsyspath)
		import sys
		sys.path.append(rsyspath)
		#sys.path.append('/Users/ploskon/devel/hepsoft/root/v5-34-34/lib/')
	try:
		import ROOT
		retval = True
	except:
		if verbose: print('[i] bailing out...')
		retval = False
	if retval == False and do_exit:
		raise SystemExit('ROOT not found.')
	return retval

def main():
	import ROOT
	tb = ROOT.TBrowser()
	tutils.gList.append(tb)

if __name__=="__main__":
	imported = try_importing_root(verbose=True)
	if imported == True:
		import tutils
		tutils.setup_basic_root()	
		main()
		if not tutils.is_arg_set('-b'):
			IPython.embed()
