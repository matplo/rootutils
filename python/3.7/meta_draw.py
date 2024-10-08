#!/usr/bin/env python

import ROOT as r
import tutils as tu
import draw_utils as du

import dlist
import sys
import pyutils as ut
import time

import os
import argparse

from eval_string import get_value 

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
		if st is None:
			st = self.fname
		return st

	def exec(self):
		st = self.get_arg('exec=', sp=',,')
		if st is None:
			return st
		return st

	def miny(self):
		st = self.get_arg('miny=')
		if st is not None:
			st = get_value(st, float, -1.)
		return st

	def maxy(self):
		st = self.get_arg('maxy=')
		if st is not None:
			st = get_value(st, float, 1.)
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
		if st is None:
			return retval
		if 'norm_self' in st.lower() or 'norm_self_width' in st.lower():
			retval = st.lower()
			print('[i] scale is',retval,type(retval))
			return retval
		try:
			retval = get_value(st, float, 1.)
			print("scale:", st, retval)
		except:
			retval = None
			print('[w] scale not understood:',self.s)
		return retval

	def flatten(self):
		st = self.get_arg('flatten=', ',')
		retval = None
		if st is None:
			return retval
		try:
			retval = get_value(st, float, 1.)
			print("flatten:", st, retval)
		except:
			retval = None
			print('[w] flatten not understood:',self.s)
		return retval


	def trim(self):
		st = self.get_arg('trim=',',')
		if st is None:
			return st
		args = []
		for s in st.split(' '):
			val = get_value(s)
			args.append(val)
		return args

class Comment(object):
	def __init__(self, s):
		self.s = s
		self.box = self.get_position()
		if self.box is None:
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
			print('failed to get the box dimensions')
			spos = None
		if spos is not None:
			pos = [None, None, None, None]
			for i in range(4):
				try:
					pos[i] = ut.float_or_None(spos.split(',')[i])
				except:
					print('[w] trouble with comment position? x1,y1,x2,y2',self.s)
					if len(spos.split(',')) > i:
						print('    ', spos.split(',')[i])
					else:
						print('    n-numbers found:',len(spos.split(',')),spos.split(','))
						print('    tip: no spaces in x1,y1,x2,y2 ...')
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
		for n in range(1,len(splits)):
			retval.append(self.filter_known_settings(splits[n]))
		if len(retval) <= 0:
			retval.append(None)
		return retval

	def filter_known_settings(self, s):
		known = ['tx_size=', 'color=', 'font=', 'alpha=', 'align=', 'bgc=', 'tx_rotation=', 'pos=']
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
			return get_value(self.get_setting('tx_size=', ' '), float, 0.035)
		return 0.025

	def get_text_rotation(self):
		if self.get_setting('tx_rotation=', ' '):
			return get_value(self.get_setting('tx_rotation=', ' '), float, 0.0)
		return 0.0

	def get_color(self):
		if self.get_setting('color=', ' '):
			return get_value(self.get_setting('color=', ' '), int, 1)
		return 1

	def get_bg_color(self):
		if self.get_setting('bgc=', ' '):
			return get_value(self.get_setting('bgc=', ' '), int, 0)
		return r.kWhite

	def get_font(self):
		if self.get_setting('font=', ' '):
			return self.get_setting('font=', ' ')
		return 42

	def get_alpha(self):
		if self.get_setting('alpha=', ' '):
			return get_value(self.get_setting('alpha=', ' '), float, 100.)
		return 0

	def get_alignment(self):
		if self.get_setting('align=', ' '):
			return get_value(self.get_setting('align=', ' '), int, 1)
		return 12

	def get_position(self):
		pos = self.get_setting('pos=', ' ')
		retval = None
		if pos:
			if pos == 'down':
				retval = [0.2,0.25,0.92,0.44]
			if pos == 'up':
				retval = [0.2,0.67,0.92,0.87]
			if pos == 'lr':
				retval = [0.52,0.25,0.92,0.44]
			if pos == 'ur':
				retval = [0.52,0.67,0.92,0.87]
			if pos == 'll':
				retval = [0.2,0.25,0.52,0.44]
			if pos == 'ul':
				retval = [0.2,0.67,0.52,0.87]
		return retval

	def legend(self):
		self.tleg = None
		if len(self.text) <=0:
			print('[e] no text in comment tag')
		else:
			option = 'brNDC #c'
			self.tleg = r.TLegend(self.box[0], self.box[1], self.box[2], self.box[3], '', option)
			self.tleg.SetToolTipText('#comment')
			self.tleg.SetNColumns(1)
			self.tleg.SetBorderSize(0)
			self.tleg.SetFillColor(self.get_bg_color())
			self.tleg.SetFillStyle(1001)
			#tleg.SetFillColorAlpha(ROOT.kWhite, 0.9)
			print('------>',self.get_bg_color())
			self.tleg.SetFillColorAlpha(self.get_bg_color(),
										self.get_alpha())
			self.tleg.SetTextAlign(self.get_alignment())
			self.tleg.SetTextSize(self.get_text_size())
			self.tleg.SetTextFont(self.get_font())
			self.tleg.SetTextColor(self.get_color())
		for s in self.text:
			e = self.tleg.AddEntry(0, s, '')
			e.SetTextAngle(self.get_text_rotation())
		return self.tleg


