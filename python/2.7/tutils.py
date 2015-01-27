import sys
import subprocess
import shlex
import signal
import time
import pyutils as ut
import datetime
import array
import ROOT

sub_p = None
exit_signal = False
print_first = False
timer = time.time()

gList = []
app = None

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
        print '[i]', __name__,'::wait() has no effect. This is interactive mode.'
    else:
        print '[i] press twice CRTL+C (fast consequtive) to exit.'
        signal.signal(signal.SIGINT, signal_handler)
        while 1:
            time.sleep(10) # this actually does not matter as long as large
            pass

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
    ROOT.gStyle.SetErrorX(0)

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

def draw_h1d_from_ntuple(fname, ntname, var, cuts, bwidth, xlow, xhigh, title=None):
    nbins = int((xhigh-xlow)/bwidth*1.)
    if nbins < 1:
        return None
    hname = ut.build_string([fname, ntname, var, cuts, xlow, xhigh],'-')
    hname = hname.replace('/', '.')
    hname = hname.replace('*', 'x')
    hname = hname.replace('(', '.')
    hname = hname.replace(')', '.')
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
                dentries = tn.Draw(dstr, cuts)
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
                         title=None):
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
            dentries = tn.Draw(dstr, cuts)
            hret = ROOT.gDirectory.Get('htmp')
            hret.SetDirectory(0)
        fin.Close()
        
        hret.SetName(hname)
        hret.SetTitle(htitle)
    return hret

def get_object_from_file(hname = '', fname = '', new_title = ''):
    if fname == None:
        return None
    cobj = None
    f = ROOT.TFile(fname)
    if f:
        h = f.Get(hname)
        if h:
            newname = h.GetName() + '-read'
            cobj = h.Clone(newname)
            cobj.SetDirectory(0)
            if len(new_title) > 0:
                cobj.SetTitle(new_title)
        f.Close()
    return cobj

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
