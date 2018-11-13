def get_quantiles_graph(nq=4, h=None, smod=''):
	xq = [0.0] * nq
	yq = [0.0] * nq
	for i in range(nq):
		xq[i] = 1.0*(i+1)/nq

	axq = array('d', xq)
	ayq = array('d', yq)

	if h is None:
		h = r.TH1F("h","demo quantiles",100,-3,3)
		h.FillRandom("gaus",5000);

	h.GetQuantiles(nq, ayq, axq);

	# show the quantiles in the bottom pad
	gr = r.TGraph(nq,axq,ayq);
	gr.SetName('q{}'.format(nq)+h.GetName())
	gr.SetTitle(h.GetTitle())
	gr.SetMarkerStyle(21);
	tutils.gList.append(h)
	tutils.gList.append(gr)

	#show the original histogram in the top pad
	if '--draw' in sys.argv:
		c1 = r.TCanvas('canvas'+h.GetName()+smod,h.GetTitle()+smod,10,10,700,900);
		c1.Divide(1,2);
		c1.cd(1);
		h.Draw();
		c1.cd(2);
		r.gPad.SetGrid();
		gr.Draw("alp");
		c1.Update()
		tutils.gList.append(c1)

	return gr, axq, ayq

def get_quantiles(nq=4, h=None, smod=''):
	xq = [0.0] * nq
	yq = [0.0] * nq
	for i in range(nq):
		xq[i] = 1.0*(i+1)/nq

	axq = array('d', xq)
	ayq = array('d', yq)

	if h is None:
		h = r.TH1F("h","demo quantiles",100,-3,3)
		h.FillRandom("gaus",5000);

	h.GetQuantiles(nq, ayq, axq);

	return axq, ayq

def get_quant_from_2D(h=None, n=50, smod = ''):
	x = []
	y = []
	for ibx in range(1, h.GetXaxis().GetNbins() + 1):
		hproj = h.ProjectionY('{}_py{}'.format(h.GetName(), ibx), ibx, ibx)
		axq, ayq = get_quantiles(100, hproj, smod + '_proj_{}'.format(ibx))
		x.append(h.GetXaxis().GetBinCenter(ibx))
		y.append(ayq[n])
	return x, y

def get_quant_from_2D_graph(h=None, n=50, smod = ''):
	x, y = get_quant_from_2D(h, n, smod)
	gr = r.TGraph(len(x), x, y)
	gr.SetName('quant_gr_{}_{}'.format(h.GetName(), n))
	tutils.gList.append(gr)
	return gr
