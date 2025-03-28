import os
import sys
import tutils as tu
import ROOT
import draw_utils as du
from array import array
gDebug = False
#needs a fix: the import below depends on where the module is...
from dbgu import debug_utils as dbgu
import pcanvas
import pyutils
from eval_string import get_value

def check_andor_make_output_dir(sname, isfilename=False):
	sdir = sname
	if isfilename:
		sdir = os.path.dirname(sname)
	if len(sdir) == 0:
		sdir = './'
	if os.path.isdir(sdir) is False:
		try:
			os.makedirs(sdir)
		except:
			return False
	return os.path.isdir(sdir)


class debugable(object):
	def __init__(self):
		pass

	def debug(self, msg):
		global gDebug
		if gDebug is True:
			print('[d]', msg)


class style_iterator(debugable):
	good_colors  = [-1, 2, 1, 9, 6, 32, 49, 40, 8, 43, 46, 39, 28, 38, 21, 22, 23,
					2, 1, 9, 6, 32, 49, 40, 8, 43, 46, 39, 28, 38, 21, 22, 23]
	good_markers = [-1, 20, 24, 21, 25, 33, 27, 28, 34, 29, 30, 20, 24, 21, 25, 27, 33, 28, 34, 29, 30,
					20, 24, 21, 25, 33, 27, 28, 34, 29, 30, 20, 24, 21, 25, 27, 33, 28, 34, 29, 30]
	# good_lines   = [ -1, 1, 2, 3, 5, 8, 6, 7, 4, 9, 10]
	good_lines   = [-1, 1, 2, 3, 5, 7, 9, 6, 8, 4, 10, 1, 2, 3, 5, 7, 9, 6, 8, 4, 10,
					1, 2, 3, 5, 7, 9, 6, 8, 4, 10, 1, 2, 3, 5, 7, 9, 6, 8, 4, 10]

	def __init__(self, reset_idx=0):
		self.reset_index = reset_idx
		self.reset()

	def reset_to_index(self, idx):
		self.reset_index = idx

	def reset(self):
		self.color_idx  = self.reset_index
		self.line_idx   = self.reset_index
		self.marker_idx = self.reset_index
		self.line_width = 2

	def colorize(self, force_color=None):
		self.color_idx = 0
		for o in self.l:
			icol = force_color
			if icol is None:
				icol = self.next_color()
			o.SetLineColor(icol)

	def lineize(self, force_line=None):
		self.line_idx = 0
		for o in self.l:
			imark = force_line
			if imark is None:
				imark = self.next_line()
			o.SetLineStyle(imark)
			o.SetLineColor(1)
			o.SetLineWidth(self.line_width)
			self.debug('::lineize set line style {} for {}'.format(imark, o.GetName()))

	def markerize(self, force_marker=None):
		self.marker_idx = 0
		scale = 1.
		for o in self.l:
			imark = self.next_marker()
			o.SetMarkerStyle(imark)
			if imark >= 27:
				scale = 1.3
			o.SetMarkerSize(self.marker_size * scale)
			o.SetMarkerColor(o.GetLineColor())

	def next_color(self):
		self.color_idx = self.color_idx + 1
		if self.color_idx >= len(self.good_colors):
			self.color_idx = 0
		return self.good_colors[self.color_idx]

	def next_marker(self):
		self.marker_idx = self.marker_idx + 1
		if self.marker_idx >= len(self.good_markers):
			self.marker_idx = 0
		return self.good_markers[self.marker_idx]

	def next_line(self):
		self.line_idx = self.line_idx + 1
		if self.line_idx >= len(self.good_lines):
			self.line_idx = 0
		return self.good_lines[self.line_idx]

	def __next__(self):
		self.next_color()
		self.next_marker()
		self.next_line()


class draw_option(debugable):

	def __init__(self, stro=''):
		self.s = stro.lower()
		self.strip = self.s
		self.debug('::draw_option with {}'.format(self.s))
		self.lstyle      = self.get_style_from_opt('l')
		self.pstyle      = self.get_style_from_opt('p')
		self.fstyle      = self.get_style_from_opt('f')
		self.kolor       = self.get_style_from_opt('k')
		self.alpha       = self.get_style_from_opt('a')  # alpha for fill
		self.lwidth      = self.get_style_from_opt('w')
		self.shift       = self.get_number_from_opt('s')
		if self.lwidth == 0:
			self.lwidth = 2
		self.psize       = self.get_style_from_opt('m')
		if self.psize == 0:
			self.psize = 0.9
		else:
			self.psize = self.psize / 100.
		self.use_line        = self.check_use_line()
		self.use_line_legend = self.check_use_line_legend()
		self.bw              = self.check_black_white()
		self.use_marker      = self.check_use_marker()
		self.is_error        = self.has(['serror'], strip=True)
		self.no_legend       = self.has(['noleg'], strip=True)
		self.hidden          = self.has(['hidden'], strip=True)
		self.rectangle       = self.has(['rect'], strip=True)
		self.overlay         = self.has(['over'], strip=True) #ignore 2D canvas splits
		self.last_kolor      = self.has(['-k'])
		self.last_line       = self.has(['-l'])
		self.smooth          = self.has(['smooth'], strip=True)
		self.is_time_x       = self.has(['timex'], strip=True)
		self.is_time_y       = self.has(['timey'], strip=True)
		self.drop_threshold  = None
		if self.has(['+thr']):
			self.drop_threshold = self.get_number_from_opt('+thr')
		print('dtop thr=', self.drop_threshold)

	def stripped(self):
		return self.strip

	def check_black_white(self):
		return self.has(['bw'])

	def check_use_line(self):
		marks = ['hist', 'l', 'c']
		return self.has(marks)

	def check_use_line_legend(self):
		marks = ['-']
		return not self.has(marks)

	def check_use_marker(self):
		marks = ['p']
		return self.has(marks)

	def legend_option(self):
		ret = ''
		if self.no_legend:
			return ret
		if self.use_marker:
			ret = ret + ' p '
		if self.use_line or self.use_line_legend:
			ret = ret + ' l '
		if self.is_error:
			ret = ret + ' f '
		if self.fstyle != 0:
			ret = ret + ' f '
		return ret

	def has(self, lst, strip=False):
		ret = False
		for e in lst:
			# for s in self.s.split(' '):
			for s in self.strip.split(' '):
				if e == s[:len(e)]:
					ret = True
					if strip is True:
						self.strip = self.strip.replace(e, '')
		return ret

	def get_style_from_opt(self, what):  # what can be l or p or f
		ts = self.s.split('+')
		# self.debug('::get_style_from_opt ' + str(ts))
		val = 0
		for t in ts:
			tt = t.split(' ')[0]
			if len(tt) <= 0:
				continue
			if what in tt[0]:
				try:
					nt  = tt[1:]
					val = int(nt)
				except:
					pass
		self.debug('::get_style_from_opt on {} returning {}'.format(what, val))
		self.strip = self.strip.replace('+{}{}'.format(what, str(val)), '')
		return val

	def get_number_from_opt(self, what):
		ts = self.s.split('+' + what)
		if len(ts) < 2:
			return 0.0
		snum = ts[1].split(' ')
		fnum = 0.0
		try:
			fnum = get_value(snum[0], float, 0.0)
		except:
			fnum = 0.0
		self.strip = self.strip.replace('+{}{}'.format(what, str(snum[0])), '')
		return fnum


def random_string(prefix='', ns=30):
	import random
	import string
	lst = [random.choice(string.ascii_letters + string.digits) for n in range(ns)]
	return str(prefix) + ''.join(lst)


class draw_object(debugable):
	def __init__(self, robj, name=None, new_title=None, dopts=''):
		self.name = name
		if self.name is None:
			self.name = '{}_{}'.format(robj.GetName(), random_string())
		self.obj  = robj.Clone(self.name)
		if self.obj.InheritsFrom('TH1'):
			self.obj.SetDirectory(0)
		if new_title:
			self.user_title = new_title
			if self.obj.InheritsFrom('TF1'):
				pass
			else:
				self.obj.SetTitle(new_title)
		if self.obj.GetTitle() == '':
			if self.obj.InheritsFrom('TF1'):
				pass
			else:
				self.obj.SetTitle(self.name)
			self.user_title = self.name
		self.dopt = draw_option(dopts)
		self.is_first = False
		self.exec = []

	def draw(self, extra_opt=''):
		sdopt = self.dopt.stripped() + ' ' + extra_opt
		if 'draw!' in extra_opt.lower():
			sdopt = extra_opt
		if self.is_first is True:
			if self.obj.InheritsFrom('TGraph'):
				sdopt = sdopt + ' A'
			self.debug('doption=' + sdopt)
			if self.dopt.is_time_x:
				self.obj.GetXaxis().SetTimeDisplay(1)
			if self.dopt.is_time_y:
				self.obj.GetYaxis().SetTimeDisplay(1)
			self.obj.Draw(sdopt)
		else:
			self.obj.Draw(sdopt + ' same')


