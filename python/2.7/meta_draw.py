#!/usr/bin/env python

import ROOT as r
import tutils as tu
import draw_utils as du

import dlist
import sys
import pyutils as ut
import IPython
import time

import os

from string import atof,atoi
import eval_string

#def get_value(st):
#	np = eval_string.NumericStringParser()
#	return np.eval(st)

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
	return retval

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
		if 'norm_self' in st.lower() or 'norm_self_width' in st.lower():
			retval = st.lower()
			print '[i] scale is',retval,type(retval)
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

	def trim(self):
		st = self.get_arg('trim=',',')
		if st == None:
			return st
		args = []
		for s in st.split(' '):
			np = eval_string.NumericStringParser()
			try:
				val = np.eval(s)
			except:
				val = None
			args.append(val)
		return args

class Comment(object):
	def __init__(self, s):
		self.s = s
		self.box = self.get_box()
		self.text = self.get_text()
		self.tleg = None

	def get_box(self):
		x1def = 0.2#0.1
		x2def = 0.8#0.9
		y1def = 0.9#0.1
		y2def = 0.8#0.9
		x1 = None
		x2 = None
		y1 = None
		y2 = None
		if self.s == None:
			return [x1def, y1def, x2def, y2def]
		try:
			spos = self.s.split('#comment ')[0].split(' ')[0]
			if '=' in spos:
				spos = spos.split('=')[0]
		except:
			print 'failed to get the box dimensions'
			spos = None
		if spos != None:
			pos = [None, None, None, None]
			for i in xrange(4):
				try:
					pos[i] = ut.float_or_None(spos.split(',')[i])
				except:
					print '[w] trouble with comment position? x1,y1,x2,y2',self.s
					if len(spos.split(',')) > i:
						print '    ', spos.split(',')[i]
					else:
						print '    n-numbers found:',len(spos.split(',')),spos.split(',')
						print '    tip: no spaces in x1,y1,x2,y2 ...'
			x1 = pos[0]
			y1 = pos[1]
			x2 = pos[2]
			y2 = pos[3]
		if x1 == None: x1 = x1def
		if x2 == None: x2 = x2def
		if y1 == None: y1 = y1def
		if y2 == None: y2 = y2def
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
		known = ['tx_size=', 'color=', 'font=', 'alpha=', 'align=', 'bgc=']
		for k in known:
			if k in s:
				s=s.split(k)[0]
		return s

	def get_setting(self, sitem, separator=''):
		setting = 0
		if self.get_settings(sitem)[-1]:
			if separator == '':
				setting = self.get_settings(sitem)[-1]
			else:
				setting = self.get_settings(sitem)[-1].split(separator)[0]
		return setting

	def get_text(self):
		return self.get_settings('item=')

	def get_text_size(self):
		if self.get_setting('tx_size=', ' '):
			return atof(self.get_setting('tx_size=', ' '))
		return 0.025

	def get_color(self):
		if self.get_setting('color=', ' '):
			return atoi(self.get_setting('color=', ' '))
		return 1

	def get_bg_color(self):
		if self.get_setting('bgc=', ' '):
			return atoi(self.get_setting('bgc=', ' '))
		return r.kWhite

	def get_font(self):
		if self.get_setting(' font=', ' '):
			return self.get_setting('font=', ' ')
		return 42

	def get_alpha(self):
		if self.get_setting('alpha=', ' '):
			return atof(self.get_setting('alpha=', ' '))/100.
		return 0

	def get_alignment(self):
		if self.get_setting('align=', ' '):
			return atoi(self.get_setting('align=', ' '))
		return 12

	def legend(self):
		self.tleg = None
		if len(self.text) <=0:
			print '[e] no text in comment tag'
		else:
			option = 'brNDC #c'
			self.tleg = r.TLegend(self.box[0], self.box[1], self.box[2], self.box[3], '', option)
			self.tleg.SetToolTipText('#comment')
			self.tleg.SetNColumns(1)
			self.tleg.SetBorderSize(0)
			self.tleg.SetFillColor(self.get_bg_color())
			self.tleg.SetFillStyle(1001)
			#tleg.SetFillColorAlpha(ROOT.kWhite, 0.9)
			print '------>',self.get_bg_color()
			self.tleg.SetFillColorAlpha(self.get_bg_color(),
										self.get_alpha())
			self.tleg.SetTextAlign(self.get_alignment())
			self.tleg.SetTextSize(self.get_text_size())
			self.tleg.SetTextFont(self.get_font())
			self.tleg.SetTextColor(self.get_color())
		for s in self.text:
			self.tleg.AddEntry(0, s, '')
		return self.tleg

