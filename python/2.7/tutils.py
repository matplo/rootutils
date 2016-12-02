import os
import sys
import subprocess
import shlex
import signal
import time
import pyutils as ut
import datetime
import array

import import_root
import_root.atry(verbose=False)
import ROOT

sub_p = None
exit_signal = False
print_first = False
timer = time.time()

gList = []
app = None

def get_gList_names():
    names = []
    for o in gList:
        try:
            n = o.GetName()
            names.append(n)
        except:
            pass
        try:
            n = o.name
            names.append(n)
        except:
            pass
    return names

def load_lib(lname, silent = True):
    stmp = ROOT.gSystem.ExpandPathName(lname)
    if not silent:
        print '[i] loading',stmp,
    try:
        retval = ROOT.gSystem.Load(stmp)
    except:
        pass
    if not silent:
        print retval
    return retval

def add_ld_path(spath):
    stmp = ROOT.gSystem.ExpandPathName(spath)
    ROOT.gSystem.AddDynamicPath(stmp)

def make_unique_name(sbase, *namemods):
    newname = '{}_{}'.format(sbase, '_'.join([str(s) for s in namemods]) )
    newname = ut.to_file_name(newname)
    newname = unique_name(newname)
    newname = ut.to_file_name(newname)
    return newname

class ObjectName(object):
    def __init__(self, name):
        self.name = name

def unique_name(name):
    n = name
    i = 0
    while n in get_gList_names():
        n = '{}_{}'.format(name, i)
        i += 1
    gList.append(ObjectName(n))
    return n

def is_arg_set(arg=''):
    for a in sys.argv:
        if a==arg:
            return True
    return False

def get_arg_with(arg=''):
    retval = None
    maxl = len(sys.argv)
    for i in range(0,maxl):
        if sys.argv[i]==arg and i < maxl-1:
            retval=sys.argv[i+1]
    return retval

def call_cmnd(cmnd='', verbose=False):
    if verbose==True:
        print '[i] calling',cmnd
    args = shlex.split(cmnd)
    try:
        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
    except OSError as e:
        out = 'Failed.'
        err = ('Error #{0} : {1}').format(e[0], e[1])
        if verbose==True:
            print '[i]',out
            print '[e]',err
    return out,err

def wait():
    import sys
    interpreter = False
    try:
        if sys.ps1: interpreter = True
    except AttributeError:
        interpreter = False
        if sys.flags.interactive: interpreter = True
    if interpreter == True:
        print '[i]', __name__,'::wait() has no effect. This is interactive mode => CTRL-D to exit.'
    else:
        print '[i] press twice CRTL+C (fast consequtive) to exit.'
        signal.signal(signal.SIGINT, signal_handler)
        while 1:
            time.sleep(10) # this actually does not matter as long as large
            pass

def app_signal_handler(signum, frame):
    global sub_p
    global exit_signal
    global print_first
    global timer
    interval = time.time() - timer
    timer=time.time()
    if interval < 0.5:
        exit_signal = True
    else:
        exit_signal = False
    if interval > 60 or exit_signal==True or print_first==False:
        print
        if exit_signal==False:
            print '[i CRTL-C] signal #',signum,'caught; do it quickly twice to exit'
            if print_first==False:
                if sub_p!=None:
                    print '    the kid:',sub_p
            else:
                print '    interval:',interval,'s => exit condition:',exit_signal
        else:
            print '[i CRTL-C] interval:',interval,'s => exit condition:',exit_signal
        print_first=True

    if exit_signal==True:
        if sub_p!=None:
            sub_p.send_signal(signal.SIGKILL)
        global app
        if app:
            app.Terminate(0)
        else:
            ROOT.gApplication.Terminate(0)
        sys.exit(0)

def run_app():
    global app
    if app:
        app.Run()
    else:
        ROOT.gApplication.Run()

def wait_i():
    import IPython
    if not '-b' in sys.argv:
        IPython.embed()

def iprompt():
    import IPython
    if not '-b' in sys.argv:
        IPython.embed()

