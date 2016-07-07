#!/usr/bin/env python

import ROOT as r 
import tutils as tu
import numpy as np
from cStringIO import StringIO
import dlist
import sys
import pyutils as ut
import IPython
from string import atof,atoi

def read_data(fn = None):
	f = sys.stdin
	if fn != None:
		f = open(fn)
   	lines = f.read()
   	if f != sys.stdin:
		f.close()
   	d = StringIO(lines)
   	return d

class DrawString(object):
	def __init__(self, s):
		self.s = s
		self.fname = ''
		self.hname = ''
		self.dopt  = ''
		self.opts  = ''
		self.process()
		print '[i] fname={} hname={} dopt={} opts={}'.format(self.fname, self.hname, self.dopt, self.opts)

	def process(self):
		sargs = self.s.split(':')
		try:
			self.fname = sargs[0].strip()
		except:
			pass
		try:
			self.hname = sargs[1].strip()
		except:
			pass
		try:
			self.dopt  = sargs[2].strip()
		except:
			pass
		try:
			self.opts  = sargs[3].strip()
		except:
			pass

	def get_arg(self, sarg):
		s = self.opts.split(',')
		for xs in s:
			if sarg in xs:
				return xs.replace(sarg, '')
		return None

	def is_arg(self, sarg):
		s = self.opts.split(',')
		for xs in s:
			if sarg in xs:
				return True
		return False

	def title(self):
		st = self.get_arg('title=')
		if st == None:
			st = self.fname
		return st

	def miny(self):
		st = self.get_arg('miny=')
		if st != None:
			st = atof(st)
		return st

	def maxy(self):
		st = self.get_arg('maxy=')
		if st != None:
			st = atof(st)
		return st

	def xt(self):
		st = self.get_arg('xt=')
		return st

	def yt(self):
		st = self.get_arg('yt=')
		return st

	def zt(self):
		st = self.get_arg('zt=')
		return st

	def logy(self):
		return self.is_arg('logy')

	def logx(self):
		return self.is_arg('logx')

	def logz(self):
		return self.is_arg('logz')

def legend_position(sleg):
	x1 = None
	x2 = None
	y1 = None
	y2 = None	
	if sleg == None:
		return x1, y1, x2, y2
	try:
		x1 = atof(sleg.split(',')[0])
		y1 = atof(sleg.split(',')[1])
		x2 = atof(sleg.split(',')[2])
		y2 = atof(sleg.split(',')[3])
	except:
		print '[w] trouble with legend position? x1,y1,x2,y2',sleg
	return x1, y1, x2, y2

def get_tag_from_file(tag, fname, default=None, split=None):
	retval = default
	clines = ut.load_file_to_strings(fname)
	for l in clines:
		if tag+' ' in l[:len(tag)+1]:
			retval = l.replace(tag+' ','')
	if split != None:
		retval.split(split)
	return retval

def axis_range(sleg):
	x1 = None
	x2 = None
	if sleg == None:
		return x1, x2
	try:
		x1 = atof(sleg.split(',')[0])
		x2 = atof(sleg.split(',')[1])
	except:
		print '[w] trouble with x-range? x1,x2',sleg
	return x1, x2

def main():
	tu.setup_basic_root()
	fname = ut.get_arg_with('-f')
	#vals = read_data(fname)
	vals = ut.load_file_to_strings(fname)
	if fname == None:
		hlname = 'stdin'
	else:
		hlname = fname

	hls = dlist.ListStorage(hlname+'storage')
	hl = hls.get_list(hlname)
	ds = None
	#for cline in vals.getvalue().split('\n'):
	for cline in vals:
		if len(cline) < 1:
			continue
		if cline[0] == '#':
			continue
		ds = DrawString(cline)
		hl.add_from_file(ds.hname, ds.fname, ds.title(), ds.dopt)

	if ds == None:
		print '[e] nothing to draw...'
		return

	hl.make_canvas()
	hl.reset_axis_titles(ds.xt(), ds.yt(), ds.zt())
	xt = get_tag_from_file('#x', fname, None)
	yt = get_tag_from_file('#y', fname, None)
	zt = get_tag_from_file('#z', fname, None)
	hl.reset_axis_titles(xt, yt, zt)

	rebin = get_tag_from_file('#rebin', fname, None, ' ')
	if rebin!=None:
		print atoi(rebin[0])
		if len(rebin) > 0:
			hl.rebin(atoi(rebin[0]))
		if len(rebin) > 1:
			if 'true' in rebin[1].lower():
				hl.rebin(atoi(rebin[0]), True)
			else:
				hl.rebin(atoi(rebin[0]), False)

	normalize = get_tag_from_file('#normalize', fname, None)
	if normalize == 'self':
		hl.normalize_self()

	miny = get_tag_from_file('#miny', fname, None)
	if miny == None:
		miny=ds.miny()
	else:
		miny=atof(miny)
	maxy = get_tag_from_file('#maxy', fname, None)
	if maxy == None:
		maxy=ds.maxy()
	else:
		maxy=atof(maxy)

	logy = get_tag_from_file('#logy', fname, None)
	if logy == 'true':
		logy=True
	if logy == None:
		logy=ds.logy()
	else:
		logy=False
	logx = get_tag_from_file('#logx', fname, None)
	if logx == 'true':
		logx=True
	if logx == None:
		logx=ds.logx()
	else:
		logx=False
	logz = get_tag_from_file('#logz', fname, None)
	if logz == 'true':
		logz=True
	if logz == None:
		logz=ds.logz()
	else:
		logz=False

	print 'logy is',logy

	sxrange = get_tag_from_file('#xrange', fname, None)
	if sxrange != None:
		x1, x2 = axis_range(sxrange)
		hl.zoom_axis(0, x1, x2)

	hl.draw(miny=miny,maxy=maxy,logy=logy)

	if logy:
		hl.set_log_multipad('y')
	if logx:
		hl.set_log_multipad('x')
	if logz:
		hl.set_log_multipad('z')

	#legend
	stitle = ut.get_arg_with('--title')
	if stitle == None:
		stitle = get_tag_from_file('#title', fname, '')
	sleg = ut.get_arg_with('--leg')
	if sleg == None:
		sleg = get_tag_from_file('#legend',fname)
	x1,y1,x2,y2 = legend_position(sleg)
	hl.self_legend(title=stitle,x1=x1,x2=x2,y1=y1,y2=y2)

	#size of the window
	x = 400
	y = 300
	gs = tu.get_arg_with('--geom')
	if gs == None:
		gs = get_tag_from_file('#geom', fname)
	if gs != None:
		try:
			x = atoi(gs.split('x')[0])
			y = atoi(gs.split('x')[1])
		except:
			print '[e] unable to understand the --geom argument',gs
	hl.resize_window(x,y)

	hl.update()

	if '--print' in sys.argv:
		hl.pdf()

if __name__ == '__main__':
	main()
	if not ut.is_arg_set('-b'):
		IPython.embed()
