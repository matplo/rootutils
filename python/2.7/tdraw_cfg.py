#!/usr/bin/env python

import tutils
import ROOT as r
import IPython
import argparse
import os
import sys

from configobj import ConfigObj

import eval_string

def dump_example():
	sexample = '''
[options]
libs =

[histogram]
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

def analyze_from_file(fname):
	if fname == None:
		return
	print '[i] using file:', fname
	config = ConfigObj(fname)

	for s in config.sections:
		if s == 'options':
			continue
		fin = r.TFile(config[s]['input_file'])
		if not fin:
			continue
		foutname = config[s]['output_file']
		if not foutname:
			foutname = 'default_out.root'
		fout = r.TFile(foutname, 'UPDATE')
		print '    processing:', config[s]['name'], ';'.join([config[s]['title'], config[s]['x_title'], config[s]['y_title']])
		hstring = 'htmp({0},{1},{2})'.format(int(get_value(config[s]['nbinsx'])), get_value(config[s]['x'][0]), get_value(config[s]['x'][1]))
		t = fin.Get(config[s]['tree_name'])
		if t:
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
		fout.cd()
		hout.Write()
		fout.Purge()
		fout.Close()
		fin.Close()

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='generate/read config files for LBL TB', prog=os.path.basename(__file__))
	#parser.add_argument('-w', '--write', help='dump the contents', action='store_true')
	#parser.add_argument('-f', '--fname', help='file name to operate on', type=str)
	#parser.add_argument('-r', '--read', help='read a file', type=str)
	#parser.add_argument('-b', '--batch', help='batchmode - do not end with IPython prompt', action='store_true')
	parser.add_argument('-i', '--ipython', help='end with IPython prompt', action='store_true')
	parser.add_argument('-g', '--example', help='dump an example file and exit', action='store_true')
	parser.add_argument('fname', nargs='?')

	args = parser.parse_args()

	if args.example:
		dump_example()
		sys.exit(0)

	tutils.setup_basic_root()
	if args.fname:
		for fn in args.fname:
			analyze_from_file(fn)

	if args.ipython:
		IPython.embed()
