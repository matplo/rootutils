import ROOT
import sys
import draw_utils as du
import tutils as tu
from array import array
gDebug = False
#needs a fix: the import below depends on where the module is...
from dbgu import debug_utils as dbgu
import pcanvas

class debugable(object):
    def __init__(self):
        pass
    
    def debug(self, msg):
        global gDebug
        if gDebug == True:
            print '[d]',msg

class style_iterator(debugable):
    good_colors  = [ -1,  2,  1,  9,  6, 32, 49, 40,  8, 43, 46, 39, 28, 38, 21, 22, 23]
    good_markers = [ -1, 20, 24, 21, 25, 33, 27, 28, 34, 29, 30, 20, 24, 21, 25, 27, 33, 28, 34, 29, 30]
    #good_lines   = [ -1,  1,  2,  3,  5,  8,  6,  7,  4,  9, 10]
    good_lines   = [ -1,  1,  2,  3,  5,  7,  9,  6, 8, 4, 10, 1,  2,  3,  5,  7,  9,  6, 8, 4, 10]
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.color_idx  = 0
        self.line_idx   = 0
        self.marker_idx = 0
        self.line_width = 2
        
    def colorize(self, force_color=None):
        self.color_idx = 0
        for o in self.l:
            icol = force_color
            if icol == None:
                icol = self.next_color()
            o.SetLineColor(icol)
        
    def lineize(self, force_line=None):
        self.line_idx = 0
        for o in self.l:
            imark = force_line
            if imark == None:
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
            if imark >= 27 : scale = 1.3
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
    
class draw_option(debugable):
        
    def __init__(self, stro = ''):
        self.s = stro.lower()
        self.strip = self.s
        self.debug('::draw_option with {}'.format(self.s))
        self.lstyle      = self.get_style_from_opt('l')
        self.pstyle      = self.get_style_from_opt('p')
        self.fstyle      = self.get_style_from_opt('f')
        self.kolor       = self.get_style_from_opt('k')
        self.alpha       = self.get_style_from_opt('a') #alpha for fill
        self.lwidth      = self.get_style_from_opt('w')
        if self.lwidth == 0:
            self.lwidth = 2
        self.psize       = self.get_style_from_opt('m')
        if self.psize == 0:
            self.psize = 0.9
        else:
            self.psize = self.psize/100.
        self.use_line        = self.check_use_line()
        self.use_line_legend = self.check_use_line_legend()
        self.bw              = self.check_black_white()
        self.use_marker      = self.check_use_marker()
        self.is_error        = self.has(['serror'], strip=True)
        self.no_legend       = self.has(['noleg'],  strip=True)
        self.hidden          = self.has(['hidden'], strip=True)
        self.last_kolor      = self.has(['-k'])
        self.last_line       = self.has(['-l'])

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
            #for s in self.s.split(' '):
            for s in self.strip.split(' '):
                if e == s[:len(e)]:
                    ret = True
                    if strip == True:
                        self.strip = self.strip.replace(e, '')
        return ret
                
    def get_style_from_opt(self, what): #what can be l or p or f
        ts = self.s.split('+')
        #self.debug('::get_style_from_opt ' + str(ts))
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
        self.strip = self.strip.replace('+{}{}'.format(what,str(val)),'')
        return val

def random_string(prefix='', ns = 30):
    lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(ns)]
    return str(prefix)+''.join(lst) 

class draw_object(debugable):
    def __init__(self, robj, name = None, new_title = None, dopts=''):
        self.name = name
        if self.name == None:
            self.name = '{}_{}'.format(robj.GetName(), random_string())
        self.obj  = robj.Clone(self.name)
        if self.obj.InheritsFrom('TH1'):
            self.obj.SetDirectory(0)
        if new_title:
            self.obj.SetTitle(new_title)
        if self.obj.GetTitle() == '':
            self.obj.SetTitle(self.name)        
        self.dopt = draw_option(dopts)
        self.is_first = False
        
    def draw(self, extra_opt=''):
        sdopt = self.dopt.stripped() + ' ' + extra_opt
        if 'draw!' in extra_opt.lower():
            sdopt = extra_opt
        if self.is_first==True:
            if self.obj.InheritsFrom('TGraph'):
                sdopt = sdopt + ' A'
            self.debug('doption=' + sdopt)
            self.obj.Draw(sdopt)
        else:
            self.obj.Draw(sdopt + ' same')
             
