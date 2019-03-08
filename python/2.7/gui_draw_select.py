#!/usr/bin/env python

# import tutils
import ROOT as r
# import IPython
# import dlist
import os
import sys
import meta_draw
import hashlib
import tempfile
import time
import argparse
import pyutils
import pyperclip


def make_temp_file_old(ext='.draw'):
	ftemp = tempfile.mkstemp(ext, 'tmp_', None, True)
	# # os.write(ftemp[0], '#figure\n')
	# os.close(ftemp[0])
	# return ftemp[1]
	print ftemp
	fn = 'test{}'.format(ext)
	with open(fn, 'w') as f:
		f.write('#figure')
	return fn


def make_temp_file(ext='.draw'):
	f = tempfile.NamedTemporaryFile(mode='rw', delete=False)  # mode='rw', suffix=ext, delete=False)
	return f


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
		except IOError:
			pass
		if data is None:
			return True
		self.hexdigest = hashlib.md5(data).hexdigest()
		if self.hexdigest != self.old_hexdigest:
			retval = True
		else:
			retval = False
		self.old_hexdigest = self.hexdigest
		return retval


class FileView(r.TGMainFrame):
	def __init__(self, parent, width, height, fname, args=None):
		r.TGMainFrame.__init__(self, parent, width, height, r.kHorizontalFrame | r.kFitHeight | r.kFitWidth)

		self.width  = width
		self.height = height
		self.fname  = fname

		self.SetWindowName(self.fname)

		self.SetLayoutManager(r.TGVerticalLayout(self))
		self.Resize(width, height)

		self.tabs = []
		self.tab = r.TGTab(self)
		self.AddFrame(self.tab, r.TGLayoutHints(r.kLHintsLeft | r.kLHintsTop | r.kLHintsExpandX | r.kLHintsExpandY))

		self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
		self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
		self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsNormal | r.kLHintsCenterX | r.kLHintsExpandX)
		self.buttonHint       = r.TGLayoutHints(r.kLHintsNormal | r.kLHintsCenterX | r.kLHintsExpandX, 1, 1, 1, 1)

		self.buttonsFrame = r.TGButtonGroup(self, 'steering', r.kHorizontalFrame)
		self.AddFrame(self.buttonsFrame, self.buttonsFrameHint)

		self.drawButton   = r.TGTextButton(self.buttonsFrame, ' ReDraw ')
		self.drawDispatch = r.TPyDispatcher(self.draw)
		self.drawButton.Connect('Clicked()', "TPyDispatcher", self.drawDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.drawButton, self.buttonHint)

		self.pdfButton   = r.TGTextButton(self.buttonsFrame, ' PDF ')
		self.pdfDispatch = r.TPyDispatcher(self.pdf)
		self.pdfButton.Connect('Clicked()', "TPyDispatcher", self.pdfDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.pdfButton, self.buttonHint)

		self.exitButton   = r.TGTextButton(self.buttonsFrame, ' &Quit ')
		#  self.exitButton.Connect('Clicked()', "TPyROOTApplication", r.gApplication, 'Close()')
		self.exitButton.SetCommand('TPython::Exec("raise SystemExit")')
		self.buttonsFrame.AddFrame(self.exitButton, self.buttonHint)

		self.timerDispatch = r.TPyDispatcher(self.on_timer)
		self.timer = r.TTimer()
		self.timer.Connect('Timeout()', "TPyDispatcher", self.timerDispatch, 'Dispatch()')

		self.logfileFrame = LogFileFrame(self, self.width, self.height, 'Log')
		self.tab.AddTab('log', self.logfileFrame)
		self.tab.SetTab(self.tab.GetNumberOfTabs() - 1, r.kFALSE)
		self.tabs.append(self.logfileFrame)
		self.flogwatch = FileWatch(self.logfileFrame.logfilename)

		self.canvasFrame = UtilCanvasFrame(self, self.width, self.height, 'UtilCanvas')
		self.tab.AddTab('utils', self.canvasFrame)
		self.tab.SetTab(self.tab.GetNumberOfTabs() - 1, r.kFALSE)
		self.tabs.append(self.canvasFrame)

		self.mdf = None
		self.draw()
		self.fwatch = FileWatch(fname)
		self.timer.Start(1000, False)

		self.SetLayoutBroken(r.kFALSE)
		self.SetMWMHints(r.kMWMDecorAll, r.kMWMFuncAll, r.kMWMInputModeless)
		self.MapSubwindows()
		self.Resize(self.GetDefaultSize())
		self.MapWindow()

		self.draw()

		if args:
			if args.preent:
				print 'printing...'
				if args.preent.lower() == 'pdf1':
					self.pdf()
				if args.preent.lower() == 'pdf':
					self.draw('pdf')
				if args.preent.lower() == 'png':
					self.draw('png')
				print 'done.'

			if args.quit:
				self.close()

	def close(self):
		self.CloseWindow()
		r.gApplication.Terminate(0)
		exit(0)

	def on_timer(self):
		self.logfileFrame.flush()
		if self.flogwatch.changed():
			self.logfileFrame.draw()
		if self.fwatch.changed():
			self.draw()

	def draw(self, preent=None):
		try:
			del self.mdf
		except:
			pass
		try:
			self.mdf = meta_draw.MetaDrawFile(self.fname)
		except:
			print '[e] failed to create MetaDrawFile with', self.fname

		#  print 'N figures:',len(self.mdf.figures), 'N tabs:',len(self.tabs)
		#  if len(self.mdf.figures) != len(self.tabs):
		#      self.tab.RemoveAll()
		#      del self.tabs
		#      self.tabs = []

		#  mem management dirty hack
		#  del tutils.gList
		#  tutils.gList = []

		for i, mf in enumerate(self.mdf.figures):
			tcname = '{}_Fig{}_canvas'.format(self.fname, i)
			if i >= len(self.tabs) - 2:  # remember the log and util tab
				dframe = DrawFrame(self, self.width, self.height, tcname)
				tabname = 'Fig {}'.format(i)
				self.tab.AddTab(tabname, dframe)
				self.tab.SetTab(self.tab.GetNumberOfTabs() - 1, r.kFALSE)
				self.tabs.append(dframe)
				dframe.do_layout()
				dframe.draw(mf)
				self.tab.Layout()
				#  self.tab.Resize(self.width, self.height)
				self.tab.MapSubwindows()
			else:
				self.logfileFrame.flush()
				self.tabs[i + 2].draw(mf)  # remember the log and util tab
				if not mf.figure_name:
					mf.figure_name = 'Fig {}'.format(i)
					stabname = '{}'.format(mf.figure_name)
				else:
					stabname = '{} {}'.format(i, mf.figure_name)
				self.tabs[i + 2].name = '{}_{}'.format(self.fname, pyutils.to_file_name(stabname))
				tabname = r.TGString(stabname)
				self.tab.GetTabTab(i + 2).SetText(tabname)
				#  '{}_{}'.format(self.fname, i, pyutils.to_file_name(mf.figure_name))
				self.tabs[i + 2].do_layout()
				if preent:
					if preent == 'pdf':
						self.tabs[i + 2].pdf()
					if preent == 'png':
						self.tabs[i + 2].png()
		self.Layout()

	def pdf(self):
		ifig = 0
		for itab, tab in enumerate(self.tabs):
			if itab < 2:
				continue  # log and util tab skip
			fname = self.fname + '.pdf'
			if ifig == 0:
				fname = self.fname + '.pdf('
			if itab == len(self.tabs) - 1:
				fname = self.fname + '.pdf)'
			print 'printing to pdf: ', fname
			tab.pdf_to_file(fname)
			ifig += 1

