import fnmatch
import os

import sys
import subprocess
import shlex
import signal
import time

import string
import random

from eval_string import get_value

def load_file_to_strings(fname):
    outl = []
    if fname != None:
        if os.path.isfile(fname):
            with open(fname) as f:
                outl = [l.strip('\n') for l in f.readlines()]
    else:
        f = sys.stdin
        outl = [l.strip('\n') for l in f.readlines()]
    return outl

def to_file_name(s):
        return "".join([x if x.isalnum() else "_" for x in s])

def find_files(rootdir='.', pattern='*'):
    return [os.path.join(rootdir, filename)
            for rootdir, dirnames, filenames in os.walk(rootdir)
            for filename in filenames
            if fnmatch.fnmatch(filename, pattern)]

def is_number(s):
    ss = str(s)
    try:
        float(ss) # for int, long and float
    except ValueError:
        try:
            complex(ss) # for complex
        except ValueError:
            return False
    return True

def float_or_None(s):
    ss = str(s)
    retval = None
    try:
        retval = float(ss)
    except ValueError:
        retval = None
    return retval

def strip_non_numbers(s):
    import re
    non_decimal = re.compile(r'[^\d.]+')
    rets = non_decimal.sub(' ', s).replace('. ', ' ').rstrip('.').lstrip(' ')
    return rets

def sorted_list_by_number(l):
    retlist = []
    for a in l:
        if len(retlist) == 0:
            retlist.append(a)
            continue
        va = float(strip_non_numbers(a).split(' ')[0])
        for b1 in retlist:
            vb1 = float(strip_non_numbers(b1).split(' ')[0])
            idx = retlist.index(b1)
            if va <= vb1:
                retlist.insert(idx, a)
                break
        if a not in retlist:
            retlist.append(a)
    return retlist

def build_string(arr, s = '_'):
    sret = ''
    for a in arr:
        if a == arr[0]:
            pass
        else:
            sret = sret + s
        if is_number(a):
            sa = str(a)
        else:
            sa = a
        sret = sret + sa
    return sret

def is_arg_set(arg=''):
    for a in sys.argv:
        if a==arg:
            return True
    return False

def get_arg_with(arg=''):
    retval = None
    maxl = len(sys.argv)
    for i in range(0,maxl):
        if sys.argv[i]==arg and i < maxl-1:
            retval=sys.argv[i+1]
    return retval

def call_cmnd(cmnd='', verbose=False):
    if verbose==True:
        print '[i] calling',cmnd
    args = shlex.split(cmnd)
    try:
        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
    except OSError as e:
        out = 'Failed.'
        err = ('Error #{0} : {1}').format(e[0], e[1])
        if verbose==True:
            print '[i]',out
            print '[e]',err
    return out,err

sub_p = None
exit_signal = False
print_first = False
timer = time.time()

exit_signal = False
print_first = False
timer = time.time()

def signal_handler(signum, frame):
    global sub_p
    global exit_signal
    global print_first
    global timer
    interval = time.time() - timer
    timer=time.time()
    if interval < 0.5:
        exit_signal = True
    else:
        exit_signal = False
    if interval > 60 or exit_signal==True or print_first==False:
        print
        if exit_signal==False:
            print '[i CRTL-C] signal #',signum,'caught; do it quickly twice to exit'
            if print_first==False:
                if sub_p!=None:
                    print '    the kid:',sub_p
            else:
                print '    interval:',interval,'s => exit condition:',exit_signal
        else:
            print '[i CRTL-C] interval:',interval,'s => exit condition:',exit_signal
        print_first=True

    if exit_signal==True:
        if sub_p!=None:
            sub_p.send_signal(signal.SIGKILL)
        sys.exit(0)

def wait():
    print '[i] press twice CRTL+C (fast consequtive) to exit.'
    signal.signal(signal.SIGINT, signal_handler)
    while 1:
        time.sleep(10) # this actually does not matter as long as large
        pass

def random_string(prefix='', ns = 30):
    lst = [random.choice(string.ascii_letters + string.digits) for n in xrange(ns)]
    return str(prefix)+''.join(lst)

def remove_duplicates(l):
    newl = []
    for o in l:
        if o in newl:
            continue
        newl.append(o)
    return newl

def substring(s, s1, s2=None, vdefault=None):
    retval = vdefault
    idx1 = s.find(s1) + len(s1)
    try:
        if s2:
            idx2 = s.find(s2)
        else:
            idx2 = len(s)
    except:
        idx1 = 0
        idx2 = len(s)
        if vdefault:
            retval = vdefault
    retval = s[idx1:idx2]
    return retval

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
