import ROOT
import tutils as tu
import math

def draw_line(x1, y1, x2, y2, col=2, style=7, width=2, option='brNDC', alpha=0.3):
    l = ROOT.TLine(x1, y1, x2, y2)
    l.SetLineColor(col)
    if alpha < 1.0:
        l.SetLineColorAlpha(col, alpha)
    l.SetLineWidth(width)
    l.SetLineStyle(style)
    l.Draw()
    tu.gList.append(l)
    return l

def to_file_name(s):
    return "".join([x if x.isalnum() else "_" for x in s])

class canvas:
    def __init__(self, name, title, w=600, h=400, split_fraction=0.0, split_mode=0):
        self.name = name
        self.tcanvas = ROOT.TCanvas(name, title, w, h)
        self.pads = []
        if split_fraction > 0:
            for i in range(2):
                pname  = name  + '-{0}'.format(i)
                ptitle = title + ' {0}'.format(i)
                x1 = 0
                x2 = split_fraction
                y1 = 0
                y2 = 1
                if i > 0:
                    x1 = split_fraction
                    x2 = 1
                if split_mode > 0:
                    y1 = x1
                    y2 = x2
                    x1 = 0
                    x2 = 1
                p = ROOT.TPad(pname, ptitle, x1, y1, x2, y2)
                p.Draw()
                self.pads.append(p)
        self.adjust_pad_margins()
        tu.gList.append(self)

    def pdf(self):
        self.tcanvas.Print(to_file_name(self.name)+'.pdf','.pdf')

    def resize_window(self, w, h):
        self.tcanvas.SetWindowSize(w, h) # + (w - self.tcanvas.GetWw()), h + (h - self.tcanvas.GetWh()));
        self.tcanvas.SetWindowSize(w + (w - self.tcanvas.GetWw()), h + (h - self.tcanvas.GetWh()));
        self.tcanvas.Update()

    def adjust_pad_margins(self, _left=0.15, _right=0.15, _top=0.1, _bottom=0.15):
        if len(self.pads) > 0:
            for sp in self.pads:
                sp.cd()
                p = ROOT.gPad
                if p:
                    p.SetLeftMargin(_left)
                    p.SetRightMargin(_right)
                    p.SetTopMargin(_top)
                    p.SetBottomMargin(_bottom)
        else:
            self.tcanvas.cd()
            p = ROOT.gPad
            if p:
                p.SetLeftMargin(_left)
                p.SetRightMargin(_right)
                p.SetTopMargin(_top)
                p.SetBottomMargin(_bottom)

    def cd(self, i):
        npads = len(self.pads)
        return self.pads[npads-(i)].cd()


class CanvasCollect(object):
    def __init__(self, outputname=''):
        self.outputname = outputname
        self.tcanvas_list = []

    def append(self, tc):
        try:
            _tc = tc.tcanvas
        except:
            _tc = tc
        self.tcanvas_list.append(_tc)

    def pdf(self, outputname=''):
        if len(self.tcanvas_list) <= 0:
            print '[w] asking to create an empty pdf file. nothing done.'
            return
        if len(outputname) > 0:
            self.outputname = outputname
        if len(self.outputname) <= 0:
            self.outputname = 'default_canvas_collect.pdf'
        self.outputname = self.outputname.split('.pdf')[0]
        self.outputname = self.outputname + '.pdf'
        for i, tc in enumerate(self.tcanvas_list):
            if i == 0:
                _outputname = self.outputname + '('
                if len(self.tcanvas_list) == 1:
                    _outputname = self.outputname
            if i == len(self.tcanvas_list) - 1:
                _outputname = self.outputname + ')'
            tc.Print(_outputname, 'pdf')
        print '[i] pdf file created:', self.outputname

def split_canvas(name, title, w=600, h=400, split_ratio=0.2, vertical=0):
    tc = ROOT.TCanvas(name, title, h, w)

    tp1 = ROOT.TPad('1', '1', 0.0, 1.0, 0.7, 0.0)
    tp1.Draw()
    tp2 = ROOT.TPad('2', '2', 0.7, 1.0, 1.0, 0.0)
    tp2.Draw()

    tu.gList.append(tc)

    return tc

