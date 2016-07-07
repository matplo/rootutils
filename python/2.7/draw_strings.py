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

class Comment(object):
	def __init__(self, s):
		self.s = s
		self.box = self.get_box()
		self.text = self.get_text()

	def get_box(self):
		x1 = 0.1
		x2 = 0.9
		y1 = 0.1
		y2 = 0.9
		if self.s == None:
			return [x1, y1, x2, y2]
		try:
			x1 = atof(self.s.split(',')[0])
			y1 = atof(self.s.split(',')[1])
			x2 = atof(self.s.split(',')[2])
			y2 = atof(self.s.split(',')[3])
		except:
			print '[w] trouble with comment position? x1,y1,x2,y2',self.s
		return [x1, y1, x2, y2]

	def get_settings(self, sitem):
		retval = []
		splits = self.s.split(sitem)
		for n in xrange(1,len(splits)):
			retval.append(self.filter_known_settings(splits[n]))
		if len(retval) <= 0:
			retval.append(None)
		return retval

	def filter_known_settings(self, s):
		known = ['tx_size=', 'color=', 'font=', 'alpha=']
		for k in known:
			if k in s:
				s=s.split(k)[0]
		return s

	def get_setting(self, sitem):		
		setting = 0
		if self.get_settings(sitem)[-1]:
			setting = self.get_settings(sitem)[-1]
		return setting

	def get_text(self):
		return self.get_settings('item=')

	def get_text_size(self):		
		if self.get_setting('tx_size='):
			return atof(self.get_setting('tx_size='))
		return 0.025

	def get_color(self):		
		if self.get_setting('color='):
			return atoi(self.get_setting('color='))
		return 1

	def get_font(self):		
		if self.get_setting('font='):
			return self.get_setting('font=')
		return 42

	def get_alpha(self):		
		if self.get_setting('alpha='):
			return self.get_setting('alpha=')/100.
		return 0

	def legend(self):
		tleg = None
		if len(self.text) <=0:
			print '[e] no text in comment tag'
		else:
			tleg = r.TLegend(self.box[0], self.box[1], self.box[2], self.box[3])
			tleg.SetNColumns(1)
			tleg.SetBorderSize(0)
			tleg.SetFillColor(r.kWhite)
			tleg.SetFillStyle(1001)
			#tleg.SetFillColorAlpha(ROOT.kWhite, 0.9)
			tleg.SetFillColorAlpha(r.kWhite, self.get_alpha())
			tleg.SetTextAlign(12)
			tleg.SetTextSize(self.get_text_size())
			tleg.SetTextFont(self.get_font())
			tleg.SetTextColor(self.get_color())
		for s in self.text:
			print s
			tleg.AddEntry(0, s, '')
		return tleg

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
	tx_size = None
	try:
		tx_size = atof(sleg.split('tx_size=')[1])
	except:
		pass
	print tx_size
	hl.self_legend(title=stitle,x1=x1,x2=x2,y1=y1,y2=y2,tx_size=tx_size)

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

	cs = get_tag_from_file('#comment', fname)
	if cs:
		tc = Comment(cs)
		leg = tc.legend()
		leg.Draw()
		tu.gList.append(leg)

	hl.update()

	if '--print' in sys.argv:
		hl.pdf()

if __name__ == '__main__':
	main()
	if not ut.is_arg_set('-b'):
		IPython.embed()
