#!/usr/bin/env python -i

import os
import sys
import tutils

def print_usage():
    print '[i] usage:',os.path.basename(sys.argv[0]),'-f <file.root> [--keep-stats] [--keep-title] [--logy] [--pattern <something in the name>] [--dopt <draw option>] [--x <min:max>] [--titles]'
    
if __name__=="__main__":
    if tutils.is_arg_set('--help') or tutils.is_arg_set('-h') or tutils.is_arg_set('-?') or tutils.is_arg_set('-help'):
        print_usage()
        sys.exit(0)
#
# here & below the ROOT stuff
#

try:
    import ROOT
except:
    print >> sys.stderr,'[error:] failed to load ROOT'
    print '[ info:] setup the environment (remember PYTHONPATH)'
    sys.exit(-1)

import ol

def run():
    ROOT.gROOT.Reset()
    ROOT.gStyle.SetScreenFactor(1)

    if not tutils.is_arg_set('--keep-stats'):
        ROOT.gStyle.SetOptStat(0)

    if not tutils.is_arg_set('--keep-title'):
        ROOT.gStyle.SetOptTitle(0)
        
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    names_not_titles = True
    if tutils.is_arg_set('--titles'):
        names_not_titles = False

    pattern = tutils.get_arg_with('--pattern')
    draw_opt = tutils.get_arg_with('--dopt')
    if draw_opt == None:
        draw_opt = 'lpf'

    xmin = None
    xmax = None
    xaxis = tutils.get_arg_with('--x')
    if xaxis:
        xmin = float(xaxis.split(':')[0])
        xmax = float(xaxis.split(':')[1])
        
    f = tutils.get_arg_with('-f')
    if f:
        #ol.gDebug = True
        l = ol.show_file(f, tutils.is_arg_set('--logy'), pattern, draw_opt, names_not_titles, xmin, xmax)
        tutils.wait()
    else:
        print >> sys.stderr,'[e] no file specified: use -f <file.root>'
        print_usage()

def main():
    run()
        
if __name__=="__main__":
    main()