def setup_basic_root():
    ROOT.gROOT.Reset()
    ROOT.gStyle.SetScreenFactor(1)

    if not is_arg_set('--keep-stats'):
        ROOT.gStyle.SetOptStat(0)

    if not is_arg_set('--keep-title'):
        ROOT.gStyle.SetOptTitle(0)

    if not is_arg_set('--no-double-ticks'):
        ROOT.gStyle.SetPadTickY(1)
        ROOT.gStyle.SetPadTickX(1)

    #print ROOT.gStyle.GetErrorX()
    #ROOT.gStyle.SetErrorX(0) #not by default; use X1 to show the x-error with ol

    ROOT.gStyle.SetEndErrorSize(0)

    ROOT.gStyle.SetPalette(53)

    global app
    app = ROOT.PyROOT.TPyROOTApplication.CreateApplication()

exit_signal = False
print_first = False
timer = time.time()

def signal_handler(signum, frame):
    global sub_p
    global exit_signal
    global print_first
    global timer
    interval = time.time() - timer
    timer=time.time()
    if interval < 0.5:
        exit_signal = True
    else:
        exit_signal = False
    if interval > 60 or exit_signal==True or print_first==False:
        print
        if exit_signal==False:
            print '[i CRTL-C] signal #',signum,'caught; do it quickly twice to exit'
            if print_first==False:
                if sub_p!=None:
                    print '    the kid:',sub_p
            else:
                print '    interval:',interval,'s => exit condition:',exit_signal
        else:
            print '[i CRTL-C] interval:',interval,'s => exit condition:',exit_signal
        print_first=True

    if exit_signal==True:
        if sub_p!=None:
            sub_p.send_signal(signal.SIGKILL)
        sys.exit(0)

def clone(obj, *namemods):
    newname = '{}_clone_{}'.format(obj.GetName(), '-'.join([str(s) for s in namemods]) )
    newname = unique_name(newname)
    clone   = obj.Clone(newname)
    clone.SetDirectory(0)
    gList.append(clone)
    #print '[i] new clone:', newname
    return clone

def filter_single_entries(h, href=None, thr=10):
    if href == None:
        href = h
    for ib in range(1, h.GetNbinsX()+1):
        if href.GetBinContent(ib) < thr:
            h.SetBinContent(ib, 0)
            h.SetBinError(ib, 0)

def filter_single_entries_3d(h, href=None, thr=10):
    if href == None:
        href = h
    for ibx in range(1, h.GetNbinsX()+1):
        for iby in range(1, h.GetNbinsY()+1):
            for ibz in range(1, h.GetNbinsZ()+1):
                if href.GetBinContent(ibx, iby, ibz) < thr:
                    print ibx, iby, ibz
                    h.SetBinContent(ibx, iby, ibz, 0)
                    h.SetBinError(ibx, iby, ibz, 0)

def __h1d_from_ntuple(fname, ntname, var, cuts, bwidth, xlow, xhigh, title=None, modname='', nev=-1):
    nbins = int((xhigh-xlow)/bwidth*1.)
    if nbins < 1:
        return None
    hname = ut.build_string([fname, ntname, var, cuts, xlow, xhigh],'-')
    hname = hname.replace('/', '.')
    hname = hname.replace('*', 'x')
    hname = hname.replace('(', '.')
    hname = hname.replace(')', '.')
    if len(modname) > 0:
        hname = modname
    if title==None:
        htitle = ut.build_string([fname, var],' ')
    else:
        htitle = title
    hret = None
    try:
        fin = ROOT.TFile(fname)
        if fin:
            tn = fin.Get(ntname)
            if tn:
                hname_tmp = 'htmp({0},{1},{2})'.format(nbins, xlow, xhigh)
                dstr = '{0}>>{1}'.format(var, hname_tmp)
                if nev > 0:
                    dentries = tn.Draw(dstr, cuts, 'e', nev) #call sumw2 before the histogram creation!
                else:
                    dentries = tn.Draw(dstr, cuts, 'e') #call sumw2 before the histogram creation!
                hret = ROOT.gDirectory.Get('htmp')
                hret.SetDirectory(0)
            fin.Close()
        hret.SetName(hname)
        hret.SetTitle(htitle)
    except:
        print >> sys.stderr,'[e] draw from ntuple failed [{}:{}:{}]'.format(fname, ntname, var)
    return hret