class dlist(debugable):
	enable_eps = False

	def __init__(self, name='hl'):
		self.name              = name
		self.title             = name
		self.l                 = []
		self.style             = style_iterator()
		self.maxy              = 1e6  # was 1
		self.miny              = -1e6  # was 0
		self.maxz              = None  # was 1
		self.minz              = None  # was 0
		self.max_adjusted      = False
		self.axis_title_offset = [5, 5, 5]  # [1.4, 1.4, 1.4]
		self.axis_title_size   = [12, 12, 12]  # [0.05, 0.05, 0.05]
		self.axis_label_size   = [12, 12, 12]  # for font 42 [0.04, 0.04, 0.04]
		self.axis_label_offset = [0.02, 0.02, 0.02]
		self.font              = 42
		self.pattern           = None
		self.tcanvas           = None
		self.minx              = None
		self.maxx              = None
		self.pad_name          = None  # pad where last drawn
		self.pad               = None  # pad where last drawn
		self.set_font(42)
		self.force_legend      = False # by default no legends on 2D plots

	def set_font(self, fn=42, scale=1.):
		self.font = fn
		if self.font == 42:
			self.axis_title_offset = [1.40, 1.45, 1.0] # y offset was 1.40 then 1.45
			self.axis_title_size   = [0.05 * scale, 0.05 * scale, 0.05 * scale]
			self.axis_label_size   = [0.04 * scale, 0.04 * scale, 0.04 * scale]
			self.axis_label_offset = [0.02, 0.02, 0.02]
		if self.font == 43:
			self.axis_title_offset = [ 3,     3,     2] #[1.4, 1.4, 1.4]
			self.axis_label_offset = [ 0.01,  0.01,  0.01]
			self.axis_title_size   = [12 * scale, 12 * scale, 12 * scale] #[0.05, 0.05, 0.05]
			self.axis_label_size   = [12 * scale, 12 * scale, 12 * scale] # for font 42 [0.04, 0.04, 0.04]

	def __getitem__(self, i):
		return self.l[i]

	def __len__(self):
		return len(self.l)

	def __str__(self):
		ret = []
		ret.append('[i] dlist named: {} titled: {}'.format(self.name, self.title))
		for i,item in enumerate(self.l):
			o = item.obj
			ret.append('    {} {} {} {}'.format(i, o.IsA().GetName(), o.GetName(), o.GetTitle()))
		return '\n'.join(ret)

	def copy_list(self, l=[]):
		for h in l:
			self.add(h)

	def copy(self, l):
		for h in l.l:
			self.add(h.obj, h.obj.GetTitle(), h.dopt.s)

	def last(self):
		if len(self.l) > 0:
			return self.l[-1]
		return None

	def last_index(self):
		return len(self.l)-1

	def is_selected(self, o):
		if self.pattern != None:
			if not self.pattern in o.name:
				return False
		return True

	def _check_name(self, name):
		for o in self.l:
			if o.name == name:
				return True
		return False

	def get_by_name(self, name):
		for l in self.l:
			if l.name == name:
				return l
		return None

	def find_miny(self, low=None, logy=False):
		miny = 1e18
		for h in self.l:
			if h.obj.InheritsFrom('TH1'):
				for nb in range(1, h.obj.GetNbinsX()):
					c = h.obj.GetBinContent(nb)
					if logy == False:
						if c!=0 and c <= miny:
							miny = c
					else:
						if c > 0 and c <= miny:
							miny = c
			if h.obj.InheritsFrom('TGraph'):
				for idx in range(h.obj.GetN()):
					v = h.obj.GetY()[idx]
					if logy == False:
						if v < miny:
							miny = v
					else:
						if v > 0 and v < miny:
							miny = v
		if low!=None:
			if miny < low:
				miny == low
		return miny

	def find_maxy(self, logy=False):
		maxy = -1e18
		for h in self.l:
			if h.obj.InheritsFrom('TH1'):
				for nb in range(1, h.obj.GetNbinsX()):
					c = h.obj.GetBinContent(nb)
					if logy == False:
						if c!=0 and c > maxy:
							maxy = c
					else:
						if c > 0 and c > maxy:
							maxy = c
			if h.obj.InheritsFrom('TGraph'):
				vy = h.obj.GetY()
				for idx in range(h.obj.GetN()):
					v = vy[idx]
					if logy == False:
						if v > maxy:
							maxy = v
					else:
						if v > 0 and v > maxy:
							maxy = v
		return maxy

	def set_min_max_z(self, minz=None, maxz=None):
		for h in self.l:
			if h.obj.InheritsFrom('TH2') or h.obj.InheritsFrom('TF2'):
				if maxz:
					h.obj.SetMaximum(maxz)
					self.maxz = maxz
				if minz:
					h.obj.SetMinimum(minz)
					self.minz = minz
			else:
				self.debug('::adjust_maxima z : object not TH2 - no minz or maxz {} {}'.format(h.obj.GetName(), h.obj.GetTitle()))
		self.max_adjusted = True
		self.debug('::adjust_maxima z-min: {} z-max {}'.format(self.minz, self.maxz))

	def adjust_maxima(self, miny=None, maxy=None, logy=False):
		if miny!=None:
			self.miny=miny
		else:
			self.miny = self.find_miny(logy=logy)
			if self.miny < 0:
				self.miny = self.miny * 1.1
			else:
				self.miny = self.miny * 0.9
			if logy==True:
				self.miny=self.find_miny(logy=logy) * 0.5
			# self.miny, miny, maxy, logy
			if logy==True and self.miny <= 0:
				miny=self.find_miny(logy=logy)
				self.miny = miny

		if maxy!=None:
			self.maxy=maxy
		else:
			self.maxy=self.find_maxy() * 1.1
			if logy==True:
				self.maxy=self.find_maxy() * 2.

		for h in self.l:
			if self.miny!=None:
				h.obj.SetMinimum(self.miny)
			if self.maxy!=None:
				h.obj.SetMaximum(self.maxy)

		self.max_adjusted = True
		self.debug('::adjust_maxima min: {} max {}'.format(self.miny, self.maxy))

	def append(self, obj=ROOT.TObject, new_title = '', draw_opt = '', prep=False):
		newname_root = obj.GetName() + '_' + self.name.replace(' ', '_')
		newname = newname_root
		if ' name=' in new_title:
			splits = new_title.split(' name=')
			new_title = splits[0]
			newname   = splits[1]
		newname = pyutils.to_file_name(newname)
		count = 1
		while self._check_name(newname) == True:
			newname = newname_root + '_' + str(count)
			count = count + 1
		if new_title == '':
			new_title = obj.GetTitle()
		if new_title[0] == '+':
			new_title = obj.GetTitle() + new_title[1:]
		o = draw_object(obj, newname, new_title, draw_opt)
		if prep == True:
			for oi in self.l:
				oi.is_first = False
		if len(self.l) == 0 or prep == True:
			o.is_first = True
		if prep == True:
			self.l.insert(0, o)
		else:
			self.l.append(o)
		self.debug('::append ' + o.name + ' ' + o.dopt.s + 'prepend:' + str(prep) )
		return o

	def add_from_file(self, hname = '', fname = '', new_title = '', draw_opt = ''):
		fn, fext = os.path.splitext(hname)
		if fext == '.root':
			if os.path.isfile(hname) and not os.path.isfile(fname):
				print('[w] correcting possible swap between hname({}) and fname({}) args...'.format(hname, fname))
				stmp = hname
				hname = fname
				fname = stmp
		cobj = None
		if not os.path.isfile(fname):
			print('[w] file {} does not exist'.format(fname))
			return None
		try:
			f = ROOT.TFile(fname)
		except:
			print('[w] could not open file {}'.format(fname))
			return None
		if f:
			h = f.Get(hname)
			if h:
				cobj = self.add(h, new_title, draw_opt)
				f.Close()
			else:
				f.Close()
				try:
					cobj = self.add_from_hashlist(hname, fname, new_title, draw_opt)
				except:
					pass
				if cobj:
					pass
				else:
					try:
						cobj = self.add_from_tfiledirectory(hname, fname, new_title, draw_opt)
					except:
						pass
		return cobj

	def add_from_hashlist(self, hname = '', fname = '', new_title = '', draw_opt = ''):
		cobj = None
		f = ROOT.TFile(fname)
		if f:
			splits = hname.split('/')
			#print splits[0], splits[1]
			hlist = f.Get(splits[0])
			h = hlist.FindObject(splits[1])
			if h:
				cobj = self.add(h, new_title, draw_opt)
			f.Close()
		return cobj

	def add_from_tfiledirectory(self, hname = '', fname = '', new_title = '', draw_opt = ''):
		cobj = None
		f = ROOT.TFile(fname)
		if f:
			splits = hname.split('/')
			#print splits[0], splits[1]
			hlist = f.Get(splits[0])
			h = hlist.Get(splits[1])
			print('[i] getting h',h,'from',splits[0],splits[1])
			if h:
				cobj = self.add(h, new_title, draw_opt)
			f.Close()
		return cobj

	def add(self, obj=ROOT.TObject, new_title = '', draw_opt = '', prep=False):
		if obj == None: return None
		cobj = None
		try:
			robj = obj.obj
		except:
			robj = obj
		if 'smooth' in draw_opt:
			if robj.InheritsFrom('TH1') or robj.InheritsFrom('TF2'):
				_robj = robj.Clone('{}_smoothed'.format(robj.GetName()))
				_robj.Smooth()
				robj = _robj
		if robj.InheritsFrom('TH2') or robj.InheritsFrom('TF2'):
			xprof_new_title = new_title
			xprof_dopt="p e1 +k6 +m70 +p20"
			if '+xprof' in draw_opt or '+xprof' in new_title:
				if '+xprof[' in draw_opt:
					xprof_dopt = draw_opt.split('+xprof[')[1].split(']')[0] + ' over'
					draw_opt = draw_opt.replace('+xprof[{}]'.format(xprof_dopt), '')
				if '+xprof[' in new_title:
					xprof_new_title = new_title.split('+xprof[')[1].split(']')[0]
					new_title = new_title.replace('+xprof[{}]'.format(xprof_new_title), '')
			yprof_drop_zero_entries = False
			yprof_new_title = new_title
			yprof_dopt="p e1 +k6 +m70 +p25"
			if '+yprof' in draw_opt or '+yprof' in new_title:
				if '+yprof[' in draw_opt:
					yprof_dopt = draw_opt.split('+yprof[')[1].split(']')[0] + ' over'
					draw_opt = draw_opt.replace('+yprof[{}]'.format(yprof_dopt), '')
					yprof_drop_zero_entries = ('-0' in yprof_dopt)
					if yprof_drop_zero_entries:
						yprof_dopt = yprof_dopt.replace('-0', '')
				if '+yprof[' in new_title:
					yprof_new_title = new_title.split('+yprof[')[1].split(']')[0]
					new_title = new_title.replace('+yprof[{}]'.format(yprof_new_title), '')
			cobj = self.append(robj, new_title, draw_opt)
			if '+xprof' in draw_opt:
				hprofx = robj.ProfileX()
				cobj_px = self.append(hprofx, xprof_new_title, xprof_dopt)
			if '+yprof' in draw_opt:
				_hprofy = robj.ProfileY()
				hprofy = h_to_graph(_hprofy, drop_zero_entries=yprof_drop_zero_entries, xerror=True, transpose=True)
				cobj_py = self.append(hprofy, yprof_new_title, yprof_dopt)
			return cobj
		if robj.InheritsFrom("TH1") \
			or robj.InheritsFrom("TGraph") \
			or robj.InheritsFrom("TF1"):
			#h = ROOT.TH1(obj)
			if draw_opt == '':
				draw_opt = 'hist'
				if robj.InheritsFrom("TF1"):
					draw_opt = 'l'
			if 'ex0' in draw_opt.split(' '):
				draw_opt = draw_opt.replace('ex0', '')
				xerror = False
			else:
				xerror = True
			if robj.InheritsFrom('TH1') and 'graph' in draw_opt.split(' '):
				y_min = True
				y_min_test = draw_opt.split('ymin')
				if len(y_min_test) > 1:
					y_min_test = y_min_test[1].split(' ')[0]
					y_min = get_value(y_min_test, float, 0.0)
				robj = h_to_graph(robj, drop_zero_entries=y_min, xerror=xerror)
				if 'no_y_error' in draw_opt.split(' '):
					scale_graph_errors(robj, 1, 0.0)
					draw_opt = draw_opt.replace('no_y_error',' ')
				if 'no_x_error' in draw_opt.split(' '):
					scale_graph_errors(robj, 0, 0.0)
					draw_opt = draw_opt.replace('no_x_error',' ')
				draw_opt = draw_opt.replace('graph',' ')
			else:
				if xerror == False:
					if robj.InheritsFrom('TGraph'):
						scale_graph_errors(robj, 0, 0.0)
			cobj = self.append(robj, new_title, draw_opt, prep)
			if self.maxy < robj.GetMaximum():
				self.maxy = robj.GetMaximum()
			if self.miny < robj.GetMinimum():
				self.miny = robj.GetMinimum()
		return cobj

	def add_list(self, hl):
		for l in hl.l:
			self.add(l.obj, l.obj.GetTitle(), l.dopt.s)

	def reset_axis_titles(self, xt=None, yt=None, zt=None):
		for o in self.l:
			if xt:
				o.obj.GetXaxis().SetTitle(xt)
			if yt:
				o.obj.GetYaxis().SetTitle(yt)
			if zt:
				if o.obj.InheritsFrom('TH1'):
					o.obj.GetZaxis().SetTitle(zt)

	def fix_x_range(self, xmin, xmax):
		try:
			sxmin = '{0:.10f}'.format(xmin)
			xminf = get_value(sxmin, float, -1.0)
		except:
			xminf = -1.
		try:
			sxmax = '{0:.10f}'.format(xmax)
			xmaxf = get_value(sxmax, float, 1.0)
		except:
			xmaxf = 1.
		reset = False
		for dobj in self.l:
			if 'zoom_axis_obj' in dobj.name:
				gr = dobj.obj
				gr.SetPoint(0, xminf,  0)
				gr.SetPoint(1, xmaxf,  0)
				if len(self.l) > 0:
					gr.GetXaxis().SetTitle(self.l[0].obj.GetYaxis().GetTitle())
					gr.GetYaxis().SetTitle(self.l[0].obj.GetXaxis().GetTitle())
				reset = True
		if reset == False:
			gr = ROOT.TGraph(2)
			gr.SetPoint(0, xminf,  0)
			gr.SetPoint(1, xmaxf,  0)
			if len(self.l) > 0:
				gr.GetXaxis().SetTitle(self.l[0].obj.GetXaxis().GetTitle())
				gr.GetYaxis().SetTitle(self.l[0].obj.GetYaxis().GetTitle())
			o = draw_object(gr, 'zoom_axis_obj', 'fake', 'noleg hidden p')
			self.l.insert(0, o)
			for oi in self.l:
				oi.is_first = False
			self.l[0].is_first = True

	def find_xlimits(self):
		xmin = 0
		xmax = 0
		for o in self.l:
			h = o.obj
			if not h.InheritsFrom('TH1'):
				if xmin > h.GetXaxis().GetXmin():
					xmin = h.GetXaxis().GetXmin()
				if xmax > h.GetXaxis().GetXmax():
					xmax = h.GetXaxis().GetXmax()
				continue
			for ix in range(1, h.GetNbinsX()+1):
				if h.GetBinContent(ix) != 0:
					if xmin > h.GetBinLowEdge(ix):
						xmin = h.GetBinLowEdge(ix)
					if xmax < h.GetBinCenter(ix) + h.GetBinWidth(ix):
						xmax = h.GetBinCenter(ix) + h.GetBinWidth(ix)
		return [xmin - xmin*0.1, xmax + xmax*0.1]

	def zoom_axis(self, which, xmin, xmax):
		try:
			sxmin = '{0:.10f}'.format(xmin)
			xminf = get_value(sxmin, float, 0.0)
		except:
			xminf = -1.
		try:
			sxmax = '{0:.10f}'.format(xmax)
			xmaxf = get_value(sxmax, float, 0.0)
		except:
			xmaxf = 1.
		ax = None
		for o in self.l:
			if which == 0:
				ax = o.obj.GetXaxis()
				#if xmax == None:
				#    xlims = self.find_xlimits()
				#    if xlims[0] != None:
				#        self.zoom_axis(which, xlims[0], xlims[1])
			if which == 1:
				ax = o.obj.GetYaxis()
			if which == 2:
				if o.obj.InheritsFrom('TH1'):
					ax = o.obj.GetZaxis()
			if ax:
				#print xmin,xmax
				ibmin = ax.FindBin(xminf)
				ibmax = ax.FindBin(xmaxf)
				#try:
				#    #print 'ibmin, ibmax, nbins:',ibmin, ibmax, o.obj.GetNbinsX()
				#    if ibmax > o.obj.GetNbinsX():
				#        ibmax = o.obj.GetNbinsX()
				#        #print 'reset axis max to:',ibmax
				#except:
				#    #print ibmin, ibmax
				#    pass
				##print xmin, xmax
				ax.SetRange(ibmin, ibmax)

	def scale_errors(self, val = 1.):
		for o in self.l:
			if o.obj.InheritsFrom('TH1') == False:
				continue
			for i in range(1, o.obj.GetNbinsX() + 1):
				err = o.obj.GetBinError(i)
				o.obj.SetBinError(i, err * val)

	def scale(self, val = 1.):
		for o in self.l:
			if o.obj.InheritsFrom('TH1') == False:
				continue
			if o.obj.GetSumw2() == None:
				o.obj.Sumw2()
			o.obj.Scale(val)
			#for i in range(1, o.GetNbinsX()):
			#    err = o.GetBinError(i)
			#    o.SetBinError(i, err * val)
			#    v = o.GetBinContent(i)
			#    o.SetBinContent(i, v * val)

	def scale_any(self, val = 1.):
		for o in self.l:
			if o.obj.InheritsFrom('TH1') == True:
				o.obj.Sumw2()
				o.obj.Scale(val)
			if o.obj.InheritsFrom('TGraph') == True:
				for i in range(o.obj.GetN()):
					o.obj.SetPoint(i, o.obj.GetX()[i], o.obj.GetY()[i] * val)
			if o.obj.InheritsFrom('TGraphErrors') == True:
				for i in range(o.obj.GetN()):
					o.obj.SetPointError(i, o.obj.GetEX()[i], o.obj.GetEY()[i] * val)
			if o.obj.InheritsFrom('TGraphAsymmErrors') == True:
				for i in range(o.obj.GetN()):
					o.obj.SetPointError(i, o.obj.GetEXlow()[i], o.obj.GetEXhigh()[i], o.obj.GetEYlow()[i] * val, o.obj.GetEYhigh()[i] * val)

	def scale_1ox_at_index(self, i=-1):
		if len(self.l) < 1:
			return
		o = self.l[i]
		if o.obj.InheritsFrom('TH1') == True:
			o.obj.Sumw2()
			#o.obj.Scale(val)
			print('[e] ::scale_1ox_at_index NOT implemented for histograms!')
		if o.obj.InheritsFrom('TGraph') == True:
			for i in range(o.obj.GetN()):
				if o.obj.GetX()[i] != 0:
					o.obj.SetPoint(i, o.obj.GetX()[i], o.obj.GetY()[i] / o.obj.GetX()[i])
		if o.obj.InheritsFrom('TGraphErrors') == True:
			for i in range(o.obj.GetN()):
				if o.obj.GetX()[i] != 0:
					o.obj.SetPointError(i, o.obj.GetEX()[i], o.obj.GetEY()[i] / o.obj.GetX()[i])
		if o.obj.InheritsFrom('TGraphAsymmErrors') == True:
			for i in range(o.obj.GetN()):
				if o.obj.GetX()[i] != 0:
					o.obj.SetPointError(i, o.obj.GetEXlow()[i], o.obj.GetEXhigh()[i], o.obj.GetEYlow()[i] / o.obj.GetX()[i], o.obj.GetEYhigh()[i] / o.obj.GetX()[i])

	def scale_1ox_at_index_any(self):
		for i in range(len(self.l)):
			self.scale_1ox_at_index(i)

	def scale_1x_at_index(self, i=-1):
		if len(self.l) < 1:
			return
		o = self.l[i]
		if o.obj.InheritsFrom('TH1') == True:
			o.obj.Sumw2()
			#o.obj.Scale(val)
			print('[e] ::scale_1x_at_index NOT implemented for histograms!')
		if o.obj.InheritsFrom('TGraph') == True:
			for i in range(o.obj.GetN()):
				o.obj.SetPoint(i, o.obj.GetX()[i], o.obj.GetY()[i] * o.obj.GetX()[i])
		if o.obj.InheritsFrom('TGraphErrors') == True:
			for i in range(o.obj.GetN()):
				o.obj.SetPointError(i, o.obj.GetEX()[i], o.obj.GetEY()[i] * o.obj.GetX()[i])
		if o.obj.InheritsFrom('TGraphAsymmErrors') == True:
			for i in range(o.obj.GetN()):
				o.obj.SetPointError(i, o.obj.GetEXlow()[i], o.obj.GetEXhigh()[i], o.obj.GetEYlow()[i] * o.obj.GetX()[i], o.obj.GetEYhigh()[i] * o.obj.GetX()[i])

	def scale_1x_at_index_any(self):
		for i in range(len(self.l)):
			self.scale_1x_at_index(i)

	def scale_at_index(self, i=-1, val = 1.):
		if len(self.l) < 1:
			return
		o = self.l[i]
		if o.obj.InheritsFrom('TH1') == True:
			o.obj.Sumw2()
			if val == 0:
				o.obj.Scale(1.0, "width")
			else:
				o.obj.Scale(val)
		if o.obj.InheritsFrom('TGraph') == True:
			for i in range(o.obj.GetN()):
				o.obj.SetPoint(i, o.obj.GetX()[i], o.obj.GetY()[i] * val)
		if o.obj.InheritsFrom('TGraphErrors') == True:
			for i in range(o.obj.GetN()):
				o.obj.SetPointError(i, o.obj.GetEX()[i], o.obj.GetEY()[i] * val)
		if o.obj.InheritsFrom('TGraphAsymmErrors') == True:
			for i in range(o.obj.GetN()):
				o.obj.SetPointError(i, o.obj.GetEXlow()[i], o.obj.GetEXhigh()[i], o.obj.GetEYlow()[i] * val, o.obj.GetEYhigh()[i] * val)

	def trim_graph_range(self, gr, xmin, xmax):
		n = gr.GetN()
		x = gr.GetX()
		if n < 1:
			return False
		if xmin == None:
			xmin = gr.GetX()[0]
		if xmax == None:
			xmin = gr.GetX()[n-1]
		for i in range(n):
			if (x[i] < xmin) or (x[i] > xmax):
				gr.RemovePoint(i)
				return self.trim_graph_range(gr, xmin, xmax)
		return False

	def trim_histogram_range(self, gr, xmin, xmax):
		ibmax = gr.GetNbinsX() + 1
		if xmin == None:
			xmin = gr.GetBinLowEdge(1)
		if xmax == None:
			xmax = gr.GetBinCenter(ibmax) + gr.GetBinWidth(ibmax)
		for ibin in range(ibmax):
			xc = gr.GetBinCenter(ibin)
			if (xc < xmin) or (xc > xmax):
				gr.SetBinContent(ibin, 0.)
				gr.SetBinError(ibin, 0.)
				#gr.SetBinWeight(ibin, 0.)
		return False

	def trim_at_index(self, i=-1, xlow=None, xhigh=None):
		if len(self.l) < 1:
			return
		o = self.l[i]
		if o.obj.InheritsFrom('TH1') == True:
			self.trim_histogram_range(o.obj, xlow, xhigh)
		if o.obj.InheritsFrom('TGraph') == True:
			self.trim_graph_range(o.obj, xlow, xhigh)
		if o.obj.InheritsFrom('TF1') == True:
			o.obj.SetRange(xlow, xhigh)

	def flatten_at_index(self, i=-1, val=None):
		if len(self.l) < 1:
			return
		o = self.l[i]
		print('flatten', o.obj.GetName(), val)
		if o.obj.InheritsFrom('TH2') and val is not None:
			h = o.obj
			if not h.GetSumw2():
				h.Sumw2()
			for ibx in range(1, h.GetXaxis().GetNbins() + 1):
				for iby in range(1, h.GetYaxis().GetNbins() + 1):
					if h.GetBinContent(ibx, iby) != 0 or h.GetBinError(ibx, iby) > 0:
						h.SetBinContent(ibx, iby, val)
						h.SetBinError(ibx, iby, 0.0)
		else:
			print('flatten implemented only for TH2')

	def rebin(self, val = 2, norm = False):
		for o in self.l:
			if o.obj.InheritsFrom('TH1') == False:
				continue
			if not o.obj.GetSumw2():
				o.obj.Sumw2()
			o.obj.Rebin(val)
			if norm == True:
				o.obj.Scale(1./(val*1.))

	def adjust_pad_margins(self, _left=0.17, _right=0.05, _top=0.1, _bottom=0.17+0.03):
		du.adjust_pad_margins(_left, _right, _top, _bottom)

	def adjust_axis_attributes(self, which, title_size=-1, label_size = -1, title_offset=-1):
		ax = None

		for o in self.l:
			if which == 0:
				ax = o.obj.GetXaxis()
			if which == 1:
				ax = o.obj.GetYaxis()
			if which == 2:
				if o.obj.InheritsFrom('TH1'):
					ax = o.obj.GetZaxis()
			if ax:
				if title_offset != -1:
					self.axis_title_offset[which] = title_offset
				if title_size != -1:
					self.axis_title_size[which]   = title_size
				if label_size != -1:
					self.axis_label_size[which]   = label_size

				ax.SetTitleFont  (self.font)
				ax.SetTitleOffset(self.axis_title_offset[which])
				ax.SetTitleSize  (self.axis_title_size[which])
				ax.SetLabelFont  (self.font)
				ax.SetLabelSize  (self.axis_label_size[which])
				ax.SetLabelOffset(self.axis_label_offset[which])

	def adjust_to_pad(self, pad):
		if pad == self.pad:
			#print '[i] nothing to adjust:',pad, self.pad
			return
		xfactor = pad.GetAbsWNDC() / self.pad.GetAbsWNDC()
		yfactor = pad.GetAbsHNDC() / self.pad.GetAbsHNDC()
		#print '::adjust_to_pad',xfactor, yfactor
		i = 0
		new_size_t  = self.axis_title_size[i]   * yfactor
		new_size_l  = self.axis_label_size[i]   * yfactor
		new_size_to = self.axis_title_offset[i] * yfactor
		self.adjust_axis_attributes(i, new_size_t, new_size_l, new_size_to)
		i = 1
		new_size_t  = self.axis_title_size[i]   * xfactor
		new_size_l  = self.axis_label_size[i]   * xfactor
		new_size_to = self.axis_title_offset[i] * xfactor
		self.adjust_axis_attributes(i, new_size_t, new_size_l, new_size_to)
		self.update()

	def _process_dopts(self, i):
		o = self.l[i]
		if o.dopt.hidden:
			kolor = 0
			o.obj.SetFillColor(kolor)
			o.obj.SetFillColorAlpha(kolor, 0.0)
			o.obj.SetLineColor(kolor)
			o.obj.SetLineColorAlpha(kolor, 0.0)
			o.obj.SetMarkerColor(kolor)
			o.obj.SetMarkerColorAlpha(kolor, 0)
			o.obj.SetFillStyle(1001)
			o.obj.SetMarkerColor(kolor)
			o.obj.SetMarkerSize(-1)
			o.obj.SetMarkerStyle(-1)
			return
		#line
		if o.dopt.lstyle > 0:
			o.obj.SetLineStyle(o.dopt.lstyle)
		else:
			if o.dopt.use_line:
				kline = -1
				if o.dopt.last_line:
					if i > 0:
						kline = self.l[i-1].obj.GetLineStyle()
				if kline < 0:
					kline = self.style.next_line()
				o.dopt.lstyle = kline
				o.obj.SetLineStyle(kline)
		#width
		if o.dopt.lwidth > 0:
			o.obj.SetLineWidth(o.dopt.lwidth)
		#marker
		if o.dopt.pstyle > 0:
			o.obj.SetMarkerStyle(o.dopt.pstyle)
		else:
			if o.dopt.use_marker:
				o.obj.SetMarkerStyle(self.style.next_marker())
		mscale = 1.
		#if o.obj.GetMarkerStyle() >= 27 and o.obj.GetMarkerStyle() != 28: mscale = 1.4
		if o.obj.GetMarkerStyle() >= 27: mscale = 1.4
		o.obj.SetMarkerSize(o.dopt.psize * mscale)
		#fill
		if o.dopt.fstyle > 0:
				o.obj.SetFillStyle(o.dopt.fstyle)
		else:
			o.obj.SetFillStyle(0000)
			o.obj.SetFillColor(0)
		#kolor
		kolor = -1
		if o.dopt.kolor > 0:
			kolor = o.dopt.kolor
		else:
			if o.dopt.last_kolor:
				if i > 0:
					kolor = self.l[i-1].dopt.kolor
		if kolor < 0:
			kolor = self.style.next_color()

		o.dopt.kolor = kolor

		o.obj.SetFillColor(kolor)
		o.obj.SetLineColor(kolor)
		o.obj.SetMarkerColor(kolor)

		alpha = 1.0
		if o.dopt.alpha > 0:
			alpha = o.dopt.alpha/100.
			o.obj.SetFillColorAlpha(kolor, alpha)
			o.obj.SetLineColorAlpha(kolor, alpha)
			o.obj.SetMarkerColorAlpha(kolor, alpha)


	def _process_serror_dopts(self, i):
		o = self.l[i]
		#errx = ROOT.gStyle.GetErrorX()
		#ROOT.gStyle.SetErrorX(0.5)
		#ROOT.gStyle.SetErrorX(errx)
		o.obj.SetMarkerColor(0)
		o.obj.SetMarkerSize(-1)
		o.obj.SetMarkerStyle(0)

		#line
		if o.dopt.lstyle > 0:
			o.obj.SetLineStyle(o.dopt.lstyle)
		#width
		if o.dopt.lwidth > 0:
			o.obj.SetLineWidth(o.dopt.lwidth)

		#kolor
		kolor = -1
		if o.dopt.kolor > 0:
			kolor = o.dopt.kolor
		else:
			if o.dopt.last_kolor:
				if i > 0:
					kolor = self.l[i-1].dopt.kolor
		if kolor < 0:
			kolor = 7

		o.dopt.kolor = kolor

		alpha = 0.3
		if o.dopt.alpha > 0:
			alpha = o.dopt.alpha/100.

		o.obj.SetFillColor(kolor)
		o.obj.SetLineColor(kolor)
		if o.dopt.rectangle == True:
			newalpha = alpha * 2.
			if newalpha > 1.0:
				newalpha = 1.0
			o.obj.SetLineColorAlpha(kolor, newalpha)
		else:
			o.obj.SetLineColorAlpha(kolor, alpha)

		o.obj.SetMarkerColor(kolor)
		o.obj.SetMarkerColorAlpha(kolor, 0)

		if o.dopt.rectangle == True:
			o.obj.SetFillColorAlpha(kolor, alpha)
			o.obj.SetFillStyle(0000)
		else:
			o.obj.SetFillColorAlpha(kolor, alpha)
			o.obj.SetFillStyle(1001)

	def has2D(self):
		has2D = False
		for i,o in enumerate(self.l):
			if o.obj.IsA().InheritsFrom('TH2') == True:
				has2D = True
			if o.obj.IsA().InheritsFrom('TF2') == True:
				has2D = True
		return has2D

	def has_overlay(self):
		for o in self.l:
			if o.dopt.overlay:
				return True
		return False

	def draw(self, option='', miny=None, maxy=None, logy=False, colopt='', adjust_pad=True, adjust_axis_attributes=True):
		if self.has2D() == False:
			if miny == -1 and maxy == -1:
				pass
			else:
				self.adjust_maxima(miny=miny, maxy=maxy, logy=logy)
		if adjust_axis_attributes == True:
			self.adjust_axis_attributes(0)
			self.adjust_axis_attributes(1)
			self.adjust_axis_attributes(2)
		drawn = False

		#gdopt = draw_option(option) unused!
		self.style.reset()

		if self.has2D():
			#self.tcanvas = ROOT.gPad
			if not self.tcanvas:
				print('[i] 2D draw - making canvas here')
				if len(self.l) > 8:
					self.make_canvas(1000, 800)
				else:
					self.make_canvas()
			if self.has_overlay:
				self.tcanvas = du.make_canvas_grid(len(self.l), self.tcanvas)
		if self.tcanvas != None:
			tcname = self.tcanvas.GetName()
		else:
			tcname = 'used only in 2D case'

		for i,o in enumerate(self.l):
			for _exec in o.exec:
				# try:
				import importlib
				_mod_name, _meth_name = _exec.rsplit('.', 1)
				if _mod_name[:2] == './':
					sys.path.append(os.getcwd())
					_mod_name = _mod_name[2:]
				print('[i] attempting to import', _mod_name)
				_module = importlib.import_module(_mod_name)
				print('[i] trying to get method', _meth_name, 'from', _module)
				_meth = getattr(_module, _meth_name)
				_meth(cobj=o, hl=self)
				#except:
				#	print('[w] failed to exec',_meth_name, 'from', _mod_name, 'on', self.last_ds.hname, ' - command in', self.last_ds.fname)
				#	pass

		for i,o in enumerate(self.l):
			if o.dopt.shift != 0:
				if o.obj.InheritsFrom('TGraph'):
					#print 'TGraph shifting...',o.dopt.shift
					tu.shift_graph(o.obj, o.dopt.shift)
				if o.obj.InheritsFrom('TH1'):
					#print 'TH1 shifting...',o.dopt.shift
					o.obj = tu.graph_from_h(o.obj, o.dopt.shift, o.dopt.drop_threshold)
				o.dopt.shift = 0.0
			self.debug('::draw ' + o.name + ' ' + o.dopt.stripped())
			if o.dopt.is_error == False:
				self._process_dopts(i)
			#errors
			extra_opt = []
			extra_opt.append(option)
			if o.dopt.is_error:
				extra_opt.append('E2')
				self._process_serror_dopts(i)
			if self.has2D():
				if self.has_overlay:
					if o.obj.InheritsFrom('TH2') or o.obj.InheritsFrom('TF2'):
						# ROOT.gStyle.SetOptTitle(False) # True
						if len(o.dopt.stripped()) > 0:
							o.obj.Draw(o.dopt.stripped())
							#print o.obj.GetName(),o.dopt.stripped()
						else:
							o.obj.Draw('colz')
						ROOT.gPad.SetToolTipText(o.obj.GetTitle(), 100)
						self.adjust_pad_margins(_right=0.17)
					else:
						o.draw('same '.join(extra_opt))
				else:
					#tc = ROOT.gROOT.FindObject(tcname)
					#tc.cd(i+1)
					self.tcanvas.cd(i+1)
					ROOT.gStyle.SetOptTitle(False) # True
					if len(o.dopt.stripped()) > 0:
						o.obj.Draw(o.dopt.stripped())
						#print o.obj.GetName(),o.dopt.stripped()
					else:
						o.obj.Draw('colz')
					ROOT.gPad.SetToolTipText(o.obj.GetTitle(), 100)
					self.adjust_pad_margins(_right=0.17)
			else:
				o.draw(' '.join(extra_opt))
			if gDebug:
				dbgu.debug_obj(o.dopt)

		if adjust_pad == True and self.has2D() == False:
			self.adjust_pad_margins()
		self.update()
		self.pad_name = ROOT.gPad.GetName() # name is better
		self.pad = self.get_pad_drawn()
		if self.pad:
			self.debug('[i] ' + self.name + ' drawing on ' + str(self.pad))

	def draw_bare(self, option=''):
		for i,o in enumerate(self.l):
			o.obj.Draw(option)

	def set_log_multipad(self, axes='', flag=True):
		l = self.tcanvas.GetListOfPrimitives()
		# print self.tcanvas.GetName(), len(l)
		# changed becaus of #logX 1 did not work?
		for i in range(len(l) + 1):
			tp = self.tcanvas.cd(i)
			if tp:
				if 'z' in axes:
					tp.SetLogz(flag)
				if 'y' in axes:
					tp.SetLogy(flag)
				if 'x' in axes:
					tp.SetLogx(flag)

	def set_grid_multipad(self, axes='', flag=True):
		l = self.tcanvas.GetListOfPrimitives()
		for i in range(len(l)):
			tp = self.tcanvas.cd(i+1)
			if tp:
				if 'y' in axes:
					tp.SetGridy(flag)
				if 'x' in axes:
					tp.SetGridx(flag)

	def get_pad_drawn(self):
		self.pad = ROOT.gROOT.FindObject(self.pad_name)
		if not self.pad:
			self.pad = None
		return self.pad

	def self_legend(self, ncols = 1, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None, option='brNDC'):
		self.empty_legend(ncols, title, x1, y1, x2, y2, tx_size, option)
		if self.has2D() and self.force_legend is False:
			self.update()
			return self.legend
		for o in self.l:
			if not self.is_selected(o):
				continue
			if o.dopt.no_legend:
				continue
			#opt = o.dopt.stripped()
			opt = o.dopt.legend_option()
			self.debug('::self_legend legend entry with opt: {0} {1}'.format(opt,o.obj.GetTitle()) )
			#self.legend.AddEntry(o.obj, o.obj.GetTitle(), opt)
			self.legend.AddEntry(o.obj, o.user_title, opt)
		self.legend.Draw()
		self.update()
		return self.legend

	def draw_legend(self, ncols = 1, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None, option='brNDC'):
		print('[w] obsolete call to draw_legend use self_legend instead...')
		self.self_legend(ncols, title, x1, y1, x2, y2, tx_size, option)

	def empty_legend(self, ncols, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None, option='brNDC'):
		if x1==None:
			x1 = 0.2 # 0.6 # was 0.3 # was 0.5
		if y1==None:
			y1 = 0.67 #0.67 #0.7 #was 0.67
		if x2==None:
			x2 = 0.92 # 0.8 #0.88
		if y2==None:
			y2 = 0.87 #0.88 #used also 0.9
		option = option + ' #l'
		self.legend = ROOT.TLegend(x1, y1, x2, y2, '', option)
		if len(title) > 0:
			self.legend.SetHeader(title)
		self.legend.SetNColumns(ncols)
		self.legend.SetBorderSize(0)
		fkolor = ROOT.kWhite
		if '+k' in option:
			try:
				fkolor = int(option.split('+k')[1].split(' ')[0])
			except:
				fkolor = ROOT.kWhite
		self.legend.SetFillColor(fkolor)
		self.legend.SetFillStyle(1001)
		if '+a' in option:
			try:
				salpha = option.split('+a')[1].split(' ')[0]
				salpha = get_value(salpha, float, 100.)/100.
			except:
				salpha = 0
			self.legend.SetFillColorAlpha(fkolor, salpha)
		else:
			if fkolor == ROOT.kWhite:
				self.legend.SetFillColorAlpha(fkolor, 0.66)
			else:
				self.legend.SetFillColorAlpha(fkolor, 0.10)
		self.legend.SetTextAlign(12)
		self.legend.SetTextFont(self.font)
		self.legend.SetTextColor(1)
		#if tx_size!=None:
		#    if self.font == 42:
		#        #tx_size=self.axis_title_size[0]
		#        _tx_size = self.axis_title_size[0] * 0.8 * tx_size #0.045
		#    if self.font == 43:
		#        _tx_size = 14 * tx_size
		#        print tx_size,self.font
		#    self.legend.SetTextSize(_tx_size)
		#else:
		#    print self.axis_title_size[0] * 0.5
		self.legend.SetTextSize(self.axis_title_size[0] * 0.5) # was 0.5
		if tx_size!=None:
			self.legend.SetTextSize(tx_size)
		self.legend.SetToolTipText('#legend')
		return self.legend

	def update(self, logy=False):
		if self.pad:
			if logy:
				self.pad.SetLogy()
			self.pad.Modified()
			self.pad.Update()
		if self.tcanvas:
			l = self.tcanvas.GetListOfPrimitives()
			for i in range(len(l)):
				tp = self.tcanvas.cd(i+1)
				if tp:
					tp.Update()
					if logy:
						tp.SetLogy()
			self.tcanvas.Modified()
			self.tcanvas.Update()

	def make_canvas(self, w=600, h=400,
					split=0, orientation=0,
					name=None, title=None):
		#print 'make_canvas called'
		if self.tcanvas==None:
			if name == None:
				name = self.name + '-canvas'
			if title == None:
				title = self.name + '-canvas'
			name = pyutils.to_file_name(name)
			self.tcanvas = ROOT.TCanvas(name, title, w, h)
			print('[i] making canvas', self.tcanvas.GetName())
			self.tcanvas.cd()
			if split > 0:
				du.split_gPad(split, orientation)
			tu.gList.append(self.tcanvas)
		return self.tcanvas

	def destroy_canvas(self):
		if self.tcanvas != None:
			self.tcanvas.Destructor()
			self.tcanvas = None

	def resize_window(self, w, h):
		self.tcanvas.SetWindowSize(w, h) # + (w - self.tcanvas.GetWw()), h + (h - self.tcanvas.GetWh()));
		self.tcanvas.SetWindowSize(w + (w - self.tcanvas.GetWw()), h + (h - self.tcanvas.GetWh()));
		self.tcanvas.Update()

	def scale_by_binwidth(self, modifYtitle = True):
		for h in self.l:
			if h.obj.InheritsFrom('TH1'):
				if h.obj.GetSumw2() == None:
					h.obj.Sumw2()
				if h.obj.GetBinWidth(1) == h.obj.GetBinWidth(2):
					bw   = h.obj.GetBinWidth(1)
					if modifYtitle == True:
						newytitle = h.obj.GetYaxis().GetTitle() + ' / {}'.format(bw)
						h.obj.GetYaxis().SetTitle(newytitle)
					h.obj.Scale(1./bw)
				else:
					for ib in range(1, h.obj.GetNbinsX() + 1):
						v = h.obj.GetBinContent(ib)
						v = v / h.obj.GetBinWidth(ib)
						ve = h.obj.GetBinError(ib)
						ve = ve / h.obj.GetBinWidth(ib)
						h.obj.SetBinContent(ib, v)
						h.obj.SetBinError(ib, ve)
					if modifYtitle == True:
						newytitle = h.obj.GetYaxis().GetTitle() + ' / {}'.format('BW')
						h.obj.GetYaxis().SetTitle(newytitle)
			else:
				print('[w] normalize not defined for non histogram...')

	def normalize_self(self, scale_by_binwidth = True, modTitle = False, scaleE = False, to_max=False):
		for h in self.l:
			if h.obj.InheritsFrom('TH3'):
				print('[w] normalize_self not implemented for TH3')
			if h.obj.InheritsFrom('TH1'):
				#if h.GetSumw2() == None:
				h.obj.Sumw2()
				if to_max == True:
					intg = h.obj.GetMaximum()
				else:
					if h.obj.InheritsFrom('TH2') or h.obj.InheritsFrom('TF2'):
						intg = h.obj.Integral(1, h.obj.GetNbinsX(), 1, h.obj.GetNbinsY())
					else:
						intg = h.obj.Integral(1, h.obj.GetNbinsX())
				if h.obj.InheritsFrom('TH2') or h.obj.InheritsFrom('TF2'):
					if scale_by_binwidth:
						print('[w] bin width for 2D histogram set to 1.')
					bw = 1.
				else:
					bw   = h.obj.GetBinWidth(1)
				if intg > 0:
					if scale_by_binwidth:
						h.obj.Scale(1./intg/bw)
						if scaleE == True:
							scale_errors(h.obj, 1./intg/bw)
							print('[i] scale by:',1./intg/bw)
					else:
						h.obj.Scale(1./intg)
						if scaleE == True:
							scale_errors(h.obj, 1./intg)
							print('[i] scale by:',1./intg)
					if modTitle == True:
						ytitle = h.obj.GetYaxis().GetTitle()
						ytitle += ' ({0})'.format(bw)
						h.obj.GetYaxis().SetTitle(ytitle)
			else:
				print('[w] normalize not defined for non histogram...')

	def normalize_to_index(self, idx, scale_by_binwidth = True, modTitle = False, scaleE = False, to_max=False):
		intg = 0
		try:
			if to_max == True:
				intg = self.l[idx].obj.GetMaximum()
			else:
				intg = self.l[idx].obj.Integral()
		except:
			print('[w] normalization to',idx,'failed')
			return
		print('[i] normalization defined by index=',idx,'intg=',intg)
		for h in self.l:
			if h.obj.InheritsFrom('TH1'):
				#if h.GetSumw2() == None:
				h.obj.Sumw2()
				bw   = h.obj.GetBinWidth(1)
				if intg > 0:
					if scale_by_binwidth:
						h.obj.Scale(1./intg/bw)
						if scaleE == True:
							scale_errors(h.obj, 1./intg/bw)
							print('[i] scale by:',1./intg/bw)
					else:
						h.obj.Scale(1./intg)
						if scaleE == True:
							scale_errors(h.obj, 1./intg)
							print('[i] scale by:',1./intg)
					if modTitle == True:
						ytitle = h.obj.GetYaxis().GetTitle()
						ytitle += ' ({0})'.format(bw)
						h.obj.GetYaxis().SetTitle(ytitle)
			else:
				print('[w] normalize not defined for non histogram...')

	def write_to_file(self, fname=None, opt='RECREATE', name_mod=''):
		if fname==None:
			fname = './' + pyutils.to_file_name(self.name) + '.root'

		if check_andor_make_output_dir(fname, isfilename=True) is False:
			print('[e] unable to create/access output dir for: ', fname, file=sys.stderr)
			return

		try:
			f = ROOT.TFile(fname, opt)
			f.cd()
		except:
			print('[e] unable to open file:',fname, file=sys.stderr)
			return

		for i,h in enumerate(self.l):
			newname = h.obj.GetName()
			if 'mod:' in name_mod or 'modn:' in name_mod:
				smod = name_mod.replace('mod:', '')
				smod = name_mod.replace('modn:', '')
				if len(smod) > 0:
					newname = self.name + '-{}-'.format(i) + smod
				else:
					if 'modn:' in name_mod:
						newname = 'o_{}'.format(i)
					else:
						newname = self.name + '-{}'.format(i)
			else:
				if len(name_mod)>0:
					if ':' == name_mod[-1]:
						newname = name_mod.replace(':','') + '_{}'.format(i)
					else:
						newname = h.obj.GetName() + name_mod

			if h.dopt.no_legend:
				newname = newname + '_noleg'
			if h.dopt.hidden:
				newname = newname + '_hidden'
			h.obj.Write(newname)
			# except:
			# 	print >> sys.stderr, '[e] unable to write object:',h.obj.GetName()

		try:
			f.Close()
			print('[i] written to file',fname)
		except:
			print('[e] writing to file {0} failed'.format(fname), file=sys.stderr)

	def ratio_to(self, ito = 0, opt='HIST'):
		hdenom = self.l[ito].obj
		hret = dlist('{}-ratio-to-index-{}'.format(self.name, ito))
		for i in range(len(self.l)):
			if i == ito:
				continue
			h = self.l[i].obj
			hlr = make_ratio(h, hdenom)
			hret.add(hlr.last().obj, hlr.last().obj.GetTitle(), opt)
		return hret

	def ratio_to_graph(self, ito = 0, opt='p'):
		hdenom = self.l[ito].obj
		hret = dlist('{}-ratio-to-index-{}'.format(self.name, ito))
		for i in range(len(self.l)):
			if i == ito:
				continue
			h = self.l[i].obj
			hlr = ROOT.TGraphAsymmErrors(h, hdenom)
			hret.add(hlr, h.GetTitle()+'_div_'+hdenom.GetTitle(), opt)
		return hret

	def ratio_to_href(self, hdenom, opt='HIST'):
		hret = dlist('{}-ratio-to-href-{}'.format(self.name, hdenom.GetName()))
		for i in range(len(self.l)):
			h = self.l[i].obj
			hlr = make_ratio(h, hdenom)
			hret.add(hlr.last().obj, hlr.last().obj.GetTitle(), opt)
		return hret

	def reset_titles(self, stitles):
		for h in self.l:
			i = self.l.index(h)
			if i < len(stitles):
				h.obj.SetTitle(stitles[i])

	def reset_user_titles(self, stitles):
		for h in self.l:
			i = self.l.index(h)
			if i < len(stitles):
				h.user_title = stitles[i]

	def draw_comment(self, comment = '', font_size=None, x1 = 0.0, y1 = 0.9, x2 = 0.99, y2 = 0.99, rotation=0.0):
		du.draw_comment(comment, font_size, x1, y1, x2, y2, rotation)

	def sum(self, scales=None):
		reth = None
		isummed = 0
		for i,h in enumerate(self.l):
			if h.dopt.hidden or h.obj.GetTitle() == 'fake':
				continue
			if isummed == 0:
				reth = draw_object(h.obj, self.name + '-sum', h.name + '-sum')
				if scales != None:
					reth.obj.Scale(scales[i])
				isummed += 1
				continue
			scale = 1.
			if scales != None:
				scale = scales[i]
			if reth.obj.InheritsFrom('TGraph') or h.obj.InheritsFrom('TGraph'):
				add_graphs(reth.obj, h.obj)
				isummed += 1
			else:
				reth.obj.Add(h.obj, scale)
				isummed += 1
		return reth

	def set_name_as_filename(self, name):
		self.name = pyutils.to_file_name(name)

	def pdf(self):
		self.tcanvas.Print(pyutils.to_file_name(self.name)+'.pdf','.pdf')
		if dlist.enable_eps:
			self.tcanvas.Print(pyutils.to_file_name(self.name)+'.eps','.eps')

	def pdf_to_file(self, fname):
		self.tcanvas.Print(fname,'pdf')

	def png(self):
		self.tcanvas.Print(pyutils.to_file_name(self.name)+'.png','.png')