class PaveText(object):
	def __init__(self, s):
		self.s = s
		self.box = self.get_position()
		if self.box is None:
			self.box = self.get_box()
		self.text = self.get_text()
		self.tleg = None

	def get_box(self):
		x1def = 0.2  # 0.1
		x2def = 0.8  # 0.9
		y1def = 0.9  # 0.1
		y2def = 0.8  # 0.9
		x1 = None
		x2 = None
		y1 = None
		y2 = None
		if self.s == None:
			return [x1def, y1def, x2def, y2def]
		try:
			spos = self.s.split('#pavetext ')[0].split(' ')[0]
			if '=' in spos:
				spos = spos.split('=')[0]
		except:
			print('failed to get the box dimensions')
			spos = None
		if spos is not None:
			pos = [None, None, None, None]
			for i in range(4):
				try:
					pos[i] = ut.float_or_None(spos.split(',')[i])
				except:
					print('[w] trouble with comment position? x1,y1,x2,y2', self.s)
					if len(spos.split(',')) > i:
						print('    ', spos.split(',')[i])
					else:
						print('    n-numbers found:', len(spos.split(',')), spos.split(','))
						print('    tip: no spaces in x1,y1,x2,y2 ...')
			x1 = pos[0]
			y1 = pos[1]
			x2 = pos[2]
			y2 = pos[3]
		if x1 == None:
			x1 = x1def
		if x2 == None:
			x2 = x2def
		if y1 == None:
			y1 = y1def
		if y2 == None:
			y2 = y2def
		return [x1, y1, x2, y2]

	def get_settings(self, sitem):
		retval = []
		splits = self.s.split(sitem)
		for n in range(1, len(splits)):
			retval.append(self.filter_known_settings(splits[n]))
		if len(retval) <= 0:
			retval.append(None)
		return retval

	def filter_known_settings(self, s):
		known = ['tx_size=', 'color=', 'font=', 'alpha=', 'align=', 'bgc=', 'tx_rotation=', 'pos=']
		for k in known:
				if k in s:
					s = s.split(k)[0]
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
			return get_value(self.get_setting('tx_size=', ' '), float, 0.035)
		return 0.025

	def get_text_rotation(self):
		if self.get_setting('tx_rotation=', ' '):
			return get_value(self.get_setting('tx_rotation=', ' '), float, 0.0)
		return 0.0

	def get_color(self):
		if self.get_setting('color=', ' '):
			return get_value(self.get_setting('color=', ' '), int, 1)
		return 1

	def get_bg_color(self):
		if self.get_setting('bgc=', ' '):
			return get_value(self.get_setting('bgc=', ' '), int, 0)
		return r.kWhite

	def get_font(self):
		if self.get_setting('font=', ' '):
			return self.get_setting('font=', ' ')
		return 42

	def get_alpha(self):
		if self.get_setting('alpha=', ' '):
			return get_value(self.get_setting('alpha=', ' '), float, 100.)
		return 0

	def get_alignment(self):
		if self.get_setting('align=', ' '):
			return get_value(self.get_setting('align=', ' '), int, 12)
		return 12

	def get_angle(self):
		if self.get_setting('angle=', ' '):
			return get_value(self.get_setting('angle=', ' '), int, 0)
		return 0

	def get_position(self):
		pos = self.get_setting('pos=', ' ')
		retval = None
		if pos:
			if pos == 'down':
				retval = [0.2, 0.25, 0.92, 0.44]
			if pos == 'up':
				retval = [0.2, 0.67, 0.92, 0.87]
			if pos == 'lr':
				retval = [0.52, 0.25, 0.92, 0.44]
			if pos == 'ur':
				retval = [0.52, 0.67, 0.92, 0.87]
			if pos == 'll':
				retval = [0.2, 0.25, 0.52, 0.44]
			if pos == 'ul':
				retval = [0.2, 0.67, 0.52, 0.87]
		return retval

	def tptext(self):
		self.tptext = None
		if len(self.text) <= 0:
			print('[e] no text in comment tag')
		else:
			self.tptext = r.TPaveText(self.box[0], self.box[1],
																self.box[2], self.box[3])
			print('paveText at:', self.box)
			for s in self.text:
				_tt = self.tptext.AddText(s)
				_tt.SetTextAlign(self.get_alignment())
				_tt.SetTextAngle(self.get_angle())
				# self.tptext.Draw();
			self.tptext.SetToolTipText('#pavetext')
			# self.tptext.SetNColumns(1)
			self.tptext.SetBorderSize(0)
			self.tptext.SetFillColor(self.get_bg_color())
			self.tptext.SetFillStyle(1001)
			#tleg.SetFillColorAlpha(ROOT.kWhite, 0.9)
			print('------>', self.get_bg_color())
			self.tptext.SetFillColorAlpha(self.get_bg_color(), self.get_alpha())
			self.tptext.SetTextAlign(self.get_alignment())
			self.tptext.SetTextSize(self.get_text_size())
			self.tptext.SetTextFont(self.get_font())
			self.tptext.SetTextColor(self.get_color())
			self.tptext.SetTextAngle(self.get_angle())
			print(self.get_angle())
		return self.tptext


