#!/usr/bin/env python -i

import sys
import tutils
import ol
import ROOT as r
from array import array
import draw_utils as du
import math

def main():
    tutils.setup_basic_root()

    hl = ol.ol('test-plot')

    sigma = 0.1

    nstat = 1000
    npx = 50
    
    signalF = r.TF1("signalF","landau(0)",-1,1);
    signalF.SetParameters(1.0, -0.2, sigma)
    signalF.SetNpx(npx)
    
    bgF = r.TF1("bgF","gaus",-1,1);
    bgF.SetParameters(0.1, -0.2, 0.8);
    bgF.SetNpx(npx)
    
    sbgF = r.TF1("sbgF","landau(0) + gaus(3)",-1,1);
    sbgF.SetParameters(1.0, -0.2, sigma,
                       0.1, -0.2, 0.8);
    sbgF.SetNpx(npx)
    
    hsignal = r.TH1F('hsignal', 'hsignal;x-axis (arb. unit);y-axis (arb. unit)', npx, -1, 1);
    hsignal.FillRandom(signalF.GetHistogram(), nstat);

    hbg = r.TH1F('hbg', 'hbg;x-axis (arb. unit);y-axis (arb. unit)', npx, -1, 1);
    hbg.FillRandom(bgF.GetHistogram(), nstat);
        
    hsbg = r.TH1F('hsbg', 'hsbg;x-axis (arb. unit);y-axis (arb. unit)', npx, -1, 1);
    #hsbg.FillRandom(sbgF.GetHistogram(), nstat);
    hsbg.Add(hsignal)
    hsbg.Add(hbg)

    ol.gDebug = True
    
    hl.addh(hsignal, 'Signal', 'P E0 +l1 nlil') #+l1 forces line style #1; nlil <-> no line in legend
    hl.addh(hsbg, 'Signal + Background', 'P E0 +l1 nlil')
    hl.addh(hbg, 'Background', 'P E0 +l1 nlil')        
    hl.last().Fit(bgF, 'RMNQ')
    hf = bgF.GetHistogram()    
    hl.add(hf, 'Fit to Background', 'HIST L +l1') #one can also add the TF1's directly
    hsyst = hsignal.Clone('hsyst')
    ol.scale_errors(hsyst, 0.7)
    hl.addh(hsyst, 'syst error', 'sError +a0.50 +k32')
    # sError indicates that this is a syst error - not to show in legend and set some default styles
    # +a0.50 sets the alpha for transparency;
    # +k32 sets the color number to 32
    
    hl.make_canvas(400, 400)    
    #hl.scale(1/nstat)
    hl.draw()
        
    hl.self_legend(1, '', 0.56,0.64,0.85,0.92)
    
    if '--print' in sys.argv:
        hl.tcanvas.Print(hl.name+'.pdf', 'pdf')
        
    hl.write_to_file('test_plot.root') # try the "$draw_file.py -f test_plot.root" to see default draw...
    
    tutils.gList.append(hl)
    
    tutils.wait()
    
if __name__=="__main__":
    main()
    