def add_graphs(o1, o2, w=1.):
	print('[w] do not trust add_graphs with errors...')
	if o1.InheritsFrom('TGraph') and o2.InheritsFrom('TGraph'):
		x = o1.GetX()
		y = o1.GetY()
		for i in range(o1.GetN()):
			if o1.InheritsFrom('TGraphErrors'):
				xe = o1.GetEX()[i]
				ye = o1.GetEY()[i]
				fractionE = ye / y[i]
			if x[i] == o2.GetX()[i]:
				y[i] = y[i] - o2.GetY[i]
				print('simple substr..')
			else:
				y[i] = y[i] + w * o2.Eval(x[i], 0, 'S')
			if o1.InheritsFrom('TGraphErrors'):
				ye = y[i] * fractionE
			o1.SetPoint(i, x[i], y[i])
			if o1.InheritsFrom('TGraphErrors'):
				o1.SetPointError(i, xe, ye)

def divide_graphs(o1, o2, w=1.):
	print('[w] do not trust add_graphs with errors...')
	if o1.InheritsFrom('TGraph') and o2.InheritsFrom('TGraph'):
		x = o1.GetX()
		y = o1.GetY()
		for i in range(o1.GetN()):
			try:
				y[i] = y[i] / (w * o2.Eval(x[i], 0, 'S'))
			except:
				y[i] = 0.
			try:
				o1.GetEY()[i] = o1.GetEY()[i] / (w * o2.Eval(x[i], 0, 'S'))
			except:
				pass