class MetaFigure(object):
	show_date = False
	def __init__(self, fname='', wname=None):
		self.wname = wname
		if self.wname is None:
			self.wname = fname
		if self.wname:
			self.name = tu.make_unique_name(self.wname)
		else:
			self.name = tu.make_unique_name('MetaFigure')
		self.figure_name = self.name
		self.fname    = fname
		self.drawable = True
		self.data     = []
		self.options  = []
		#self.hls      = dlist.ListStorage(self.name+'_storage')
		#self.hl       = self.hls.get_list(self.name+'_list')
		self.hl        = dlist.dlist(self.name + '_list')
		self.last_ds  = None
		self.comments = []

	def file_ok(self, test_path):
		if test_path:
			if '~' == test_path[0]:
				test_path = test_path.replace('~', '$HOME')
			if '$' in test_path:
				test_path = r.gSystem.ExpandPathName(test_path)
		rval = None
		try:
			f = open(test_path)
			f.close()
			rval = test_path
		except:
			pass
		return rval

	def adjust_filepath(self, path):
		# if $ within the path -> expand it and continue testing
		# if the path does not exist
		# if this does not apply
		# try to guess that it is a relative path wrt self.fname
		test_path = self.file_ok(path)
		if self.file_ok(test_path) is None:
			user_dirs = self.get_tags('#dir')
			user_dirs.append(os.path.dirname(os.path.abspath(self.fname)))
			for user_dir in user_dirs:
				test_path = os.path.join(user_dir, path)
				test_path = self.file_ok(test_path)
				if test_path:
					break
		if test_path is None:
			test_path = path
		if path != test_path:
			print('[w] file path adjusted:',path,'->',test_path, file=sys.stderr)
		return test_path

	def process_line(self, cline):
		if len(cline) < 1:
			return
		self.data.append(cline)
		self.figure_name = self.get_tag('#figure', None)
		if cline[0] == '#':
			return
		self.last_ds = DrawString(cline)
		self.last_ds.fname = self.adjust_filepath(self.last_ds.fname)
		cobj = self.hl.add_from_file(self.last_ds.hname, self.last_ds.fname, self.last_ds.title(), self.last_ds.dopt)
		if cobj is not None:
			scale = self.last_ds.scale()
			if scale is not None:
				if type(scale) is str:
					scale = scale.lower()
					if 'norm_self_width' in scale:
						self.hl.scale_at_index(-1, 0.0)
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
			if self.last_ds.trim() is not None:
				self.hl.trim_at_index(-1, self.last_ds.trim()[0], self.last_ds.trim()[1])
			flatten = self.last_ds.flatten()
			if flatten is not None:
				print('flattening by', flatten)
				self.hl.flatten_at_index(-1, flatten)
			_exec = self.last_ds.exec()
			if _exec is not None:
				cobj.exec.append(_exec)
		else:
			print('[w] failed to add',self.last_ds.hname,'from',self.last_ds.fname)

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
			x1 = get_value(sleg.split(',')[0], float, None)
			y1 = get_value(sleg.split(',')[1], float, None)
			x2 = get_value(sleg.split(',')[2], float, None)
			y2 = get_value(sleg.split(',')[3], float, None)
		except:
			print('[w] trouble with legend position? x1,y1,x2,y2',sleg)
		return x1, y1, x2, y2

	def get_tag(self, tag, default=None, split=None):
		retval = default
		for l in self.data:
			if tag+' ' in l[:len(tag)+1]:
				retval = l.replace(tag+' ','')
			else:
				if tag == l.strip():
					retval = l.replace(tag,'')
		if split is not None and retval is not None:
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
			args = ['0' for i in range(9)]
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
				print('[w] trouble with line:',t)
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
			x1 = get_value(sleg.split(',')[0], float, -1)
			x2 = get_value(sleg.split(',')[1], float, +1)
		except:
			print('[w] trouble with x-range? x1,x2',sleg)
		return x1, x2

	def add_dummy(self):
		gr = r.TGraph(2)
		gr.SetPoint(0, -1,  1)
		gr.SetPoint(1, +1,  1)
		self.hl.add(gr, 'WARNING: LIST EMPTY!', 'hidden')

	def draw(self, no_canvas=False, add_dummy=True):
		self.figure_name = self.get_tag('#figure', None)
		if self.get_tag('#debug', None):
			dlist.gDebug = True
		if add_dummy == True:
			if len(self.hl.l) < 1:
				#self.add_dummy()
				self.add_option('#comment -0.1,0.4,1.0,0.6,item=WARNING: empty drawing list... tx_size=0.06')
		else:
			if self.last_ds == None:
				print('[e] nothing to draw for',self.name)
				self.drawable = False
				return

		sxrange = self.get_tag('#xrange', None)
		if sxrange is not None:
			x1, x2 = self.axis_range(sxrange)
			self.hl.fix_x_range(x1, x2)
			self.hl.zoom_axis(0, x1, x2)

		sxrange = self.get_tag('#2dxrange', None)
		if sxrange is not None:
			x1, x2 = self.axis_range(sxrange)
			ax = self.hl[0].obj.GetXaxis()
			ib1 = ax.FindBin(x1)
			ib2 = ax.FindBin(x2)
			ax.SetRange(ib1,ib2)

		sxrange = self.get_tag('#2dyrange', None)
		if sxrange is not None:
			x1, x2 = self.axis_range(sxrange)
			ax = self.hl[0].obj.GetYaxis()
			ib1 = ax.FindBin(x1)
			ib2 = ax.FindBin(x2)
			ax.SetRange(ib1,ib2)

		if no_canvas == True:
			if r.gPad:
				#print '[i] will draw in the current gPad=',r.gPad.GetName()
				self.hl.tcanvas = r.gPad
			else:
				print('[w] this will likely not work well... gPad is',r.gPad)
		else:
			self.hl.make_canvas()

		if self.last_ds :
			self.hl.reset_axis_titles(self.last_ds.xt(), self.last_ds.yt(), self.last_ds.zt())
		xt = self.get_tag('#x', None)
		yt = self.get_tag('#y', None)
		zt = self.get_tag('#z', None)
		self.hl.reset_axis_titles(xt, yt, zt)

		fleg = self.get_tag('#force_legend', None)
		if get_value(fleg, int, 0) > 0:
			self.hl.force_legend = True

		rebin = self.get_tag('#rebin', None, ' ')
		if rebin!=None:
			print('[i] rebin arg:',get_value(rebin[0], int, 1))
			if len(rebin) > 0:
				self.hl.rebin(get_value(rebin[0], int, 1))
			if len(rebin) > 1:
				if 'true' in rebin[1].lower():
					print('[i] rebin with renorm...')
					self.hl.rebin(get_value(rebin[0], int, 1), True)
				else:
					print('[i] rebin w/o renorm...')
					self.hl.rebin(get_value(rebin[0], int, 1), False)

		normalize = self.get_tag('#normalize', None)
		if normalize:
			if normalize == 'self':
				self.hl.normalize_self()
			else:
				if 'index' in normalize:
					idx = normalize.split('index=')[1].split(' ')[0]
					vidx = get_value(idx, int, -1)
					print('[i] to normalize to',vidx)
					self.hl.normalize_to_index(vidx)

		sscale = self.get_tag('#scale', None)
		if sscale:
			if 'const' in sscale:
				sval = sscale.split('const=')[1].split(' ')[0]
				val = get_value(sval, float, 1.)
				print('[i] scale any to', val)
				self.hl.scale_any(val)
			if 'indexGraph=' in sscale:
				idx = sscale.split('indexGraph=')[1].split(' ')[0]
				vidx = get_value(idx, int, -1)
				print('[i] to scale to', vidx)
				newhl = self.hl.ratio_to_graph(vidx)
				try:
					ratio_fout_name = sscale.split('fout=')[1].split(' ')[0]
					newhl.write_to_file(fname=ratio_fout_name, name_mod = "modn:")
					print('[i] ratio to {} written to {}'.format(vidx, ratio_fout_name))
				except:
					print('[e] failed: ratio to index {} writing to {}'.format(vidx, ratio_fout_name))

			if 'index=' in sscale:
				idx = sscale.split('index=')[1].split(' ')[0]
				vidx = get_value(idx, int, -1)
				print('[i] to scale to', vidx)
				newhl = self.hl.ratio_to(vidx)
				if 'limit_error' in sscale:
					yemax = None
					if 'limit_error_max' in sscale:
						yemaxs = sscale.split('limit_error_max=')[1].split(' ')[0]
						yemax = get_value(yemaxs, float, 0.0)
					yemin = None
					if 'limit_error_min' in sscale:
						yemins = sscale.split('limit_error_min=')[1].split(' ')[0]
						yemin = get_value(yemins, float, 0.0)
					grhl_tmp = dlist.dlist('tmp')
					for o in newhl:
						if o.obj.InheritsFrom('TH1'):
							_gr = r.TGraphAsymmErrors(o.obj)
							for _i in range(_gr.GetN()):
								if yemax is not None:
									_eymax = _gr.GetY()[_i] + _gr.GetEYhigh()[_i]
									if _eymax > yemax:
										_gr.SetPointEYhigh(_i, yemax - _gr.GetY()[_i])
								if yemin is not None:
									_eymin = _gr.GetY()[_i] - _gr.GetEYlow()[_i]
									if _eymin < yemin:
										_gr.SetPointEYlow(_i, _gr.GetY()[_i] - yemin)
						grhl_tmp.add(_gr, o.obj.GetTitle() + '_gr', 'p')
					if len(grhl_tmp.l) > 0:
						newhl.add_list(grhl_tmp)
				try:
					ratio_fout_name = sscale.split('fout=')[1].split(' ')[0]
					newhl.write_to_file(fname=ratio_fout_name, name_mod = "modn:")
					print('[i] ratio to {} written to {}'.format(vidx, ratio_fout_name))
				except:
					print('[e] failed: ratio to index {} writing to {}'.format(vidx, ratio_fout_name))


		scalebwidth = self.get_tag('#scalebwidth', None)
		if scalebwidth:
			if len(scalebwidth.split(' ')) > 1:
				modifYtitle = False
				if scalebwidth.split(' ')[1] == 'True':
					modifYtitle = True
				self.hl.scale_by_binwidth(modifYtitle=modifYtitle)
			else:
				self.hl.scale_by_binwidth(modifYtitle=True)

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
			if miny is not None:
				if miny <= 0:
					print('[w] overriding logy miny<=0',miny)
					logy=False
			if maxy is not None:
				if maxy <= 0:
					print('[w] overriding logy maxy<=0',maxy)
					logy=False

		self.hl.set_log_multipad('xyz', False)

		# axis shapes and sizes etc..
		atos = self.get_tags('#ato')
		for s in atos:
			for i, ax in enumerate(s.split(',')):
				print(i, ax)
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_title_offset[i] = v
		atss = self.get_tags('#ats')
		for s in atss:
			for i, ax in enumerate(s.split(',')):
				print(i, ax)
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_title_size[i] = v
		alos = self.get_tags('#alo')
		for s in alos:
			for i, ax in enumerate(s.split(',')):
				print(i, ax)
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_label_offset[i] = v
		alss = self.get_tags('#als')
		for s in alss:
			for i, ax in enumerate(s.split(',')):
				print(i, ax)
				v = get_value(ax, float, None)
				if v:
					if v > 0:
						self.hl.axis_label_size[i] = v

		self.hl.draw(miny=miny,maxy=maxy,logy=logy)

		minz = self.get_tag('#minz', None)
		if minz:
			minz = get_value(minz, float, None)
		maxz = self.get_tag('#maxz', None)
		if maxz:
			maxz = get_value(maxz, float, None)
		if minz or maxz:
			self.hl.set_min_max_z(minz, maxz)
		self.hl.update()

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
		if grids is not None:
			self.hl.set_grid_multipad(grids)

		sfigtitle = self.get_tag('#title', '')
		if len(sfigtitle) > 0:
			self.add_option('#comment -0.1,0.9,1.0,1.0, tx_size=0.06 align=22 item={}'.format(sfigtitle))

		#legend
		sleg = self.get_tag('#legend')
		if sleg:
			x1 = None
			x2 = None
			y1 = None
			y2 = None

			tx_size = 0.035 #0.025
			try:
				tx_size = get_value(sleg.split('tx_size=')[1].split(' ')[0], float, 0.035)
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
				ncol = int(sleg.split('ncol=')[1].split(' ')[0])
			except:
				ncol = 1
			fcol = 0
			try:
				fcol = int(sleg.split('fcol=')[1].split(' ')[0])
			except:
				fcol = 0
			if fcol > 0:
				# leg.SetFillColor(fcol)
				leg_opt = leg_opt + ' +k{}'.format(fcol)
			try:
				pos = sleg.split('pos=')[1].split(' ')[0]
			except:
				pos = None
			if pos:
				if pos == 'max':
					x1,y1,x2,y2 = 0.2,0.25,0.92,0.87
				if pos == 'down':
					x1,y1,x2,y2 = 0.2,0.25,0.92,0.44
				if pos == 'up':
					x1,y1,x2,y2 = 0.2,0.67,0.92,0.87
				if pos == 'lr':
					x1,y1,x2,y2 = 0.52,0.25,0.92,0.44
				if pos == 'ur':
					x1,y1,x2,y2 = 0.52,0.67,0.92,0.87
				if pos == 'll':
					x1,y1,x2,y2 = 0.2,0.25,0.52,0.44
				if pos == 'ul':
					x1,y1,x2,y2 = 0.2,0.67,0.52,0.87
			else:
				x1,y1,x2,y2 = self.legend_position(sleg)
			self.leg = self.hl.self_legend(ncols=ncol,title=stitle,x1=x1,x2=x2,y1=y1,y2=y2,tx_size=tx_size,option=leg_opt)

		#line
		self.draw_lines()
		#size of the window
		x = 400
		y = 300
		gs = self.get_tag('#geom')
		if gs is not None:
			try:
				x = get_value(gs.split('x')[0], int, 0)
				y = get_value(gs.split('x')[1], int, 0)
			except:
				print('[e] unable to understand the --geom argument',gs)
		if no_canvas == False:
			self.hl.resize_window(x,y)

		ds = self.get_tag('#date')
		if ds is not None and self.show_date is True:
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

		cs = self.get_tags('#pavetext')
		for c in cs:
			if c == None:
				continue
			if len(c) > 0:
				tc = PaveText(c)
				tpt = tc.tptext()
				tpt.Draw()
				self.comments.append(tc)
				#tu.gList.append(leg)

		sname = self.get_tag('#name', None)
		if sname is not None:
			#self.hl.tcanvas.SetName(sname)
			self.hl.tcanvas.SetTitle(sname)
			self.hl.name = tu.unique_name(ut.to_file_name(sname))

		self.hl.update()

		# note: for making funky stuff you probably need root6...
		groots = self.get_tags('#r')
		for c in groots:
			print('[i] trying root to process line', c)
			# result = r.gROOT.ProcessLine(c)
			# print '  ->', result
			r.gInterpreter.ProcessLine(c)

		# this is also no good...
		groots = self.get_tags('#rpy')
		for c in groots:
			print('[i] trying root to process line', c)
			with open('./tmp.py', 'w') as f:
				print('import tutils', file=f)
				print('import ROOT as r', file=f)
				print(c, file=f)
			sys.path.append(os.getcwd())
			import tmp

		# this is overwritten by hl but a good idea
		gpads = self.get_tags('#gpad')
		for s in gpads:
			print(s)
			if 'lm ' in s:
				v = get_value(s.split(' ')[-1], float, None)
				if v:
					r.gPad.SetLeftMargin(v)
					print('gpad set left margin to', v)
			if 'rm ' in s:
				v = get_value(s.split(' ')[-1], float, None)
				if v:
					r.gPad.SetRightMargin(v)
					print('gpad set right margin to', v)

	def pdf(self):
		if self.drawable == True:
			self.hl.pdf()

	def pdf_to_file(self, fname):
		if self.drawable == True:
			self.hl.pdf_to_file(fname)

	def png(self):
		if self.drawable == True:
			self.hl.png()

	def add_option(self, opt):
		self.options.append(opt)
		self.data.append(opt)

