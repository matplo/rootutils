#!/usr/bin/env python

from configobj import ConfigObj
import argparse
import os
import sys

def read_config(fname, skey):
	config = ConfigObj(fname, raise_errors=True)
	return config[skey]

def main():
	parser = argparse.ArgumentParser(description='read a value from a ConfigObj file', prog=os.path.basename(__file__))
	parser.add_argument('-f', '--file', help='input file', type=str)
	parser.add_argument('-k', '--key', help='key to read', type=str)
	args = parser.parse_args()

	if args.file is None:
		parser.print_usage()
		return

	if args.key is None:
		parser.print_usage()
		return

	if os.path.isfile(args.file):
		try:
			value = read_config(args.file, args.key)
			print value
		except:
			print >> sys.stderr, '[e] unable to read key:', args.key
			return
	else:
		print >> sys.stderr, '[e] unable to access file:', args.file

if __name__ == '__main__':
	main()