# class MyTextView(r.TGTextView):
# 	def __init__(self, parent):
# 		r.TGTextView.__init__(self, parent)
# 	def getClipText(self):
# 		return self.fClipText.GetCurrentLine().GetText()


class LogFileFrame(r.TGCompositeFrame):
	def __init__(self, parent, width, height, name, logfilename=None):
		r.TGCompositeFrame.__init__(self, parent, width, height, r.kLHintsExpandX | r.kLHintsExpandY)
		self.initialized = False

		self.name = name

		self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
		self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
		self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 5, 5, 3, 4)

		self.contentFrame = r.TGGroupFrame(self, 'log')
		self.AddFrame(self.contentFrame, self.frameHint)
		# self.content     = r.TGTextEdit(self)
		# self.content.SetReadOnly()
		# self.content     = MyTextView(self) #r.TGTextView(self)
		self.content     = r.TGTextView(self)
		self.contentFrame.AddFrame(self.content, self.frameHint)

		self.buttonsFrame = r.TGButtonGroup(self, 'tools', r.kHorizontalFrame)
		self.AddFrame(self.buttonsFrame, self.buttonsFrameHint)

		self.copyToClipboardButton   = r.TGTextButton(self.buttonsFrame, 'Copy to clipboard')
		self.copyToClipboardDispatch = r.TPyDispatcher(self.copyToClipboard)
		self.copyToClipboardButton.Connect('Clicked()', "TPyDispatcher", self.copyToClipboardDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.copyToClipboardButton, self.buttonHint)

		self.clearButton   = r.TGTextButton(self.buttonsFrame, 'Clear')
		self.clearDispatch = r.TPyDispatcher(self.clear)
		self.clearButton.Connect('Clicked()', "TPyDispatcher", self.clearDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.clearButton, self.buttonHint)

		self.logfile = None
		self.logfilename = logfilename
		if self.logfilename is None:
			self.logfile = tempfile.NamedTemporaryFile(mode='rw', delete=False)
			self.logfilename = self.logfile.name
		else:
			self.logfile = open(self.logfilename, 'w')
		self.logfile_fd = self.logfile.fileno()
		print '[i] log goes to:', self.logfilename
		self.keep_stdout_fd = sys.stdout.fileno()
		# self.keep_stderr_fd = sys.stderr.fileno()
		self.keep_stdout = sys.stdout
		# self.keep_stderr = sys.stderr
		# sys.stdout = self.logfile
		# sys.stderr = self.logfile
		# deep
		os.dup2(self.logfile_fd, 1)
		# os.dup2(self.logfile_fd, 2)
		print '[i] log goes to:', self.logfilename
		print sys.argv
		self.initialized = True
		self.lines_read = 0

	def flush(self):
		sys.stdout.flush()
		# sys.stderr.flush()

	def copyToClipboard(self):
		copied = self.content.Copy()
		# print "[i] logfile text copied to clipboard", copied

		if not pyperclip.is_available():
			# print >> sys.stderr, '[e] no pyperclip functionality available'
			print '[w] no pyperclip functionality available'
		try:
			cl = []
			with open(self.logfilename, 'r') as f:
				cl = f.readlines()
			pyperclip.copy(''.join(cl))
		except:
			print '[e] pyperclip.copy failed.'
		# print >> sys.stderr, self.content.getClipText()
		self.draw()

	def clear(self):
		# self.content.SelectAll()
		self.content.Clear()

	def __del__(self):
		if self.initialized:
			sys.stdout = self.keep_stdout
			sys.stderr = self.keep_stderr
			os.dup2(self.keep_stdout_fd, 1)
			# os.dup2(self.keep_stderr_fd, 2)
			self.logfile.close()
		print 'LogFileFrame closed.', self.logfilename

	def draw_old(self, p=None):
		self.content.Clear()
		with open(self.logfilename, 'r') as f:
			cl = f.readlines()
		self.content.AddLineFast('[i] read log... lines:{}'.format(len(cl)))
		for i, l in enumerate(cl):
			if i == self.lines_read:
				self.content.AddLineFast('')
				self.content.AddLineFast('- new content - {}'.format(time.strftime('%c')))
			self.content.AddLineFast(l.strip())
		self.lines_read = len(cl)
		# if self.content.ReturnLineCount() > visible_lines:
		# self.content.SetVsbPosition(self.content.ReturnLineCount())
		self.content.Update()
		self.content.ShowBottom()
		self.content.Update()

	def draw(self, p=None):
		self.content.LoadFile(self.logfilename)
		self.content.ShowBottom()
		self.content.Update()

