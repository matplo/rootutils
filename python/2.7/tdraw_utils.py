import ROOT as r


def reset_file(foutname):
	f = r.TFile(foutname, 'recreate')
	f.Close()


def draw_to_a_file(foutname, tree, swhat, scond, scale=None):
	fout = r.TFile(foutname, 'update')
	fout.cd()
	hname = swhat.split('>>')[1].split('(')[0]
	tree.Draw(swhat, scond, 'e')
	h = r.gDirectory.Get(hname)
	nentries = h.GetEntries()
	print h, nentries
	fout.cd()
	if scale:
		h.Sumw2()
		h.Scale(scale)
	h.Write()
	fout.Close()
	return nentries


def normalize_along_y(h):
	for ibx in range(1, h.GetXaxis().GetNbins() + 1):
		intx = h.Integral(ibx, ibx, 1, h.GetYaxis().GetNbins() + 1)
		if intx > 0:
			for iby in range(1, h.GetYaxis().GetNbins() + 1):
				v = h.GetBinContent(ibx, iby)
				ve = h.GetBinError(ibx, iby)
				h.SetBinContent(ibx, iby, v / intx)
				h.SetBinError(ibx, iby, ve / intx)


def normalize_by(h, intx=1.):
	for ibx in range(1, h.GetXaxis().GetNbins() + 1):
		for iby in range(1, h.GetYaxis().GetNbins() + 1):
			v = h.GetBinContent(ibx, iby)
			ve = h.GetBinError(ibx, iby)
			h.SetBinContent(ibx, iby, v / intx)
			h.SetBinError(ibx, iby, ve / intx)


def filter_single_entries_2d_error(h, thr=10):
	for ibx in range(1, h.GetNbinsX() + 1):
		for iby in range(1, h.GetNbinsY() + 1):
			if h.GetBinContent(ibx, iby):
				relat_err = r.TMath.Abs(h.GetBinError(ibx, iby) / h.GetBinContent(ibx, iby))
				if relat_err > thr:
					h.SetBinContent(ibx, iby, 0)
					h.SetBinError(ibx, iby, 0)


def make_ratio(f1name, h1name, f2name, h2name, houtname, foutname, relat=False, normy=False):
	fout = r.TFile(foutname, "UPDATE")

	fout.cd()
	f1 = r.TFile(f1name)
	h1 = f1.Get(h1name)
	f2 = r.TFile(f2name)
	h2 = f2.Get(h2name)

	hout = h1.Clone(houtname)
	if normy:
		if h1.InheritsFrom('TH2'):
			normalize_along_y(hout)
			filter_single_entries_2d_error(hout, 0.33)
			normalize_along_y(h2)
			filter_single_entries_2d_error(h2, 0.33)
	if relat:
		hout.Add(h2, -1.)
	hout.Divide(h2)

	fout.cd()
	hout.Write()
	fout.Close()

	f1.Close()
	f2.Close()


def reset_bin_contents(h, val=0):
	for ibx in range(1, h.GetXaxis().GetNbins() + 1):
		for iby in range(1, h.GetYaxis().GetNbins() + 1):
			h.SetBinContent(ibx, iby, val)
			h.SetBinError(ibx, iby, 0.0)


def reset_non_zero_bin_contents(h, val=0):
	h.Sumw2()
	for ibx in range(1, h.GetXaxis().GetNbins() + 1):
		for iby in range(1, h.GetYaxis().GetNbins() + 1):
			if h.GetBinError(ibx, iby) != 0:
				h.SetBinContent(ibx, iby, val)
				h.SetBinError(ibx, iby, 0.0)
