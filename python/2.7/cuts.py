    def draw_old(self, option='', miny=None, maxy=None, logy=False, colopt=''):
        self.adjust_maxima(miny=miny, maxy=maxy, logy=logy)
        self.adjust_axis_attributes(0)
        self.adjust_axis_attributes(1)
        self.adjust_axis_attributes(2)
        drawn = False

        opts = self.all_options() + ' ' + option.lower()
        dopt = draw_option(opts)

        if dopt.use_line:
            self.lineize()                   
        if 'bw' in opts:
            pass
        else:
            self.colorize()
        if 'p' in opts:
            self.markerize()
        
        for h in self.l:
            i = self.l.index(h)
            if self.lopts[i] == '':
                self.lopts[i] = option
            opt = self.lopts[i]
            self.debug('::draw ' + h.GetName() + ' ' + opt)

            if dopt.is_error:
                h.SetLineWidth(0)
                h.SetLineStyle(0)                
                h.SetMarkerSize(0)
                h.SetMarkerStyle(0)
                if fstyle > 0:
                    h.SetFillStyle(fstyle)
                else:
                    h.SetFillStyle(1001)
                if kolor <= 0:
                    kolor = h.GetLineColor()
                h.SetFillColor(kolor)
                h.SetLineColor(kolor)
                h.SetMarkerColor(kolor)
                if alpha > 0 and alpha <= 1:
                    h.SetFillColorAlpha(kolor, alpha);                    
            else:
                if dopt.lstyle > 0:
                    h.SetLineStyle(dopt.lstyle)
                if dopt.pstyle > 0:
                    h.SetMarkerStyle(dopt.pstyle)
                if dopt.fstyle > 0:
                    h.SetFillStyle(dopt.fstyle)
                else:
                    h.SetFillStyle(0000)                
                    h.SetFillColor(0)
                if dopt.kolor > 0:
                    h.SetFillColor(dopt.kolor)
                    h.SetLineColor(dopt.kolor)
                    h.SetMarkerColor(dopt.kolor)                                

            optd = opt
            if drawn == True or 'same' in option.lower():
                optd = optd + ' same'
            else:
                drawn = True
                if h.InheritsFrom('TGraph'):
                    optd = optd + ' a'
                self.minx = h.GetXaxis().GetXmin()
                self.maxx = h.GetXaxis().GetXmax()
                
            if 'serror' in opt.lower():
                #errx = ROOT.gStyle.GetErrorX()
                #ROOT.gStyle.SetErrorX(0.5)
                optd = optd + ' E2'
                #ROOT.gStyle.SetErrorX(errx)                
            else:
                if 'X1' in opt:
                    pass
                else:
                    optd = optd + ' X0'
            self.debug('drawing {} with opt: {}'.format(h.GetName(), optd))
            h.Draw(optd)
        self.adjust_pad_margins()            
        self.update()
