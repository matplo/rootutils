#!/usr/bin/env python

import tutils
import ROOT as R

import os
import sys
import fnmatch
import dlist

def find_files(rootdir='.', pattern='*'):
	return [os.path.join(rootdir, filename)
			for rootdir, dirnames, filenames in os.walk(rootdir)
			for filename in filenames
			if fnmatch.fnmatch(filename, pattern)]

def print_preamb(fout, stitle = ''):
	print >> fout,'#-----------------------'
	print >> fout,'#figure'
	print >> fout,'#geom 500x500'
	print >> fout,'#title: {}'.format(stitle)

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
		print_preamb(fout, fdraw)
		for opt in extra_opts:
			print >> fout,opt
		for k in td:
			if k.ReadObj().InheritsFrom('TList'):
				pass
			else:
				ctit = k.GetTitle()
				if len(ctit) < 1:
					ctit = k.GetName()
				print >> fout,os.path.abspath(fn),'		:'+k.GetName(),':p',':','title='+ctit
		print >> fout, ''
		for k in td:
			if k.ReadObj().InheritsFrom('TList'):
				print_preamb(fout, fdraw)
				for opt in extra_opts:
					print >> fout,opt
				print >> fout, '#legend title={}'.format(k.GetName())
				for o in k.ReadObj():
					ctit = o.GetTitle()
					if len(ctit) < 1:
						ctit = o.GetName()
					print >> fout,os.path.abspath(fn),'		:'+k.GetName()+'/'+o.GetName(),':p',':','title='+ctit
		print >> fout, ''
	return fdraw

def make_draw_file_dlist(fn, extra_opts=[], force=False):
	l = dlist.load_file(fn)
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
		for obj in l.l:
			o = obj.obj
			print >> fout,os.path.abspath(fn),'		:'+o.GetName(),':p',':','title='+o.GetTitle()
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
