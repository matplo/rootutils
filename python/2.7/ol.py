import ROOT
import sys
import draw_utils as du

gDebug = False

class ol:

    def __init__(self, name='hl'):
        self.name = name
        self.l = []
        self.lopts = []
        self.marker_size = 1.1
        self.good_colors  = [ -1,  2,  1,  9,  6,  8, 40, 43, 46, 49, 32, 39, 28, 38]
        self.good_markers = [ -1, 20, 24, 21, 25, 27, 28, 33, 34, 29, 30]
        self.good_lines   = [ -1,  1,  7,  3,  5,  8,  6,  2,  4,  9, 10]
        self.maxy = 1e6 # was 1
        self.miny = -1e6 # was 0
        self.max_adjusted = False
        self.axis_title_offset = [1.4, 1.4, 1.4]
        self.axis_title_size   = [0.06, 0.06, 0.06]
        self.axis_label_size   = [0.06, 0.06, 0.06]
        self.pattern = None
        self.tcanvas = None

    def __getitem__(self, i):
        if i < len(self.l) and i >= 0:
            return self.l[i]
        else:
            return None
        
    def copy_list(self, l=[]):
        for h in l:
            self.addh(h)

    def copy(self, l):
        for h in l.l:
            idx = l.l.index(h)
            self.addh(h, h.GetTitle() + '_copy', l.lopts[idx])
            hc = self.last()
            hc.SetLineColor(h.GetLineColor())
            hc.SetLineStyle(h.GetLineStyle())            
            hc.SetLineWidth(h.GetLineWidth())                        
            hc.SetMarkerColor(h.GetMarkerColor())
            hc.SetMarkerStyle(h.GetMarkerStyle())            
            hc.SetMarkerSize(h.GetMarkerSize())                        
            hc.SetFillColor(h.GetFillColor())
            hc.SetFillStyle(h.GetFillStyle())            
            
    def last(self):
        if len(self.l) > 0:
            return self.l[len(self.l)-1]
        return None
            
    def is_selected(self, o):
        if self.pattern != None:
            if not self.pattern in o.GetName():
                return False
        return True        
        
    def debug(self, msg):
        global gDebug
        if gDebug == True:
            print '[d]',msg

    def _check_name(self, name):
        for o in self.l:
            if o.GetName() == name:
                return True
        return False
        
    def find_miny(self, low=None):
        miny = 1e12
        for h in self.l:
            if not h.InheritsFrom('TH1'):
                continue
            for nb in range(1, h.GetNbinsX()):
                c = h.GetBinContent(nb)
                if c!=0 and c <= miny:
                    miny = c
        if low!=None:
            if miny < low:
                miny == low
        return miny

    def find_maxy(self):
        maxy = -1e12
        for h in self.l:
            if not h.InheritsFrom('TH1'):
                continue
            for nb in range(1, h.GetNbinsX()):
                c = h.GetBinContent(nb)
                if c!=0 and c > maxy:
                    maxy = c
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
                h.SetMinimum(self.miny)
            if self.maxy!=None:
                h.SetMaximum(self.maxy)

        self.max_adjusted = True
        self.debug('::adjust_maxima min: {} max {}'.format(self.miny, self.maxy))

    def append(self, obj=ROOT.TObject, new_title = '', draw_opt = ''):
        newname_root = obj.GetName() + '_' + self.name.replace(' ', '_')
        newname = newname_root
        count = 1
        while self._check_name(newname) == True:
            newname = newname_root + '_' + str(count)
            count = count + 1
        cobj = obj.Clone(newname)
        if obj.InheritsFrom('TH1'):
            cobj.SetDirectory(0)
        if new_title:
            cobj.SetTitle(new_title)
        if cobj.GetTitle() == '':
            cobj.SetTitle(newname)
        self.l.append(cobj)
        self.lopts.append(draw_opt)
        self.debug('::append '+cobj.GetName()+' '+draw_opt)
        return cobj    

    def addh_from_file(self, hname = '', fname = '', new_title = '', draw_opt = ''):
        cobj = None
        f = ROOT.TFile(fname)
        if f:
            h = f.Get(hname)
            if h:
                cobj = self.addh(h, new_title, draw_opt)
            f.Close()
        return cobj
    
    def add_from_file(self, hname = '', fname = '', new_title = '', draw_opt = ''):
        cobj = None
        f = ROOT.TFile(fname)
        if f:
            h = f.Get(hname)
            if h:
                cobj = self.add(h, new_title, draw_opt)
            f.Close()
        return cobj

    def add(self, obj=ROOT.TObject, new_title = '', draw_opt = ''):
        if obj == None: return
        cobj = None
        if obj.IsA().InheritsFrom("TH1") \
            or obj.IsA().InheritsFrom("TGraph") \
            or obj.IsA().InheritsFrom("TF1"):
            #h = ROOT.TH1(obj)
            cobj = self.append(obj, new_title, draw_opt)
            if self.maxy < obj.GetMaximum():
                self.maxy = obj.GetMaximum()
            if self.miny < obj.GetMinimum():
                self.miny = obj.GetMinimum()
        return cobj    
    
    def addh(self, obj=ROOT.TObject, new_title = '', draw_opt = ''):
        if obj == None: return
        cobj = None
        if obj.IsA().InheritsFrom("TH1"):
            #h = ROOT.TH1(obj)
            cobj = self.append(obj, new_title, draw_opt)
            if self.maxy < obj.GetMaximum():
                self.maxy = obj.GetMaximum()
            if self.miny < obj.GetMinimum():
                self.miny = obj.GetMinimum()
        return cobj
    
    def addgr(self, obj=ROOT.TObject, new_title = '', draw_opt = ''):
        cobj = None
        if obj.IsA().InheritsFrom("TGraph"):
            #h = ROOT.TH1(obj)
            cobj = self.append(obj, new_title, draw_opt)
            if self.maxy < obj.GetMaximum():
                self.maxy = obj.GetMaximum()
            if self.miny < obj.GetMinimum():
                self.miny = obj.GetMinimum()
        return cobj

    def addf(self, obj=ROOT.TObject, new_title = '', draw_opt = ''):
        cobj = None
        if obj.IsA().InheritsFrom("TF1"):
            #h = ROOT.TH1(obj)
            cobj = self.append(obj, new_title, draw_opt)
            if self.maxy < obj.GetMaximum():
                self.maxy = obj.GetMaximum()
            if self.miny < obj.GetMinimum():
                self.miny = obj.GetMinimum()
        return cobj
    
    def reset_axis_titles(self, xt=None, yt=None, zt=None):
        for o in self.l:
            if xt:
                o.GetXaxis().SetTitle(xt)
            if yt:
                o.GetYaxis().SetTitle(yt)
            if zt:
                if o.InheritsFrom('TH1'):
                    o.GetZaxis().SetTitle(zt)

    def zoom_axis(self, which, xmin, xmax):
        ax = None
        for o in self.l:
            if which == 0:
                ax = o.GetXaxis()
            if which == 1:
                ax = o.GetYaxis()
            if which == 2:
                if o.InheritsFrom('TH1'):
                    ax = o.GetZaxis()
            if ax:
                ax.SetRange(ax.FindBin(xmin), ax.FindBin(xmax))
                
    def scale_errors(self, val = 1.):
        for o in self.l:
            if o.InheritsFrom('TH1') == False:
                continue
            for i in range(1, o.GetNbinsX()):
                err = o.GetBinError(i)
                o.SetBinError(i, err * val)
    
    def scale(self, val = 1.):
        for o in self.l:
            if o.InheritsFrom('TH1') == False:
                continue
            if o.GetSumw2() == None:
                o.Sumw2()
            o.Scale(val)
            #for i in range(1, o.GetNbinsX()):
            #    err = o.GetBinError(i)
            #    o.SetBinError(i, err * val)
            #    v = o.GetBinContent(i)
            #    o.SetBinContent(i, v * val)
                
    def rebin(self, val = 2, norm = False):
        for o in self.l:
            if o.InheritsFrom('TH1') == False:
                continue
            if not o.GetSumw2():
                o.Sumw2()
            o.Rebin(val)
            if norm == True:
                o.Scale(1./val)
                
    def adjust_pad_margins(self, _left=0.17, _right=0.05, _top=0.1, _bottom=0.17+0.03):
        du.adjust_pad_margins(_left, _right, _top, _bottom)
        
    def adjust_axis_attributes(self, which, title_size=-1, label_size = -1, title_offset=-1):
        ax = None

        for o in self.l:
            if which == 0:
                ax = o.GetXaxis()
            if which == 1:
                ax = o.GetYaxis()
            if which == 2:
                if o.InheritsFrom('TH1'):
                    ax = o.GetZaxis()
            if ax:
                if title_offset != -1:
                    self.axis_title_offset[which] = title_offset
                if title_size != -1:
                    self.axis_title_size[which]   = title_size
                if label_size != -1:
                    self.axis_label_size[which]   = label_size

                _title_offset = self.axis_title_offset[which]
                _title_size   = self.axis_title_size[which]
                _label_size   = self.axis_label_size[which]
                ax.SetTitleOffset(_title_offset)
                ax.SetTitleSize(_title_size)
                ax.SetTitleFont(42)
                ax.SetLabelSize(_label_size)
                ax.SetLabelFont(42)

    def get_style_from_opt(self, opt, what): #what can be l or p or f
        ts = opt.split('+')
        #self.debug('::get_style_from_opt ' + str(ts))
        val = 0       
        for t in ts:
            tt = t.split(' ')[0]
            if len(tt) <= 0:
                continue
            if tt[0]==what:
                try:
                    nt = tt[1:]
                    val = int(nt)
                except:
                    pass
        self.debug('::get_style_from_opt on {} returning {}'.format(what, val))
        return val

    def all_options(self):
        ret = []
        for h in self.l:
            i = self.l.index(h)
            opt = self.lopts[i]
            ret.append(opt)
        return ' '.join(ret).lower()
            
    def draw(self, option='', miny=None, maxy=None, logy=False, colopt=''):
        self.adjust_maxima(miny=miny, maxy=maxy, logy=logy)
        self.adjust_axis_attributes(0)
        self.adjust_axis_attributes(1)
        self.adjust_axis_attributes(2)
        drawn = False

        opts = self.all_options() + ' ' + option.lower()
        if 'hist' in opts or 'l' in opts or 'c' in opts:
            self.lineize()
        if 'bw' in opts:
            pass
        else:
            self.colorize()
        if 'p' in opts:
            self.markerize()
        
        for h in self.l:
            i = self.l.index(h)
            if self.lopts[i] == '':
                self.lopts[i] = option
            opt = self.lopts[i]
            self.debug('::draw ' + h.GetName() + ' ' + opt)
            lstyle = self.get_style_from_opt(opt.lower(), 'l')
            if lstyle > 0:
                h.SetLineStyle(lstyle)
            pstyle = self.get_style_from_opt(opt.lower(), 'p')
            if pstyle > 0:
                h.SetMarkerStyle(pstyle)
            fstyle = self.get_style_from_opt(opt.lower(), 'f')
            if fstyle > 0:
                h.SetFillStyle(fstyle)
            kolor = self.get_style_from_opt(opt.lower(), 'k')
            if kolor > 0:
                h.SetFillColor(kolor)
                h.SetLineColor(kolor)
                h.SetMarkerColor(kolor)                                
            
            if drawn == True:
                opt = opt + ' same'
            else:
                drawn = True                
            h.Draw(opt)                
        self.adjust_pad_margins()            
        self.update()
        
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
            
    def self_legend(self, ncols = 1, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None):
        self.empty_legend(ncols, title, x1, y1, x2, y2, tx_size)
        for o in self.l:
            if not self.is_selected(o):
                continue
            opts = self.lopts[self.l.index(o)].split(' ')
            opt = ''
            for op in opts:
                if 'p' in op.lower():
                    opt = opt + 'p'
                if 'l' in op.lower() or 'c' in op.lower():
                    opt = opt + 'l'
                if 'hist' in op.lower():
                    opt = opt + 'l'
                if 'f' in op.lower():
                    opt = opt + 'f'                    
            self.debug('::self_legend legend entry with opt: {0} {1}'.format(opt,o.GetTitle()) )
            self.legend.AddEntry(o, o.GetTitle(), opt)
        self.legend.Draw()
        self.update()
        
    def empty_legend(self, ncols, title='', x1=None, y1=None, x2=None, y2=None, tx_size=None):
        if x1==None:
            x1 = 0.5
        if y1==None:
            y1 = 0.67
        if x2==None:
            x2 = 0.88
        if y2==None:
            y2 = 0.88            

        self.legend = ROOT.TLegend(x1, y1, x2, y2)
        self.legend.SetHeader(title)
        self.legend.SetNColumns(ncols)
        self.legend.SetBorderSize(0)
        self.legend.SetFillColor(ROOT.kWhite)
        self.legend.SetFillStyle(0)            
        #self.legend.SetTextSize(0.032)
        if tx_size==None:
            #tx_size=self.axis_title_size[0]
            tx_size = 0.03
        self.legend.SetTextSize(tx_size)
        
        return self.legend

    def update(self):
        ROOT.gPad.Update()        

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
        return self.tcanvas
        
    def normalize_self(self, scale_by_binwidth = True, modTitle = False):
        for h in self.l:
            if h.GetSumw2() == None:
                h.Sumw2()
            intg = h.Integral(1, h.GetNbinsX())
            bw   = h.GetBinWidth(1)
            if intg > 0:
                if scale_by_binwidth:
                    h.Scale(1./intg/bw)
                else:
                    h.Scale(1./intg)
                    if modTitle == True:
                        ytitle = h.GetYaxis().GetTitle()
                        ytitle += ' ({0})'.format(bw)
                        h.GetYaxis().SetTitle(ytitle)

    def write_to_file(self, fname, opt='RECREATE', name_mod=''):
        try:
            f = ROOT.TFile(fname, opt)
            f.cd()
            for h in self.l:
                newname = h.GetName() + name_mod
                h.Write(newname)
            f.Close()
            print '[i] written to file',fname
        except:
            print >> sys.stderr,'[e] writing to file {0} failed'.format(fname)
        
