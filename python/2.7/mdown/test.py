#!/usr/bin/env python

import pyutils as pyut

import markdown
md = markdown.Markdown(extensions = ['markdown.extensions.meta'])
strings = pyut.load_file_to_strings('test.txt')
text = '\n'.join(strings)
html = md.convert(text)
print md.Meta

