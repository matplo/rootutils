#!/usr/bin/env python

import tutils
import ROOT as r
import IPython
import dlist
import os
import pyutils as ut
import sys

class ConfDB(object):
	verbosity = 0

	def __init__(self, sconfig=''):
		if self.verbosity > 0:
			print '[i]',self.__class__.__name__
		self.names_config = sconfig
		if self.names_config == None:
			self.names_config = ''
		self.valid_names = []
		self.load_names()
		if self.verbosity > 0:
			print '    number of entries in the valid names list', len(self.valid_names)

	def is_valid(self, name):
		pass

	def load_names(self):
		with open(self.names_config) as f:
			for l in f.readlines():
				if l[0] == '#':
					continue
				sname = l.strip('\n')
				if self.is_valid(sname):
					self.valid_names.append(sname)
		if self.verbosity > 1:
			print '    using list of names:', self.valid_names

class SFileDB(ConfDB):
	def __init__(self, sconfig='fnames.conf', sdir=None):
		self.sdir = sdir
		super(SFileDB, self).__init__(sconfig)

	def is_valid(self, fname):
		if os.path.isfile(fname):
			return fname
		return False

	def load_names(self):
		if os.path.isfile(self.names_config):
			super(SFileDB, self).load_names()
			return
		_sdir = self.sdir
		if _sdir == None:
			_sdir = '.'
		self.valid_names = ut.find_files(_sdir, self.names_config)
		if self.verbosity > 1:
			print '    using list of names:', self.valid_names

class HistNames(ConfDB):
	def __init__(self, hor='hnames.conf', rfile=''):
		self.rfile = rfile
		#self.info()
		super(HistNames, self).__init__(hor)

	def load_names(self):
		if os.path.isfile(self.names_config):
			super(HistNames, self).load_names()
			return
		snames = self.names_config.split(',')
		if len(snames) > 0:
			for name in snames:
				self.is_valid(name)
		else:
			self.is_valid('')

		if self.verbosity > 1:
			print '    using list of names:', self.valid_names

	def info(self):
		print '    checking for histograms in:',self.rfile
		if os.path.isfile(self.rfile) and self.is_root_file(self.rfile):
			tfile = r.TFile(self.rfile)
			if tfile:
				if self.verbosity > 1:
					print '    number of entries in the file:', tfile.GetListOfKeys().GetEntries()

	def is_root_file(self, spath, silent=True):
		filename, file_extension = os.path.splitext(spath)
		if file_extension != '.root':
			if silent == False:
				print '[w] skipped:',self.rfile,'bad extention... not .root .'
			return False
		return True

	#def is_valid(self, name):
	#	if os.path.isfile(self.rfile) and self.is_root_file(self.rfile):
	#		tfile = r.TFile(self.rfile)
	#		if tfile:
	#			h = tfile.Get(name)
	#			if h != None:
	#				return name
	#			tfile.Close()
	#	return False

	def is_valid(self, name):
		if os.path.isfile(self.rfile) and self.is_root_file(self.rfile):
			tfile = r.TFile(self.rfile)
			if tfile:
				if self.verbosity > 1:
					print '    number of entries in', self.rfile, ':', tfile.GetListOfKeys().GetEntries()
				for k in tfile.GetListOfKeys():
					if name in k.GetName() or name=='':
						h = tfile.Get(k.GetName())
						if h != None:
							#print '[d] found!',name,'in',k.GetName()
							self.valid_names.append(k.GetName())
				tfile.Close()

def demo():
    tutils.setup_basic_root()
    fdb = SFileDB('test_file_list.txt')
    #hdb = HistNames('hnames.conf', fdb.valid_names[0])
    hdb = HistNames('Aj', fdb.valid_names[0])
    fdb = SFileDB('jewel*.root', '/Volumes/SAMSUNG/data/subjets/comp/')
    hdb = HistNames('Aj', fdb.valid_names[0])

def has_and(name, patterns):
	if patterns == None:
		return True
	sp = patterns.split(',')
	for s in sp:
		if s not in name:
			return False
	return True

def main():
	sdir             = tutils.get_arg_with('--dir')
	cfile            = tutils.get_arg_with('-f')
	if cfile == None:
		cfile = '*.root'
	hor              = tutils.get_arg_with('--hor')
	hand             = tutils.get_arg_with('--hand')
	ConfDB.verbosity = tutils.get_arg_with('--verbosity')
	opts             = tutils.get_arg_with('--opts')

	if ConfDB.verbosity == None:
		ConfDB.verbosity = 0

	if '--demo' in sys.argv:
		demo()
		return
	fdb = SFileDB(cfile, sdir)
	for fn in fdb.valid_names:
		hdb = HistNames(hor, fn)
		for h in hdb.valid_names:
			if has_and(h, hand):
				if opts != None:
					print ':'.join([fn,h,opts])
				else:
					print ':'.join([fn,h])

if __name__=="__main__":
	if '--usage' in sys.argv:
		print '[i] usage:',__file__,'[-f <path or string/filter>] [--dir <path>] [--hor <path or h filter>] [--hand <filter>] [--opts <additional string to print>]'
	else:
		main()
