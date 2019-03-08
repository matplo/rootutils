#!/usr/bin/env python

import tutils
import ROOT as r
import IPython
import argparse
import os

def main():

	# tutils.setup_basic_root()

	h = r.TH1D('test', 'test', 10, 0, 1)
	h.Fill(.2)
	h.Fill(.5)
	h.Fill(.4,3.145)
	h.Draw()
	r.gPad.Update()
	tutils.gList.append(h)

if __name__=="__main__":
	# https://docs.python.org/2/howto/argparse.html
	parser = argparse.ArgumentParser(description='another starter not much more...', prog=os.path.basename(__file__))
	parser.add_argument('-b', '--batch', help='batchmode - do not end with IPython prompt', action='store_true')
	parser.add_argument('-i', '--prompt', help='end with IPython prompt', action='store_true')
	args = parser.parse_args()
	main()
	#if not args.batch:
	#	tutils.run_app()
	#if args.prompt:
	#	tutils.run_app()
