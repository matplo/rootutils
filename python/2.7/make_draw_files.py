#!/usr/bin/env python

import ROOT as R

import os
import sys
import fnmatch

def find_files(rootdir='.', pattern='*'):
	return [os.path.join(rootdir, filename)
			for rootdir, dirnames, filenames in os.walk(rootdir)
			for filename in filenames
			if fnmatch.fnmatch(filename, pattern)]

def make_draw_file(fn):
	f  = R.TFile(fn)
	td = f.GetListOfKeys()
	fdraw = fn+'.draw'
	if os.path.isfile(fdraw):
		print '[w] draw file exists:',fdraw
		if '--force' not in sys.argv:
			print '[w] override with --force'
			return fdraw
		else:
			print '[w] overwriting...'
	with open(fdraw, 'w') as fout:
		print >> fout,'#figure'
		print >> fout,'#geom 500x500'
		print >> fout,'#title: {}'.format(fdraw)
		for k in td:
			print >> fout,os.path.abspath(fn),'		:'+k.GetName(),':p',':','title='+k.GetTitle()
	return fdraw	

def make_draw_files(dname='.'):
	l = find_files(dname, '*.root')
	for fn in l:
		make_draw_file(fn)

def main():
	make_draw_files('./')

if __name__ == '__main__':
	main()