#def adjust_pad_margins(_left=0.17, _right=0.01, _top=0.05, _bottom=0.13):
def adjust_pad_margins(_left=0.17, _right=0.01, _top=0.1, _bottom=0.17):
    p = ROOT.gPad
    if p:
        if _left:
            p.SetLeftMargin(_left)
        if _right:
            p.SetRightMargin(_right)
        if _top:
            p.SetTopMargin(_top)
        if _bottom:
            p.SetBottomMargin(_bottom)

def split_gPad_old(split_ratio=0.5, orient=0):
    # this will have a delete problem...
    retlist = []
    savepad = ROOT.gPad.cd()
    if orient == 0:
        tp1 = ROOT.TPad('1', '1', 0.0, 1.0, 1. - split_ratio, 0.0)
        tp1.Draw()
        adjust_pad_margins()
        retlist.append(tp1)
        tp2 = ROOT.TPad('2', '2',1.-split_ratio, 1.0, 1.0, 0.0)
        tp2.Draw()
        adjust_pad_margins()
        retlist.append(tp2)
    if orient == 1:
        tp1 = ROOT.TPad('1', '1', 0.0, split_ratio, 1., 1.)
        tp1.Draw()
        adjust_pad_margins()
        retlist.append(tp1)
        tp2 = ROOT.TPad('2', '2', 0.0, 0., 1., 1. - split_ratio)
        tp2.Draw()
        tp2.cd()
        adjust_pad_margins()
        retlist.append(tp2)
    savepad.cd()
    #return savepad
    return retlist

def split_gPad(split_ratio=0.5, orient=0):
    savepad = ROOT.gPad.cd()
    if orient == 0:
        savepad.Divide(1,2)
        tp1 = savepad.cd(1)
        #tp1.SetPad( 0.0, 1.0, 1. - split_ratio, 0.0)
        tp1.SetPad( 0.0, 1.0, split_ratio, 0.0)
        adjust_pad_margins()
        tp2 = savepad.cd(2)
        tp2.SetPad(split_ratio, 1.0, 1.0, 0.0)
        adjust_pad_margins()
        tp1.cd()
    else:
        savepad.Divide(2,1)
        tp1 = savepad.cd(1)
        #tp1.SetPad(0.0, split_ratio, 1., 1.)
        tp1.SetPad(0.0, 1., 1., split_ratio)
        adjust_pad_margins()
        tp2 = savepad.cd(2)
        tp2.SetPad(0.0, split_ratio, 1., 0)
        adjust_pad_margins()
        tp1.cd()
    return savepad

def draw_comment(comment, font_size = None, x1 = 0.0, y1 = 0.9, x2 = 0.99, y2 = 0.99, rotation=0.0, font = 42, dopt='brNDC'):
    if font_size == None:
        font_size = 0.04
    p = ROOT.gPad
    if p and x1==0.0:
        x1 = p.GetLeftMargin()
        x2 = 1. - p.GetRightMargin()
    tx = ROOT.TPaveText(x1, y1, x2, y2, dopt)
    tx.SetBorderSize(0)
    tx.SetTextAlign(22)
    tx.SetTextSize( font_size )
    tx.SetTextFont( font )
    tx.AddText(comment)
    tx.GetListOfLines().Last().SetTextRotation( rotation )
    tx.SetFillColor(ROOT.kWhite)
    tx.SetFillColorAlpha(ROOT.kWhite, 0.0)
    tx.Draw()
    tu.gList.append(tx)
    return tx

def draw_comment_multiline(comment = [], font_size = None, x1 = 0.0, y1 = 0.9, x2 = 0.99, y2 = 0.99, font = 42, dopt='brNDC'):
    for i,c in enumerate(comment):
        draw_comment(c, font_size, x1, y1 - font_size * 1.2 * (i+1), x2, y2 - font_size * 1.2 * i, font, dopt)