class ListStorage:
	def __init__(self, name = None):
		if name == None:
			name = 'global_debug_list_of_lists'
		self.name = name
		self.name = tu.unique_name(name)
		tu.gList.append(self)
		self.lists = []
		self.tcanvas = None
		self.lx1 = None
		self.lx2 = None
		self.ly1 = None
		self.ly2 = None
		self.legend_font_scale = 1.

	def __getitem__(self, i):
		return self.lists[i]

	def reset_axis_titles(self, titlex=None, titley=None, titlez=None):
		for hl in self.lists:
			hl.reset_axis_titles(titlex, titley, titlez)

	def add_to_list(self, lname, obj, title, dopt):
		hl = self.get(lname)
		hl.add(obj, title, dopt)

	def add_from_file(self, lname, hname, fname, htitle, dopt):
		hl = self.get(lname)
		return hl.add_from_file(hname, fname, htitle, dopt)

	def get(self, lname):
		for l in self.lists:
			if lname == l.name:
				return l
		retl = dlist(lname)
		self.lists.append(retl)
		return self.get(lname)

	def get_list(self, lname):
		return self.get(lname)

	def zoom_axis(self, which, xmin, xmax):
		for l in self.lists:
			l.zoom_axis(which, xmin, xmax)
		self.update()

	def append(self, hl):
		self.lists.append(hl)

	def prepend(self, hl):
		self.lists.insert(0, hl)

	def legend_position(self, x1=None, y1=None, x2=None, y2=None):
		self.lx1 = x1
		self.lx2 = x2
		self.ly1 = y1
		self.ly2 = y2

	def resize_window(self, w, h):
		self.tcanvas.SetWindowSize(w, h) # + (w - self.tcanvas.GetWw()), h + (h - self.tcanvas.GetWh()));
		self.tcanvas.SetWindowSize(w + (w - self.tcanvas.GetWw()), h + (h - self.tcanvas.GetWh()));
		self.tcanvas.Update()

	def fix_x_range(self, xmin, xmax):
		for l in self.lists:
			l.fix_x_range(xmin, xmax)
			#print l

	def draw_all(self, option='', miny=None, maxy=None, logy=False, colopt='', legtitle='', orient=0, condense=False, draw_legend=True):
		legoption = 'brNDC'
		if len(self.lists) <= 0:
			return
		if condense == False:
			self.tcanvas = du.make_canvas_grid(len(self.lists), None, self.name+'-canvas', self.name, orient=orient)
		else:
			tmptc = ROOT.TCanvas('tc-'+self.name, 'tc-'+self.name)
			self.tcanvas = pcanvas.pcanvas(tmptc, len(self.lists))
			legoption = 'br'
		for i,l in enumerate(self.lists):
			if legtitle == '':
				slegtitle = l.title
			else:
				slegtitle = legtitle
			if legtitle == None:
				slegtitle = ''
			if ';single_pad' in legtitle:
				slegtitle = legtitle
				slegtitle = slegtitle.replace(';single_pad', '')
				if i > 0:
					slegtitle = ' '
			self.tcanvas.cd(i+1)
			if condense == True:
				l.set_font(43, 1.4)
			if condense == False:
				l.draw(logy=logy, option=option, miny=miny, maxy=maxy, colopt=colopt)
			else:
				l.draw(logy=logy, option=option, miny=miny, maxy=maxy, colopt=colopt, adjust_pad=False)
			if draw_legend:
				if self.lx1 != None:
					legend = l.self_legend(1, slegtitle, self.lx1, self.ly1, self.lx2, self.ly2,
						tx_size=self.legend_font_scale * 0.04, option=legoption)
				else:
					legend = l.self_legend(ncols=1, title=slegtitle, tx_size=self.legend_font_scale * 0.04, option=legoption)
			else:
				if legtitle == 'self':
					l.draw_comment(l.title, 0.05, 0, 0.9, 1., 1.)
			l.update(logy=logy)
		self.adjust_pads()

	def draw_mpad(self, miny=None, maxy=None, logy=False, legtitle = []):
		ncol = 1
		nrow = 1
		while ncol * nrow < len(self.lists):
			if ncol * nrow < len(self.lists):
				ncol = ncol + 1
			if ncol * nrow < len(self.lists):
				nrow = nrow + 1
		remap = []
		for n in range(ncol * nrow):
			if n < ncol:
				remap.append(n*2+1)
			else:
				remap.append((n-ncol)*2)
		print(remap)
		import canvas2
		tcname = '{}-canvas-condensed'.format(self.name)
		self.tcanvas = canvas2.CanvasSplit(tcname, ncol, nrow, None, int(850*1.2), int(600*1.2))
		for i in range(len(self.lists)):
			hl = self.lists[i]
			hl.set_font(42)
			tp = self.tcanvas.cd(remap[i])
			self.tcanvas.adjust_axis(hl, scaleTSize=1.2, scaleLSize=1.2)
			hl.draw(logy=True, miny=miny,maxy=maxy,adjust_pad=False, adjust_axis_attributes=False)
			tp.SetLogy(logy)
			xf = self.tcanvas.get_axis_factor(0)
			yf = self.tcanvas.get_axis_factor(1)
			#leg = hl.self_legend(1, '', x1=10, x2=18, y1=1e-6, y2=5.e-4, option='br')
			leg = hl.self_legend(1, '', self.lx1, self.ly1, self.lx2, self.ly2, option='br')
			for i,st in enumerate(legtitle):
				if i == 0: continue
				leg.AddEntry(0, st, '')
			pad_width  = ROOT.gPad.XtoPixel(ROOT.gPad.GetX2())
			pad_height = ROOT.gPad.YtoPixel(ROOT.gPad.GetY1())
			#print pad_width, pad_height
			pxlsize = 16.
			if pad_width < pad_height:
				#charheight = textsize*pad_width;
				textsize = pxlsize / pad_width
			else:
				#charheight = textsize*pad_height;
				textsize = pxlsize / pad_height
			fsize = 1
			#print xf, yf, xf * yf, fsize, textsize
			leg.SetTextSize(textsize)
			leg.Draw()
		self.tcanvas.tc.Update()

	def adjust_pads(self):
		for i,hl in enumerate(self.lists):
			hl.adjust_to_pad(self.lists[0].pad)

	def pdf(self):
		self.tcanvas.Print(pyutils.to_file_name(self.name)+'.pdf','.pdf')

	def png(self):
		self.tcanvas.Print(pyutils.to_file_name(self.name)+'.png','.png')

	def write_all(self, mod='', opt='RECREATE'):
		for i,hl in enumerate(self.lists):
			hl.write_to_file(opt=opt, name_mod = mod)

	def update(self, logy=False):
		for l in self.lists:
			l.update(logy=logy)

	def get_pads(self):
		self.pads = []
		for ip in [ self.tcanvas.cd(i+1) for i in range(len(self.lists)) ]:
			self.pads.append(ip)
		return self.pads

	def set_grid_x(self, what=True):
		for p in self.get_pads():
			p.SetGridx(what)
			p.Update()

	def set_grid_y(self, what=True):
		for p in self.get_pads():
			p.SetGridy(what)
			p.Update()

	def set_log_axis(self, axis='', what=True):
		for p in self.get_pads():
			if 'x' in axis:
				p.SetLogx(what)
			if 'y' in axis:
				p.SetLogy(what)
			if 'z' in axis:
				p.SetLogz(what)
			p.Update()

