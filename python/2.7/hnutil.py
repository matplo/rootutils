import dlist
import tutils as tu

def make_ratio(h1, h2):
    hl = dlist.dlist('ratio {} div {}'.format(h1.GetName(), h2.GetName()).replace(' ', '_'))
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
    oret = dlist.dlist(olin.name + '_yat')
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
    oret = dlist.dlist(olin.name + '_fyat')
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
    if axis == 0:
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
    hl = dlist.dlist(hname+htitle)
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

def get_projections_axis(hname, fname, htitle, vmin, vmax, step, opt='P L HIST', axis = 1, vs=None):
    h2d = tu.get_object_from_file(hname, fname, htitle + '2d')
    if h2d == None:
        print '[i] unable to get:',hname,'from:',fname
        return None
    hlname = 'projections-{}-{}-{}-{}-{}-{}'.format(hname, fname, htitle, vmin, vmax, step)
    hl = dlist.dlist(hname+htitle)
    v = vmin
    while v + step < vmax:
        if vs != None:
            vs.append(v)
        htitlepy = '{} [{}-{}]'.format(htitle, v, v + step)
        if axis == 1:
            hn     = '{}-py-{}-{}'.format(hname, v, v + step)
        else:
            hn     = '{}-px-{}-{}'.format(hname, v, v + step)            
        hp = get_projection_axis(hn, h2d, axis, v, v + step)            
        hp.Sumw2()
        hl.append(hp, htitlepy, 'P L HIST')
        v = v + step            
    return hl

def get_projections(hname, fname, htitle, vmin, vmax, step, opt='P L HIST', vs=None):
    return get_projections_axis(hname, fname, htitle, vmin, vmax, step, opt, 1, vs)

def get_projectionsY(hname, fname, htitle, vmin, vmax, step, opt='P L HIST', vs=None):
    return get_projections_axis(hname, fname, htitle, vmin, vmax, step, opt, 1, vs)

def get_projectionsX(hname, fname, htitle, vmin, vmax, step, opt='P L HIST', vs=None):
    return get_projections_axis(hname, fname, htitle, vmin, vmax, step, opt, 0, vs)

def to_file_name(s):
        return "".join([x if x.isalnum() else "_" for x in s])

#for TH3F
class Proj3to1d(object):
    def __init__(self, h3d):
        if h3d == None:
            print '[e] ::Proj3to1d pass None in __init__ - this will not work'
        self.h = h3d
        self.is3d = False
        if self.h.IsA().InheritsFrom('TH3'):
            self.is3d = True
        self.name = 'Proj3to1d-' + self.h.GetName()
        self.ls = dlist.ListStorage(self.name)

    def make_name(self, axis, ixmin, ixmax, iymin, iymax):
        s = '{}-{}--{}-{}--{}-{}'.format(axis, ixmin, ixmax, iymin, iymax)
        return s

    def get_projection_axis(self, axis, ixmin=0., ixmax=1e6, iymin=0., iymax=1e6):
        hname = '{}--{}--{}-{}-{}-{}'.format(self.h.GetName(), axis, ixmin, ixmax, iymin, iymax)
        if self.is3d:
            hname = '{}--{}--{}-{}-{}-{}'.format(self.h.GetName(), axis, ixmin, ixmax, iymin, iymax)            
        else:
            hname = '{}--{}--{}-{}'.format(self.h.GetName(), axis, ixmin, ixmax)
        hproj = None
        if axis == 0:
            ixminb  = self.h.GetYaxis().FindBin(ixmin)
            ixmaxb  = self.h.GetYaxis().FindBin(ixmax)
            if self.is3d:
                iyminb  = self.h.GetZaxis().FindBin(iymin)
                iymaxb  = self.h.GetZaxis().FindBin(iymax)
                hproj   = self.h.ProjectionX(hname, ixminb, ixmaxb, iyminb, iymaxb)        
            else:
                hproj   = self.h.ProjectionX(hname, ixminb, ixmaxb)
        if axis == 1:
            ixminb  = self.h.GetXaxis().FindBin(ixmin)
            ixmaxb  = self.h.GetXaxis().FindBin(ixmax)
            if self.is3d:
                iyminb  = self.h.GetZaxis().FindBin(iymin)
                iymaxb  = self.h.GetZaxis().FindBin(iymax)
                hproj   = self.h.ProjectionY(hname, ixminb, ixmaxb, iyminb, iymaxb)        
            else:
                hproj   = self.h.ProjectionY(hname, ixminb, ixmaxb)
        if self.is3d == True and axis == 2:
            ixminb  = self.h.GetXaxis().FindBin(ixmin)
            ixmaxb  = self.h.GetXaxis().FindBin(ixmax)
            iyminb  = self.h.GetYaxis().FindBin(iymin)
            iymaxb  = self.h.GetYaxis().FindBin(iymax)
            hproj   = self.h.ProjectionZ(hname, ixminb, ixmaxb, iyminb, iymaxb)
        #hproj.Sumw2()
        return hproj

    def get_projections_axis(self, axis, binsx, binsy=None, nrebin = None):
        if self.is3d:
            outlname = '{}-{}-{}-{}'.format(self.name, axis, to_file_name(str(binsx)), to_file_name(str(binsy)))
        else:
            outlname = '{}-{}-{}'.format(self.name, axis, to_file_name(str(binsx)))            
        print '[i] new list:', outlname
        for i,x in enumerate(binsx):
            if self.is3d:
                y = binsy[i]
                proj = self.get_projection_axis(axis, x[0], x[1], y[0], y[1])
            else:
                proj = self.get_projection_axis(axis, x[0], x[1])
            if nrebin!=None:
                proj.Rebin(nrebin)
                proj.Scale(1./nrebin)
            if self.is3d:
                titles = '{} -> {} [{}:{}] [{}:{}]'.format(self.h.GetTitle(), axis, x[0], x[1], y[0], y[1])
            else:
                titles = '{} -> {} [{}:{}]'.format(self.h.GetTitle(), axis, x[0], x[1])
            self.ls.add_to_list(outlname, proj, titles, 'p')
