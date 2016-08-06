#!/usr/bin/env python

import os
import sys
import tutils
import pyutils as ut
import txtable

def print_usage():
    print '[i] usage:',os.path.basename(sys.argv[0]),'-f <file.root> [--pattern <something in the name>] '
    
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

import dlist as ol

def dump_graph(gr):
    print '[i] dumping TGraph numbers of',gr.GetName(),gr.GetTitle()
    for i in xrange(gr.GetN()):
        l = []
        l.append(i)
        l.append(gr.GetX()[i])
        l.append(gr.GetY()[i])
        try:
            l.append(gr.GetEX()[i])
            l.append(gr.GetEY()[i])
        except:
            pass
        try:
            l.append(gr.GetEXlow()[i])
            l.append(gr.GetEXhigh()[i])
            l.append(gr.GetEYlow()[i])
            l.append(gr.GetEYhigh()[i])
        except:
            pass
        print ' '.join([str(s) for s in l])
        #txtable.print_table(['{}'.format(num) for num in l], ' | ')

def dump_histogram(h):
    print '[i] dumping TH1 numbers of',h.GetName(),h.GetTitle()
    for ix in xrange(1, h.GetNbinsX()+1):
        l = []
        l.append(ix)
        l.append(h.GetBinCenter(ix))
        l.append(h.GetBinLowEdge(ix))
        l.append(h.GetBinLowEdge(ix) + h.GetBinWidth(ix))
        l.append(h.GetBinContent(ix))
        l.append(h.GetBinError(ix))
        print ' '.join([str(s) for s in l])

def dump_text(o):
    if o.InheritsFrom('TGraph'):
        dump_graph(o)
    if o.InheritsFrom('TH1'):
        dump_histogram(o)

def run():
    ROOT.gROOT.Reset()
        
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    pattern = tutils.get_arg_with('--pattern')
        
    f = tutils.get_arg_with('-f')
    if not f:
        try:
            f = sys.argv[1]
        except:
            f = None
    if f:
        l = ol.load_file(f, pattern)
        print "[i] File:",f
        table = []
        table.append(['', 'Class', 'Name', 'Title', 'GetEntries', 'Integral'])
        for obj in l.l:
            o = obj.obj
            oname = o.GetName()
            oname = oname.replace(f.replace("/", "_"), "").replace("_--hlist", "")            
            try:
                table.append(['', o.IsA().GetName(), oname, o.GetTitle(), o.GetEntries(), o.Integral()])
            except:
                table.append(['', o.IsA().GetName(), oname, o.GetTitle()])
        txtable.print_table(table, ' | ')
        if '--dump' in sys.argv:
            for obj in l.l:
                o = obj.obj
                sselect = ut.get_arg_with('--dump')
                if sselect.lower() == 'all':
                    dump_text(o)
                else:
                    if sselect == o.GetName():
                        dump_text(o)
        #tutils.wait()
    else:
        print >> sys.stderr,'[e] no file specified: use -f <file.root>'
        print_usage()

def main():
    run()
        
if __name__=="__main__":
    main()
