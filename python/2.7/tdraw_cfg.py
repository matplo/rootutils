#!/usr/bin/env python

from time import sleep
import sys
sys.argv.append( '-b' )
import tutils
import ROOT as r
import IPython
import argparse
import os
import fnmatch

from configobj import ConfigObj

import eval_string

from tqdm import tqdm
from tabulate import tabulate

from string import atoi
from string import atof

def dump_example():
	sexample = '''
[options]
libs =

[histogram]
	# will draw only if varexp defined (here or in the parent tree)
	input_dir =
	active = True
	output_file = default_output.root
	input_file = job3/Tree_AnalysisResults.root
	tree_name = t
	varexp = muons.Phi()
	selection =
	option = e
	nentries =
	firstentry =
	x = -PI,PI
	nbinsx = 100
	x_title = '#varphi (rad)'
	y_title = counts
	title = muons phi
	name = muons_phi

[[another]]
	selection = (pt>10)

[[another1]]
	selection = +(pt<20)

[special]
	# this will copy all the features of the [another]
	# but change only the one specified here (note: copy IS RECURSIVE - will copy tree of sections)
	copy = another
	nbinsx = 20

[histogram_from_dir]
	active = True
	output_file = +_output
	input_file = Tree_AnalysisResults.root
	input_dir = .
	tree_name = t
	varexp = muons.Phi()
	selection =
	option = e
	nentries =
	firstentry =
	x = -PI,PI
	nbinsx = 2*PI*11
	x_title = '#varphi (rad)'
	y_title = counts
	title = muons phi
	name = muons_phi
'''
	with open('tdraw_example.cfg', 'w') as f:
		print >> f, sexample
	print '[i] tdraw_example.cfg written.'

def get_value(s, op=None, vdefault=None):
	if type(s) != str:
		s = '{}'.format(s)
	retval = 0
	try:
		np = eval_string.NumericStringParser()
		retval = np.eval(s)
	except:
		if vdefault is None:
			print >> sys.stderr, '[e] unable to convert to a value:[',s,']',type(s), len(s)
		else:
			retval = vdefault
	if op != None:
		if op == int:
			rest = retval - op(retval)
			if rest > 0.5:
				rest = int(1)
			else:
				rest = 0
			retval = op(retval) + rest
		if op == bool:
			retval = op(retval)
	return retval


def find_files(rootdir='.', pattern='*'):
	return [os.path.join(rootdir, filename)
			for rootdir, dirnames, filenames in os.walk(rootdir)
			for filename in filenames
			if fnmatch.fnmatch(filename, pattern)]


def quick_check_section(s, sname):
	once_per_section = 0
	opts= ['active', 'output_file', 'input_file', 'input_dir', 'tree_name', 'varexp', 'selection', 'option', 'nentries', 'firstentry', 'x', 'nbinsx', 'x_title', 'y_title', 'title', 'name']
	retval = True
	for o in opts:
		try:
			s[o]
		except:
			print >> sys.stderr, '[e] option [', o, '] missing in section [', sname, ']'
			if once_per_section == 0:
				once_per_section = 1
				print '    note: some options can be blank but present anyhow'
			retval = False
	return retval


def section_has_setting(what, section, recursive=True):
	retval = None
	try:
		retval = section[what]
	except:
		# check the parent whether setting exists
		retval = None
	if retval is None and recursive is True:
		if section.parent.name:
			retval = section_has_setting(what, section.parent, recursive)
	return retval