class dlist(debugable):
    def __init__(self, name='hl'):
        self.name              = name
        self.title             = name
        self.l                 = []
        self.style             = style_iterator()
        self.maxy              = 1e6 # was 1
        self.miny              = -1e6 # was 0
        self.max_adjusted      = False
        self.axis_title_offset = [5,   5,  5] #[1.4, 1.4, 1.4]
        self.axis_title_size   = [12, 12, 12] #[0.05, 0.05, 0.05]
        self.axis_label_size   = [12, 12, 12] # for font 42 [0.04, 0.04, 0.04]
        self.axis_label_offset = [0.02, 0.02, 0.02]
        self.font              = 42
        self.pattern           = None
        self.tcanvas           = None
        self.minx              = None
        self.maxx              = None
        self.pad_name          = None # pad where last drawn
        self.pad               = None # pad where last drawn
        self.set_font(42)

    def set_font(self, fn=42, scale=1.):
        self.font = fn
        if self.font == 42:
            self.axis_title_offset = [1.40, 1.40, 1.40] # y offset was 1.40 then 1.45
            self.axis_title_size   = [0.05 * scale, 0.05 * scale, 0.05 * scale]
            self.axis_label_size   = [0.04 * scale, 0.04 * scale, 0.04 * scale]
            self.axis_label_offset = [0.02, 0.02, 0.02]
        if self.font == 43:
            self.axis_title_offset = [ 3,     3,     3] #[1.4, 1.4, 1.4]
            self.axis_label_offset = [ 0.01,  0.01,  0.01]
            self.axis_title_size   = [12 * scale, 12 * scale, 12 * scale] #[0.05, 0.05, 0.05]
            self.axis_label_size   = [12 * scale, 12 * scale, 12 * scale] # for font 42 [0.04, 0.04, 0.04]

    def __getitem__(self, i):
        if i < len(self.l) and i >= 0:
            return self.l[i]
        else:
            return None

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
        
    def find_miny(self, low=None):
        miny = 1e12
        for h in self.l:
            if h.obj.InheritsFrom('TH1'):
                for nb in range(1, h.obj.GetNbinsX()):
                    c = h.obj.GetBinContent(nb)
                    if c!=0 and c <= miny:
                        miny = c 
            if h.obj.InheritsFrom('TGraph'):
                for idx in range(h.obj.GetN()):
                    v = h.obj.GetY()[idx]
                    if v < miny:
                        miny = v                                               
        if low!=None:
            if miny < low:
                miny == low
        return miny

    def find_maxy(self):
        maxy = -1e15
        for h in self.l:
            if h.obj.InheritsFrom('TH1'):
                for nb in range(1, h.obj.GetNbinsX()):
                    c = h.obj.GetBinContent(nb)
                    if c!=0 and c > maxy:
                        maxy = c                
            if h.obj.InheritsFrom('TGraph'):
                for idx in range(h.obj.GetN()):
                    v = h.obj.GetY()[idx]
                    if v > maxy:
                        maxy = v                        
        return maxy
    
    def adjust_maxima(self, miny=None, maxy=None, logy=False):
        if miny!=None:
            self.miny=miny
        else:
            self.miny = self.find_miny()
            if self.miny < 0:
                self.miny = self.miny * 1.1
            else:
                self.miny = self.miny * 0.9
            if logy==True:
                self.miny=self.find_miny() * 0.5
            # self.miny, miny, maxy, logy
            if logy==True and self.miny <= 0:
                miny=self.find_miny(0)
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
        count = 1
        while self._check_name(newname) == True:
            newname = newname_root + '_' + str(count)
            count = count + 1
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
   
    def add_from_file(self, hname = '', fname = '', new_title = '', draw_opt = ''):
        cobj = None
        f = ROOT.TFile(fname)
        if f:
            h = f.Get(hname)
            if h:
                cobj = self.add(h, new_title, draw_opt)
            f.Close()
        return cobj

    def add(self, obj=ROOT.TObject, new_title = '', draw_opt = '', prep=False):
        if obj == None: return
        cobj = None
        try:
            robj = obj.obj
        except:
            robj = obj
        if robj.InheritsFrom('TH2'):
            cobj = self.append(robj, new_title, draw_opt)            
            return cobj
        if robj.InheritsFrom("TH1") \
            or robj.InheritsFrom("TGraph") \
            or robj.InheritsFrom("TF1"):
            #h = ROOT.TH1(obj)
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
        gr = ROOT.TGraph(2)
        gr.SetPoint(0, xmin,  100)
        gr.SetPoint(1, xmax,  200)
        o = draw_object(gr, 'zoom_axis_obj', 'fake', 'noleg hidden p')
        self.l.insert(0, o)

    def find_xlimits(self):
        xmin = 0
        xmax = 0
        for o in self.l:
            h = o.obj
            for ix in range(1, h.GetNbinsX()+1):
                if h.GetBinContent(ix) != 0:
                    if xmin > h.GetBinLowEdge(ix):
                        xmin = h.GetBinLowEdge(ix)
                    if xmax < h.GetBinCenter(ix) + h.GetBinWidth(ix):
                        xmax = h.GetBinCenter(ix) + h.GetBinWidth(ix)
        return [xmin - xmin*0.1, xmax + xmax*0.1]

    def zoom_axis(self, which, xmin, xmax):
        ax = None            
        for o in self.l:
            if which == 0:
                ax = o.obj.GetXaxis()
                if xmax == None:
                    xlims = self.find_xlimits()
                    self.zoom_axis(which, xlims[0], xlims[1])
                    return
            if which == 1:
                ax = o.obj.GetYaxis()
            if which == 2:
                if o.obj.InheritsFrom('TH1'):
                    ax = o.obj.GetZaxis()
            if ax:
                ibmin = ax.FindBin(xmin)
                ibmax = ax.FindBin(xmax)
                try:
                    #print 'ibmin, ibmax, nbins:',ibmin, ibmax, o.obj.GetNbinsX()
                    if ibmax > o.obj.GetNbinsX():
                        ibmax = o.obj.GetNbinsX()
                        #print 'reset axis max to:',ibmax
                except:
                    #print ibmin, ibmax
                    pass
                ax.SetRange(ibmin, ibmax)
                
    def scale_errors(self, val = 1.):
        for o in self.l:
            if o.obj.InheritsFrom('TH1') == False:
                continue
            for i in range(1, o.obj.GetNbinsX()):
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

    def scale_at_index(self, i=-1, val = 1.):
        if i < 0:
            return
        o = self.l[i]
        if o.obj.InheritsFrom('TH1') == True:
            o.obj.Sumw2()
            o.obj.Scale(val)
        if o.obj.InheritsFrom('TGraph') == True:
            for i in range(o.obj.GetN()):
                o.obj.SetPoint(i, o.obj.GetX()[i], o.obj.GetY()[i] * val)
        if o.obj.InheritsFrom('TGraphErrors') == True:
            for i in range(o.obj.GetN()):
                o.obj.SetPointError(i, o.obj.GetEX()[i], o.obj.GetEY()[i] * val)
            
    def rebin(self, val = 2, norm = False):
        for o in self.l:
            if o.obj.InheritsFrom('TH1') == False:
                continue
            if not o.obj.GetSumw2():
                o.obj.Sumw2()
            o.obj.Rebin(val)
            if norm == True:
                o.obj.Scale(1./val)
                
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
        o.obj.SetLineColorAlpha(kolor, alpha)

        o.obj.SetMarkerColor(kolor)                           
        o.obj.SetMarkerColorAlpha(kolor, 0)

        o.obj.SetFillColorAlpha(kolor, alpha)
        o.obj.SetFillStyle(1001)

    def has2D(self):
        has2D = False
        for i,o in enumerate(self.l):
            if o.obj.IsA().InheritsFrom('TH2') == True:
                has2D = True
        return has2D

    def draw(self, option='', miny=None, maxy=None, logy=False, colopt='', adjust_pad=True):
        if self.has2D() == False:
            self.adjust_maxima(miny=miny, maxy=maxy, logy=logy)
        self.adjust_axis_attributes(0)
        self.adjust_axis_attributes(1)
        self.adjust_axis_attributes(2)
        drawn = False

        gdopt = draw_option(option)
        self.style.reset()
        
        if self.has2D():
            self.tcanvas = ROOT.gPad
            if not self.tcanvas:
                self.make_canvas()
            self.tcanvas = du.make_canvas_grid(len(self.l), self.tcanvas)
        if self.tcanvas != None:
            tcname = self.tcanvas.GetName()
        else:
            tcname = 'used only in 2D case'

        for i,o in enumerate(self.l):
            self.debug('::draw ' + o.name + ' ' + o.dopt.stripped())
            if o.dopt.is_error == False:
                self._process_dopts(i)
            #errors
            extra_opt = []
            if o.dopt.is_error:
                extra_opt.append('E2')
                self._process_serror_dopts(i)
            if self.has2D():
                #tc = ROOT.gROOT.FindObject(tcname)
                #tc.cd(i+1)
                ROOT.gStyle.SetOptTitle(True)
                o.obj.Draw('colz')
                self.adjust_pad_margins(_right=0.17)
            else:
                o.draw(' '.join(extra_opt))
            if gDebug:
                dbgu.debug_obj(o.dopt)

        if adjust_pad == True and self.has2D() == False:
            self.adjust_pad_margins()

        self.update()
        self.pad_name = ROOT.gPad.GetName() # name is better
        self.get_pad_drawn();
        self.debug('[i] ' + self.name + ' drawing on ' + str(self.pad))

    def get_pad_drawn(self):
        self.pad = ROOT.gROOT.FindObject(self.pad_name);
        return self.pad

    def self_legend(self, ncols = 1, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None, option='brNDC'):
        self.empty_legend(ncols, title, x1, y1, x2, y2, tx_size, option)
        if self.has2D():
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
            self.legend.AddEntry(o.obj, o.obj.GetTitle(), opt)
        self.legend.Draw()
        self.update()
        return self.legend

    def draw_legend(self, ncols = 1, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None, option='brNDC'):
        print '[w] obsolete call to draw_legend use self_legend instead...'
        self.self_legend(ncols, title, x1, y1, x2, y2, tx_size, option)

    def empty_legend(self, ncols, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None, option='brNDC'):
        if x1==None:
            x1 = 0.6 # was 0.3 # was 0.5
        if y1==None:
            y1 = 0.67 #0.7 #was 0.67
        if x2==None:
            x2 = 0.8 #0.88
        if y2==None:
            y2 = 0.87 #0.88 #used also 0.9            
        self.legend = ROOT.TLegend(x1, y1, x2, y2, title, option)
        #self.legend.SetHeader(title)
        self.legend.SetNColumns(ncols)
        self.legend.SetBorderSize(0)
        self.legend.SetFillColor(ROOT.kWhite)
        self.legend.SetFillStyle(1001)
        self.legend.SetFillColorAlpha(ROOT.kWhite, 0.9)
        self.legend.SetTextAlign(12)
        self.legend.SetTextSize(self.axis_title_size[0] * 0.5)
        self.legend.SetTextFont(self.font)
        self.legend.SetTextColor(1)
        if tx_size!=None:
            if self.font == 42:
                #tx_size=self.axis_title_size[0]
                tx_size = self.axis_title_size[0] * 0.8 * tx_size #0.045
            if self.font == 43:
                tx_size = 14 * tx_size
            #print tx_size,self.font
            self.legend.SetTextSize(tx_size)
        
        return self.legend

    def update(self, logy=False):
        if self.pad:
            if logy:
                self.pad.SetLogy()
            self.pad.Modified()
            self.pad.Update()        

    def make_canvas(self, w=600, h=400, 
                    split=0, orientation=0, 
                    name=None, title=None):                
        if self.tcanvas==None:
            if name == None:
                name = self.name + '-canvas'
            if title == None:
                title = self.name + '-canvas'
            self.tcanvas = ROOT.TCanvas(name, title, w, h)
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
                bw   = h.obj.GetBinWidth(1)
                if modifYtitle == True:
                    newytitle = h.obj.GetYaxis().GetTitle() + ' / {}'.format(bw)
                    h.obj.GetYaxis().SetTitle(newytitle)
                h.obj.Scale(1./bw)
            else:
                print '[w] normalize not defined for non histogram...'

    def normalize_self(self, scale_by_binwidth = True, modTitle = False, scaleE = False):
        for h in self.l:
            if h.obj.InheritsFrom('TH1'):
                #if h.GetSumw2() == None:
                h.obj.Sumw2()
                intg = h.obj.Integral(1, h.obj.GetNbinsX())
                bw   = h.obj.GetBinWidth(1)
                if intg > 0:
                    if scale_by_binwidth:
                        h.obj.Scale(1./intg/bw)
                        if scaleE == True:
                            scale_errors(h.obj, 1./intg/bw)
                            print '[i] scale by:',1./intg/bw
                    else:
                        h.obj.Scale(1./intg)
                        if scaleE == True:
                            scale_errors(h.obj, 1./intg)
                            print '[i] scale by:',1./intg
                    if modTitle == True:
                        ytitle = h.obj.GetYaxis().GetTitle()
                        ytitle += ' ({0})'.format(bw)
                        h.obj.GetYaxis().SetTitle(ytitle)
            else:
                print '[w] normalize not defined for non histogram...'
                
    def write_to_file(self, fname=None, opt='RECREATE', name_mod=''):
        if fname==None:
            fname = self.name.replace(' ','_').replace('&&','and') + '.root'
        try:
            f = ROOT.TFile(fname, opt)
            f.cd()
        except:
            print >> sys.stderr, '[e] unable to open file:',fname
            return

        for i,h in enumerate(self.l):
            if 'mod:' in name_mod or 'modn:' in name_mod:
                smod = name_mod.replace('mod:', '')
                smod = name_mod.replace('modn:', '')                    
                if len(smod) > 0:
                    newname = self.name + '-{}-'.format(i) + smod
                else:
                    if 'modn:' in name_mod:
                        newname =  'o_{}'.format(i)                            
                    else:
                        newname = self.name + '-{}'.format(i)
            else:
                newname = h.obj.GetName() + name_mod
            try:
                h.obj.Write(newname)
            except:
                print >> sys.stderr, '[e] unable to write object:',h.obj.GetName()

        try:
            f.Close()
            print '[i] written to file',fname
        except:
            print >> sys.stderr,'[e] writing to file {0} failed'.format(fname)

    def ratio_to(self, ito = 0, extra_opt=''):
        hdenom = self.l[ito].obj
        hret = dlist('{}-ratio-to-index-{}'.format(self.name, ito))
        for i in range(len(self.l)):
            if i == ito:
                continue
            h = self.l[i].obj
            hlr = make_ratio(h, hdenom)
            hret.add(hlr.last().obj, hlr.last().obj.GetTitle(), 'HIST ' + extra_opt)
        return hret

    def reset_titles(self, stitles):
        for h in self.l:
            i = self.l.index(h)
            if i < len(stitles):
                h.obj.SetTitle(stitles[i])

    def draw_comment(self, comment = '', font_size=None, x1 = 0.0, y1 = 0.9, x2 = 0.99, y2 = 0.99):
        du.draw_comment(comment, font_size, x1, y1, x2, y2)
        
    def sum(self, scales=None):
        reth = None
        for i,h in enumerate(self.l):
            if i == 0:
                reth = draw_object(h.obj,self.name + '-sum', h.name + '-sum')
                if scales != None:
                    reth.Scale(scales[i])
                continue
            scale = 1.
            if scales != None:
                scale = scales[i]
            reth.obj.Add(h.obj, scale)
        return reth

    def pdf(self):
        self.tcanvas.Print(self.name+'.pdf','.pdf')

    def png(self):
        self.tcanvas.Print(self.name+'.png','.png')
    
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
        if i < len(self.lists) and i >= 0:
            return self.lists[i]
        else:
            return None

    def add_to_list(self, lname, obj, title, dopt):
        hl = self.get(lname)
        hl.add(obj, title, dopt)

    def get(self, lname):
        for l in self.lists:
            if lname == l.name:
                return l
        retl = dlist(lname)
        self.lists.append(retl)
        return self.get(lname)

    def zoom_axis(self, which, xmin, xmax):
        for l in self.lists:
            l.zoom_axis(which, xmin, xmax)
        self.update()

    def append(self, hl):
        self.lists.append(hl)

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
            print l

    def draw_all(self, option='', miny=None, maxy=None, logy=False, colopt='', legtitle='', orient=0, condense=False):
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
            self.tcanvas.cd(i+1)
            if condense == True:
                l.set_font(43, 1.4)
            if condense == False:
                l.draw(logy=logy, option=option, miny=miny, maxy=maxy, colopt=colopt)
            else:
                l.draw(logy=logy, option=option, miny=miny, maxy=maxy, colopt=colopt, adjust_pad=False)
            if self.lx1 != None:
                legend = l.self_legend(1, slegtitle, self.lx1, self.ly1, self.lx2, self.ly2, 
                    tx_size=self.legend_font_scale, option=legoption)
            else:
                legend = l.self_legend(ncols=1, title=slegtitle, tx_size=self.legend_font_scale, option=legoption)
            l.update(logy=logy)
        self.adjust_pads()

    def adjust_pads(self):
        for i,hl in enumerate(self.lists):
            hl.adjust_to_pad(self.lists[0].pad)

    def pdf(self):
        self.tcanvas.Print(self.name+'.pdf','.pdf')

    def png(self):
        self.tcanvas.Print(self.name+'.png','.png')

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
                hl.addh (obj, newname, draw_opt)
                hl.addgr(obj, newname)
                hl.addf (obj, newname, 'L')                
            else:
                hl.addh(obj, draw_opt=draw_opt)
                hl.addgr(obj)
                hl.addf(obj, None, 'L')                
            #print '[i] add   :',obj.GetName()
        else:
            #print '[i] ignore:',obj.GetName()
            pass
    return ol