def draw_h2d_from_ntuple(fname, ntname, var, cuts,
                         xbwidth, xlow, xhigh,
                         ybwidth, ylow, yhigh,
                         title=None, modname='', nev=-1):
    xnbins = int((xhigh-xlow)/xbwidth*1.)
    if xnbins < 1:
        return None
    ynbins = int((yhigh-ylow)/ybwidth*1.)
    if ynbins < 1:
        return None
    hname = ut.build_string([fname, ntname, var, cuts, xlow, xhigh, ylow, yhigh],'-')
    hname = hname.replace('/', '.')
    hname = hname.replace('*', 'x')
    hname = hname.replace('(', '.')
    hname = hname.replace(')', '.')
    if len(modname) > 0:
        hname = modname
    if title==None:
        htitle = ut.build_string([fname, var],' ')
    else:
        htitle = title
    hret = None
    fin = ROOT.TFile(fname)
    if fin:
        tn = fin.Get(ntname)
        if tn:
            hname_tmp = 'htmp({0},{1},{2},{3},{4},{5})'.format(xnbins, xlow, xhigh, ynbins, ylow, yhigh)
            dstr = '{0}>>{1}'.format(var, hname_tmp)
            if nev > 0:
                dentries = tn.Draw(dstr, cuts, 'e', nev)
            else:
                dentries = tn.Draw(dstr, cuts, 'e')
            hret = ROOT.gDirectory.Get('htmp')
            hret.SetDirectory(0)
        fin.Close()

        hret.SetName(hname)
        hret.SetTitle(htitle)
    return hret

def get_max_from_ntuple(fname, ntname, var, cuts = None):
    fin = ROOT.TFile(fname)
    if fin:
        tn = fin.Get(ntname)
        if tn:
            return tn.GetMaximum(var)
    print >> sys.stderr, '[e] unable to get maximum of',var,'from',fname,ntname
    return None

def get_mean_from_ntuple(fname, ntname, var, cuts = ''):
    fin = ROOT.TFile(fname)
    if fin:
        tn = fin.Get(ntname)
        if tn:
            print '*** var:',var
            #xmax = tn.GetMaximum(var)
            #xmin = tn.GetMinimum(var)
            #hname_tmp = 'htmp({0},{1},{2})'.format(100, xmin, xmax)
            hname_tmp = 'htmp'
            dstr = '{0}>>{1}'.format(var, hname_tmp)
            dentries = tn.Draw(dstr, cuts, 'e') #call sumw2 before the histogram creation!
            hret = ROOT.gDirectory.Get(hname_tmp)
            hret.SetDirectory(0)
            mean = hret.GetMean()
            hret.Reset()
            print '*** mean = ', mean
            return mean
    print >> sys.stderr, '[e] unable to get mean of',var,'from',fname,ntname
    return None

def get_object_from_file(hname = '', fname = '', new_title = '', nmod=None):
    if fname == None:
        return None
    name_mod = '_read'
    if nmod:
        name_mod = nmod
    cobj = None
    f = ROOT.TFile(fname)
    if f:
        h = f.Get(hname)
        if h:
            newname = h.GetName() + name_mod
            cobj = h.Clone(newname)
            cobj.SetDirectory(0)
            if len(new_title) > 0:
                cobj.SetTitle(new_title)
        f.Close()
    return cobj

def get_sum_of_bins(h):
    sum = 0.0
    for ib in range(1, h.GetNbinsX()+1):
        sum += h.GetBinContent(ib)
    return sum

def resample(hin, hout, n):
    if hout.GetSumw2N() == 0:
        hout.Sumw2()
    for i in range(0, int(n)):
        rndm = hin.GetRandom()
        hout.Fill(rndm)
    scale = (get_sum_of_bins(hin) / get_sum_of_bins(hout)) * (hin.GetBinWidth(1) / hout.GetBinWidth(1))
    hout.Scale(scale)

def resample_new(hin, hout, n):
    nsamples = 10
    if hout.GetSumw2N() == 0:
        hout.Sumw2()
    integral_in = get_sum_of_bins(hin) #hin.Integral()
    for ib in range(1, hin.GetNbinsX()):
        w = hin.GetBinContent(ib) / integral_in * 1.
        if w == 0:
            continue
        print 'bin=',ib,'w=',w
        bwidth = hin.GetBinWidth(ib)
        for i in range(0, int(nsamples)):
            v = hin.GetBinLowEdge(ib) + ROOT.gRandom.Rndm() * bwidth
            hout.Fill(v/nsamples/w)
    #scale = (get_sum_of_bins(hin) / get_sum_of_bins(hout)) * (hin.GetBinWidth(1) / hout.GetBinWidth(1))
    #hout.Scale(scale)

