#!/usr/bin/env python

import pyutils
import sys
import os

def usage():
	print '[i]',os.path.basename(sys.argv[0]),'<--dir directory> [--pattern <file name pattern>]'
	print '    default pattern is *.root'

def main():
	sdir = pyutils.get_arg_with('--dir')
	if len(sys.argv) < 2:
		usage()
		return 

	pattern = pyutils.get_arg_with('--pattern')
	if pattern == None:
		pattern = '*.root'

	cmnd = [ 'hadd -f hadd_out.root ']
	files = pyutils.find_files(sdir, pattern)
	for fn in files:
		print fn
		cmnd.append(fn)

	pyutils.call_cmnd(cmnd=' '.join(cmnd), verbose=True)

if __name__ == '__main__':
	main()