# class FeaturesFrameBox(r.TGMsgBox):
# 	def __init__(self, parent, main, title, msg):
# 		r.TGMsgBox.__init__(self, parent, main, title, msg)


class CanvasFrame(r.TGCompositeFrame):
	def __init__(self, parent, width, height, name):
		r.TGCompositeFrame.__init__(self, parent, width, height, r.kLHintsExpandX | r.kLHintsExpandY)
		self.width = width
		self.height = height
		self.name = name

		self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
		self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
		self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 5, 5, 3, 4)

		self.canvasFrame = r.TGGroupFrame(self, 'drawing')
		self.AddFrame(self.canvasFrame, self.frameHint)
		self.canvas     = r.TRootEmbeddedCanvas(self.name, self.canvasFrame, 50, 50)
		self.canvasFrame.AddFrame(self.canvas, self.frameHint)

		self.tcanvas = self.canvas.GetCanvas()

	def do_layout(self):
		self.Layout()
		self.Resize(self.width, self.height)
		self.MapSubwindows()


class UtilCanvasFrame(r.TGCompositeFrame):
	def __init__(self, parent, width, height, name):
		r.TGCompositeFrame.__init__(self, parent, width, height, r.kLHintsExpandX | r.kLHintsExpandY)
		self.name = name

		self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
		self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
		self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 5, 5, 3, 4)

		self.canvasFrame = r.TGGroupFrame(self, 'drawing')
		self.AddFrame(self.canvasFrame, self.frameHint)
		self.canvas     = r.TRootEmbeddedCanvas(self.name, self.canvasFrame, 50, 50)
		self.canvasFrame.AddFrame(self.canvas, self.frameHint)

		self.tcanvas = self.canvas.GetCanvas()

		self.buttonsFrame = r.TGButtonGroup(self, 'tools', r.kHorizontalFrame)
		self.AddFrame(self.buttonsFrame, self.buttonsFrameHint)

		self.tcw = None
		self.colorWheelButton   = r.TGTextButton(self.buttonsFrame, 'CWheel')
		self.colorWheelDispatch = r.TPyDispatcher(self.colorWheel)
		self.colorWheelButton.Connect('Clicked()', "TPyDispatcher", self.colorWheelDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.colorWheelButton, self.buttonHint)

		self.colorTableButton   = r.TGTextButton(self.buttonsFrame, 'Colors')
		self.colorTableDispatch = r.TPyDispatcher(self.colorTable)
		self.colorTableButton.Connect('Clicked()', "TPyDispatcher", self.colorTableDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.colorTableButton, self.buttonHint)

		self.markerTableImage = None
		self.markerTableButton   = r.TGTextButton(self.buttonsFrame, 'Markers')
		self.markerTableDispatch = r.TPyDispatcher(self.markerTable)
		self.markerTableButton.Connect('Clicked()', "TPyDispatcher", self.markerTableDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.markerTableButton, self.buttonHint)

		self.lineTableImage = None
		self.lineTableButton   = r.TGTextButton(self.buttonsFrame, 'Lines')
		self.lineTableDispatch = r.TPyDispatcher(self.lineTable)
		self.lineTableButton.Connect('Clicked()', "TPyDispatcher", self.lineTableDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.lineTableButton, self.buttonHint)

	def colorWheel(self):
		self.tcanvas.cd()
		self.tcanvas.Clear()
		if self.tcw is None:
			self.tcw = r.TColorWheel()
		self.tcw.SetCanvas(self.tcanvas)
		self.tcw.Draw()
		self.tcanvas.Update()

	def colorTable(self):
		self.tcanvas.cd()
		self.tcanvas.Clear()
		self.tcanvas.DrawColorTable()
		self.tcanvas.Update()

	def markerTable(self):
		self.tcanvas.cd()
		self.tcanvas.Clear()
		self.tcanvas.SetFillColor(r.kWhite)
		if self.markerTableImage is None:
			imgpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'pict1_TAttMarker_002.png')
			self.markerTableImage = r.TImage.Open(imgpath)
		self.markerTableImage.Draw()
		self.tcanvas.Update()

	def lineTable(self):
		self.tcanvas.cd()
		self.tcanvas.Clear()
		self.tcanvas.SetFillColor(r.kWhite)
		if self.lineTableImage is None:
			imgpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'pict1_TAttLine_003.png')
			self.lineTableImage = r.TImage.Open(imgpath)
		self.lineTableImage.Draw()
		self.tcanvas.Update()


