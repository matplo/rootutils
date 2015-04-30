from os import path

def not_none(a,b):
    if b == None:
        return a
    return b

import traceback
def debug(*msg):
    stack = traceback.extract_stack()
    #print stack[0]
    #print len(stack)
    filename, codeline, funcName, text = stack[-2] #was [-2]
    #funcName = stack[0][-1] + ' ({})'.format(codeline) + ' ' + funcName + ' '
    #if 'debug(' in str(stack[1][-1]):
    #    funcName = '({}) '.format(codeline) + stack[0][-1]
    #else:
    #    funcName =  '({}) '.format(codeline) + stack[0][-1] + '-' + stack[1][-1] 
    #return funcName
    slineno = '({})'.format(codeline)
    out_str = path.basename(filename) + slineno + '::' + funcName
    msg_str = []
    if len(msg) == 0:
        msg_str.append('begin')
    else:
        for e in msg:
            msg_str.append(str(e))
    if msg_str[0] == '.':
        msg_str[0] = 'done.'
    if msg_str[0] == '-':
        msg_str[0] = ''
        print '   ',out_str,':',' '.join(msg_str)
    else:
        if msg_str[0] == 'e':
            msg_str.remove(msg_str[0])
            print '[error]',out_str,':',' '.join(msg_str)
        else:
            if msg_str[0] == '|':
                msg_str[0] = ''
                print '[d]',out_str,':\n',''.join(msg_str)
            else:
                print '[d]',out_str,':',' '.join(msg_str)

def debug_obj(obj, msg=' ', truncate=50):
    debug ( '|', msg, type(obj), '\n', Inspector(obj).table_members_basic(truncate=truncate) )
    try:
        obj._debug()
    except:
        pass
    
import inspect
from tabulate import tabulate
class Inspector:

    def __init__(self, a):
        self.a = a
        
    def table_members_basic(self, truncate=50, skip='__'):
        members = inspect.getmembers(self.a)
        retval = [ ['type','name','value'] ]
        for name,value in members:
            if inspect.ismethod(value) == False:
                if skip == '__' and name[0:2] != '__':
                    t = type(getattr(self.a, name))
                    if truncate > 0 and len(str(value)) > truncate:
                        value = str(value)[:truncate]+'...'
                    retval.append([t, name, value])
        return tabulate(retval, headers='firstrow')
    
    def table_members_all(self, skip='__'):
        members = inspect.getmembers(self.a)
        retval = [ ['type','name','value'] ]
        for name,value in members:
            if skip == '__' and name[0:2] != '__':
                t = type(getattr(self.a, name))
                retval.append([t, name, value])
        return tabulate(retval, headers='firstrow')