def load_file(fname='', pattern=None, names_not_titles=True, draw_opt='HIST', xmin=None, xmax=None):
    if not fname:
        return None

    fin = None
    try:
        fin = ROOT.TFile(fname)
    except:
        print >> sys.stderr, '[e] root file open failed for',fname
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
            if obj.InheritsFrom('TF1'):
                draw_opt = draw_opt + 'l'
            if names_not_titles:
                hl.add(obj, obj.GetName(), draw_opt)
                hl.last().obj.SetName(key.GetName())
            else:
                hl.add(obj, draw_opt=draw_opt)                    
                hl.last().obj.SetName(key.GetName())
            #print '[i] add   :',key.GetName()
        else:
            #print '[i] ignore:',key.GetName()
            pass
    fin.Close()

    if len(hl.l) <= 0:
        print >> sys.stderr,'[w] No entries in the list!'

    return hl

def show_file(fname='', logy=False, pattern=None, draw_opt='p', names_not_titles=True, xmin=None, xmax=None, ymin=None, ymax=None):

    tu.setup_basic_root()
    #ROOT.gROOT.Reset()
    #ROOT.gStyle.SetScreenFactor(1)

    hl = load_file(fname, pattern, names_not_titles, draw_opt, xmin, xmax)
    hl.pattern = pattern

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
    hl.self_legend(1, fname + ' [ {0} ]'.format(pattern), 0.0, 0.0, 1, 1, 0.03)
    hl.tcanvas.Update()
    #the one below is better (?)
    ROOT.gPad.Update()
    
    return hl

