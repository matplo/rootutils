#!/usr/bin/env python

from configobj import ConfigObj
import IPython
import argparse
import os
import sys
import dbgu

import eval_string

def get_value(s, op=None, vdefault=None):
	if type(s) != str:
		s = '{}'.format(s)
	retval = 0
	try:
		np = eval_string.NumericStringParser()
		retval = np.eval(s)
	except:
		if vdefault is None:
			print >> sys.stderr, '[e] unable to convert to a value:[',s,']',type(s), len(s)
		else:
			retval = vdefault
	if op != None:
		if op == int:
			rest = retval - op(retval)
			if rest > 0.5:
				rest = int(1)
			else:
				rest = 0
			retval = op(retval) + rest
	return retval

class ConfigObject(object):
	def __init__(self, input, mode = 0):
		self._config = None
		self._section = None
		self._fname = None
		if mode == 0:
			# mode == 0 is file
			self.load_from_file(input)
		if mode == 1:
			# mode == 1 is config
			self.load_from_config(input)
		if mode == 2:
			# mode == 2 is section
			self.load_from_section(input)

	def get(s):
		return self.__getattribute__(s)

	def load_from_file(self, input):
		self._fname = input
		self._config = ConfigObj(input, raise_errors = True)
		for s in self._config.sections:
			self.load_from_section(self._config[s])
		self._process_scalars(self._config)

	def load_from_config(self, input):
		self._config = input
		for s in self._config.sections:
			self.load_from_section(self._config[s])
		self._process_scalars(self._config)

	def load_from_section(self, input):
		self._section = input
		self._import_atributes(self._section)

	def _import_atributes(self, section):
		self._process_section(section)

	def _process_scalars(self, section, varname_prefix=None):
		for i,s in enumerate(section.scalars):
			if varname_prefix:
				varname = '{}_{}'.format(varname_prefix, s)
			else:
				varname = s
			#print varname, section.scalars[i], section[section.scalars[i]]
			sv = section[section.scalars[i]]
			v = sv
			if s[:2] == 'f_':
				v = get_value(sv, float)
			if s[:2] == 'i_':
				v = get_value(sv, int)
			if s[:2] == 's_':
				v = str(sv)
			setattr(self, varname, v)

	def _process_section(self, section):
		varname_prefix = self.make_name(section)
		if len(section.sections):
			for s in section.sections:
				self._process_section(section[s])
		self._process_scalars(section, varname_prefix)

	def _setting(self, what, section):
		retval = None
		try:
			retval = section[what]
		except:
			# check the parent whether setting exists
			retval = None
		if retval is None:
			if section.parent.name:
				retval = self._setting(what, section.parent)
		return retval

	def make_name(self, section):
		s = section
		name = [section.name]
		while s:
			if s.parent.name:
				name.append(s.parent.name)
			else:
				break
			s = s.parent
		name.reverse()
		return '_'.join(name)

def test(args):
	conf = '''
	s_x = unbound?
	f_x = 'PI * 2'
	[test]
	i_bela = 2.6
	s_something = 1E6
	[[sub]]
	f_ala = 1.0
	'''

	fname = args.fname + '_test'

	with open(fname, 'w') as f:
		f.write(conf)

	print '[i] loading from a file...'
	obj = ConfigObject(fname, mode=0)
	dbgu.debug_obj(obj)
	print

	print '[i] loading from a config...'
	config = ConfigObj(fname, raise_errors = True)
	obj2 = ConfigObject(config, mode=1)
	dbgu.debug_obj(obj2)
	print

	for s in config.sections:
		print '[i] loading from section...',s
		objx = ConfigObject(config[s], mode=2)
		dbgu.debug_obj(objx)
	print


if __name__=="__main__":
	parser = argparse.ArgumentParser(description='execute tdraw based on the config file', prog=os.path.basename(__file__))
	parser.add_argument('-i', '--ipython', help='end with IPython prompt', action='store_true')
	parser.add_argument('fname', type=str, help='file name to load the class from')
	parser.add_argument('--test', help='test with a selfwritten file', action='store_true')

	args = parser.parse_args()

	if args.test:
		test(args)
	else:
		obj = ConfigObject(args.fname, mode=0)
		dbgu.debug_obj(obj)

	if args.ipython:
		IPython.embed()
