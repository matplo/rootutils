#!/usr/bin/env python

import ROOT
import ol
import sys
import tutils
import pyutils

class plot:
    def __init__(self, inlist):
        self.data = inlist
        self.name = self.find_name()
        self.ol   = ol.ol(self.name)
        self.logy = self.is_logy()
        self.add_objects()
        self.x = []
        self.y = []
        self.z = []
        self.find_xyz()
        self.xtitle = None
        self.ytitle = None
        self.ztitle = None
        self.find_axis_titles()
        self.min  = None
        self.max  = None
        self.find_min_max()
        self.dopt, tmp = self.find_tag('#dopt ')
        if self.dopt == None:
            self.dopt = ''
        self.normalize = None
        self.find_normalize()
        
    def find_normalize(self):
        self.normalize, tmp = self.find_tag('#normalize ')
            
    def find_min_max(self):
        mins, tmp = self.find_tag('#min ')
        if pyutils.is_number(mins):
            self.min = float(mins)
        maxs, tmp = self.find_tag('#max ')
        if pyutils.is_number(maxs):
            self.max = float(maxs)
        
    def find_axis_titles(self):
        self.xtitle, index = self.find_tag('#xtitle ')
        self.ytitle, index = self.find_tag('#ytitle ')
        self.ztitle, index = self.find_tag('#ztitle ')
        
    def find_xyz(self):
        sx, i = self.find_tag('#x ')
        if sx != None:
            for vs in sx.split(' '):
                if pyutils.is_number(vs):
                    v = float(vs)
                    self.x.append(v)
        sx, i = self.find_tag('#y ')
        if sx != None:
            for vs in sx.split(' '):
                if pyutils.is_number(vs):
                    v = float(vs)
                    self.y.append(v)
        sx, i = self.find_tag('#z ')
        if sx != None:
            for vs in sx.split(' '):
                if pyutils.is_number(vs):
                    v = float(vs)
                    self.z.append(v)                    
                                        
    def find_name(self):
        for l in self.data:
            if '#figname' in l:
                name = l.replace('#figname ', '')
        return name

    def find_next_tag(self, tag, index_start = None, index_end = None):
        if index_start == None:
            index_start = -1
        if index_end == None:
            index_end = len(self.data)
        tag_string = None
        tag_index  = None
        #print '[d] looking for',tag,'start from',index_start,'+1'
        for index in range(len(self.data)):
            if index > index_start and index < index_end:
                l = self.data[index].strip('\n')
                #print '[d] line:',index,l
                if tag in l:
                    tag_string = l.replace(tag, '')
                    tag_index = index
                    #print '[d] found tag:',tag,'at',index
                    break
        return tag_string, tag_index

    def find_tag(self, tag):
        # by definition returns the last tag
        index_start = -1
        index_end = len(self.data)
        tag_string = None
        tag_index  = None
        #print '[d] looking for',tag,'start from',index_start,'+1'
        for index in range(len(self.data)):
            if index > index_start and index < index_end:
                l = self.data[index].strip('\n')
                #print '[d] line:',index,l
                if tag in l:
                    tag_string = l.replace(tag, '')
                    tag_index = index
                    #print '[d] found tag:',tag,'at',index
        return tag_string, tag_index
    
    def find_next_file_tag(self, index):
        fileok = False
        fname, findex = self.find_next_tag('#file ', index)
        return fname, findex

    def process_object_line(self, l):
        elems = l.split(';')
        if len(elems) > 0:
            name = elems[0]
        if len(elems) > 1:
            title = elems[1]
        if len(elems) > 2:
            dopt = elems[2]
        elems_dict = { 'name': name,
                        'title': title,
                        'drawopt': dopt
                        }
        return elems_dict
        
    def add_objects(self):
        findex = -1
        files = []
        while findex != None:
            fname, findex = self.find_next_file_tag(findex)
            if findex != None:
                files.append([fname, findex])

        for i in range(len(files)):
            f = files[i]
            fname        = f[0]
            oindex_start = f[1]            
            try:
                f = open(fname)
                f.close()
            except:
                print '[w] skipping:',oindex_start,fname
                continue            
            if i+1 >= len(files):
                oindex_end = len(self.data)
            else:
                oindex_end = files[i+1][1]
            oindex = oindex_start
            while oindex != None:
                oname, oindex = self.find_next_tag('#name ', oindex, oindex_end)
                if oindex >= 0:
                    #print '[d] adding:',oname,'from:',fname
                    d = self.process_object_line(oname)
                    self.ol.add_from_file(d['name'], fname, d['title'], d['drawopt'])
                    
    def is_logy(self):
        for l in self.data:
            if '#logy' in l:
                return True                    
        return False

    def draw(self):
        self.ol.make_canvas()
        self.ol.reset_axis_titles(self.xtitle, self.ytitle, self.ztitle)
        if len(self.x) > 1:
            self.ol.zoom_axis(0, self.x[0], self.x[1])
        if len(self.y) > 1:
            self.ol.zoom_axis(1, self.y[0], self.y[1])
        if len(self.z) > 1:
            self.ol.zoom_axis(2, self.z[0], self.z[1])
        if self.normalize != None:
            width = False
            if 'width' in self.normalize:
                width = True
            update = False
            if 'update' in self.normalize:
                update = True
            if 'self' in self.normalize:
                self.ol.normalize_self(width, update)
            else:                
                if pyutils.is_number(self.normalize):
                    v = float(self.normalize)
                    if v != 0:
                        self.ol.scale(1./v)
                                    
        self.ol.draw(self.dopt, self.min, self.max, self.logy)
        if self.logy:
            ROOT.gPad.SetLogy()
        self.ol.self_legend()
        self.ol.update()
        
def process_fig(intext):
    pl = plot(intext)
    pl.draw()
    return pl

def process_text(intext):
    newfig = []
    plots  = []
    for l in intext:
        if '#endfig' in l:
            pl = process_fig(newfig)
            newfig = []
        else:
            is_comment = False
            if '##' in l:
                if l.index('##') == 0:
                    is_comment = True
            if is_comment == False:
                newfig.append(l)
    plots.append(pl)
    return plots

def process_file(fname):
    print '[i] processing:',fname
    with open(fname) as f:
        intext = f.readlines()
        plots = process_text(intext)
    return plots

if __name__=="__main__":
    tutils.setup_basic_root()
    fin = sys.argv[1]
    plots = process_file(fin)    
    tutils.wait()            

#    except:
#        print >> sys.stderr, '[e] error processing input'
    