gDebugLists = ListStorage()
gDL = gDebugLists

def load_tlist(tlist, pattern=None, names_not_titles=True, draw_opt='HIST', hl = None):
	listname = tlist.GetName()
	if hl == None:
		hl = ol(listname)
	for obj in tlist:
		to_load=False
		if pattern:
			if pattern in obj.GetName():
				to_load=True
			else:
				to_load=False
		else:
			to_load=True

		if to_load:
			if names_not_titles == True:
				newname = "{}:{}".format(tlist.GetName(), obj.GetName())
				hl.add (obj, newname, draw_opt)
				#hl.addh (obj, newname, draw_opt)
				#hl.addgr(obj, newname)
				#hl.addf (obj, newname, 'L')
			else:
				hl.add (obj, draw_opt=draw_opt)
				#hl.addh(obj, draw_opt=draw_opt)
				#hl.addgr(obj)
				#hl.addf(obj, None, 'L')
			#print '[i] add   :',obj.GetName()
		else:
			#print '[i] ignore:',obj.GetName()
			pass
	return hl

def load_file(fname='', pattern=None, names_not_titles=True, draw_opt='', xmin=None, xmax=None):
	if not fname:
		return None

	fin = None
	try:
		fin = ROOT.TFile(fname)
	except:
		print('[e] root file open failed for',fname, file=sys.stderr)
		return None

	listname = fname.replace('/','_')+'-'+'-hlist'
	if pattern:
		listname = fname.replace('/','_')+'-'+pattern.replace(' ','-')+'-hlist'

	hl = dlist(listname)
	if xmin!=None and xmax!=None:
		hl = make_list(listname, xmin, xmax)

	lkeys = fin.GetListOfKeys()
	for key in lkeys:
		if key.GetClassName() == "TList":
			load_tlist(key.ReadObj(), pattern, names_not_titles, draw_opt, hl)
		to_load=False
		if pattern:
			if pattern in key.GetName():
				to_load=True
			else:
				to_load=False
		else:
			to_load=True

		if to_load:
			obj = key.ReadObj()
			if names_not_titles:
				hl.add(obj, obj.GetName(), draw_opt)
				hl.last().obj.SetName(key.GetName())
			else:
				hl.add(obj, '', draw_opt=draw_opt)
				hl.last().obj.SetName(key.GetName())
			#print '[i] add   :',key.GetName()
		else:
			#print '[i] ignore:',key.GetName()
			pass
	fin.Close()

	if len(hl.l) <= 0:
		print('[w] No entries in the list!', file=sys.stderr)

	return hl