class MetaDrawFile(object):
	def __init__(self, fname=None, wname=None, args=None):
		self.data_raw = ut.load_file_to_strings(fname)
		print('[i] got data:', self.data_raw)
		self.data = []
		if args.replace:
			for s in self.data_raw:
				sr = s
				for srepl in args.replace:
					splits = srepl.split(':')
					sfrom = splits[0]
					sto = ''
					if len(splits)>1:
						sto = splits[1]
						if len(sfrom) > 0:
							if '<{}>'.format(sfrom) in sr:
								sr = sr.replace('<{}>'.format(sfrom), sto)
							else:
								sr = sr.replace(' {} '.format(sfrom), ' {} '.format(sto))
						else:
							sr = sr
				self.data.append(sr)
		else:
			self.data = self.data_raw
		print('[i] drawing data:', self.data)
		self.figures = []
		fig = MetaFigure(fname, wname)
		self.figures.append(fig)
		for d in self.data:
			if d[:len('#figure')] == '#figure':
				if len(self.figures[-1].data) > 1:
					fig = MetaFigure(fname, wname)
					self.figures.append(fig)
				# continue
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
	# tu.setup_basic_root()
	parser = argparse.ArgumentParser(description='draw a .draw file', prog=os.path.basename(__file__))
	parser.add_argument('fname', help='what file to draw', type=str, default="", nargs="?")
	args = parser.parse_args()
	print('[i] arguments:', args)
	fname = args.fname
	fn, fext = os.path.splitext(fname)
	metafname = None
	if fext == '.root':
		import make_draw_files as makedf
		#metafname = makedf.make_draw_file(fname)
		metafname = makedf.make_draw_file_smart_group(fname)
	else:
		metafname = fname
	print('[i] got to draw:', metafname)
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
		print(fname)
		#metafname = makedf.make_draw_file(fname, mdf.options, force=True)
		metafname = makedf.make_draw_file_smart_group(fname, mdf.options, force=True)
		mdf   = MetaDrawFile(metafname)
	mdf.draw()
	if '--print' in sys.argv:
		mdf.pdf()
	if not ut.is_arg_set('-b'):
		r.gApplication.Run()
