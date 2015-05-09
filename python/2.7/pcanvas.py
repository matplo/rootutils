import ROOT
import math

class pcanvas(object):
	def __init__(self, tc, n, lm = 0.15, rm = 0.05, bm = 0.15, tm = 0.05):
		self.tc = tc
		self.nx = 0
		self.ny = 0
		self.n  = n
		self.pads = []
		self.set_nx_ny(self.n)
		self.partition(self.nx, self.ny, lm, rm, bm, tm)

	def cd(self, i):
		return self.pads[i-1].cd()

	def pad(self, i):
		return self.pads[i].cd()

	def set_nx_ny(self, n):
		nv = float(n)
		ir = int(math.sqrt(nv))
		ic = int(math.sqrt(nv))
		while (ir * ic) < n:
			ir = ir + 1
			if (ir * ic) < n:        
				ic = ic + 1
		self.nx = ir
		self.ny = ic
		print self.ny, self.nx

	def partition(self, Nx = 2, Ny = 2,
					lMargin = 0.15, rMargin = 0.05,
					bMargin = 0.15, tMargin = 0.05):
		# Setup Pad layout:
		vSpacing = 0.0;
		vStep  = (1.- bMargin - tMargin - (Ny-1) * vSpacing) / Ny;
		hSpacing = 0.0;
		hStep  = (1.- lMargin - rMargin - (Nx-1) * hSpacing) / Nx;

		print Nx, Ny

		for i in range(Nx):
			if i==0:
				hposl = 0.0
				hposr = lMargin + hStep
				hfactor = hposr-hposl
				hmarl = lMargin / hfactor
				hmarr = 0.0
			elif i == Nx-1:
				hposl = hposr + hSpacing
				hposr = hposl + hStep + rMargin
				hfactor = hposr-hposl
				hmarl = 0.0
				hmarr = rMargin / (hposr-hposl)
			else:
				hposl = hposr + hSpacing
				hposr = hposl + hStep
				hfactor = hposr-hposl
				hmarl = 0.0
				hmarr = 0.0

			for j in range(Ny):
				if j == 0:
					vposd = 0.0;
					vposu = bMargin + vStep
					vfactor = vposu-vposd
					vmard = bMargin / vfactor
					vmaru = 0.0
				elif j == Ny-1:
					vposd = vposu + vSpacing
					vposu = vposd + vStep + tMargin
					vfactor = vposu-vposd
					vmard = 0.0;
					vmaru = tMargin / (vposu-vposd)
				else:
					vposd = vposu + vSpacing
					vposu = vposd + vStep
					vfactor = vposu-vposd
					vmard = 0.0
					vmaru = 0.0

				self.tc.cd(0)
				name = '{}_pad_{}_{}'.format(self.tc.GetName(), i, j)
				pad = ROOT.TPad(name,"",hposl,vposd,hposr,vposu);
				pad.SetLeftMargin(hmarl)
				pad.SetRightMargin(hmarr)
				pad.SetBottomMargin(vmard)
				pad.SetTopMargin(vmaru)
				pad.SetFrameBorderMode(0)
				pad.SetBorderMode(0)
				pad.SetBorderSize(0)
				self.pads.append(pad)
				pad.Draw()