def load_file(fname='', pattern=None, names_not_titles=True):
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

    hl = ol(listname)

    lkeys = fin.GetListOfKeys()
    for key in lkeys:
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
                hl.addh(obj, obj.GetName())
                hl.addgr(obj, obj.GetName())
                hl.addf(obj, obj.GetName(), 'L')                
            else:
                hl.addh(obj)
                hl.addgr(obj)
                hl.addf(obj, None, 'L')                
            #print '[i] add   :',key.GetName()
        else:
            #print '[i] ignore:',key.GetName()
            pass
    fin.Close()

    if len(hl.l) <= 0:
        print >> sys.stderr,'[w] No entries in the list!'

    return hl

def show_file(fname='', logy=False, pattern=None, draw_opt='lpf', names_not_titles=True, xmin=None, xmax=None):

    ROOT.gROOT.Reset()
    ROOT.gStyle.SetScreenFactor(1)

    hl = load_file(fname, pattern, names_not_titles)
    hl.pattern = pattern

    hl.make_canvas()
    hl.tcanvas.Divide(2,1)
    hl.tcanvas.cd(1)
    if 'self' in draw_opt:
        hl.draw(draw_opt, None, None, logy)
    else:
        hl.colorize()
        hl.markerize()
        hl.lineize()
        if xmin!=None and xmax!=None:
            hl.zoom_axis(0, xmin, xmax)
        hl.draw(draw_opt, None, None, logy)
    if logy:
        ROOT.gPad.SetLogy()

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
    hl = ol('ratio {} div {}'.format(h1.GetName(), h2.GetName()).replace(' ', '_'))
    newname = '{}_div_{}'.format(h1.GetName(), h2.GetName())
    newtitle = '{} / {}'.format(h1.GetTitle(), h2.GetTitle())
    hr = h1.Clone(newname)
    hr.SetTitle(newtitle)

    hr.SetDirectory(0)
    hr.Divide(h2)
    hl.addh(hr)

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
    oret = ol(olin.name + '_yat')
    oret.copy(olin)
    for h in oret.l:
        h.Reset()
        idx = oret.l.index(h)
        hin = olin.l[idx]
        for ib in range(1, hin.GetNbinsX()):
            maxbin = hin.GetNbinsX()
            yat    = hin.Integral(ib, maxbin)
            h.SetBinContent(ib, yat)
            #oret.lopts[idx] = olin.lopts[idx] # not needed - within copy
    return oret
