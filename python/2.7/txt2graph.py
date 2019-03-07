#!/usr/bin/env python

import tutils as tu
import ROOT as r
import numpy as np
from StringIO import StringIO
import dlist
import sys
import pyutils as ut
import IPython
import eval_string
import argparse
import os


def read_data(fn=None):
	f = sys.stdin
	if fn is not None:
		f = open(fn)
	lines = f.read()
	if f != sys.stdin:
		f.close()
	d = StringIO(lines)
	retvals = np.genfromtxt(d, comments='#', autostrip=True)
	return retvals


def make_graph_from_file(fn=None, xye=[0, 1, 2, 3]):
	d = read_data(fn)
	x  = d[:,xye[0]]
	y  = d[:,xye[1]]
	try:
		xe = d[:,xye[2]]
	except:
		xe = []
	try:
		ye = d[:,xye[3]]
	except:
		ye = []
	grname = 'graph'
	gr = dlist.make_graph_xy(grname,x,y,xe=xe,ye=ye)
	return gr

def get_hep_xeye(err=False):
	if err == True:
		return [0, 3, 1, 2, 6, 7]
	return [0, 3, 1, 2, 4, 5]

def make_graph_from_hepfile(fn = None, xye = [0,1,2,3,4,5], xe=None):
	d     = read_data(fn)
	x     = d[:,xye[0]]
	y     = d[:,xye[1]]
	xlow  = []
	xhigh = []
	dyem  = []
	dyep  = []

	if xye[2] >= 0:
		try:
			xlow  = d[:,xye[2]]
		except:
			xlow  = []
	if xye[3] >= 0:
		try:
			xhigh = d[:,xye[3]]
		except:
			xhigh = []
	if xye[4] >= 0:
		try:
			dyem = d[:,xye[4]]
		except:
			dyem = []
	if xye[5] >= 0:
		try:
			dyep = d[:,xye[5]]
		except:
			dyep = []
	name = 'graph_hepfile_' + str(xye)

	if len(xlow) > 0:
		for i, ix in enumerate(xlow):
			v = x[i] - ix
			if xe:
				v = xe
			xlow[i] = v
	else:
		if xe:
			xlow = []
			for i, ix in enumerate(x):
				if xe < 0:
					dx1 = -1
					if i > 0:
						dx1 = ix - x[i-1]
					else:
						dx1 = 1e12
					dx2 = -1
					if i < len(x) - 1:
						dx2 = x[i + 1] - ix
					else:
						dx2 = 1e12
					xe = min(dx1/2., dx2/2.)
				xlow.append(xe)

	if len(xhigh) > 0:
		for i, ix in enumerate(xhigh):
			v = ix - x[i]
			if xe:
				v = xe
			xhigh[i] = v
	else:
		if xe:
			xhigh = []
			for i, ix in enumerate(x):
				if xe < 0:
					dx1 = -1
					if i > 0:
						dx1 = ix - x[i-1]
					else:
						dx1 = 1e12
					dx2 = -1
					if i < len(x) - 1:
						dx2 = x[i + 1] - ix
					else:
						dx2 = 1e12
					xe = min(dx1/2., dx2/2.)
				xhigh.append(xe)

	if len(dyem) > 0:
		for i, ix in enumerate(dyem):
			v = dyem[i]
			dyem[i] = abs(v)
	if len(dyep) > 0:
		for i, ix in enumerate(dyep):
			v = dyep[i]
			dyep[i] = abs(v)
	#print name
	#print ' - ',x, y
	#print ' - ',xlow, xhigh
	#print ' - ',dyem, dyep
	gr = dlist.make_graph_ae_xy(name, x, y, xlow, xhigh, dyem, dyep)
	return gr

def graph(args):
	if not args.fname:
		hlname = 'stdin'
	else:
		hlname = args.fname
	hl = dlist.dlist(hlname)
	xye  = [0, 1, 2, 3, 4, 5]
	sxye = args.xye
	if sxye != None:
		xye  = [-1, -1, -1, -1, -1, -1]
		sa = sxye.split(',')
		for i,s in enumerate(sa):
			xye[i] = int(s)
	if args.hep:
		xe = None
		if args.xe:
			sxe = args.xe
			xe = eval_string.get_value(sxe, float, None)
		gr = make_graph_from_hepfile(args.fname, xye, xe=xe)
	else:
		gr = make_graph_from_file(args.fname, args.xye)
	stitle = args.title
	if stitle == None:
		stitle = hlname
	hl.add(gr, stitle, args.style)
	sname = args.name
	if sname != None:
		hl.l[-1].obj.SetName(sname)
	hl.make_canvas()
	logy = args.logy
	hl.draw(logy=logy)
	hl.self_legend()
	if logy:
		r.gPad.SetLogy()
	xlabel = ut.get_arg_with('-x')
	ylabel = ut.get_arg_with('-y')
	hl.reset_axis_titles(xlabel,ylabel)
	hl.update()
	if args.prnt:
		hl.tcanvas.Print(hl.tcanvas.GetName() + '.pdf', '.pdf')

	tu.gList.append(hl)

	if args.write==True:
		stitle = args.title
		if stitle == None:
			hl.write_to_file(hl.name+'.root')
		else:
			stitle = ut.to_file_name(stitle.split(';')[0])
			hl.write_to_file(hl.name+'_'+stitle+'.root')

	return gr

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='make root graphs from text files', prog=os.path.basename(__file__))
	parser.add_argument('-g', '--debug', help='debug mode', action='store_true')
	parser.add_argument('-w', '--write', help='write a root file - otherwise nothing is written', action='store_true')
	parser.add_argument('-i', '--prompt', help='end with IPython prompt', action='store_true')
	parser.add_argument('-p', '--prnt', help='draw to a file', action='store_true', default = False)
	parser.add_argument('--logy', help='set log y axis', action='store_true', default = False)
	parser.add_argument('--hep', help='file is in some HEP standard', action='store_true', default = False)

	parser.add_argument('--xye', help='comma separated column numbers for x,y, and errors', default = '0,1,2', type=str)
	parser.add_argument('--xe', help='set x errors to a value', default = '0', type=str)
	parser.add_argument('--style', help='draw style', default = 'P', type=str)

	parser.add_argument('-t', '--title', help='output title', default = 'default title', type=str)
	parser.add_argument('-n', '--name', help='output name', default = 'graph', type=str)
	parser.add_argument('fname', help='input file name - if missing then stdin', nargs='?')

	args = parser.parse_args()

	tu.setup_basic_root()
	if args.debug:
		dlist.gDebug = True
	gr = graph(args)
