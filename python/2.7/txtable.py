#!/usr/bin/env python

def print_table(t, sep = '   '):
    ncols = max(len(row) for row in t)
    maxwcols = []
    for i in range(ncols):
        maxwcols.append(0)        
    for row in t:
        for nc in range(len(row)):
            c = row[nc]
            strlen = len(str(c))
            #print nc,c,strlen
            if maxwcols[nc] < strlen:
                #print nc,c,strlen,'=>',maxwcols[nc]
                maxwcols[nc] = strlen

    #print '[i] number of columns:',ncols
    #print '    max col width:',maxwcols

    for row in t:
        str_row = []
        for c in row:
            strx = str(c).ljust(maxwcols[row.index(c)])
            str_row.append(strx)
        print sep.join(str_row)

def get_table(t, sep = '   '):
    ncols = max(len(row) for row in t)
    maxwcols = []
    for i in range(ncols):
        maxwcols.append(0)        
    for row in t:
        for nc in range(len(row)):
            c = row[nc]
            strlen = len(str(c))
            #print nc,c,strlen
            if maxwcols[nc] < strlen:
                #print nc,c,strlen,'=>',maxwcols[nc]
                maxwcols[nc] = strlen

    #print '[i] number of columns:',ncols
    #print '    max col width:',maxwcols

    out = []
    for row in t:
        str_row = []
        for c in row:
            strx = str(c).ljust(maxwcols[row.index(c)])
            str_row.append(strx)
        out.append(sep.join(str_row))
    return out
    
def main():
    table = []
    table.append([0, 1, 2, 3.23])
    table.append([0, 1, 'ala ma', 3.23, 0])
    print_table(table)

if __name__=="__main__":
    main()
