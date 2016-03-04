#!/usr/bin/env python

import tutils
import ROOT as r
import IPython

def main():

    tutils.setup_basic_root()

    h = r.TH1D('test', 'test', 10, 0, 1)
    h.Fill(.2)
    h.Fill(.5)
    h.Fill(.4,3.145)        
    h.Draw()
    r.gPad.Update()    
    tutils.gList.append(h)
    
if __name__=="__main__":
    main()
    if not tutils.is_arg_set('-b'):
        IPython.embed()