class TDrawEntry(object):
	def __init__(self, section):
		self.fields      = ['name', 'title', 'active', 'input_dir',
							'input_file', 'tree_name', 'varexp',
							'selection', 'nentries', 'firstentry',
							'x', 'nbinsx', 'x_title', 'y_title',
							'option', 'output_file']

		self.section     = section
		self.parents     = self.get_parents()
		self.title       = self.setting('title', section, '')
		self.active      = get_value(str(self.setting('active', section, True)), bool, 1)
		self.input_dir   = self.setting('input_dir', section, '')
		if '$' in self.input_dir:
			self.input_dir = os.path.expandvars(self.input_dir)
		self.input_file  = self.setting('input_file', section, '')
		self.output_file = self.setting('output_file', section, 'tdraw_out.root')
		self.tree_name   = self.setting('tree_name', section, 't')
		self.varexp      = self.setting('varexp', section, '')
		self.selection   = self.setting('selection', section, '')
		self.option      = self.setting('option', section, 'e')
		self.nentries    = self.setting('nentries', section, 1000000000)
		self.firstentry  = self.setting('firstentry', section, 0)
		self.nbinsx      = self.setting('nbinsx', section, 10)
		self.nbinsy      = self.setting('nbinsy', section, 10)
		self.x_title     = self.setting('x_title', section, 'default x title')
		self.y_title     = self.setting('y_title', section, 'default y title')
		self.name        = self.make_name(section)  # section.name
		self.x           = []
		self.selection   = self.get_selection(section)
		self.x.append(get_value(self.setting('x', section, [-1, 1])[0], float))
		self.x.append(get_value(self.setting('x', section, [-1, 1])[1], float))
		self.y           = []
		self.y.append(get_value(self.setting('y', section, [-1, 1])[0], float))
		self.y.append(get_value(self.setting('y', section, [-1, 1])[1], float))

		if not self.title:
			# self.title = self.name
			if len(self.selection) > 1:
				self.title = '{} w/ {}'.format(self.varexp, self.selection)
			else:
				self.title = '{}'.format(self.varexp)

	def copy_fields(self, t):
		for f in self.fields:
			self.__setattr__(f, t.__getattribute__(f))
		if len(self.title) < 1:
			if len(self.selection) > 1:
				self.title = '{} w/ {}'.format(self.varexp, self.selection)
			else:
				self.title = '{}'.format(self.varexp)

	def get_selection(self, section):
		sel = self.setting('selection', section, '')
		if len(sel) > 0:
			if sel[0] == '+':
				if len(sel) > 1:
					if len(self.get_selection(section.parent)) > 0:
						sel = self.get_selection(section.parent) + ' && ' + sel[1:]
					else:
						sel = sel[1:]
				else:
					sel = self.get_selection(section.parent)
		return sel

	def is_iterable(self, o):
		retval = False
		try:
			iter(o)
			retval = True
		except TypeError:
			retval = False
		return retval

	def _setting(self, what, section):
		retval = None
		try:
			retval = section[what]
		except:
			# check the parent whether setting exists
			retval = None
		if retval is None:
			if section.parent.name:
				retval = self._setting(what, section.parent)
		return retval

	def _setting_self(self, what, section):
		retval = None
		try:
			retval = section[what]
		except:
			# check the parent whether setting exists
			retval = None
		return retval

	def setting(self, what, section, vdefault):
		retval = self._setting(what, section)
		if retval is None:
			if vdefault is None:
				retval = ''
			else:
				retval = vdefault
		else:
			if vdefault is None:
				pass
			else:
				if self.is_iterable(vdefault):
					if type(vdefault) == str:
						pass
					else:
						if type(retval) == str:
							retval = retval.split(',')
							if self.is_iterable(vdefault) and len(vdefault) > 0:
								if type(vdefault[0]) == int:
									retval = [int(get_value(x, int, vdefault)) for x in retval]
								if type(vdefault[0]) == float:
									retval = [float(get_value(x, float, vdefault)) for x in retval]
								if type(vdefault[0]) == bool:
									retval = [bool(get_value(x, bool, vdefault)) for x in retval]
				else:
					if type(vdefault) == int:
						retval = int(get_value(retval, int, vdefault))
					if type(vdefault) == float:
						retval = float(get_value(retval, float, vdefault))
					if type(vdefault) == bool:
						retval = bool(get_value(retval, bool, vdefault))
		return retval

	def make_name(self, section):
		s = section
		name = [section.name]
		while s:
			if s.parent.name:
				name.append(s.parent.name)
			else:
				break
			s = s.parent
		name.reverse()
		return '_'.join(name)

	def get_parents(self):
		s = self.section
		name = [self.section.name]
		while s:
			if s.parent.name:
				name.append(s.parent.name)
			else:
				break
			s = s.parent
		name.reverse()
		return ' '.join(name)

	def row_full(self):
		return [self.name, self.title, self.active, self.input_dir, self.input_file, self.tree_name, self.varexp, self.selection, self.nentries, self.firstentry, str(self.x), self.nbinsx, self.x_title, self.y_title, self.option, self.output_file]

	def row_head_full(self):
		return ['name', 'title', 'active', 'input_dir', 'input_file', 'tree_name', 'varexp', 'selection', 'nentries', 'firstentry', 'x-range', 'nbinsx', 'x_title', 'y_title', 'option', 'output_file']

	def row_more(self):
		return [self.val_and_type(x) for x in [self.name, self.active, self.input_dir, self.input_file, self.tree_name, self.varexp, self.selection, self.x, self.nentries, self.option, self.output_file]]

	def row_head_more(self):
		return ['name', 'active', 'in_dir', 'in_file', 'tree', 'varexp', 'sel.', 'x-range', 'NE', 'opt', 'output_file']

	def row(self):
		return [self.val_and_type(x) for x in [self.name, self.active, self.input_dir, self.input_file, self.tree_name, self.varexp, self.selection]]

	def row_head(self):
		return ['name', 'active', 'dir', 'in_file', 'tree', 'varexp', 'sel.']

	def row_commented(self):
		return [x for x in ['#', self.name, self.active, self.input_dir, self.input_file, self.tree_name, self.varexp, self.selection]]

	def row_head_commented(self):
		return ['#', 'name', 'active', 'dir', 'in_file', 'tree', 'varexp', 'sel.']

	def val_and_type(self, x):
		if type(x) == str:
			return '"{}"'.format(x)
		else:
			return str(x)

	def __repr__(self):
		return self.parents + '\n' + ' | '.join([self.val_and_type(x) for x in [self.name, self.title, self.active, self.input_dir, self.input_file, self.tree_name, self.varexp, self.selection, self.nentries, self.firstentry, self.x, self.nbinsx, self.x_title, self.y_title, self.option, self.output_file]])