def resample_test(hin, hout, n, shift=0.0):
    if hout.GetSumw2N() == 0:
        hout.Sumw2()
    for i in range(0, int(n)):
        rndm = hin.GetRandom() + shift
        rndm_bin = hin.FindBin(rndm)
        bc = hin.GetBinContent(rndm_bin)
        hout.Fill(rndm, bc)
    hout.Scale(1./n)
    #scale = (get_sum_of_bins(hin) / get_sum_of_bins(hout)) * (hin.GetBinWidth(1) / hout.GetBinWidth(1))
    #hout.Scale(scale)

def shift_h(hin, delta=0.0):
    hout = hin.Clone(hin.GetName() + '-delta-{}'.format(delta))
    hout.Reset('M')
    for ib in range(1, hin.GetNbinsX() + 1):
        bc   = hin.GetBinCenter(ib) + delta
        bnew = hout.FindBin(bc)
        if bnew > 1 and bnew <= hin.GetNbinsX():
            val  = hin.GetBinContent(ib)
            vale = hin.GetBinError(ib)
            hout.SetBinContent(bnew, val)
            hout.SetBinError(bnew, vale)
    return hout

def resample_to_new(hin, ntimes, nb, minx, maxx, shift=0.0):
    hname = hin.GetName() + '-resampled'
    htitle = hin.GetTitle() + '-resampled'
    hout = ROOT.TH1D(hname, htitle, nb, minx, maxx)
    hout.Sumw2()
    resample(hin, hout, ntimes)
    #resample_new(hin, hout, ntimes)
    return hout

def next_weekday(d, weekday):
    # note: next is ok if this is the same day
    days_ahead = weekday - d.weekday()
    if days_ahead < 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def prev_weekday(d, weekday):
    # note: prev is ok if this is the same day
    days_ahead = weekday - d.weekday()
    return d + datetime.timedelta(days_ahead)

#d = datetime.date(2011, 7, 2)
#next_monday = next_weekday(d, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
#print(next_monday)

