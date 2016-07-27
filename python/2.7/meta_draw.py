#!/usr/bin/env python

import ROOT as r 
import tutils as tu
import draw_utils as du

import dlist
import sys
import pyutils as ut
import IPython

import os

from string import atof,atoi
import eval_string

class DrawString(object):
	def __init__(self, s):
		self.s = s
		self.fname = ''
		self.hname = ''
		self.dopt  = ''
		self.opts  = ''
		self.process()
		#print '[i] fname={} hname={} dopt={} opts={}'.format(self.fname, self.hname, self.dopt, self.opts)

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

	def get_arg(self, sarg, sp = ','):
		s = self.opts.split(sp)
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
		st = self.get_arg('title=', sp=',,')
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

	def scale(self):
		st = self.get_arg('scale=',',')
		retval = None
		if st == None:
			return retval
		try:
			#retval = atof(st)
			np = eval_string.NumericStringParser()
			retval = np.eval(st)
			#print st,retval
		except:
			retval = None
			print '[w] scale not understood:',self.s
		return retval

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
			tleg.AddEntry(0, s, '')
		return tleg

class MetaFigure(object):
	def __init__(self, fname=''):
		if fname:
			self.name = tu.make_unique_name(fname)
		else:
			self.name = tu.make_unique_name('MetaFigure')
		self.fname    = fname
		self.drawable = True
		self.data     = []
		self.hls      = dlist.ListStorage(self.name+'_storage')
		self.hl       = self.hls.get_list(self.name+'_list')
		self.last_ds  = None

	def check_filepath(self, path):
		# if $ within the path -> expand it and continue testing
		# if the path does not exist
		# if this does not apply
		# try to guess that it is a relative path wrt self.fname
		test_path = path
		if '$' in path:
			#expand and try...
			test_path = r.gSystem.ExpandPathName(path)
		try:
			f = open(test_path)
			f.close()
		except:
			dname = os.path.dirname(os.path.abspath(self.fname))
			test_path = os.path.join(dname, path)
		try:
			f = open(test_path)
			f.close()
		except:
			test_path = path
		if path != test_path:
			print >> sys.stderr,'[w] file path adjusted:',path,'->',test_path
		return test_path

	def process_line(self, cline):
		if len(cline) < 1:
			return
		self.data.append(cline)
		if cline[0] == '#':
			return
		self.last_ds = DrawString(cline)
		self.last_ds.fname = self.check_filepath(self.last_ds.fname)
		self.hl.add_from_file(self.last_ds.hname, self.last_ds.fname, self.last_ds.title(), self.last_ds.dopt)		
		if self.last_ds.scale() != None:
			self.hl.scale_at_index(-1, self.last_ds.scale())

	def process_lines(self, clines):
		for l in clines:
			self.process_line(l)

	def legend_position(self, sleg):
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

	def get_tag(self, tag, default=None, split=None):
		retval = default
		for l in self.data:
			if tag+' ' in l[:len(tag)+1]:
				retval = l.replace(tag+' ','')
		if split != None and retval != None:
			retval = retval.split(split)
		return retval

	def get_tags(self, tag):
		retvals = []
		for l in self.data:
			if tag+' ' in l[:len(tag)+1]:
				retval = l.replace(tag+' ','')
				retvals.append(retval)
		return retvals

	def draw_lines(self):
		ts = self.get_tags('#line')
		for t in ts:
			args = ['0' for i in xrange(9)]
			args[0] = '0'
			args[1] = '0'
			args[2] = '1'
			args[3] = '1'
			args[4] = '2 '#color
			args[5] = '7 '#style
			args[6] = '2 '#width
			args[7] = '1.' #alpha
			args[8] = 'brNDC'
			nums = t.split(',')
			try:
				for i,n in enumerate(nums):
					if len(n) > 0:
						args[i] = n
			except:
				print '[w] trouble with line:',t
		#du.draw_line(x1, y1, x2, y2, col=2, style=7, width=2, option='brNDC', alpha=0.3)
			du.draw_line(	atof(args[0]), atof(args[1]), atof(args[2]), atof(args[3]),
							atoi(args[4]), atoi(args[5]), atoi(args[6]), args[8], atof(args[7]));

	def axis_range(self, sleg):
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

	def add_dummy(self):
		gr = r.TGraph(2)
		gr.SetPoint(0, -1,  1)
		gr.SetPoint(1, +1,  1)
		self.hl.add(gr, 'WARNING: LIST EMPTY!', 'hidden')

	def draw(self, no_canvas=False, add_dummy=True):
		if add_dummy == True:
			if len(self.hl.l) < 1:
				#self.add_dummy()
				self.add_option('#comment -0.1,0.9,1.0,1.0,item=WARNING: empty drawing list... tx_size=0.06')
		else:
			if self.last_ds == None:
				print '[e] nothing to draw for',self.name
				self.drawable = False
				return

		sxrange = self.get_tag('#xrange', None)
		if sxrange != None:
			x1, x2 = self.axis_range(sxrange)
			self.hl.fix_x_range(x1, x2)
			self.hl.zoom_axis(0, x1, x2)

		if no_canvas == True:
			if r.gPad:
				#print '[i] will draw in the current gPad=',r.gPad.GetName()
				self.hl.tcanvas = r.gPad
			else:
				print '[w] this will likely not work well... gPad is',r.gPad
		else:
			self.hl.make_canvas()

		self.hl.reset_axis_titles(self.last_ds.xt(), self.last_ds.yt(), self.last_ds.zt())
		xt = self.get_tag('#x', None)
		yt = self.get_tag('#y', None)
		zt = self.get_tag('#z', None)
		self.hl.reset_axis_titles(xt, yt, zt)

		rebin = self.get_tag('#rebin', None, ' ')
		if rebin!=None:
			print atoi(rebin[0])
			if len(rebin) > 0:
				self.hl.rebin(atoi(rebin[0]))
			if len(rebin) > 1:
				if 'true' in rebin[1].lower():
					print '[i] rebin with renorm...'
					self.hl.rebin(atoi(rebin[0]), True)
				else:
					print '[i] rebin w/o renorm...'
					self.hl.rebin(atoi(rebin[0]), False)

		normalize = self.get_tag('#normalize', None)
		if normalize == 'self':
			self.hl.normalize_self()

		miny = self.get_tag('#miny', None)
		if miny == None:
			miny=self.last_ds.miny()
		else:
			miny=atof(miny)
		maxy = self.get_tag('#maxy', None)
		if maxy == None:
			maxy=self.last_ds.maxy()
		else:
			maxy=atof(maxy)

		logy = self.get_tag('#logy', None)
		if logy == 'true':
			logy=True
		if logy == None:
			logy=self.last_ds.logy()
		logx = self.get_tag('#logx', None)
		if logx == 'true':
			logx=True
		if logx == None:
			logx=self.last_ds.logx()
		else:
			logx=False
		logz = self.get_tag('#logz', None)
		if logz == 'true':
			logz=True
		if logz == None:
			logz=self.last_ds.logz()
		else:
			logz=False

		#print 'logy is',logy

		self.hl.draw(miny=miny,maxy=maxy,logy=logy)

		if logy:
			self.hl.set_log_multipad('y')
		if logx:
			self.hl.set_log_multipad('x')
		if logz:
			self.hl.set_log_multipad('z')

		#setgridxy
		self.hl.set_grid_multipad('xy', False)
		grids = self.get_tag('#grid', None)
		if grids != None:
			self.hl.set_grid_multipad(grids)
		#legend
		stitle = self.get_tag('#title', '')
		sleg = self.get_tag('#legend')
		x1,y1,x2,y2 = self.legend_position(sleg)
		tx_size = None
		try:
			tx_size = atof(sleg.split('tx_size=')[1])
		except:
			pass
		self.hl.self_legend(title=stitle,x1=x1,x2=x2,y1=y1,y2=y2,tx_size=tx_size)

		#line
		self.draw_lines()

		#size of the window
		x = 400
		y = 300
		gs = self.get_tag('#geom')
		if gs != None:
			try:
				x = atoi(gs.split('x')[0])
				y = atoi(gs.split('x')[1])
			except:
				print '[e] unable to understand the --geom argument',gs
		if no_canvas == False:
			self.hl.resize_window(x,y)

		cs = self.get_tags('#comment')
		for c in cs:
			if c == None:
				continue
			if len(c) > 0:
				tc = Comment(c)
				leg = tc.legend()
				leg.Draw()
				tu.gList.append(leg)

		sname = self.get_tag('#name', None)
		if sname != None:
			#self.hl.tcanvas.SetName(sname)
			self.hl.tcanvas.SetTitle(sname)
			self.hl.name = tu.unique_name(ut.to_file_name(sname))

		self.hl.update()

	def pdf(self):
		if self.drawable == True:
			self.hl.pdf()

	def add_option(self, opt):
		self.data.append(opt)

class MetaDrawFile(object):
	def __init__(self, fname=None):
		self.data = ut.load_file_to_strings(fname)
		self.figures = []
		fig = MetaFigure(fname)
		self.figures.append(fig)
		for d in self.data:
			if d[:len('#figure')] == '#figure':
				if len(self.figures[-1].data) > 1:
					fig = MetaFigure(fname)
					self.figures.append(fig)
				continue
			self.figures[-1].process_line(d)

	def draw(self):
		for f in self.figures:
			f.draw()

	def pdf(self):
		for f in self.figures:
			f.pdf()		

	def add_option(self, opt):
		for f in self.figures:
			f.add_option(opt)

if __name__ == '__main__':
	tu.setup_basic_root()
	fname = ut.get_arg_with('-f')
	fn, fext = os.path.splitext(fname)
	if fext == '.root':
		import make_draw_files as mdf
		fname = mdf.make_draw_file(fname)
	mdf   = MetaDrawFile(fname)
	if '--logy' in sys.argv:
		mdf.add_option('#logy true')
	mdf.draw()
	if '--print' in sys.argv:
		mdf.pdf()
	if not ut.is_arg_set('-b'):
		IPython.embed()