class TDrawConfig(object):
	def __init__(self, fname, opts=None):
		self.fname = fname
		self.config = ConfigObj(fname, raise_errors=True)
		self.recreate = False
		self.clean = True
		if opts:
			self.recreate = opts.recreate
			self.clean = opts.clean
		self.cleaned_files = []
		self.entries = []
		self.copies = []
		self.process()

	def process_section(self, section):
		if section.name == 'config':
			return
		if len(section.sections):
			for s in section.sections:
				self.process_section(section[s])
			if section_has_setting('varexp', section, recursive=True):
				tde = TDrawEntry(section)
				self.entries.append(tde)
		else:
			if self.is_copy(section):
				self.process_copy(section)
			else:
				if section_has_setting('varexp', section, recursive=True):
					tde = TDrawEntry(section)
					self.entries.append(tde)

	def is_copy(self, s):
		try:
			if len(s['copy']) > 0:
				return True
		except:
			return False

	def process_copy(self, s):
		scopy = s['copy']
		copy_names = []
		if type(scopy) is str:
			copy_names.append(scopy)
		else:
			for scp in scopy:
				copy_names.append(scp)
		#print 'to copy..',copy_names
		for scopy in copy_names:
			model = TDrawEntry(s)
			current_entries = list(self.entries)
			for se in current_entries:
				docopy = False
				#if type(se.parents) is str:
				#	if scopy in se.parents.split(' '):
				#		docopy = True
				#else:
				#	if scopy in se.parents:
				#		docopy = True
				if scopy == se.name[:len(scopy)]:
					docopy = True
					#print 'copy:    ', scopy, se.name, docopy, type(se.parents), se.parents
				if docopy:
					# print '[i] use for copy:', se.name
					newtde = TDrawEntry(se.section)
					newtde.copy_fields(se)
					#newtde.name = se.name
					#newtde.parents = se.parents
					for sf in model.fields:
						setting = model._setting_self(sf, model.section)
						if setting:
							if sf == 'selection':
								if setting[0] == '+':
									if len(setting.strip()) > 1:
										setting = '({}) && ({})'.format(newtde.selection, setting[1:])
							newtde.__setattr__(sf, setting)
					newtde.parents = '{} {}'.format(model.name, newtde.parents)
					newtde.name = '{}_{}'.format(model.name, newtde.name)
					newtde.title = '{} {}'.format(newtde.title, s.name)
					#print 'new name:', newtde.name
					#print
					#self.copies.append(newtde)
					self.entries.append(newtde)

	def load_lib(self, libpath):
		#sexplib = r.gSystem.ExpandPathName(libpath.strip())
		sexplib = r.gSystem.DynamicPathName(libpath.strip())
		sexplib_lib = os.path.basename(sexplib)
		sexplib_dir = os.path.dirname(sexplib)
		sexplib_fullpath = os.path.join(sexplib_dir, sexplib_lib)
		#s = r.TString(sexplib_fullpath)
		#sp = r.gSystem.FindDynamicLibrary(s)
		#print sp
		print '[i] loading', sexplib_fullpath
		r.gSystem.AddDynamicPath(sexplib_dir)
		retval = r.gSystem.Load(sexplib_lib)
		print '    status', retval

	def process(self):
		for s in self.config.sections:
			if s == 'options':
				try:
					slibs = self.config[s]['libs']
					if type(slibs) == list:
						for slib in slibs:
							self.load_lib(slib)
					else:
						self.load_lib(slibs)
				except:
					pass
				continue
			#if self.is_copy(self.config[s]):
			#	#print '[i]', s, 'is a copy'
			#	continue
			self.process_section(self.config[s])

		# now add copies
		# for s in self.config.sections:
		# 	if s != 'options':
		# 		if self.is_copy(self.config[s]):
		# 			self.process_copy(s)

		#for e in self.copies:
		#	self.entries.append(e)

		for e in self.entries:
			if len(e.input_file) < 1:
				e.active = False
			if len(e.output_file) < 1:
				e.active = False
			if len(e.varexp) < 1:
				e.active = False

	def __repr__(self):
		#return '\n'.join(['[i] {} {}'.format(i, str(s)) for i,s in enumerate(self.entries)])
		return tabulate([e.row() for e in self.entries], headers=self.entries[0].row_head())

	def tab_comment(self):
		print tabulate([e.row_commented() for e in self.entries], headers=self.entries[0].row_head_commented(), tablefmt='plain')
		#print tabulate([e.row_commented() for e in self.entries])

	def dump_class_config(self, fout):
		outs = sys.stdout
		sys.stdout = fout
		self.tab_comment()
		for e in self.entries:
			print e.name,'=',e.name
			print '{}_file = {}'.format(e.name, e.output_file)
			print '{}_title = {}'.format(e.name, e.title)
			print '{}_varexp = {}'.format(e.name, e.varexp)
			print '{}_selection = {}'.format(e.name, e.selection)

		print 'histograms = {}'.format(','.join([e.name for e in self.entries]))
		print 'files = {}'.format(','.join([e.output_file for e in self.entries]))
		print 'titles = {}'.format(','.join([e.title for e in self.entries]))
		sys.stdout = outs

	def run(self):
		print '[i] run...'
		cleaned = []
		errors = []
		errors.append('[e] errors:')
		if len(self.entries)<1:
			print '[i] no entries?'
			return
		pbare = tqdm(self.entries, desc='    entry')
		for e in pbare:
			# pbare.set_description('    {}:{}'.format(pbare.n, e.name))
			# pbare.update(0)
			if not e.active:
				continue
			foutname = e.output_file
			if not foutname:
				foutname = '+out'
			if e.input_dir:
				input_files = find_files(e.input_dir, pattern=e.input_file)
				#print '    e.input_dir:',e.input_dir, 'input_file:',e.input_file
			else:
				input_files = [e.input_file]
			pbar = tqdm(input_files, desc='    file')
			for fn in pbar:
				ifn = input_files.index(fn)
				#pbar.set_description('    file #{}'.format(pbar.n))
				sfn = fn
				if len(fn) > 40:
					sfn = fn[:18] + '..' + fn[len(fn)-20:]
				if foutname[0] == '+':
					sfoutname = fn.replace('.root', foutname[1:].replace('.root', '') + '.root')
				else:
					if (len(input_files) > 1):
						sfoutname = foutname.replace('.root', '_{}.root'.format(ifn))
					else:
						sfoutname = foutname
				#if sfoutname in cleaned:
				#	pbar.set_description('    {} : {}'.format(e.name, sfn))
				#else:
				#	if self.clean:
				#		pbar.set_description('    {} : (c:{}) {}'.format(e.name, sfoutname, sfn))
				#	else:
				#		pbar.set_description('    {} : (o:{}) {}'.format(e.name, sfoutname, sfn))
				fin = r.TFile(fn)
				if not fin:
					continue
					errors.append('[e] file {} unable to open'.format(fn))
				dopt = e.option
				if 'norange' in dopt:
					hstring = 'htmp'
					dopt = e.option.replace('norange', '')
				else:
					# check if drawing in 2D
					if ':' in e.varexp:
						hstring = 'htmp({0},{1},{2},{3},{4},{5})'.format(e.nbinsx, e.x[0], e.x[1], e.nbinsy, e.y[0], e.y[1])
					else:
						hstring = 'htmp({0},{1},{2})'.format(e.nbinsx, e.x[0], e.x[1])
				#print e.name, dopt, e.option
				t = fin.Get(e.tree_name)
				hout = None
				if t:
					# print e.varexp, e.selection, e.option, e.nentries, e.firstentry
					nentr = t.Draw(e.varexp + '>>{}'.format(hstring), e.selection, dopt, e.nentries, e.firstentry)
					# print '[i] number of entries drawn:',nentr
					hout = r.gDirectory.Get('htmp')
					hout.SetDirectory(0)
					hout.SetName(e.name)
					hout.SetTitle(e.title)
					hout.GetXaxis().SetTitle(e.x_title)
					hout.GetYaxis().SetTitle(e.y_title)
				else:
					errors.append('[e] tree {} not found - file {}'.format(e.tree_name, fn))
					continue
				if hout:
					if self.clean is True:
						if sfoutname in cleaned:
							pass
						else:
							# print '[i] clean', sfoutname, 'requested'
							try:
								os.remove(sfoutname)
							except:
								pass
						if sfoutname not in cleaned:
							cleaned.append(sfoutname)
					fout = r.TFile(sfoutname, 'UPDATE')
					fout.cd()
					hout.Write()
					fout.Purge()
					fout.Close()
					fin.Close()
				else:
					errors.append('[e] output histogram {} {} not made'.format(e.name, hstring))
		print
		print '[i] output files:'
		for fn in cleaned:
			print '    '+fn
		if len(errors) > 1:
			for i, er in enumerate(errors):
				if i > 0:
					print er.replace('[e] ', '    ')
				else:
					print er
		print '[i] done.'

