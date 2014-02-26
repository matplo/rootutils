import sys
import subprocess
import shlex
import signal
import time
import pyutils as ut

sub_p = None
exit_signal = False
print_first = False
timer = time.time()

gList = []

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
    print '[i] press twice CRTL+C (fast consequtive) to exit.'
    signal.signal(signal.SIGINT, signal_handler)
    while 1:
        time.sleep(10) # this actually does not matter as long as large
        pass

def setup_basic_root():
    import ROOT
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
    import ROOT
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
    import ROOT
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
    import ROOT
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
