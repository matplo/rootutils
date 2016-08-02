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

def make_draw_file(fn, extra_opts=[], force=False):
	f  = R.TFile(fn)
	td = f.GetListOfKeys()
	fdraw = fn+'.draw'
	if os.path.isfile(fdraw):
		print '[w] draw file exists:',fdraw
		if '--force' in sys.argv or force==True:
			print '[w] overwriting...'
		else:
			print '[w] override with --force'
			return fdraw
	with open(fdraw, 'w') as fout:
		print >> fout,'#-----------------------'
		print >> fout,'#figure'
		print >> fout,'#geom 500x500'
		print >> fout,'#title: {}'.format(fdraw)
		for opt in extra_opts:
			print >> fout,opt
		for k in td:
			print >> fout,os.path.abspath(fn),'		:'+k.GetName(),':p',':','title='+k.GetTitle()
		print >> fout, ''
	return fdraw	

def make_draw_files(dname='.'):
	l = find_files(dname, '*.root')
	for fn in l:
		make_draw_file(fn)

def main():
	make_draw_files('./')

if __name__ == '__main__':
	main()