def tdraw_from_file(fname, recreate=False, clean_first=False):
	cleaned = []
	smode = 'UPDATE'
	if recreate == True:
		smode = 'RECREATE'
	if fname == None:
		return
	print '[i] file write mode is:',smode
	print '[i] config file:', fname
	config = ConfigObj(fname, raise_errors = True)
	for s in config.sections:
		if s == 'options':
			try:
				slibs = config[s]['libs']
				if type(slibs) == list:
					for slib in slibs:
						sexplib = r.gSystem.ExpandPathName(slib.strip())
						print '[i] loading',sexplib
						r.gSystem.Load(sexplib)
				else:
					sexplib = r.gSystem.ExpandPathName(slibs)
					print '[i] loading',sexplib
					r.gSystem.Load(sexplib)
			except:
				pass
			continue
		if quick_check_section(config[s], s) == False:
			continue
		if get_value(config[s]['active']) == 0:
			continue
		print '[i] section [',s,']'
		input_fname = config[s]['input_file']
		foutname = config[s]['output_file']
		if not foutname:
			foutname = '+out'
		sdir = config[s]['input_dir']
		if sdir:
			input_files = find_files(sdir, pattern=input_fname)
			print '    sdir is:',sdir
		else:
			input_files = [input_fname]
		print '    tdraw:', config[s]['name'], ';'.join([config[s]['title'], config[s]['x_title'], config[s]['y_title']])
		pbar = tqdm(input_files)
		for fn in pbar:
			# pbar.set_description('    processing file: %s' % fn)
			nchars = 0
			sfn = fn
			if len(fn) > 40:
				sfn = fn[:18] + '..' + fn[len(fn)-20:]
			pbar.set_description('    {} : {}'.format(s, sfn))
			if foutname[0] == '+':
				sfoutname = fn.replace('.root', foutname[1:] + '.root')
			else:
				sfoutname = foutname
			#print '    output:',sfoutname
			fin = r.TFile(fn)
			if not fin:
				continue
			hstring = 'htmp({0},{1},{2})'.format(int(get_value(config[s]['nbinsx'])), get_value(config[s]['x'][0]), get_value(config[s]['x'][1]))
			t = fin.Get(config[s]['tree_name'])
			if t:
				#t.MakeClass('Correlations')
				nentries = config[s]['nentries']
				if not nentries:
					nentries = '1000000000'
				firstentry = config[s]['firstentry']
				if not firstentry:
					firstentry = '0'
				t.Draw(config[s]['varexp'] + '>>{}'.format(hstring), config[s]['selection'], config[s]['option'], int(get_value(nentries)), int(get_value(firstentry)))
				hout = r.gDirectory.Get('htmp')
				hout.SetDirectory(0)
				hout.SetName(config[s]['name'])
				hout.SetTitle(config[s]['title'])
				hout.GetXaxis().SetTitle(config[s]['x_title'])
				hout.GetYaxis().SetTitle(config[s]['y_title'])
			if clean_first == True:
				if sfoutname in cleaned:
					pass
				else:
					# print '[i] clean',sfoutname,'requested'
					fout = r.TFile(sfoutname, 'recreate')
					fout.Close()
					cleaned.append(sfoutname)
			fout = r.TFile(sfoutname, smode)
			fout.cd()
			hout.Write()
			fout.Purge()
			fout.Close()
			fin.Close()
	print '    done.'

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='execute tdraw based on the config file', prog=os.path.basename(__file__))
	#parser.add_argument('-w', '--write', help='dump the contents', action='store_true')
	#parser.add_argument('-f', '--fname', help='file name to operate on', type=str)
	#parser.add_argument('-r', '--read', help='read a file', type=str)
	parser.add_argument('-b', '--batch', help='batchmode - do not end with IPython prompt', action='store_true')
	parser.add_argument('-i', '--ipython', help='end with IPython prompt', action='store_true')
	parser.add_argument('-g', '--example', help='dump an example file and exit', action='store_true')
	parser.add_argument('--recreate', help='write files with "recreate" instead of "update"', action='store_true')
	parser.add_argument('--clean', help='remove output file - once before start...', action='store_true')
	parser.add_argument('fname', type=str, nargs='*')
	parser.add_argument('--old', help='old implementation', action='store_true')
	parser.add_argument('--test', help='show what we get from the config...', action='store_true')
	parser.add_argument('--configobj', help='show what we get from the config...', action='store_true')

	args = parser.parse_args()

	if args.example:
		dump_example()
		sys.exit(0)

	tutils.setup_basic_root()
	if args.fname:
		tc = r.TCanvas('ctmp', 'ctmp')
		for fn in args.fname:
			tc.cd()
			if args.old:
				tdraw_from_file(fn, args.recreate, args.clean)
			else:
				cfg = TDrawConfig(fn, args)
				if args.configobj:
					cfg.dump_class_config()
				else:
					print cfg
					if not args.test:
						cfg.run()
						fconfobj = fn.replace('.cfg', '_out.confobj')
						with open(fconfobj, 'w') as f:
							cfg.dump_class_config(f)
						print '[i]',fconfobj,'written.'
	if args.ipython:
		IPython.embed()
