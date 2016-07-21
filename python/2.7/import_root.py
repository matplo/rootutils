#!/usr/bin/env python

import IPython

def try_importing_root():
	try:
		import ROOT
	except:
		print 'tried importing root and failed... adding path...'
		sys.path.append('/Users/ploskon/devel/hepsoft/root/v5-34-34/lib/')
	import ROOT

def main():
	import ROOT
	tb = ROOT.TBrowser()
	tutils.gList.append(tb)

if __name__=="__main__":
	try_importing_root()
	import tutils
	tutils.setup_basic_root()	
	main()
	if not tutils.is_arg_set('-b'):
		IPython.embed()