class DateHistogramRoot(object):
    def __init__(self, name, title):
        self.name     = name
        self.title    = title
        self.dates    = []
        self.datenums = []
        self.ticks    = []
        self.labels   = []
        self.values   = []
        self.cumuls   = []

        self.histogram = None
        self.hcumulant = None

    def date2num(self, d):
        dt =  ROOT.TDatime(d.year, d.month, d.day, 0, 0, 0)
        try:
            dt = ROOT.TDatime(d.year, d.month, d.day,
                            d.hour, d.minute, d.second)
        except:
            pass
        return dt.Convert()

    def fill(self, date, val):
        idx = None
        try:
            idx = self.dates.index(date)
            self.values[idx] += val
        except:
            self.values.append(val)
            self.dates.append(date)
            self.datenums.append(self.date2num(date))

    def cumulate(self):
        c = 0
        self.cumuls = []
        for v in self.values:
            c += v
            self.cumuls.append(c)

    def makeGraph(self, cumulant = False):
        npoints = len(self.values)
        x = array.array('f', self.datenums)
        if cumulant == False:
            y = array.array('f', self.values)
        else:
            self.cumulate()
            y = array.array('f', self.cumuls)

        gr = ROOT.TGraph(npoints, x, y)
        gr.SetMarkerStyle(20)

        gr.GetXaxis().SetTimeDisplay(1)
        gr.GetXaxis().SetNdivisions(-503)
        #gr.GetXaxis().SetTimeFormat("%Y-%m-%d %H:%M")
        gr.GetXaxis().SetTimeFormat("%Y-%m-%d")
        gr.GetXaxis().SetTimeOffset(0,"gmt")

        #gr.GetYaxis().SetTitle(what)
        gr_name = 'gr-{0}-cumul:{1}'.format(self.name, str(cumulant))
        gr.SetName(gr_name)
        gr_title = '{0} cumul:{1}'.format(self.title, str(cumulant))
        gr.SetTitle(gr_title)
        return gr

    def _fix_h(self, h):
        if h == None:
            return
        #h.GetXaxis().SetLabelSize(0.06);
        h.GetXaxis().SetTimeDisplay(1);
        h.GetXaxis().SetTimeFormat("%Y-%m-%d")
        h.GetXaxis().SetTimeOffset(0,"gmt")
        #h->GetXaxis()->SetTimeFormat("%d\/%m\/%y%F2000-02-28 13:00:01");


    def get_histogram(self, cumulant = False, binned = 1):
        #npoints = len(self.values)
        #xmin    = self.values[0]
        #xmax    = self.values[len(self.values)-1]

        d1           = self.dates[0] + datetime.timedelta(days=-7)
        firstMonday  = prev_weekday(d1, 0) # 0 is Monday
        xmin         = self.date2num(firstMonday)
        d2           = self.dates[len(self.dates)-1]
        lastSunday   = next_weekday(d2, 6) # 6 is Sunday
        xmax         = self.date2num(lastSunday)
        interval     = self.date2num(firstMonday + datetime.timedelta(binned)) - self.date2num(firstMonday)
        npoints      = (xmax - xmin) / interval # daily/weekly? n-days
        #print npoints

        if self.histogram == None:
            hname = 'h_{}'.format(self.name)
            htitle = 'h_{}'.format(self.title)
            self.histogram = ROOT.TH1F(hname, htitle, npoints, xmin, xmax)
            self.histogram.SetDirectory(0)
            for x in self.datenums:
                i = self.datenums.index(x)
                v = self.values[i]
                self.histogram.Fill(x, v)

        if cumulant == True:
            hname = 'hcumul_{}'.format(self.name)
            htitle = 'hcumul_{}'.format(self.title)
            self.hcumulant = ROOT.TH1F(hname, htitle, npoints, xmin, xmax)
            self.hcumulant.SetDirectory(0)
            for ib in range(1, npoints+1):
                newval = htmp.Integral(1, ib)
                hcumulant.SetBinContent(ib, newval)
                hcumulant.SetBinError(ib, ROOT.TMath.Sqrt(newval))

        self._fix_h(self.hcumulant)
        self._fix_h(self.histogram)

        if cumulant == True:
            return self.hcumulant

        return self.histogram

def graph_from_h(h, xdelta):
    if not h.InheritsFrom('TH1'):
        return None
    gr = ROOT.TGraphErrors(h.GetNbinsX())
    for ib in xrange(1, h.GetNbinsX() + 1):
        x = h.GetBinCenter(ib) + xdelta
        y = h.GetBinContent(ib)
        ex = h.GetBinWidth(ib)/2.
        ey = h.GetBinError(ib)
        gr.SetPoint(ib-1, x, y)
        gr.SetPointError(ib-1, ex, ey)
    gr.SetName(h.GetName())
    gr.SetTitle(h.GetTitle())
    return gr

def shift_graph(gr, xdelta):
    npoints = gr.GetN()
    for i in range(0, npoints):
        xgr = gr.GetX()[i]
        gr.GetX()[i] = xgr + xdelta
        #gr.SetPoint(i, xgr + xdelta, gr.GetY()[i])
        #print i, xgr,'->',xgr + xdelta

gTempCanvas = None
def getTempCanvas():
    global gTempCanvas
    if gTempCanvas == None:
        gTempCanvas = ROOT.TCanvas('tc_temp_canvas', 'tc_temp_canvas')
    return gTempCanvas

def tchain_from_dir(tname, dname, pattern='*.root'):
    ch = ROOT.TChain(tname)
    flist = ut.find_files(dname, pattern)
    for fn in flist:
        ch.AddFile(fn)
    print '[i] tchain_from_dir: Nfiles:',ch.GetNtrees()
    return ch

gLibsLoaded = False
def rinterp(cline):
    global gLibsLoaded
    if gLibsLoaded == False:
        sdir = os.path.join(os.getenv('ROOTSYS'), 'lib')
        print >> sys.stderr, '[add ld path]', sdir
        ROOT.gSystem.AddDynamicPath(sdir)
        #slibs = ut.find_files(sdir, '*.so')
        slibs = ['libGui']
        for sil in slibs:
            iload = ROOT.gSystem.Load(sil)
            print >> sys.stderr, '[load]', sil, iload
        gLibsLoaded = True
    return ROOT.gInterpreter.ProcessLine(cline)
