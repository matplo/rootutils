#!/usr/bin/env python

import sys
import os
import argparse

def main(fname):
	try:
		open(fname,'rb+')
	except:
		print '[e] unable to open file (mode: rb+):',fname
		sys.exit(-2)
	with open(fname, 'rb+') as f:
		content = f.read()
		f.seek(0)
		f.write(content.replace(b'\r', b''))
		f.truncate()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='clear CR; http://stackoverflow.com/questions/19425857/env-python-r-no-such-file-or-directory', prog=os.path.basename(__file__))
	parser.add_argument('fname', help='file to cleanup')
	args = parser.parse_args()
	main(args.fname)