def make_ratio(h1, h2):
    hl = dlist('ratio {} div {}'.format(h1.GetName(), h2.GetName()).replace(' ', '_'))
    newname = '{}_div_{}'.format(h1.GetName(), h2.GetName())
    newtitle = '{} / {}'.format(h1.GetTitle(), h2.GetTitle())
    hr = h1.Clone(newname)
    hr.SetTitle(newtitle)

    hr.SetDirectory(0)
    hr.Divide(h2)
    hl.add(hr)

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

def fractional_yats(olin):
    oret = dlist(olin.name + '_fyat')
    oret.copy(olin)
    for idx,ho in enumerate(oret.l):
        h = ho.obj
        h.Reset()
        hin    = olin.l[idx].obj
        maxbin = hin.GetNbinsX()
        integ  = hin.Integral(1, maxbin, "width")
        if integ <= 0:
            print "[w] integral ? ",integ
            integ = -1.
        for ib in range(1, maxbin):
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
    
def filter_single_entries(hl, hlref, thr=10):
    for ih in range(len(hl.l)):
        h    = hl.l[ih]
        href = hlref.l[ih]
        for ib in range(h.GetNbinsX()+1):
            if href.GetBinContent(ib) < thr:
                h.SetBinContent(ib, 0)
                h.SetBinError(ib, 0)

def get_projection_axis(hname, h2d, axis, ixmin=0, ixmax=105):
    if axis == 1:
        ixminb = h2d.GetXaxis().FindBin(ixmin)
        ixmaxb = h2d.GetXaxis().FindBin(ixmax)
        hproj = h2d.ProjectionY(hname, ixminb, ixmaxb)
    else:
        ixminb = h2d.GetYaxis().FindBin(ixmin)
        ixmaxb = h2d.GetYaxis().FindBin(ixmax)
        hproj = h2d.ProjectionX(hname, ixminb, ixmaxb)        
    return hproj

def get_projectionY(hname, h2d, ixmin=0, ixmax=105):
    return get_projection_axis(hname, h2d, 1, ixmin=0, ixmax=105)

def get_projections_axis_bins(hname, fname, htitle, opt, axis, pTs):
    h2d = tu.get_object_from_file(hname, fname, htitle + '2d')
    if h2d == None:
        print '[i] unable to get:',hname,'from:',fname
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
        print '[i] unable to get:',hname,'from:',fname
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