class MetaFigure(object):
	def __init__(self, fname=''):
		if fname:
			self.name = tu.make_unique_name(fname)
		else:
			self.name = tu.make_unique_name('MetaFigure')
		self.fname    = fname
		self.drawable = True
		self.data     = []
		self.options  = []
		#self.hls      = dlist.ListStorage(self.name+'_storage')
		#self.hl       = self.hls.get_list(self.name+'_list')
		self.hl        = dlist.dlist(self.name + '_list')
		self.last_ds  = None
		self.comments = []

	def check_filepath(self, path):
		# if $ within the path -> expand it and continue testing
		# if the path does not exist
		# if this does not apply
		# try to guess that it is a relative path wrt self.fname
		test_path = path
		if '$' in path:
			# expand and try...
			test_path = r.gSystem.ExpandPathName(path)
		try:
			f = open(test_path)
			f.close()
		except:
			user_dir = self.get_tag('#dir', None)
			if user_dir:
				dname = user_dir
			else:
				dname = os.path.dirname(os.path.abspath(self.fname))
			test_path = os.path.join(dname, path)
			if '$' in test_path:
				test_path = r.gSystem.ExpandPathName(test_path)
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
		cobj = self.hl.add_from_file(self.last_ds.hname, self.last_ds.fname, self.last_ds.title(), self.last_ds.dopt)
		if cobj != None:
			scale = self.last_ds.scale()
			if scale != None:
				if type(scale) is str:
					scale = scale.lower()
					if 'norm_self_width' in scale:
						intv = self.hl[-1].obj.Integral('width')
						if intv != 0:
							self.hl.scale_at_index(-1, 1./intv)
						scale = scale.replace('norm_self_width', '1.')
					if 'norm_self' in scale:
						intv = self.hl[-1].obj.Integral()
						if intv != 0:
							self.hl.scale_at_index(-1, 1./intv)
						scale = scale.replace('norm_self', '1.')
					vscale = get_value(scale, float, 1.)
					if vscale != 1.:
						self.hl.scale_at_index(-1, vscale)
				else:
					self.hl.scale_at_index(-1, scale)
			if self.last_ds.trim() != None:
				self.hl.trim_at_index(-1, self.last_ds.trim()[0], self.last_ds.trim()[1])
		else:
			print '[w] failed to add',self.last_ds.hname,'from',self.last_ds.fname

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
			else:
				if tag == l.strip():
					retval = l.replace(tag,'')
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
			args[5] = '1 '#style
			args[6] = '3 '#width
			args[7] = '0.5' #alpha
			args[8] = 'brNDC'
			nums = t.split(',')
			try:
				for i,n in enumerate(nums):
					if len(n) > 0:
						args[i] = n
			except:
				print '[w] trouble with line:',t
			# du.draw_line(x1, y1, x2, y2, col=2, style=7, width=2, option='brNDC', alpha=0.3)
			du.draw_line(	get_value(args[0]), get_value(args[1]), get_value(args[2]), get_value(args[3]),
							get_value(args[4], int, 2), get_value(args[5], int, 1), get_value(args[6], int, 3), args[8],
							get_value(args[7], float, 0.8));

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
				self.add_option('#comment -0.1,0.4,1.0,0.6,item=WARNING: empty drawing list... tx_size=0.06')
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

		if self.last_ds :
			self.hl.reset_axis_titles(self.last_ds.xt(), self.last_ds.yt(), self.last_ds.zt())
		xt = self.get_tag('#x', None)
		yt = self.get_tag('#y', None)
		zt = self.get_tag('#z', None)
		self.hl.reset_axis_titles(xt, yt, zt)

		rebin = self.get_tag('#rebin', None, ' ')
		if rebin!=None:
			print '[i] rebin arg:',atoi(rebin[0])
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
		maxy = self.get_tag('#maxy', None)
		logx = self.get_tag('#logx', None)
		if logx == 'true' or logx == '1':
			logx=True
		else:
			logx=False
		logy = self.get_tag('#logy', None)
		if logy == 'true' or logy == '1':
			logy=True
		else:
			logy=False
		logz = self.get_tag('#logz', None)
		if logz == 'true' or logz == '1':
			logz=True
		else:
			logz=False

		if self.last_ds :
			if miny == None:
				miny=self.last_ds.miny()
			else:
				miny=get_value(miny, float, -1)
			if maxy == None:
				maxy=self.last_ds.maxy()
			else:
				maxy=get_value(maxy, float,  1.)
			if logy == False:
				logy=self.last_ds.logy()
			if logx == False:
				logx=self.last_ds.logx()
			if logz == False:
				logz=self.last_ds.logz()

		if logy == True:
			if miny != None:
				if miny <= 0:
					print '[w] overrdingin logy miny<=0',miny
					logy=False
			if maxy != None:
				if maxy <= 0:
					print '[w] overrdingin logy maxy<=0',maxy
					logy=False

		self.hl.set_log_multipad('xyz', False)

		# axis shapes and sizes etc..
		atos = self.get_tags('#ato')
		for s in atos:
			for i, ax in enumerate(s.split(',')):
				print i, ax
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_title_offset[i] = v
		atss = self.get_tags('#ats')
		for s in atss:
			for i, ax in enumerate(s.split(',')):
				print i, ax
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_title_size[i] = v
		alos = self.get_tags('#alo')
		for s in alos:
			for i, ax in enumerate(s.split(',')):
				print i, ax
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_label_offset[i] = v
		alss = self.get_tags('#als')
		for s in alss:
			for i, ax in enumerate(s.split(',')):
				print i, ax
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_label_size[i] = v

		self.hl.draw(miny=miny,maxy=maxy,logy=logy)

		pmargs = self.get_tags('#pad_margins')
		for s in pmargs:
			ors = s.split(',')
			vals = [None, None, None, None]
			for i, so in enumerate(ors):
				if i < 4:
					vals[i] = get_value(so, float, None)
			self.hl.adjust_pad_margins(vals[0], vals[1], vals[2], vals[3])

		if logy:
			self.hl.set_log_multipad('y')
		else:
			self.hl.set_log_multipad('y', False)
		if logx:
			self.hl.set_log_multipad('x')
		else:
			self.hl.set_log_multipad('x', False)
		if logz:
			self.hl.set_log_multipad('z')
		else:
			self.hl.set_log_multipad('z', False)

		#setgridxy
		self.hl.set_grid_multipad('xy', False)
		grids = self.get_tag('#grid', None)
		if grids != None:
			self.hl.set_grid_multipad(grids)

		sfigtitle = self.get_tag('#title', '')
		if len(sfigtitle) > 0:
			self.add_option('#comment -0.1,0.9,1.0,1.0, tx_size=0.06 align=22 item={}'.format(sfigtitle))

		#legend
		sleg = self.get_tag('#legend')
		x1,y1,x2,y2 = self.legend_position(sleg)
		tx_size = 0.025
		try:
			tx_size = atof(sleg.split('tx_size=')[1].split(' ')[0])
		except:
			pass
		leg_opt = 'brNDC'
		try:
			if 'alpha=' in sleg:
				leg_opt = leg_opt + ' +a' + sleg.split('alpha=')[1].split(' ')[0]
		except:
			leg_opt = 'brNDC'
		#print '[i] legend options:',leg_opt
		stitle = ''
		try:
			stitle = sleg.split('title=')[1].split(',,')[0]
		except:
			pass
		ncol = 1
		try:
			ncol = int(sleg.split('ncol=')[1].split(',,')[0])
		except:
			ncol = 1
		self.hl.self_legend(ncols=ncol,title=stitle,x1=x1,x2=x2,y1=y1,y2=y2,tx_size=tx_size,option=leg_opt)

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

		ds = self.get_tag('#date')
		if ds != None:
			try:
				st = ds.replace('#date', '').strip()
			except:
				pass
			if len(st) > 0:
				self.add_option('#comment 0.0,0.0,0.05,0.05,item={} alpha=0.5 tx_size=0.02'.format(st))
			else:
				stime = time.strftime("%H:%M:%S %Z")
				#sdate = time.strftime("%a, %d/%m/%Y")
				sdate = time.strftime("%a %d/%m/%Y")
				#sdate = time.strftime("%c")
				#0.00352112676056,0.00196078431373,0.0774647887324,0.101960784314
				self.add_option('#comment 0.0,0.0,0.05,0.05,item={} {} alpha=0.5 tx_size=0.02'.format(sdate, stime))

		cs = self.get_tags('#comment')
		for c in cs:
			if c == None:
				continue
			if len(c) > 0:
				tc = Comment(c)
				leg = tc.legend()
				leg.Draw()
				self.comments.append(tc)
				#tu.gList.append(leg)

		sname = self.get_tag('#name', None)
		if sname != None:
			#self.hl.tcanvas.SetName(sname)
			self.hl.tcanvas.SetTitle(sname)
			self.hl.name = tu.unique_name(ut.to_file_name(sname))

		self.hl.update()

		# note: for making funky stuff you probably need root6...
		groots = self.get_tags('#r')
		for c in groots:
			print '[i] trying root to process line', c
			# result = r.gROOT.ProcessLine(c)
			# print '  ->', result
			r.gInterpreter.ProcessLine(c)

		# this is also no good...
		groots = self.get_tags('#rpy')
		for c in groots:
			print '[i] trying root to process line', c
			with open('./tmp.py', 'w') as f:
				print >> f, 'import tutils'
				print >> f, 'import ROOT as r'
				print >> f, c
			sys.path.append(os.getcwd())
			import tmp

		# this is overwritten by hl but a good idea
		gpads = self.get_tags('#gpad')
		for s in gpads:
			print s
			if 'lm ' in s:
				v = get_value(s.split(' ')[-1], float, None)
				if v:
					r.gPad.SetLeftMargin(v)
					print 'gpad set left margin to', v
			if 'rm ' in s:
				v = get_value(s.split(' ')[-1], float, None)
				if v:
					r.gPad.SetRightMargin(v)
					print 'gpad set right margin to', v

	def pdf(self):
		if self.drawable == True:
			self.hl.pdf()

	def png(self):
		if self.drawable == True:
			self.hl.png()

	def add_option(self, opt):
		self.options.append(opt)
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
		self.options = []

	def draw(self):
		for f in self.figures:
			f.draw()

	def pdf(self):
		for f in self.figures:
			f.pdf()

	def png(self):
		for f in self.figures:
			f.png()

	def add_option(self, opt):
		for f in self.figures:
			f.add_option(opt)
		self.options.append(opt)

if __name__ == '__main__':
	tu.setup_basic_root()
	fname = ut.get_arg_with('-f')
	fn, fext = os.path.splitext(fname)
	metafname = None
	if fext == '.root':
		import make_draw_files as makedf
		#metafname = makedf.make_draw_file(fname)
		metafname = makedf.make_draw_file_smart_group(fname)
	else:
		metafname = fname
	mdf   = MetaDrawFile(metafname)
	if '--logy' in sys.argv:
		mdf.add_option('#logy true')
	if '--date' in sys.argv:
		mdf.add_option('#date')
	if '--comment' in sys.argv:
		c = ut.get_arg_with('--comment')
	else:
		c = fname
	mdf.add_option('#comment item={}'.format(c))
	if fext == '.root':
		print fname
		#metafname = makedf.make_draw_file(fname, mdf.options, force=True)
		metafname = makedf.make_draw_file_smart_group(fname, mdf.options, force=True)
		mdf   = MetaDrawFile(metafname)
	mdf.draw()
	if '--print' in sys.argv:
		mdf.pdf()
	if not ut.is_arg_set('-b'):
		IPython.embed()
