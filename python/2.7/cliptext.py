#!/usr/bin/env python

import os
import argparse
import Tkinter as tk

#from Tkinter import *
#def main(args):
#	root = Tk()
#	S = Scrollbar(root)
#	T = Text(root, height=4, width=50)
#	S.pack(side=RIGHT, fill=Y)
#	T.pack(side=LEFT, fill=Y)
#	S.config(command=T.yview)
#	T.config(yscrollcommand=S.set)
#	quote = ' '.join(args.text)
#	T.insert(END, quote)
#	T.pack(side=LEFT)
#	S.pack(side=RIGHT, fill=Y)
#	mainloop(  )

#def main(stext):
#	master = tk.Tk()
#	msg = tk.Message(master, text = stext)
#	msg.config(bg='white', font=('fixed', 12), takefocus=True, width=250)
#	msg.pack()
#	button = tk.Button(master, text='Close', command=master.destroy)
#	button.pack()
#	tk.mainloop()

# http://www.booneputney.com/development/tkinter-copy-to-clipboard/

master = tk.Tk()

def copy_text_to_clipboard(stext):
	master.clipboard_clear()  # clear clipboard contents
	master.clipboard_append(stext)  # append new value to clipbaord

def main(stext):
	S = tk.Scrollbar(master)
	T = tk.Text(master, height=20, width=80)
	S.pack(side=tk.RIGHT, fill=tk.Y)
	T.pack(side=tk.LEFT, fill=tk.Y)
	S.config(command=T.yview)
	T.config(yscrollcommand=S.set)
	T.insert(tk.END, stext)
	T.pack(side=tk.LEFT, fill=tk.X)
	S.pack(side=tk.RIGHT, fill=tk.Y)

	button_copy = tk.Button(master, text='Copy', command=copy_text_to_clipboard(stext))
	button_copy.pack(fill=tk.Y)
	button_close = tk.Button(master, text='Close', command=master.destroy)
	button_close.pack(fill=tk.Y)

	# T.config(state=tk.DISABLED)

	copy_text_to_clipboard(stext)

	tk.mainloop()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='popup text & clip', prog=os.path.basename(__file__))
	parser.add_argument('-t', '--text', help='what to pop', type=str, default="", nargs='+')
	parser.add_argument('-f', '--file', help='pop from files', type=str, default="", nargs='+')
	parser.add_argument('-s', '--silent', help='do not show the widget', action="store_true")
	args = parser.parse_args()
	stext = ''
	if args.text:
		stext = ' '.join(args.text)
	if args.file:
		for fn in args.file:
			try:
				cl = []
				with open(fn, 'r') as f:
					cl = f.readlines()
				for l in cl:
					stext = stext + l
			except:
				pass
	if stext:
		if args.silent:
			copy_text_to_clipboard(stext)
		else:
			main(stext)
