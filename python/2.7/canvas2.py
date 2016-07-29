#!/usr/bin/env python

import ROOT as r
import IPython
import tutils as tu

# based on $ROOTSYS/tutorials/graphics/canvas2.C

class CanvasSplit(object):
   def __init__(self, name, nx, ny, title=None, w=600, h=400):
      self.name = name
      self.title = title
      if self.title == None:
         self.title = self.name
      self.tc = r.TCanvas(self.name, self.name, w, h)
      self.Nx = nx
      self.Ny = ny

      self.lMargin = 0.08 # was 0.12
      self.rMargin = 0.05
      self.bMargin = 0.12 # was 0.15
      self.tMargin = 0.05

      self.pads = []

      self.htest = None

      self.xFactor = 1.0
      self.yFactor = 1.0

      self.setup()
      self.test()

   def cd(self, i):
      if len(self.pads) > 0:
         self.pads[i].cd()
      else:
         self.tc.cd()
      self.xFactor = self.pads[0].GetAbsWNDC()/r.gPad.GetAbsWNDC()
      self.yFactor = self.pads[0].GetAbsHNDC()/r.gPad.GetAbsHNDC()

   def setup(self):
      # Setup Pad layout:
      self.vSpacing = 0.0
      self.vStep  = (1.- self.bMargin - self.tMargin - (self.Ny-1) * self.vSpacing) / self.Ny

      self.hSpacing = 0.0
      self.hStep  = (1.- self.lMargin - self.rMargin - (self.Nx-1) * self.hSpacing) / self.Nx

      #vposd,vposu,vmard,vmaru,vfactor
      #hposl,hposr,hmarl,hmarr,hfactor

      for i in xrange(self.Nx):
         if i==0:
            hposl = 0.0
            hposr = self.lMargin + self.hStep
            hfactor = hposr-hposl
            hmarl = self.lMargin / hfactor
            hmarr = 0.0
         else:
            if i == self.Nx-1:
               hposl = hposr + self.hSpacing
               hposr = hposl + self.hStep + self.rMargin
               hfactor = hposr-hposl
               hmarl = 0.0
               hmarr = self.rMargin / (hposr-hposl)
            else:
               hposl = hposr + self.hSpacing
               hposr = hposl + self.hStep
               hfactor = hposr-hposl
               hmarl = 0.0
               hmarr = 0.0

         for j in xrange(self.Ny):
            if j==0:
               vposd = 0.0
               vposu = self.bMargin + self.vStep
               vfactor = vposu-vposd
               vmard = self.bMargin / vfactor
               vmaru = 0.0
            else:
               if j == self.Ny-1:
                  vposd = vposu + self.vSpacing
                  vposu = vposd + self.vStep + self.tMargin
                  vfactor = vposu-vposd
                  vmard = 0.0
                  vmaru = self.tMargin / (vposu-vposd)
               else:
                  vposd = vposu + self.vSpacing
                  vposu = vposd + self.vStep
                  vfactor = vposu-vposd
                  vmard = 0.0
                  vmaru = 0.0

            self.tc.cd(0)
            name = 'pad_{}_{}'.format(i,j)
            #pad = r.gROOT.FindObject(name)
            pad = r.TPad(name,name,hposl,vposd,hposr,vposu)
            print '[i] creating a pad',name
            pad.SetLeftMargin(hmarl)
            pad.SetRightMargin(hmarr)
            pad.SetBottomMargin(vmard)
            pad.SetTopMargin(vmaru)

            pad.SetFrameBorderMode(0)
            pad.SetBorderMode(0)
            pad.SetBorderSize(0)

            pad.Draw()

            self.pads.append(pad)
            print '[i] pad setup done',name

   def test(self):
      pass

   def get_axis_factor(self, i):
      try:
         self.xFactor = self.pads[0].GetAbsWNDC()/r.gPad.GetAbsWNDC()
         self.yFactor = self.pads[0].GetAbsHNDC()/r.gPad.GetAbsHNDC()
         if i == 0:
            lfactor = self.yFactor * 0.06 / self.xFactor
         else:
            lfactor = self.xFactor * 0.04 / self.yFactor
      except:
         lfactor = 1.0
      return lfactor

   def adjust_axis(self, lh, scaleTSize = 1.0, scaleLSize = 1.0):
      for h in lh:
         try:
            h = h.obj
         except:
            pass
         for i in xrange(2):
            if i == 0:
               axis = h.GetXaxis()
               lfactor = self.yFactor * 0.06 / self.xFactor
               title_offset = 2 * scaleTSize
               tsize = 16
            else:
               axis = h.GetYaxis()
               lfactor = self.xFactor * 0.04 / self.yFactor
               title_offset = 2 * scaleTSize
               tsize = 18
            axis.SetTickLength(lfactor)
            axis.SetLabelFont(43)
            axis.SetLabelSize(14 * scaleLSize)
            axis.SetLabelOffset(0.03 * scaleLSize / 2.)
            axis.SetTitleFont(43)
            axis.SetTitleSize(tsize * scaleTSize)
            axis.SetTitleOffset(title_offset)

   def test_h_draw(self, i = 0):
      print 'drawing...'
      if self.htest == None:
         self.htest = r.TH1F('hx', 'hx;x;y', 10, 0, 10)
         self.htest.FillRandom('gaus')
      self.cd(i)
      self.htest.SetTitle(r.gPad.GetName())
      self.adjust_axis([self.htest])
      self.htest.DrawCopy()

def main():
   c = CanvasSplit('test', 3, 2)
   for i in xrange(6):
      c.test_h_draw(i)
   tu.gList.append(c)

if __name__ == '__main__':
   main()
   IPython.embed()