class DrawFrame(r.TGCompositeFrame):
	def __init__(self, parent, width, height, name):
		r.TGCompositeFrame.__init__(self, parent, width, height, r.kLHintsExpandX | r.kLHintsExpandY)
		self.width = width
		self.height = height
		self.name = name

		self.frameHint        = r.TGLayoutHints(r.kLHintsExpandX | r.kLHintsExpandY)
		self.frameHintEY      = r.TGLayoutHints(r.kLHintsExpandY)
		self.frameHintEX      = r.TGLayoutHints(r.kLHintsExpandX)
		self.buttonsFrameHint = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX)
		# self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 0, 0, 0, 0)  #5,5,3,4)
		self.buttonHint       = r.TGLayoutHints(r.kLHintsCenterX | r.kLHintsExpandX, 0, 0, 0, 0)  # 5,5,3,4)

		self.canvasFrame = r.TGGroupFrame(self, 'drawing')
		self.AddFrame(self.canvasFrame, self.frameHint)
		self.canvas     = r.TRootEmbeddedCanvas(self.name, self.canvasFrame, 100, 100)
		self.canvasFrame.AddFrame(self.canvas, self.frameHint)

		self.buttonsFrame = r.TGButtonGroup(self, 'actions', r.kHorizontalFrame)
		self.AddFrame(self.buttonsFrame, self.buttonsFrameHint)

		self.dumpFeaturesButton   = r.TGTextButton(self.buttonsFrame, 'Features->Log', 0)
		self.dumpFeaturesDispatch = r.TPyDispatcher(self.dumpFeatures)
		self.dumpFeaturesButton.Connect('Clicked()', "TPyDispatcher", self.dumpFeaturesDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.dumpFeaturesButton, self.buttonHint)
		self.dumpFeaturesButton.SetWrapLength(50)

		self.copyToClipperFeaturesButton   = r.TGTextButton(self.buttonsFrame, 'Features->ClipB', 1)
		self.copyToClipperFeaturesDispatch = r.TPyDispatcher(self.copyToClipperFeatures)
		self.copyToClipperFeaturesButton.Connect('Clicked()', "TPyDispatcher", self.copyToClipperFeaturesDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.copyToClipperFeaturesButton, self.buttonHint)
		self.copyToClipperFeaturesButton.SetWrapLength(50)

		self.writeRootMacroButton   = r.TGTextButton(self.buttonsFrame, '.C', 2)
		self.writeRootMacroDispatch = r.TPyDispatcher(self.writeRootMacro)
		self.writeRootMacroButton.Connect('Clicked()', "TPyDispatcher", self.writeRootMacroDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.writeRootMacroButton, self.buttonHint)

		self.writeRootFileButton   = r.TGTextButton(self.buttonsFrame, 'ROOT', 3)
		self.writeRootFileDispatch = r.TPyDispatcher(self.writeRootFile)
		self.writeRootFileButton.Connect('Clicked()', "TPyDispatcher", self.writeRootFileDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.writeRootFileButton, self.buttonHint)

		self.pdfButton   = r.TGTextButton(self.buttonsFrame, 'PDF', 4)
		self.pdfDispatch = r.TPyDispatcher(self.pdf)
		self.pdfButton.Connect('Clicked()', "TPyDispatcher", self.pdfDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.pdfButton, self.buttonHint)

		self.pngButton   = r.TGTextButton(self.buttonsFrame, 'PNG', 5)
		self.pngDispatch = r.TPyDispatcher(self.png)
		self.pngButton.Connect('Clicked()', "TPyDispatcher", self.pngDispatch, 'Dispatch()')
		self.buttonsFrame.AddFrame(self.pngButton, self.buttonHint)

		self.mf = None

		self.do_layout()

	def do_layout(self):
		self.Layout()
		self.Resize(self.width, self.height)
		self.MapSubwindows()

	def writeRootFile(self):
		self.mf.hl.write_to_file(self.name + '.root', name_mod='modn:')

	def writeRootMacro(self):
		self.mf.hl.tcanvas.SaveAs(self.name + '.C', '.C')

	def pdf(self):
		# if self.mf:
		#     self.mf.hl.pdf()
		self.canvas.GetCanvas().Print(self.name + '.pdf', 'pdf')

	def pdf_to_file(self, fname):
		self.canvas.GetCanvas().Print(fname, 'pdf')

	def png(self):
		# if self.mf:
		#     self.mf.hl.png()
		self.canvas.GetCanvas().Print(self.name + '.png', 'png')

	def features_text(self):
		stext = []
		stext.append(self.name)
		tc = self.canvas.GetCanvas()
		lop = tc.GetListOfPrimitives()
		for o in lop:
			if o.InheritsFrom('TGraph'):
				continue
			if o.InheritsFrom('TH1'):
				continue
			stext.append(' '.join([o.GetName(), o.Class().GetName(), o.GetOption()]))
			if o.Class().GetName() == 'TLegend':
				# TLegend::GetListOfPrimitives() triggers a crash when clearing (redraw) the gPad/Canvas
				# this is why we are unable to iterate on the TLegend items...
				stype = '#legend'
				items = ''
				# l = o.GetListOfPrimitives()
				# l = []
				if '#c' in o.GetOption().split():
					stype = '#comment'
					# for p in l:
					# 	items = items + ' item={}'.format(p.GetLabel())
				if '#l' in o.GetOption().split():
					stype = '#legend'
				lposs = '{:.3},{:.3},{:.3},{:.3},'.format(o.GetX1NDC(), o.GetY1NDC(), o.GetX2NDC(), o.GetY2NDC())
				if len(items) == 0:
					stext.append(' '.join([stype, lposs, 'tx_size=', str(o.GetTextSize())]))
				else:
					stext.append(' '.join([stype, lposs, items, 'tx_size=', str(o.GetTextSize())]))
		return stext

	def dumpFeatures(self):
		# NOTE:
		print '-----'
		print '[i] Features of',
		for s in self.features_text():
			print s
		print

	def copyToClipperFeatures(self):
		if not pyperclip.is_available():
			# print >> sys.stderr, '[e] no pyperclip functionality available'
			print '[w] no pyperclip functionality available'
		try:
			print '[i] features copied to clipboard'
			sf = self.features_text()
			pyperclip.copy('\n'.join(sf))
		except:
			print '[e] pyperclip.copy failed.'

	def draw(self, mf):
		print '[i]', mf
		print '[i] DrawFrame {} drawing MetaFigure {}'.format(self.name, mf.name)
		self.mf = mf
		if self.canvas:
			if self.canvas.GetCanvas():
				self.canvas.GetCanvas().Clear()
				self.canvas.GetCanvas().cd()
				# consider here adding a handler for more that 1 figure in a draw file
				try:
					# print '[d] drawing', mf.name
					mf.draw(no_canvas=True, add_dummy=True)
				except:
					print '[e] something went wrong with drawing...', self.fname, 'figure number:', self.draw_figure
				# self.canvas.GetCanvas().Modified()
				self.canvas.GetCanvas().Update()
			else:
				'[e] get canvas failed for', self.name
		else:
			print '[e] no canvas?', self.name

