#!/usr/bin/env python

import os
import markdown
from string import atof,atoi

class MDHist(object):
	def __init__(self, text):
		self.text = text.replace('\t', ' ')
		self.fname = self.text.split(' ')[0]
		self.hname = self.text.split(' ')[1]
		#self.title = self.get('title')
		#self.title = self['title']

	def __getitem__(self, opt):
		retvals = []
		si = self.text.split(opt+'=')
		for s in si[1:]:
			opttx = s.split('=')[0]
			if len(opttx)>0:
				sopttx = opttx.split(' ')
				del sopttx[-1]
				retvals.append(' '.join(sopttx))
		if len(retvals) < 1:
			retvals.append(None)
		return retvals[-1]

	def __repr__(self):
		return 'fname:[{}] hname:[{}] title:[{}] dopt:[{}]'.format(self.fname, self.hname, str(self['title']), str(self['dopt']))

class MDFigure(object):
	def __init__(self, text):
		self.data = text
		self.md = markdown.Markdown(extensions = ['markdown.extensions.meta'])
		self.html = self.md.convert(text)
		#print self.md.Meta

	def string(self, key):
		try:
			smeta = self.md.Meta[key]
		except:
			return ''
		return ' '.join(smeta)

	def strings(self, key, n=None):
		try:
			smeta = self.md.Meta[key]
		except:
			return ['']
		s = ' '.join(smeta)
		s = s.replace('\t', ' ')
		si = s.split(' ')
		retvals = []
		if n==None:
			n=len(si)
		for i in xrange(n):
			val = ''
			if len(si) > i:
				val = si[i]
			retvals.append(val)
		return retvals

	def floats(self, key, n=None):
		retvals = []
		rs = self.strings(key, n)
		for s in rs:
			try:
				retvals.append(atof(s))
			except:
				pass
		return retvals

	def options(self, key, opt):
		retvals = []
		try:
			smeta = self.md.Meta[key]
		except:
			retvals.append('{} key not found'.format(key))
			return retvals
		for sm in smeta:
			si = sm.split(opt+'=')
			for s in si[1:]:
				opttx = s.split('=')[0].split(' ')
				if len(opttx)>1:
					soptx = ' '.join(opttx[:len(opttx)-1])
				else:
					soptx = opttx[0]
				retvals.append(soptx)
		return retvals

	def option(self, key, opt):
		retvals = self.options(key, opt)
		if len(retvals) < 1:
			retvals.append(None)
		return retvals[-1]

	def objects(self, key='h'):
		retvals = []
		try:
			smeta = self.md.Meta[key]
		except:
			retvals.append('{} key not found'.format(key))
			return retvals			
		for sm in smeta:
			smm = ''.join(sm)
			h = MDHist(smm)
			retvals.append(h)
		return retvals

	def demo(self):
		print 
		print '---> new figure <---'
		print self.md.Meta
		print 'geom 2 floats:',self.floats('geometry', 2)
		print 'geom 1 float: ',self.floats('geometry', 1)
		print 'title:', self.strings('title')
		print 'title:', self.string('title')
		print 'logz:',self.option('options','logz')
		hists = self.objects('h')
		print 'n objects:',len(hists)
		for h in hists:
			print h
		print 'now fit objects...'
		hists = self.objects('fit')
		for h in hists:
			print h

class MDFigureFile(object):
	def __init__(self, fname):
		self.data = self.load_file_to_strings(fname)
		self.text = '\n'.join(self.data)
		self.fig_texts = self.text.split('figure:')
		self.figures = []
		for ftx in self.fig_texts[1:len(self.fig_texts)]:
			ftxs = 'figure:{}'.format(ftx)
			mdfig = MDFigure(ftxs)
			self.figures.append(mdfig)

	def load_file_to_strings(self, fname):
		outl = []
		if fname != None:
			if os.path.isfile(fname):
				with open(fname) as f:
					outl = [l.strip('\n') for l in f.readlines()]
		else:
			f = sys.stdin
			outl = [l.strip('\n') for l in f.readlines()]        

		for l in outl:
			if len(l.strip('\n')) < 1:
				outl.remove(l)
		return outl

	def demo(self):
		for f in self.figures:
			f.demo()

def main():
	mdfilefig = MDFigureFile('test.txt')
	mdfilefig.demo()

if __name__ == '__main__':
	main()