def show_file(fname='', logy=False, pattern=None, draw_opt='p', names_not_titles=True, xmin=None, xmax=None, ymin=None, ymax=None):

	tu.setup_basic_root()
	#ROOT.gROOT.Reset()
	#ROOT.gStyle.SetScreenFactor(1)

	hl = load_file(fname, pattern, names_not_titles, draw_opt, xmin, xmax)
	hl.pattern = pattern
	if not hl.has2D():
		hl.make_canvas()
		hl.tcanvas.Divide(2,1)
		hl.tcanvas.cd(1)

	if 'self' in draw_opt:
		hl.draw(draw_opt, None, None, logy)
	else:
		#hl.colorize()
		#hl.markerize()
		#hl.lineize()
		if xmin!=None and xmax!=None:
			hl.zoom_axis(0, xmin, xmax)
		hl.draw(draw_opt, ymin, ymax, logy)
	if logy:
		ROOT.gPad.SetLogy()
	if tu.is_arg_set('--logx'):
		ROOT.gPad.SetLogx()

	exs = ' '.join(sys.argv)
	exs = exs.replace(sys.argv[0], 'show_file:')
	fnsize = float(1.5/len(exs))
	du.draw_comment(exs, fnsize, 0, 0.9, 1., 1.)
	# ::draw_comment was ol method at some point

	hl.tcanvas.cd(2)
	#hl.draw_legend(1,fname+'[{0}]'.format(pattern))
	hl.self_legend(1, fname + ' [ {0} ]'.format(pattern), 0.0, 0.0, 1, 1)
	hl.tcanvas.Update()
	#the one below is better (?)
	#ROOT.gPad.Update()
	return hl