def make_canvas_grid(n, tc = None, name = 'tmp_tc', title = 'tmp_tc', orient=0, xm=0.01, ym=0.01):
    if tc == None:
        if orient == 0:
            tc = ROOT.TCanvas(name, title, 800, 600)
        else:
            tc = ROOT.TCanvas(name, title, 600, 800)
    nv = float(n)
    ir = int(math.sqrt(nv))
    ic = int(math.sqrt(nv))
    while (ir * ic) < n:
        ir = ir + 1
        if (ir * ic) < n:
            ic = ic + 1
    if orient == 0:
        tc.Divide(ir, ic, xm, ym)
    else:
        tc.Divide(ic, ir, xm, ym)
    return tc

def readjust_6fold(tc):
    tc.cd(1)
    gp = ROOT.gPad
    gp.SetBottomMargin(0)
    gp.SetRightMargin(0)
    gp.Update()
    tc.cd(2)
    gp = ROOT.gPad
    gp.SetBottomMargin(0)
    gp.SetLeftMargin(0)
    gp.SetRightMargin(0)
    tc.Update()

def resize_window(tcanvas, w, h):
    tcanvas.SetWindowSize(w, h) # + (w - self.tcanvas.GetWw()), h + (h - self.tcanvas.GetWh()));
    tcanvas.SetWindowSize(w + (w - tcanvas.GetWw()), h + (h - tcanvas.GetWh()));
    tcanvas.Update()


def fix_graph(gr, thr=None, debug=False):
    xgr              = gr.GetX()
    ygr              = gr.GetY()
    points_to_remove = []
    npoints = gr.GetN()
    for i in range(0, npoints):
        if thr != None:
            if ygr[i] < thr:
                points_to_remove.append(i)
                continue
        if math.isinf(xgr[i]) or math.isinf(ygr[i]):
            points_to_remove.append(i)
            continue
        if math.isnan(xgr[i]) or math.isnan(ygr[i]):
            points_to_remove.append(i)
            continue
        if i == 0:
            if xgr[i] == 0 and ygr[i] == 0:
                points_to_remove.append(i)
            continue
        if xgr[i] <= xgr[i-1]:
            points_to_remove.append(i)
            continue

    for i in points_to_remove:
        if i == 0:
            if debug:
                print '[e] problem with:',gr.GetName()
        if debug:
            print '    removing point at',i, xgr[i], ygr[i]
        gr.RemovePoint(i)

    if len(points_to_remove)>0:
        fix_graph(gr)

    npoints = gr.GetN()
    for i in range(0, npoints):
        xgr = gr.GetX()
        ygr = gr.GetY()
        if debug:
            print '    left point at',i, xgr[i], ygr[i]
    npoints_new = gr.GetN()
    if debug:
        print '[i]', gr.GetName(),'npoints:',npoints_new,'was:',npoints
    return gr


def get_axis_factor(i, refpad):
    try:
        xFactor = refpad.GetAbsWNDC()/ROOT.gPad.GetAbsWNDC()
        yFactor = refpad.GetAbsHNDC()/ROOT.gPad.GetAbsHNDC()
        if i == 0:
            lfactor = yFactor * 0.06 / xFactor
        else:
            lfactor = xFactor * 0.04 / yFactor
    except:
        lfactor = 1.0
    return lfactor


def adjust_axis(h, refpad, scaleTSize = 1.0, scaleLSize = 1.0, scaleTOffset = 1.0):
    xFactor = get_axis_factor(0, refpad)
    yFactor = get_axis_factor(1, refpad)
    print xFactor, yFactor
    for i in xrange(2):
        if i == 0:
            axis = h.GetXaxis()
            lfactor = yFactor / xFactor
            title_offset = lfactor * scaleTSize * scaleTOffset
            tsize = 16
        else:
            axis = h.GetYaxis()
            lfactor = xFactor / yFactor
            title_offset = lfactor * scaleTSize * scaleTOffset
            tsize = 18
        axis.SetTickLength(lfactor * 0.01)
        axis.SetLabelFont(43)
        axis.SetLabelSize(14 * scaleLSize)
        axis.SetLabelOffset(0.03 * scaleLSize / 2.)
        axis.SetTitleFont(43)
        axis.SetTitleSize(tsize * scaleTSize)
        axis.SetTitleOffset(title_offset)
