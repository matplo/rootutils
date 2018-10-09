#!/usr/bin/env python

import tutils
import ROOT as r
import IPython
import argparse
import os

g = None
i = 0
nfile = 0

def myexec():
	# get event information
	event = r.gPad.GetEvent()
	px    = r.gPad.GetEventX()
	py    = r.gPad.GetEventY()
	# some magic to get the coordinates...
	xd = r.gPad.AbsPixeltoX(px);
	yd = r.gPad.AbsPixeltoY(py);
	x = r.gPad.PadtoX(xd);
	y = r.gPad.PadtoY(yd);
	# left mouse button click
	# print x, y

	global g, i, nfile


	if event == 1:
		D = 1./r.TMath.Exp(x)
		k = r.TMath.Exp(y)
		z = k / D
		print 'ln(1/D)=', x,  'D=', 1./r.TMath.Exp(x), 'ln(k)=', y, 'k=', r.TMath.Exp(y), 'z=', z
		print 'ln(1/D)=', r.TMath.Log(1./D),  'D=', 1./r.TMath.Exp(x), 'ln(k)=', r.TMath.Log(z*D), 'k=', r.TMath.Exp(y), 'z=', z

		if g is None:
			g = r.TGraph()
			tutils.gList.append(g)
		g.SetPoint(i,x,y)
		if i == 0:
			g.Draw("L")
		i = i + 1
		r.gPad.Update();

	if event == 24:
		fout = r.TFile("click_tgraph_{}.root".format(nfile), "recreate");
		g.Write();
		print "dumpding graph... to " , fout.GetName()
		fout.Close();
		g = None
		i = 0
		nfile = nfile + 1
		r.gPad.Update();

	return

class TestCall( r.TObject ):
	def __init__(self):
		r.TObject()
	def callback(self):
		print 'call...'

def main():

	tutils.setup_basic_root()

	tc = r.TCanvas('lund_projections_z', 'lund_projections_z', 1000, 1000)
	tutils.gList.append(tc)
	r.gPad.SetGridx()
	r.gPad.SetGridy()

	r.gPad.AddExec("myexec",'TPython::Exec("myexec()");')

	log1od_low = 0.9
	log1od_hi = 6.1
	log1od_low = 0.9
	log1od_hi = 8.9
	h = r.TH2D('tmp', 'tmp', 8, log1od_low, log1od_hi, 8, -8, 0)
	h.Draw("colz")
	tutils.gList.append(h)

	iz = 0
	for z in [0.01, 0.05, 0.1, 0.2, 0.25, 0.5]:
		iz = iz + 1
		d_low = 1./r.TMath.Exp(log1od_low)
		d_hi = 1./r.TMath.Exp(log1od_hi)
		fname = 'k_z_{}'.format(z)
		# f = r.TF1(fname, 'TMath::Log({} * x[0])'.format(z), d_low, d_hi)
		f = r.TF1(fname, 'TMath::Log({} * 1./TMath::Exp(x[0]))'.format(z), log1od_low, log1od_hi)
		f.SetTitle('z = {}'.format(z))
		f.SetLineColor(iz)
		f.Draw("same")
		tutils.gList.append(f)

	r.gPad.BuildLegend()
	r.gPad.Update()

if __name__=="__main__":
	# https://docs.python.org/2/howto/argparse.html
	parser = argparse.ArgumentParser(description='another starter not much more...', prog=os.path.basename(__file__))
	parser.add_argument('-b', '--batch', help='batchmode - do not end with IPython prompt', action='store_true')
	parser.add_argument('-i', '--prompt', help='end with IPython prompt', action='store_true')
	args = parser.parse_args()
	main()
	if not args.batch:
		tutils.run_app()
	if args.prompt:
		tutils.run_app()
