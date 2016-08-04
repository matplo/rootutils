#!/usr/bin/env python

import import_root as impr
import sys

def test():
	try:
		impr.try_importing_root(verbose=False)
		import ROOT
		h = ROOT.TH1F ("testh", "test", 10, 0, 10)
		print 'success'
	except:
		print 'failed'

def main():
	import subprocess
	try: 
		out = subprocess.check_output([__file__, 'test'])
	except:
		out = 'failed'		
	print out

if __name__ == '__main__':
	if len(sys.argv) > 1:
		if sys.argv[1] == 'test':
			test()
		else:
			main()
	else:
		main()
