#!/usr/bin/env python -i

import tutils
import ROOT as r
def main():

    tutils.setup_basic_root()

    h = r.TH1D('test', 'test', 10, 0, 1)
    h.Fill(.2)
    h.Fill(.5)
    h.Fill(.4,3.145)        
    h.Draw()
    r.gPad.Update()    
    tutils.gList.append(h)
    tutils.wait()
    
if __name__=="__main__":
    main()