def make_ratio(h1, h2):
	hl = dlist('ratio {} div {}'.format(h1.GetName(), h2.GetName()).replace(' ', '_'))
	newname = '{}_div_{}'.format(h1.GetName(), h2.GetName())
	newtitle = '{} / {}'.format(h1.GetTitle(), h2.GetTitle())
	hr = h1.Clone(newname)
	hr.SetTitle(newtitle)

	if h1.InheritsFrom('TGraph') and h2.InheritsFrom('TGraph'):
		divide_graphs(hr, h2)
	else:
		if not h1.InheritsFrom('TGraphAsymmErrors'):
			hr.SetDirectory(0)
			hr.Divide(h2)
		else:
			for i in range(1, h1.GetN()):
				x = h1.GetX()[i]
				y = h1.GetY()[i]
				vy = 0
				if h2.InheritsFrom('TGraph'):
					vy = h2.Eval(x, 0, 'S')
				if h2.InheritsFrom('TH1'):
					vy = h2.GetBinContent(h2.FindBin(x))
				if vy != 0:
					hr.SetPoint(i, x, y / vy)
					# hr.SetPointError(i, ex, h1.GetEY()[i] / h2.GetY()[i])
					# SetPointError (Int_t i, Double_t exl, Double_t exh, Double_t eyl, Double_t eyh)
					hr.SetPointError(i, h1.GetEXlow()[i], h1.GetEXhigh()[i], h1.GetEYlow()[i] / vy, h1.GetEYhigh()[i] / vy)	
				else:
					hr.SetPoint(i, x, 0)
					# hr.SetPointError(i, h1.GetEXlow(), 0)
					hr.SetPointError(i, h1.GetEXlow()[i], h1.GetEXhigh()[i], 0, 0)
	hl.add(hr, newtitle, 'p')

	hl.reset_axis_titles(None, newtitle)

	return hl

def make_sum(h1, h2, w=1.):
	hl = dlist('sum {} and {} w{}'.format(h1.GetName(), h2.GetName(), w).replace(' ', '_'))
	newname = '{}_and_{}_w={}'.format(h1.GetName(), h2.GetName(), w)
	newtitle = 'sum {} + {} w={}'.format(h1.GetTitle(), h2.GetTitle(), w)
	hr = h1.Clone(newname)
	hr.SetTitle(newtitle)

	if h1.InheritsFrom('TGraph') and h2.InheritsFrom('TGraph'):
		add_graphs(hr, h2, w)
	else:
		hr.SetDirectory(0)
		hr.Add(h2, w)
	hl.add(hr, newtitle, 'p')

	hl.reset_axis_titles(None, newtitle)

	return hl

def scale_errors(h, val):
	for i in range(1, h.GetNbinsX()):
		err = h.GetBinError(i)
		h.SetBinError(i, err * val)

def reset_errors(h, herr, relative=False):
	for i in range(1, h.GetNbinsX()):
		if h.GetBinContent(i) == 0 and h.GetBinError(i) == 0:
			continue
		err = herr.GetBinError(i)
		if relative == True:
			if herr.GetBinContent(i) != 0:
				relat = h.GetBinContent(i) / herr.GetBinContent(i)
			else:
				relat = 1.
			err = err * relat
		h.SetBinError(i, err)

def reset_points(h, xmin, xmax, val=0.0, err=0.0):
	for ib in range(1, h.GetNbinsX()+1):
		if h.GetBinCenter(ib) > xmin and h.GetBinCenter(ib) < xmax:
			h.SetBinContent(ib, val)
			h.SetBinError(ib, err)

#yields above threshold - bin-by-bin
def yats(olin):
	oret = dlist(olin.name + '_yat')
	oret.copy(olin)
	for idx,ho in enumerate(oret.l):
		h = ho.obj
		h.Reset()
		hin = olin.l[idx].obj
		for ib in range(1, hin.GetNbinsX()):
			maxbin = hin.GetNbinsX()
			yat    = hin.Integral(ib, maxbin, "width")
			h.SetBinContent(ib, yat)
			#oret.lopts[idx] = olin.lopts[idx] # not needed - within copy
	return oret

def fractional_yats(olin, refidx=-1):
	oret = dlist(olin.name + '_fyat')
	oret.copy(olin)

	integRef = 1.
	if refidx >= 0:
		hin      = olin.l[refidx].obj
		maxbin   = hin.GetNbinsX()
		integRef = hin.Integral(1, maxbin, "width")

	for idx,ho in enumerate(oret.l):
		h = ho.obj
		h.Reset()
		hin    = olin.l[idx].obj
		maxbin = hin.GetNbinsX()
		integ  = hin.Integral(1, maxbin, "width")
		if integ <= 0:
			print("[w] integral ? ",integ)
			integ = -1.
		for ib in range(1, maxbin):
			if refidx >= 0:
				yat    = hin.Integral(ib, maxbin, "width") / integRef
			else:
				yat    = hin.Integral(ib, maxbin, "width") / integ
			h.SetBinContent(ib, yat)
			#oret.lopts[idx] = olin.lopts[idx] # not needed - within copy
	return oret

def rejs(olin):
	oret = ol(olin.name + '_rej')
	oret.copy(olin)
	for h in oret.l:
		h.Reset()
		idx = oret.l.index(h)
		hin = olin.l[idx]
		for ib in range(1, hin.GetNbinsX()):
			maxbin = hin.GetNbinsX()
			yat    = hin.Integral(ib  , maxbin)
			yatp1  = hin.Integral(1   , maxbin)
			h.SetBinContent(ib, yat/yatp1)
	return oret

def filter_single_entries_h(h, href=None, thr=10):
	if href == None:
		href = h
	for ib in range(1, h.GetNbinsX()+1):
		if href.GetBinContent(ib) < thr:
			h.SetBinContent(ib, 0)
			h.SetBinError(ib, 0)

def filter_single_entries_h2d(h, href=None, thr=10):
	if href == None:
		href = h
	for ib in range(1, h.GetNbinsX()+1):
		for iby in range(1, h.GetNbinsY()+1):
			if href.GetBinContent(ib, iby) < thr:
				h.SetBinContent(ib, iby, 0)
				h.SetBinError(ib, iby, 0)

def filter_single_entries(hl, hlref, thr=10):
	for ih in range(len(hl.l)):
		h    = hl.l[ih].obj
		href = hlref.l[ih].obj
		for ib in range(h.GetNbinsX()+1):
			if href.GetBinContent(ib) < thr:
				h.SetBinContent(ib, 0)
				h.SetBinError(ib, 0)