def setup_style(args):
	# r.gROOT.Reset()
	r.gStyle.SetScreenFactor(1)
	if not args.keep_stats:
		r.gStyle.SetOptStat(0)
	if not args.keep_title:
		r.gStyle.SetOptTitle(0)
	if not args.no_double_ticks:
		r.gStyle.SetPadTickY(1)
		r.gStyle.SetPadTickX(1)
	# r.gStyle.SetErrorX(0) #not by default; use X1 to show the x-error with ol
	r.gStyle.SetEndErrorSize(0)

	# added on 01.02.2017
	r.gStyle.SetLabelSize(0.05, "X")
	r.gStyle.SetLabelSize(0.05, "Y")

	r.gStyle.SetTitleOffset(1.2, "X")
	r.gStyle.SetTitleOffset(1.0, "Y")

	r.gStyle.SetTitleSize(0.06, "X")
	r.gStyle.SetTitleSize(0.06, "Y")

	r.gStyle.SetPadTopMargin(0.1)
	r.gStyle.SetPadBottomMargin(0.1)
	r.gStyle.SetPadLeftMargin(0.1)
	r.gStyle.SetPadRightMargin(0.1)

	NRGBs = 5
	# NCont = 255
	NCont = 100

	from array import array
	stops = array('d', [0.00, 0.34, 0.61, 0.84, 1.00])
	red   = array('d', [0.00, 0.00, 0.87, 1.00, 0.51])
	green = array('d', [0.00, 0.81, 1.00, 0.20, 0.00])
	blue  = array('d', [0.51, 1.00, 0.12, 0.00, 0.00])
	r.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
	# r.gStyle.SetNumberContours(NCont)

	if args.mono_palette and not args.color:
		# colNum = 30
		# palette = []
		# for i in range(0, colNum):
		# 	# color = r.TColor(1001+i, pow(i/((colNum)*1.0),0.3), pow(i/((colNum)*1.0),0.3), 0.5*(i/((colNum)*1.0)),"")
		# 	fi = i * 1.0
		# 	# color = r.TColor(1001+i, pow(fi/((colNum)*1.0),0.3), pow(fi/((colNum)*1.0),0.3), 0.5*(fi/((colNum)*1.0)),"")
		# 	color = r.TColor(1001 + i, i + 1, i + 1, 0)
		# 	palette.append(1001 + i)
		# 	# if(color)
		# palette_i = array('i', palette)
		# r.gStyle.SetPalette(colNum, palette_i)

		palette = []
		paletteSize = 1024
		rgb = [	0.80, 0.55, 0.40,
				0.85, 0.60, 0.45,
				0.90, 0.65, 0.50,
				0.95, 0.70, 0.55,
				1.,   0.75, 0.60,
				1.,   0.80, 0.65,
				1.,   0.85, 0.70,
				1.,   0.90, 0.75,
				1.,   0.95, 0.80,
				1.,   1.,   0.85]
		for i in range(0, paletteSize):
			# palette.append(r.TColor.GetColor(rgb[i * 3], rgb[i * 3 + 1], rgb[i * 3 + 2]))
			palette.append(r.TColor.GetColor(1. - (i * 1.0) / paletteSize, 1. - (i * 1.0) / paletteSize, 1. - (i * 1.0) / paletteSize))
		palette_i = array('i', palette)
		r.gStyle.SetPalette(paletteSize, palette_i)


