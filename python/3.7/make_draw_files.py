#!/usr/bin/env python

import tutils
import ROOT as R

import os
import sys
import fnmatch
import dlist
import copy
from fuzzywuzzy import fuzz


def find_files(rootdir='.', pattern='*'):
	return [os.path.join(rootdir, filename)
			for rootdir, dirnames, filenames in os.walk(rootdir)
			for filename in filenames
			if fnmatch.fnmatch(filename, pattern)]


def print_preamb(fout, stitle=''):
	print('#-----------------------', file=fout)
	print('#figure', file=fout)
	print('#geom 500x500', file=fout)
	print('#date', file=fout)
	print('#title: {}'.format(stitle), file=fout)
	print('#legend pos=ur', file=fout)


def make_draw_file(fn, extra_opts=[], force=False):
	f  = R.TFile(fn)
	td = f.GetListOfKeys()
	fdraw = fn + '.draw'
	if os.path.isfile(fdraw):
		print('[w] draw file exists:', fdraw)
		if '--force' in sys.argv or force is True:
			print('[w] overwriting...')
		else:
			print('[w] override with --force')
			return fdraw
	with open(fdraw, 'w') as fout:
		print_preamb(fout, fdraw)
		for opt in extra_opts:
			print(opt, file=fout)
		for k in td:
			if k.ReadObj().InheritsFrom('TList'):
				pass
			else:
				ctit = k.GetTitle()
				if len(ctit) < 1:
					ctit = k.GetName()
				print(os.path.abspath(fn), '		:' + k.GetName(), ':p', ':', 'title=' + ctit, file=fout)
		print('', file=fout)
		for k in td:
			if k.ReadObj().InheritsFrom('TList'):
				print_preamb(fout, fdraw)
				for opt in extra_opts:
					print(opt, file=fout)
				print('#legend title={}'.format(k.GetName()), file=fout)
				for o in k.ReadObj():
					ctit = o.GetTitle()
					if len(ctit) < 1:
						ctit = o.GetName()
					print(os.path.abspath(fn), '		:' + k.GetName() + '/' + o.GetName(), ':p', ':', 'title=' + ctit, file=fout)
		print('', file=fout)
	return fdraw


class HistGroup(object):
	def __init__(self):
		self.xlow = None
		self.xhigh = None
		self.list = []
		self.options = []

	def is_fuzzy_ok(self, e, threshold=65):
		if len(self.list) > 0:
			scores = []
			name = e.split(':')[1]
			for ec in self.list:
				namec = ec.split(':')[1]
				sc = fuzz.ratio(name, namec)
				scores.append(sc)
			mean = sum(scores) / len(scores)
			if mean > threshold:
				return True
			else:
				return False
		return True

	def add_object(self, obj, sdescr):
		if obj.InheritsFrom('TH1') or obj.InheritsFrom('TH2') or obj.InheritsFrom('TF1') or obj.InheritsFrom('TGraph'):
			if len(self.list) < 1:
				self.xlow = obj.GetXaxis().GetXmin()
				self.xhigh = obj.GetXaxis().GetXmax()
			if obj.GetXaxis().GetXmin() == self.xlow and obj.GetXaxis().GetXmax() == self.xhigh:
				if self.is_fuzzy_ok(sdescr):
					self.list.append(sdescr)
					return True
		return False

	def dump(self, fout=sys.stdout):
		if len(self.list) < 1:
			return
		print_preamb(fout, 'smart group')
		for opt in self.options:
			print(opt, file=fout)
		for l in self.list:
			print(l, file=fout)


