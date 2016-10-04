#!/usr/bin/env python

import tutils
import ROOT as R

import os
import sys
import fnmatch
import dlist
import copy

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

class HistGroup(object):
	def __init__(self):
		self.xlow = None
		self.xhigh = None
		self.list = []
		self.options = []

	def add_object(self, obj, sdescr):
		if obj.InheritsFrom('TH1'):
			if len(self.list) < 1:
				self.xlow = obj.GetXaxis().GetXmin()
				self.xhigh = obj.GetXaxis().GetXmax()
			if obj.GetXaxis().GetXmin() == self.xlow and obj.GetXaxis().GetXmax() == self.xhigh:
				self.list.append(sdescr)
				return True
		return False

	def dump(self, fout=sys.stdout):
		print_preamb(fout, 'smart group')
		for opt in self.options:
			print >> fout,opt
		for l in self.list:
			print >> fout, l

class HistGroups(object):
	def __init__(self):
		self.list = []
		self.options = []

	def add_object(self, obj, sdescr):
		for l in self.list:
			if l.add_object(obj, sdescr):
				return True
			else:
				hg = HistGroup()
				hg.options = copy.deepcopy(self.options)
				hg.add_object(obj, sdescr)
				self.list.append(hg)

	def dump(self):
		for l in self.list:
			l.dump(fout)

def make_draw_file_smart_group(fn, extra_opts=[], force=False):
	groups = []

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

	hg = HistGroup()
	hg.options = copy.deepcopy(extra_opts)
	for k in td:
		if k.ReadObj().InheritsFrom('TList'):
			pass
		else:
			ctit = k.GetTitle()
			if len(ctit) < 1:
				ctit = k.GetName()
			sdescr = ' '.join([os.path.abspath(fn),'		:'+k.GetName(),':p',':','title='+ctit])
			obj = k.ReadObj()
			hg.add_object(obj, sdescr)

	for k in td:
		if k.ReadObj().InheritsFrom('TList'):
			for o in k.ReadObj():
				ctit = o.GetTitle()
				if len(ctit) < 1:
					ctit = o.GetName()
				sdescr = ' '.join([os.path.abspath(fn),'		:'+k.GetName()+'/'+o.GetName(),':p',':','title='+ctit])
				obj = k.ReadObj()
				hg.add_object(obj, sdescr)

	with open(fdraw, 'w') as fout:
		hg.dump(fout)
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
		#make_draw_file(fn)
		make_draw_file_smart_group(fn)

def main():
	make_draw_files('./')

if __name__ == '__main__':
	main()