def main():
	parser = argparse.ArgumentParser(description='draw a .draw file', prog=os.path.basename(__file__))
	parser.add_argument('fname', help='what file to draw', type=str, default="", nargs="?")
	parser.add_argument('--keep-stats', help='keep statistics in the histograms', action='store_true')
	parser.add_argument('--keep-title', help='keep title in canvas', action='store_true')
	parser.add_argument('--no-double-ticks', help='no double ticks - whatever this is', action='store_true')
	parser.add_argument('--mono-palette', help='b&w', action='store_true', default=True)
	parser.add_argument('--no-date', help='ignore #date', action='store_true', default=False)
	parser.add_argument('--color', help='not b&w', action='store_true', default=False)
	parser.add_argument('--preent', help='just preent - specify the file format: pdf, pdf1 (all in one file), png', type=str)
	parser.add_argument('--quit', help='quit after showing the windo - good for --print and --quit combination', action='store_true')
	args = parser.parse_args()
	print '[i] arguments:', args
	meta_draw.MetaFigure.show_date = not args.no_date
	setup_style(args)
	tmp_file = None
	if not args.fname:
		tmp_file = tempfile.NamedTemporaryFile(mode='rw', delete=False)
		args.fname = tmp_file.name
	if not os.path.isfile(args.fname):
		args.fname = None
	if args.fname:
		fn, fext = os.path.splitext(args.fname)
		if fext == '.root':
			import make_draw_files as mdf
			print '[i] make draw file...'
			# args.fname = mdf.make_draw_file(args.fname)
			args.fname = mdf.make_draw_file_smart_group(args.fname)
		print '[i] working with ', args.fname
		window = FileView(0, 600, 600, args.fname, args)
		window.RaiseWindow()
		r.gApplication.Run()
	if tmp_file:
		tmp_file.close()


if __name__ == '__main__':
	main()
