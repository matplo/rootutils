import pyutils as ut
import dlist
import sys
import ROOT

def filter_single_entries(h, href=None, thr=10):
    if href == None:
        href = h
    for ib in range(1, h.GetNbinsX()+1):
        if href.GetBinContent(ib) < thr:
            h.SetBinContent(ib, 0)
            h.SetBinError(ib, 0)

def h1d_from_ntuple(fname, ntname, var, cuts, bwidth, xlow, xhigh, title=None, modname='', nev=-1):
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
            else:
                print '[e] no ntuple:',ntname
            fin.Close()
        else:
            print '[e] no root file:',fname
        hret.SetName(hname)
        hret.SetTitle(htitle)
    except:
        print >> sys.stderr,'[e] draw from ntuple failed [{}:{}:{}]'.format(fname, ntname, var)
    return hret

def h1d_from_ntuple_flist(flist, ntname, var, cuts, bwidth, xlow, xhigh, title='h', modname='', nev=-1):
    hltitle = ' '.join([title, ntname, var, cuts])
    hltitle = ut.to_file_name(hltitle)
    hl = dlist.dlist(hltitle)
    for i,fname in enumerate(flist):
        htitle = title + '_{}'.format(i)
        h = h1d_from_ntuple(fname, ntname, var, cuts, bwidth, xlow, xhigh, htitle, modname, nev)
        hl.add(h, htitle, 'hist')
    return hl

def h1d_from_ntuple_dir(cdir, ntname, var, cuts, bwidth, xlow, xhigh, title='h', modname='', nev=-1):
    flist = ut.find_files(cdir, '*.root')
    return h1d_from_ntuple_flist(flist, ntname, var, cuts, bwidth, xlow, xhigh, title, modname, nev)

def h1d_from_ntuple_dir_filter(cdir, ntname, var, cuts, bwidth, xlow, xhigh, title='h', modname='', nev=-1, refcuts=None, thr=100):
    hl      = h1d_from_ntuple_dir(cdir, ntname, var,    cuts, bwidth, xlow, xhigh, title, modname, nev)
    hlref   = h1d_from_ntuple_dir(cdir, ntname, var, refcuts, bwidth, xlow, xhigh, title, modname, nev)
    lstore  = dlist.ListStorage(hl.name)
    hlret    = dlist.dlist(hl.name + '_filtered')
    hlretref = dlist.dlist(hl.name + '_filtered_ref')
    hlretref.copy(hlref)
    for i,o in enumerate(hl.l):
        h     = o.obj
        href  = hlref[i].obj
        hrefc = hlretref[i].obj
        filter_single_entries(h, href, thr)
        hlret.add(h, h.GetTitle(), 'hist')
        filter_single_entries(hrefc, href, thr)
    hl.add(hl.sum(), 'sum', 'hist', prep=True)
    hlref.add(hlref.sum(), 'sum', 'hist', prep=True)
    hlret.add(hlret.sum(), 'sum', 'hist', prep=True)
    hlretref.add(hlretref.sum(), 'sum', 'hist', prep=True)
    hl.reset_axis_titles(var, cuts)
    hlref.reset_axis_titles(var, refcuts)
    hlret.reset_axis_titles(var, cuts)
    hlretref.reset_axis_titles(var, refcuts)
    lstore.append(hl)
    lstore.append(hlref)
    lstore.append(hlret)
    lstore.append(hlretref)
    lstore.draw_all(logy=True)
    return hlret

