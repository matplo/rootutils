#!/usr/bin/env python

import os
import sys
import tutils as tu
import IPython

def print_usage():
	print '[i] usage:',os.path.basename(sys.argv[0]),'-b'

if __name__=="__main__":
	if tu.is_arg_set('--help') or tu.is_arg_set('-h') or tu.is_arg_set('-?') or tu.is_arg_set('-help'):
		print_usage()
		sys.exit(0)

#
# here & below the ROOT stuff
#

try:
	import ROOT as r
except:
	print >> sys.stderr,'[error:] failed to load ROOT'
	print '[ info:] setup the environment (remember PYTHONPATH)'
	sys.exit(-1)

def main():
	tu.setup_basic_root()

	h = r.TH1D('test', 'test', 10, 0, 1)
	h.Fill(.2)
	h.Fill(.5)
	h.Fill(.4,3.145)        
	h.Draw()
	r.gPad.Update()    
	tu.gList.append(h)

	tb = r.TBrowser()

	tu.gList.append(tb)

if __name__=="__main__":
	main()
	if not tu.is_arg_set('-b'):
		IPython.embed()
