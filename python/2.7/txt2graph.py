#!/usr/bin/env python -i

import ROOT as r 
import tutils as tu
import numpy as np
from StringIO import StringIO
import dlist
import sys
import pyutils as ut

def read_data(fn = None):
    f = sys.stdin
    if fn != None:
        f = open(fn)
    lines = f.read()
    if f != sys.stdin:
        f.close()
    d = StringIO(lines)
    retvals = np.genfromtxt(d, comments='#', autostrip=True)
    return retvals

def make_graph_from_file(fn = None, xye = [0, 1, 2, 3]):
    d = read_data(fn)
    x  = d[:,xye[0]]
    y  = d[:,xye[1]]
    try:
        xe = d[:,xye[2]]
    except:
        xe = []
    try:
        ye = d[:,xye[3]]
    except:
        ye = []
    grname = 'graph'
    gr = dlist.make_graph_xy(grname,x,y,xe=xe,ye=ye)
    return gr

def make_graph_from_hepfile(fn = None, xye = [0,1,2,3,4,5], xe=None):
    d     = read_data(fn)
    x     = d[:,xye[0]]
    y     = d[:,xye[1]]
    xlow  = []
    xhigh = []
    dyem  = []    
    dyep  = []    

    if xye[2] >= 0:
        try:
            xlow  = d[:,xye[2]]
        except:
            xlow  = []
    if xye[3] >= 0:
        try:
            xhigh = d[:,xye[3]]
        except:
            xhigh = []
    if xye[4] >= 0:
        try:
            dyem = d[:,xye[4]]
        except:
            dyem = []    
    if xye[5] >= 0:
        try:
            dyep = d[:,xye[5]]
        except:
            dyep = []    
    name = 'graph_hepfile_' + str(xye)
    if len(xlow) > 0:
        for i,ix in enumerate(xlow):
            v = x[i] - ix
            if xe != None:
                v = xe
            xlow[i] = v
    if len(xhigh) > 0:
        for i,ix in enumerate(xhigh):
            v = ix - x[i]
            if xe != None:
                v = xe
            xhigh[i] = v
    if len(dyem) > 0:
        for i, ix in enumerate(dyem):
            v = dyem[i]
            dyem[i] = abs(v)
    if len(dyep) > 0:
        for i, ix in enumerate(dyep):
            v = dyep[i]
            dyep[i] = abs(v)
    print name
    print ' - ',x, y
    print ' - ',xlow, xhigh
    print ' - ',dyem, dyep
    gr = dlist.make_graph_ae_xy(name, x, y, xlow, xhigh, dyem, dyep)
    return gr

def graph(fname):    
    if fname == None:
        hlname = 'stdin'
    else:
        hlname = fname
    hl = dlist.dlist(hlname)
    xye  = [0, 1, 2, 3]
    sxye = ut.get_arg_with('--xye')
    if sxye != None:
        sa = sxye.split(',')
        for i,s in enumerate(sa):
            xye[i] = int(s)            
    gr = make_graph_from_file(fname, xye)
    stitle = ut.get_arg_with('--title')
    if stitle == None:
        stitle = hlname
    hl.add(gr, stitle, 'P')
    hl.make_canvas()
    logy = ut.is_arg_set('--logy')
    hl.draw(logy=logy)
    hl.self_legend()
    if logy:
        r.gPad.SetLogy()
    xlabel = ut.get_arg_with('-x')
    ylabel = ut.get_arg_with('-y')
    hl.reset_axis_titles(xlabel,ylabel)
    hl.update()    
    if ut.is_arg_set('--print'):
        hl.tcanvas.Print()
    
    tu.gList.append(hl)

    hl.write_to_file(hl.name+'.root')
    
    return gr

if __name__=="__main__":
    tu.setup_basic_root()
    if ut.is_arg_set('--debug'):
        dlist.gDebug = True    
    fname = ut.get_arg_with('-f')
    graph(fname)
    tu.wait()
