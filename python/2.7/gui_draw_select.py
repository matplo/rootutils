#!/usr/bin/env python

import tutils
import ROOT as r
import IPython
import dlist
import os
import os, sys
import meta_draw
import hashlib

class FileWatch(object):
    def __init__(self, fname):
        self.fname = fname
        self.hexdigest = None
        self.old_hexdigest = None
        self.changed()

    def changed(self):
        data = None
        try:
            with open(self.fname, 'r') as f:
                data = f.read()
        except:
            pass
        self.hexdigest = hashlib.md5(data).hexdigest()
        if self.hexdigest != self.old_hexdigest:
            retval = True
        else:
            retval = False
        self.old_hexdigest = self.hexdigest
        return retval

class FileView( r.TGMainFrame ):
    def __init__( self, parent, width, height, fname):
        r.TGMainFrame.__init__( self, parent, width, height, r.kHorizontalFrame | r.kFitHeight | r.kFitWidth )

        self.width  = width
        self.height = height
        self.fname  = fname

        self.SetWindowName( self.fname )

        self.SetLayoutManager(r.TGVerticalLayout(self));
        self.Resize(width, height);

        self.tabs = []
        self.tab = r.TGTab(self);
        self.AddFrame(self.tab, r.TGLayoutHints(r.kLHintsLeft | r.kLHintsTop | r.kLHintsExpandX | r.kLHintsExpandY));

        self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
        self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
        self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
        self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsExpandX)
        self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 5,5,5,5)

        self.buttonsFrame = r.TGButtonGroup( self, 'steering', r.kHorizontalFrame)
        self.AddFrame( self.buttonsFrame, self.buttonsFrameHint )

        self.drawButton   = r.TGTextButton( self.buttonsFrame, ' ReDraw ', 10 )
        self.drawDispatch = r.TPyDispatcher( self.draw )
        self.drawButton.Connect( 'Clicked()', "TPyDispatcher", self.drawDispatch, 'Dispatch()' )
        self.buttonsFrame.AddFrame( self.drawButton, self.buttonHint )

        self.exitButton   = r.TGTextButton( self.buttonsFrame, ' &Quit ', 20 )
        #self.exitButton.Connect( 'Clicked()', "TPyROOTApplication", r.gApplication, 'Close()' )
        self.exitButton.SetCommand( 'TPython::Exec( "raise SystemExit" )' )
        self.buttonsFrame.AddFrame( self.exitButton, self.buttonHint )

        self.timerDispatch = r.TPyDispatcher( self.on_timer )
        self.timer = r.TTimer()
        self.timer.Connect('Timeout()', "TPyDispatcher", self.timerDispatch, 'Dispatch()')

        self.mdf = None
        self.draw()
        self.fwatch = FileWatch(fname)
        self.timer.Start(1000, False);

        self.SetLayoutBroken(r.kFALSE);
        self.SetMWMHints(r.kMWMDecorAll, r.kMWMFuncAll, r.kMWMInputModeless);
        self.MapSubwindows()
        self.Resize( self.GetDefaultSize() )
        self.MapWindow()

        self.draw()

    def close(self):
        self.CloseWindow()
        r.gApplication.Close()

    def on_timer(self):
        if self.fwatch.changed():
            self.draw()

    def draw(self):
        del self.mdf
        self.mdf = meta_draw.MetaDrawFile(self.fname)
        
        #print 'N figures:',len(self.mdf.figures), 'N tabs:',len(self.tabs)
        #if len(self.mdf.figures) != len(self.tabs):
        #    self.tab.RemoveAll()
        #    del self.tabs
        #    self.tabs = []

        for i,mf in enumerate(self.mdf.figures):
            tcname = '{}_Fig{}_canvas'.format(self.fname, i)
            if i >= len(self.tabs):
                dframe = DrawFrame(self, self.width, self.height, tcname)
                tabname = 'Fig {}'.format(i)
                self.tab.AddTab(tabname, dframe)
                self.tab.SetTab(self.tab.GetNumberOfTabs()-1, r.kFALSE)
                self.tabs.append(dframe)
                dframe.Layout()
                dframe.MapSubwindows()
            else:
                self.tabs[i].draw(mf)

class DrawFrame( r.TGCompositeFrame ):
    def __init__( self, parent, width, height, name):
        r.TGCompositeFrame.__init__( self, parent, width, height, r.kLHintsExpandX | r.kLHintsExpandY)
        self.name = name

        self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
        self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
        self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
        self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsExpandX)
        self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 5,5,3,4)

        self.canvasFrame = r.TGGroupFrame( self, 'drawing')
        self.AddFrame(self.canvasFrame, self.frameHint )
        self.canvas     = r.TRootEmbeddedCanvas( self.name, self.canvasFrame, 50, 50 )
        self.canvasFrame.AddFrame( self.canvas, self.frameHint )

        self.buttonsFrame = r.TGButtonGroup( self, 'this tab actions', r.kHorizontalFrame)
        self.AddFrame( self.buttonsFrame, self.buttonsFrameHint )
        self.pdfButton   = r.TGTextButton( self.buttonsFrame, ' PDF ', 10 )
        self.pdfDispatch = r.TPyDispatcher( self.pdf )
        self.pdfButton.Connect( 'Clicked()', "TPyDispatcher", self.pdfDispatch, 'Dispatch()' )
        self.buttonsFrame.AddFrame( self.pdfButton, self.buttonHint )

        self.mf = None

    def pdf(self):
        #if self.mf:
        #    self.mf.hl.pdf()
        self.canvas.GetCanvas().Print(self.name+'.pdf', 'pdf')

    def draw(self, mf):
        self.mf = mf
        self.canvas.GetCanvas().cd()
        #consider here adding a handler for more that 1 figure in a draw file
        mf.draw(no_canvas=True)
        #except:
        #    print '[e] something went wrong with drawing...', self.fname, 'figure number:', self.draw_figure
        self.canvas.GetCanvas().Modified()
        self.canvas.GetCanvas().Update()

def setup_style():
    #r.gROOT.Reset()
    r.gStyle.SetScreenFactor(1)
    if not tutils.is_arg_set('--keep-stats'):
        r.gStyle.SetOptStat(0)
    if not tutils.is_arg_set('--keep-title'):
        r.gStyle.SetOptTitle(0)
    if not tutils.is_arg_set('--no-double-ticks'):
        r.gStyle.SetPadTickY(1)
        r.gStyle.SetPadTickX(1)
    r.gStyle.SetErrorX(0) #not by default; use X1 to show the x-error with ol
    r.gStyle.SetEndErrorSize(0)

def main():
    setup_style()
    fname = tutils.get_arg_with('-f')
    if not fname:
        if len(sys.argv) > 1:
            fname = sys.argv[1]
        else:
            return
    if not os.path.isfile(fname):
        fname = None
    if fname:
        fn, fext = os.path.splitext(fname)
        if fext == '.root':
            import make_draw_files as mdf
            fname = mdf.make_draw_file(fname)
        window = FileView(0, 600, 600, fname)
        window.RaiseWindow()
        r.gApplication.Run()

if __name__ == '__main__':
    main()
