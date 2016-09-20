#!/usr/bin/env python

import tutils
import ROOT as r
import IPython
import argparse
import os
import fnmatch
import sys

from configobj import ConfigObj

import eval_string

from tqdm import tqdm

def dump_example():
	sexample = '''
[options]
libs =

[histogram]
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

[histogram from dir]
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

def get_value(s):
	retval = 0
	try:
		np = eval_string.NumericStringParser()
		retval = np.eval(s)
	except:
		print >> sys.stderr, '[e] unable to convert to a value:',s
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
			print >> sys.stderr, '[e] option [',o,'] missing in section [',sname,']'
			if once_per_section == 0:
				once_per_section = 1
				print '    note: some options can be blank but present anyhow'
			retval = False
	return retval

def tdraw_from_file(fname, recreate=False):
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
	#parser.add_argument('-b', '--batch', help='batchmode - do not end with IPython prompt', action='store_true')
	parser.add_argument('-i', '--ipython', help='end with IPython prompt', action='store_true')
	parser.add_argument('-g', '--example', help='dump an example file and exit', action='store_true')
	parser.add_argument('--recreate', help='write files with "recreate" instead of "update"', action='store_true')
	parser.add_argument('fname', type=str, nargs='*')

	args = parser.parse_args()

	if args.example:
		dump_example()
		sys.exit(0)

	tutils.setup_basic_root()
	if args.fname:
		tc = r.TCanvas('ctmp', 'ctmp')
		for fn in args.fname:
			tc.cd()
			tdraw_from_file(fn, args.recreate)

	if args.ipython:
		IPython.embed()