def filter_single_entries_2d(hl, hlref, thr=10):
	for ih in range(len(hl.l)):
		h    = hl.l[ih].obj
		href = hlref.l[ih].obj
		for ib in range(1, h.GetNbinsX()+1):
			for iby in range(1, h.GetNbinsY()+1):
				if href.GetBinContent(ib, iby) < thr:
					h.SetBinContent(ib, iby, 0)
					h.SetBinError(ib, iby, 0)

def get_projection_axis(hname, h2d, axis, ixmin=0, ixmax=105):
	if axis == 1:
		ixminb = h2d.GetXaxis().FindBin(ixmin)
		ixmaxb = h2d.GetXaxis().FindBin(ixmax)
		if ixmaxb > h2d.GetXaxis().GetNbins():
			imaxb = h2d.GetXaxis().GetNbins()
		hproj = h2d.ProjectionY(hname, ixminb, ixmaxb)
	else:
		ixminb = h2d.GetYaxis().FindBin(ixmin)
		ixmaxb = h2d.GetYaxis().FindBin(ixmax)
		if ixmaxb > h2d.GetYaxis().GetNbins():
			imaxb = h2d.GetYaxis().GetNbins()
		hproj = h2d.ProjectionX(hname, ixminb, ixmaxb)
	return hproj

def get_projectionY(hname, h2d, ixmin=0, ixmax=105):
	return get_projection_axis(hname, h2d, 1, ixmin=0, ixmax=105)

def get_projections_axis_bins(hname, fname, htitle, opt, axis, pTs):
	h2d = tu.get_object_from_file(hname, fname, htitle + '2d')
	if h2d == None:
		print('[i] unable to get:',hname,'from:',fname)
		return None
	pTmin = pTs[0][0]
	pTmax = pTs[len(pTs)-1][1]
	hlname = 'projections-{}-{}-{}-{}-{}'.format(hname, fname, htitle, pTmin, pTmax)
	hl = dlist(hname+htitle)
	for i in range(len(pTs)):
		pTmin = pTs[i][0]
		pTmax = pTs[i][1]
		htitlepy = '{} [{}-{}]'.format(htitle, pTmin, pTmax)
		if axis == 1:
			hn     = '{}-py-{}-{}'.format(hname, pTmin, pTmax)
		else:
			hn     = '{}-px-{}-{}'.format(hname, pTmin, pTmax)
		hp = get_projection_axis(hn, h2d, axis, pTmin, pTmax)
		hp.Sumw2()
		hl.append(hp, htitlepy, 'P L HIST')
	return hl

def get_projections_axis(hname, fname, htitle, pTmin, pTmax, step, opt='P L HIST', axis = 1, pTs=None):
	h2d = tu.get_object_from_file(hname, fname, htitle + '2d')
	if h2d == None:
		print('[i] unable to get:',hname,'from:',fname)
		return None
	hlname = 'projections-{}-{}-{}-{}-{}-{}'.format(hname, fname, htitle, pTmin, pTmax, step)
	hl = dlist(hname+htitle)
	pT = pTmin
	while pT + step < pTmax:
		if pTs != None:
			pTs.append(pT)
		htitlepy = '{} [{}-{}]'.format(htitle, pT, pT + step)
		if axis == 1:
			hn     = '{}-py-{}-{}'.format(hname, pT, pT + step)
		else:
			hn     = '{}-px-{}-{}'.format(hname, pT, pT + step)
		hp = get_projection_axis(hn, h2d, axis, pT, pT + step)
		hp.Sumw2()
		hl.append(hp, htitlepy, 'P L HIST')
		pT = pT + step
	return hl

def get_projections_axis_lowcut(hname, fname, htitle, pTmin, pTmax, step, opt='P L HIST', axis = 1, pTs=None):
	h2d = tu.get_object_from_file(hname, fname, htitle + '2d')
	if h2d == None:
		print('[i] unable to get:',hname,'from:',fname)
		return None
	hlname = 'projections-{}-{}-{}-{}-{}-{}'.format(hname, fname, htitle, pTmin, pTmax, step)
	hl = dlist(hname+htitle)
	pT = pTmin
	Amax = h2d.GetXaxis().GetXmax()
	if axis == 0:
		Amax = h2d.GetYaxis().GetXmax()
	while pT + step <= pTmax:
		if pTs != None:
			pTs.append(pT)
		htitlepy = '{} [{}-{}]'.format(htitle, pT, Amax)
		if axis == 1:
			hn     = '{}-py-{}-{}'.format(hname, pT, Amax)
		else:
			hn     = '{}-px-{}-{}'.format(hname, pT, Amax)
		hp = get_projection_axis(hn, h2d, axis, pT, Amax)
		hp.Sumw2()
		hl.append(hp, htitlepy, 'P L HIST')
		pT = pT + step
	return hl

def get_projections(hname, fname, htitle, pTmin, pTmax, step, opt='P L HIST', pTs=None):
	return get_projections_axis(hname, fname, htitle, pTmin, pTmax, step, opt, 1, pTs)

def get_projectionsY(hname, fname, htitle, pTmin, pTmax, step, opt='P L HIST', pTs=None):
	return get_projections_axis(hname, fname, htitle, pTmin, pTmax, step, opt, 1, pTs)

def get_projectionsX(hname, fname, htitle, pTmin, pTmax, step, opt='P L HIST', pTs=None):
	return get_projections_axis(hname, fname, htitle, pTmin, pTmax, step, opt, 0, pTs)

def make_graph_xy(name, x, y, xe = [], ye = []):
	xf = []
	yf = []
	xef = []
	yef = []
	for v in x:
		xf.append(float(v))
	for v in y:
		yf.append(float(v))
	xa = array('f', xf)
	ya = array('f', yf)
	if len(xe) == 0:
		for ix in x:
			xef.append(0)
	else:
		for v in xe:
			xef.append(float(v))
	xae = array('f', xef)
	if len(ye) == 0:
		for iy in y:
			yef.append(0)
	else:
		for v in ye:
			yef.append(float(v))
	yae = array('f', yef)
	if len(ye) == 0 and len(xe) == 0:
		gr = ROOT.TGraph(len(xf), xa, ya)
	else:
		gr = ROOT.TGraphErrors(len(xf), xa, ya, xae, yae)
	gr.SetName(name)
	return gr

def make_graph(name, data):
	x = []
	y = []
	xe = []
	ye = []
	for ix in data:
		x.append(ix[0])
		y.append(ix[1])
		try:
			xe.append(ix[2])
		except:
			pass
		try:
			ye.append(ix[3])
		except:
			pass

	return make_graph_xy(name, x, y, xe, ye)

def make_graph_ae_xy(name, x, y, xlow = [], xhigh = [], ylow = [], yhigh = []):
	xf     = array('f', x)
	yf     = array('f', y)
	zs     = []
	for i in range(len(x)):
		zs.append(0)

	if len(xlow) > 0:
		xflow  = array('f', xlow)
	else:
		xflow  = array('f', zs)

	if len(xhigh) > 0:
	   xfhigh = array('f', xhigh)
	else:
	   xfhigh = array('f', zs)

	if len(ylow) > 0:
		yflow  = array('f', ylow)
	else:
		yflow  = array('f', zs)

	if len(yhigh) > 0:
	   yfhigh = array('f', yhigh)
	else:
	   yfhigh = array('f', zs)

	#print len(x), xf, yf, xflow, xfhigh, yflow, yfhigh
	gr = ROOT.TGraphAsymmErrors(len(x), xf, yf, xflow, xfhigh, yflow, yfhigh)
	gr.SetName(name)
	return gr

def norm_error_graph(name, x, width, y, ymin, ymax=-1):
	ax = [x - width/2.]
	xl = [width/2.]
	xh = [width/2.]
	ay = [y]
	yl = [ymin]
	yh = [ymax]
	if ymax < 0:
		yh = [ymin]
	return make_graph_ae_xy(name, ax, ay, xl, xh, yl, yh)

def make_list(name, xmin, xmax):
	hl = dlist(name)
	gr = ROOT.TGraph(2)
	gr.SetPoint(0, xmin, 0)
	gr.SetPoint(1, xmax,  0)
	hl.add(gr, 'fake', 'noleg hidden p')
	return hl

def h_to_graph(h, drop_zero_entries=False, xerror=False, transpose=False):
	x = []
	y = []
	ex = []
	ey = []
	for ib in range(1,h.GetNbinsX()+1):
		if drop_zero_entries:
			if type(drop_zero_entries) is bool:
				ymin = 0.0
				if (h.GetBinContent(ib)*h.GetBinContent(ib)) <= ymin:
					print('dropped bin bool', ib, h.GetBinContent(ib), ymin)
					continue
			else:
				ymin = drop_zero_entries
				if h.GetBinContent(ib) <= ymin:
					print('dropped bin', ib, h.GetBinContent(ib), ymin)
					continue
		x.append(h.GetBinCenter(ib))
		y.append(h.GetBinContent(ib))
		if xerror == True:
			ex.append(h.GetBinCenter(ib) - h.GetBinLowEdge(ib))
		else:
			ex.append(0)
		ey.append(h.GetBinError(ib))
	name = h.GetName() + '_to_graph'
	title = h.GetTitle()
	if transpose:
		gr = make_graph_xy(name, y, x, ey, ex)
	else:
		gr = make_graph_xy(name, x, y, ex, ey)
	gr.SetTitle(title)
	return gr

def scale_graph_errors(gr, axis, scale=1.):
	if gr.InheritsFrom('TGraphErrors'):
		for i in range(gr.GetN()):
			if axis == 0:
				gr.GetEX()[i] = gr.GetEX()[i] * scale
			else:
				gr.GetEY()[i] = gr.GetEY()[i] * scale
	if gr.InheritsFrom('TGraphAsymmErrors'):
		for i in range(gr.GetN()):
			if axis == 0:
				gr.GetEXlow()[i] = gr.GetEXlow()[i] * scale
				gr.GetEXhigh()[i] = gr.GetEXhigh()[i] * scale
			else:
				gr.GetEYlow()[i] = gr.GetEYlow()[i] * scale
				gr.GetEYhigh()[i] = gr.GetEYhigh()[i] * scale

def scale_by_binwidth(h, modifYtitle = True):
	if h.InheritsFrom('TH1'):
		if h.GetSumw2() == None:
			h.Sumw2()
		if h.GetBinWidth(1) == h.GetBinWidth(2):
			bw   = h.GetBinWidth(1)
			if modifYtitle == True:
				newytitle = h.GetYaxis().GetTitle() + ' / {}'.format(bw)
				h.GetYaxis().SetTitle(newytitle)
			h.Scale(1./bw)
		else:
			for ib in range(1, h.GetNbinsX() + 1):
				v = h.GetBinContent(ib)
				v = v / h.GetBinWidth(ib)
				ve = h.GetBinError(ib)
				ve = ve / h.GetBinWidth(ib)
				h.SetBinContent(ib, v)
				h.SetBinError(ib, ve)
			if modifYtitle == True:
				newytitle = h.GetYaxis().GetTitle() + ' / {}'.format('BW')
				h.GetYaxis().SetTitle(newytitle)
	else:
		print('[w] normalize not defined for non histogram...')
