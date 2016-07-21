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
        r.TGMainFrame.__init__( self, parent, width, height )
        self.fname = fname

class DrawMainFrame( r.TGMainFrame ):
    def __init__( self, parent, width, height, fname, draw_figure=0):
        r.TGMainFrame.__init__( self, parent, width, height )

        self.fname = fname
        self.draw_figure = draw_figure

        self.mdf = meta_draw.MetaDrawFile(fname)
        self.fwatch = FileWatch(fname)

        self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
        self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
        self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
        self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsExpandX)
        self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 5,5,3,4)

        self.canvasFrame = r.TGGroupFrame( self, 'drawing')
        self.AddFrame(self.canvasFrame, self.frameHintEX )
        tcname = '{}_Fig{}_canvas'.format(self.fname, self.draw_figure)
        self.canvas     = r.TRootEmbeddedCanvas( tcname, self.canvasFrame, 600, 600 )
        self.canvasFrame.AddFrame( self.canvas, self.frameHint )

        self.buttonsFrame = r.TGGroupFrame( self, 'steering', r.kHorizontalFrame)
        self.AddFrame( self.buttonsFrame, self.buttonsFrameHint )

        self.drawButton   = r.TGTextButton( self.buttonsFrame, '&ReDraw', 10 )
        self.drawDispatch = r.TPyDispatcher( self.draw )
        self.drawButton.Connect( 'Clicked()', "TPyDispatcher", self.drawDispatch, 'Dispatch()' )
        self.buttonsFrame.AddFrame( self.drawButton, self.buttonHint )

        self.exitButton   = r.TGTextButton( self.buttonsFrame, '&Exit', 20 )
        #self.exitButton.Connect( 'Clicked()', "TPyROOTApplication", r.gApplication, 'Close()' )
        self.exitButton.SetCommand( 'TPython::Exec( "raise SystemExit" )' )
        self.buttonsFrame.AddFrame( self.exitButton, self.buttonHint )

        self.timerDispatch = r.TPyDispatcher( self.on_timer )
        self.timer = r.TTimer()
        self.timer.Connect('Timeout()', "TPyDispatcher", self.timerDispatch, 'Dispatch()')

        self.SetWindowName( 'GUI draw file' )
        self.remap()

        self.draw()

        self.timer.Start(1000, False);

    def remap(self):
        self.MapSubwindows()
        self.Resize( self.GetDefaultSize() )
        self.MapWindow()
        pass

    def on_timer(self):
        if self.fwatch.changed():
            del self.mdf
            self.mdf = meta_draw.MetaDrawFile(fname)
            self.draw()

    def draw(self):
        self.canvas.GetCanvas().cd()
        #consider here adding a handler for more that 1 figure in a draw file
        self.mdf.figures[self.draw_figure].draw(no_canvas=True)
        #except:
        #    print '[e] something went wrong with drawing...', self.fname, 'figure number:', self.draw_figure

    def close(self):
        r.gApplication.Close()

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

if __name__ == '__main__':
    setup_style()
    fname = tutils.get_arg_with('-f')

    if fname:
        fn, fext = os.path.splitext(fname)
        if fext == '.root':
            import make_draw_files as mdf
            fname = mdf.make_draw_file(fname)
        window = DrawMainFrame( 0, 800, 400, fname, 0)
        r.gApplication.Run()

