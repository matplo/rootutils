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

class canvas:
    def __init__(self, name, title, w=600, h=400, split_fraction=0.0, split_mode=0):
        self.tcanvas = ROOT.TCanvas(name, title, h, w)        
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
        tu.gList.append(self)
    
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
        p.SetLeftMargin(_left)
        p.SetRightMargin(_right)
        p.SetTopMargin(_top)
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

def draw_comment(comment, font_size = None, x1 = 0.0, y1 = 0.9, x2 = 0.99, y2 = 0.99, font = 42, dopt='brNDC'):
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
    tx.SetFillColor(ROOT.kWhite)
    tx.SetFillColorAlpha(ROOT.kWhite, 0.0)
    tx.Draw()
    tu.gList.append(tx)
    return tx

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

