#!/usr/bin/env python

import ROOT
import argparse
import os
import sys

def call_draw_1dim(t, b, fout):
  fout.cd()
  hname = t.GetName() + '_' + b.GetName()
  t.Draw(f'{b.GetName()}>>{hname}', '', 'goff')
  h = ROOT.gDirectory.Get(hname)
  if not h or not h.InheritsFrom(ROOT.TH1.Class()):
    print("Error: Retrieved object is not a histogram.", h, hname)
    sys.exit(1)
  fout.cd()
  h.SetTitle(f'{t.GetName()}_{b.GetName()};b.GetName();Entries')
  h.Write()

def call_draw_2dim(t, b1, b2, fout):
  fout.cd()
  hname = t.GetName() + '_' + b1.GetName() + '_' + b2.GetName()
  t.Draw(f'{b2.GetName()}:{b1.GetName()}>>{hname}', '', 'goff')
  h = ROOT.gDirectory.Get(hname)
  if not h or not h.InheritsFrom(ROOT.TH2.Class()):
    print("Error: Retrieved object is not a histogram.", h, hname)
    sys.exit(1)
  fout.cd()
  h.SetTitle(f'{t.GetName()}_{b1.GetName()}_{b2.GetName()};{b1.GetName()};{b2.GetName()};Entries')
  h.Write()

def main():
  parser = argparse.ArgumentParser(description='Plot the number of events in a given file')
  parser.add_argument('input', help='Input file')
  parser.add_argument('--output', help='Output file', default='')
 
  args = parser.parse_args()
  if args.output == '':
    args.output = os.path.splitext(args.input)[0] + '_h.root'
  
  fout = ROOT.TFile(args.output, 'recreate')
  
  f = ROOT.TFile(args.input)
  td = f.GetListOfKeys()
  print('[i] reading from file', f.GetName())
  for k in td:
    if k.ReadObj().InheritsFrom('TTree'):
      t = k.ReadObj()
      print('    number of entries in', t.GetName(), ':', t.GetEntries())
      # for each member of the tree project it to a histogram and save it to the output file
      for b in t.GetListOfBranches():
        call_draw_1dim(t, b, fout)
      for b1 in t.GetListOfBranches():
        for b2 in t.GetListOfBranches():
          if b1 == b2:
            continue
          call_draw_2dim(t, b1, b2, fout)
  f.Close()
  fout.Close()
  print('[i] written to file', fout.GetName())
  
if __name__ == "__main__":
  main()