#!/usr/bin/env python

import ol
import sys
import tutils as tu
import pyutils as ut
import ROOT

def main():
    tu.setup_basic_root()
    fnames  = ut.get_arg_with('-f')
    hnames  = ut.get_arg_with('-n')
    htitles = ut.get_arg_with('-t')
    xmins   = ut.get_arg_with('-xmin')
    xmaxs   = ut.get_arg_with('-xmax')
    steps   = ut.get_arg_with('-d')
    dopts   = ut.get_arg_with('-dopt')
    outfs   = ut.get_arg_with('-out')

    if htitles == None:
        htitles = hnames
    
    xmin = float(xmins)
    xmax = float(xmaxs)
    step = float(steps)

    pTs   = []

    try:
        hl = ol.get_projections(hnames, fnames, htitles, xmin, xmax, step, dopts, pTs)
        print '[i] number of projections:',len(hl.l)
    except:
        print >> sys.stderr, '[e] unable to project'
    try:
        hl.write_to_file(outfs)
    except:
        pass
    
    if '--wait' in sys.argv:
        if '--logy' in sys.argv:
            logy = True
        hl.draw('', None, None, logy)
        if logy:
            ROOT.gPad.SetLogy()
        hl.self_legend()
    
        tu.wait()

if __name__=="__main__":
    main()
