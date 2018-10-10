#!/usr/bin/env python

import tutils
import ROOT as r
import argparse
import os


class ExecHandler(object):
	def __init__(self):
		self.graph = None
		self.i = 0
		self.nfile = 0

	def set_coordinates(self, pad):
		# get event information
		self.event = pad.GetEvent()
		self.px    = pad.GetEventX()
		self.py    = pad.GetEventY()
		# some magic to get the coordinates...
		self.xd    = pad.AbsPixeltoX(self.px)
		self.yd    = pad.AbsPixeltoY(self.py)
		self.x     = pad.PadtoX(self.xd)
		self.y     = pad.PadtoY(self.yd)

	def handle_event(self, pad):
		self.set_coordinates(pad)
		self.user_handle_event()

	def user_handle_event(self):
		if self.event == 1:
			D = 1. / r.TMath.Exp(self.x)
			k = r.TMath.Exp(self.y)
			z = k / D
			print 'ln(1/D)=', self.x, 'D=', 1. / r.TMath.Exp(self.x), 'ln(k)=', self.y,
			print 'k=', r.TMath.Exp(self.y), 'z=', z
			print 'ln(1/D)=', r.TMath.Log(1. / D), 'D=', 1. / r.TMath.Exp(self.x), 'ln(k)=', r.TMath.Log(z * D),
			print 'k=', r.TMath.Exp(self.y), 'z=', z

			if self.graph is None:
				self.graph = r.TGraph()
				self.graph.SetName('{}_{}'.format(type(self).__name__, self.i))
				tutils.gList.append(self.graph)
			self.graph.SetPoint(self.i, self.x, self.y)
			if self.i == 0:
				self.graph.Draw("L")
			self.i = self.i + 1
			r.gPad.Update()

		if self.event == 24:
			if self.graph:
				fout = r.TFile("click_tgraph_{}.root".format(self.nfile), "recreate")
				self.graph.Write()
				print "dumpding graph... to ", fout.GetName()
				fout.Close()
				self.graph = None
				self.i = 0
				self.nfile = self.nfile + 1
				r.gPad.Update()


class ExecOnClick(object):
	lhandlers = []

	@staticmethod
	def click():
		for h in ExecOnClick.lhandlers:
			h.handle_event(r.gPad)
		return

	@staticmethod
	def add_handler(h):
		ExecOnClick.lhandlers.append(h)

	@staticmethod
	def add_exec_to_pad(pad):
		pad.AddExec("myexec", 'TPython::Exec("ExecOnClick.click()");')


def main():

	tutils.setup_basic_root()

	tc = r.TCanvas('lund_projections_z', 'lund_projections_z', 400, 400)
	tutils.gList.append(tc)
	r.gPad.SetGridx()
	r.gPad.SetGridy()

	eh = ExecHandler()
	ExecOnClick.add_handler(eh)

	ExecOnClick.add_exec_to_pad(r.gPad)

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
		# d_low = 1. / r.TMath.Exp(log1od_low)
		# d_hi = 1. / r.TMath.Exp(log1od_hi)
		fname = 'k_z_{}'.format(z)
		# f = r.TF1(fname, 'TMath::Log({} * x[0])'.format(z), d_low, d_hi)
		f = r.TF1(fname, 'TMath::Log({} * 1./TMath::Exp(x[0]))'.format(z), log1od_low, log1od_hi)
		f.SetTitle('z = {}'.format(z))
		f.SetLineColor(iz)
		f.Draw("same")
		tutils.gList.append(f)

	r.gPad.BuildLegend()
	r.gPad.Update()


if __name__ == "__main__":
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
