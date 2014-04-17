#!/usr/bin/env python

import os
import sys
import tutils
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

import ol

def run():
    ROOT.gROOT.Reset()
        
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    pattern = tutils.get_arg_with('--pattern')
        
    f = tutils.get_arg_with('-f')
    if f:
        l = ol.load_file(f, pattern)
        print "[i] File:",f
        table = []
        table.append(['', 'Class', 'Name', 'Title', 'GetEntries', 'Integral'])
        for o in l.l:
            oname = o.GetName()
            oname = oname.replace(f.replace("/", "_"), "").replace("_--hlist", "")            
            try:
                table.append(['', o.IsA().GetName(), oname, o.GetTitle(), o.GetEntries(), o.Integral()])
            except:
                table.append(['', o.IsA().GetName(), oname, o.GetTitle()])
        txtable.print_table(table, ' | ')
        #tutils.wait()
    else:
        print >> sys.stderr,'[e] no file specified: use -f <file.root>'
        print_usage()

def main():
    run()
        
if __name__=="__main__":
    main()
