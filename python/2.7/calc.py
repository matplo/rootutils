#!/usr/bin/env python

from eval_string import NumericStringParser
import sys

def main():
	s = ' '.join(sys.argv[1:]).replace('x','*').replace('[','(').replace(']',')')
	parser = NumericStringParser()
	try:
		v = parser.eval(s)
	except:
		v = '?'
	print s,'=',v

if __name__ == '__main__':
	main()