class HistGroups(object):
	def __init__(self):
		self.list = []
		self.options = []

	def add_object(self, obj, sdescr):
		for l in self.list:
			if l.add_object(obj, sdescr):
				return True
		if obj.InheritsFrom('TH1') or obj.InheritsFrom('TH2') or obj.InheritsFrom('TF1') or obj.InheritsFrom('TGraph'):
			hg = HistGroup()
			hg.options = copy.deepcopy(self.options)
			hg.add_object(obj, sdescr)
			self.list.append(hg)

	def fuzzy_recombine(self):
		for l in self.list:
			all_ratios = []
			for i in range(len(l.list)):
				for j in range(i + 1, len(l.list)):
					e1 = l.list[i].split(':')[1]
					e2 = l.list[j].split(':')[1]
					fr = fuzz.ratio(e1, e2)
					print(e1, e2, fr)
					all_ratios.append(fr)
			print(all_ratios)

	def dump(self, fout):
		# self.fuzzy_recombine()
		for l in self.list:
			l.dump(fout)

def make_draw_file_smart_group(fn, extra_opts=[], force=False):
	print('[i] make_draw_file_smart_group:', fn)
	f  = R.TFile(fn)
	td = f.GetListOfKeys()
	fdraw = fn + '.draw'
	if os.path.isfile(fdraw):
		print('[w] draw file exists:', fdraw)
		if '--force' in sys.argv or force is True:
			print('[w] overwriting...')
		else:
			print('[w] override with --force')
			return fdraw

	hg = HistGroups()
	hg.options = copy.deepcopy(extra_opts)
	for k in td:
		if k.ReadObj().InheritsFrom('TList'):
			pass
		else:
			sdopt = ':p '
			if k.ReadObj().InheritsFrom('TF1'):
				sdopt = ':l '
			ctit = k.GetTitle()
			if len(ctit) < 1:
				ctit = k.GetName()
			sdescr = ' '.join([os.path.abspath(fn), '		:' + k.GetName(), sdopt, ':', 'title=' + ctit])
			obj = k.ReadObj()
			hg.add_object(obj, sdescr)

	for k in td:
		if k.ReadObj().InheritsFrom('TList'):
			for o in k.ReadObj():
				sdopt = ':p '
				if k.ReadObj().InheritsFrom('TF1'):
					sdopt = ':l '
				ctit = o.GetTitle()
				if len(ctit) < 1:
					ctit = o.GetName()
				sdescr = ' '.join([os.path.abspath(fn), '		:' + k.GetName() + '/' + o.GetName(), sdopt, ':', 'title=' + ctit])
				obj = k.ReadObj()
				hg.add_object(o, sdescr)

	for k in td:
		if k.ReadObj().InheritsFrom('TDirectoryFile'):
			for ko in k.ReadObj().GetListOfKeys():
				o = ko.ReadObj()
				sdopt = ':p '
				if k.ReadObj().InheritsFrom('TF1'):
					sdopt = ':l '
				ctit = o.GetTitle()
				if len(ctit) < 1:
					ctit = o.GetName()
				sdescr = ' '.join([os.path.abspath(fn), '		:' + k.GetName() + '/' + o.GetName(), sdopt, ':', 'title=' + ctit])
				obj = k.ReadObj()
				hg.add_object(o, sdescr)

	with open(fdraw, 'w') as fout:
		hg.dump(fout)
		print('', file=fout)
	return fdraw


def make_draw_file_dlist(fn, extra_opts=[], force=False):
	l = dlist.load_file(fn)
	fdraw = fn + '.draw'
	if os.path.isfile(fdraw):
		print('[w] draw file exists:', fdraw)
		if '--force' in sys.argv or force is True:
			print('[w] overwriting...')
		else:
			print('[w] override with --force')
			return fdraw
	with open(fdraw, 'w') as fout:
		print('#-----------------------', file=fout)
		print('#figure', file=fout)
		print('#geom 500x500', file=fout)
		print('#title: {}'.format(fdraw), file=fout)
		for opt in extra_opts:
			print(opt, file=fout)
		for obj in l.l:
			o = obj.obj
			print(os.path.abspath(fn), '		:' + o.GetName(), ':p', ':', 'title=' + o.GetTitle(), file=fout)
		print('', file=fout)
	return fdraw


def make_draw_files(dname='.'):
	l = find_files(dname, '*.root')
	for fn in l:
		# make_draw_file(fn)
		make_draw_file_smart_group(fn)


def main():
	make_draw_files('./')

if __name__ == '__main__':
	main()
