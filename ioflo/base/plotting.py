"""plotting.py  wradia plotting module

"""
#print "module %s" % __name__

#imports
import exceptions
import pickle
import pdb
import string
import math
import types
import socket
import os
import time

from numpy import *
from math import *
from pylab import *

#Function Definitions

def PlotPosition(path = './test/logs/', name = "position.txt", 
                 figNum = 1, figsize = (6,6)):
    """Function to automatically generate plot of vehicle path
       figsize is (width, height)
       needs from pylab import *
    """
    fullname = path + name
    fp = open(fullname, 'r')
    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    plotTitle = "Vehicle Position\n" # + name.split('/')[-1] #strip off path

    chunks = fp.readline().split('\t') #read header labels
    ni = None
    ei = None
    for i, chunk in enumerate(chunks):
        if 'position.north' in chunk:
            if ni is None: #get first occurence
                ni = i
        if 'position.east'in chunk:
            if ei is None: #get first occurence
                ei = i

    if (ni is None) or (ei is None):
        print "Bad header format can't find all headers %s" % str(chunks)
        return

    count = 0
    norths = []
    easts = []
    line = fp.readline() #empty if end of file
    while (line):
        count  += 1 #inc line counter
        chunks = line.split('\t')
        norths.append(chunks[ni])
        easts.append(chunks[ei])

        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )
    subplot(111)

    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    n = array(norths)
    e = array(easts)
    plot(e,n, label = 'Vehicle')


    grid(True)
    legend(loc = 'upper right') #has to come after plot
    axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    b = [a[0] - 50, a[1] + 50, a[2] - 50, a[3] + 50]
    axis(b)

    show()
    draw()
    ion()


def PlotGPSPosition(path = './test/logs/', name = "position.txt",
                    figNum = 1, figsize = (6,6)):
    """Function to automatically generate plot of vehicle position
       figsize is (width, height)
       needs from pylab import *
    """
    fullname = path + name
    fp = open(fullname, 'r')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    plotTitle = "Vehicle Position\n" # + name.split('/')[-1] #strip off path

    chunks = fp.readline().split('\t') #read header labels
    ni = None
    ei = None
    gpni = None
    gpei = None


    for i, chunk in enumerate(chunks):

        if 'position.north' in chunk:
            if ni is None: #get first occurence
                ni = i
        elif 'position.east'in chunk:
            if ei is None: #get first occurence
                ei = i
        elif 'gpspos.north' in chunk:
            if gpni is None: #get first occurence
                gpni = i
        elif 'gpspos.east'in chunk:
            if gpei is None: #get first occurence
                gpei = i


    if (ni is None) or (ei is None) or (gpni is None) or (gpei is None):
        print "Bad header format can't find all headers %s" % str(chunks)
        return

    count = 0
    ns = []
    es = []
    gpns = []
    gpes = []

    line = fp.readline() #empty if end of file
    while (line):
        count  += 1 #inc line counter
        chunks = line.split('\t')
        ns.append(chunks[ni])
        es.append(chunks[ei])
        gpns.append(chunks[gpni])
        gpes.append(chunks[gpei])

        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )
    subplot(111)

    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    n = array(ns)
    e = array(es)
    plot(e,n, label = 'Ideal Position')

    n = array(gpns)
    e = array(gpes)
    plot(e,n, label = 'GPS Position')


    grid(True)
    legend(loc = 'upper right') #has to come after plot
    axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    b = [a[0] - 50, a[1] + 50, a[2] - 50, a[3] + 50]
    axis(b)

    show()
    draw()
    ion()


def PlotPositions(path = './test/logs/', name = "position.txt",
                  figNum = 1, figsize = (6,10)):
    """Function to automatically generate plot of vehicle position
       figsize is (width, height)
       needs from pylab import *
    """
    fullname = path + name
    fp = open(fullname, 'r')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    plotTitle = "Vehicle Position\n" # + name.split('/')[-1] #strip off path

    names = [] #plot names
    nis = [] #north indexes
    eis = [] # east indexes

    chunks = fp.readline().strip().split('\t') #read header labels

    for i, chunk in enumerate(chunks):
        if 'north' in chunk:
            nis.append(i)
            name = chunk.split('.')[0]
            if name not in names:
                names.append(name)
        elif 'east' in chunk:
            eis.append(i)
            name = chunk.split('.')[0]
            if name not in names:
                names.append(name)

    #print names
    #print nis
    #print eis

    if not names or (len(names) != len(eis)) or (len(eis) != len(nis)):
        print "Bad header format can't find all headers %s" % str(chunks)
        return


    data = []
    for i, name in enumerate(names):
        data.append(([],[])) #(norths, easts)

    line = fp.readline() #empty if end of file
    while (line):
        chunks = line.split('\t')

        for i, name in enumerate(names):
            data[i][0].append(chunks[nis[i]])
            data[i][1].append(chunks[eis[i]])

        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )
    subplot(111)

    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    for i, name in enumerate(names):
        n = array(data[i][0])
        e = array(data[i][1])

        plot(e,n, label = name)


    grid(True)
    legend(loc = 'upper left') #has to come after plot
    axis('scaled')
    xmin, xmax, ymin, ymax = axis()  #[xmin xmax ymin ymax]

    if xmax - xmin < 1000:
        c = (xmax + xmin) / 2.0
        xmin = c - 500.0
        xmax = c + 500.0
    b = [xmin - 50.0,  xmax + 50, ymin - 100, ymax + 10]
    #b = [a[0] - 50, a[1] + 50, a[2] - 100, a[3] + 10]
    axis(b)

    show()
    draw()
    ion()

def FilterByField(path = './test/logs/', filein = "data.txt", 
                  fileout = 'datafilter.txt',
                  label = 'depth',  value = 5.0, tolerance = 0.5):
    """Function to select only those data points that are at the desired
       value +- tolerance of loggee named label
    """

    fpin = open(path + filein, 'rU')

    linelog = fpin.readline()
    kind, rule, name = linelog.split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    lineheader = fpin.readline()
    chunks = lineheader.strip().split('\t') #read header labels
    print chunks

    from .odicting import odict
    indices = odict() 
    indices[label] = None #label index
    #could have list of multiple field labels that have to exist

    for i, chunk in enumerate(chunks): #gets first occurrence
        for key, index in indices.items():
            if (key in chunk) and (index == None):
                indices[key] = i #index

    for key, index in indices.items():
        if (index is None):
            print "Can't find  '%s' in header" % (key)
            return
        else:
            print "Index %s = %d " % (key, index)

    fpout = open(path + fileout, 'w')
    fpout.write(linelog) #write log type line
    fpout.write(lineheader) #write log header line

    line = fpin.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')

        if (value - tolerance) < float(chunks[indices[label]]) < (value + tolerance):
            fpout.write(line) #write log  line
        line = fpin.readline() #empty if end of file


    if fpin and not fpin.closed:
        fpin.close()

    if fpout and not fpout.closed:
        fpout.close()

def BoxLineSegs(north = 0.0, east = 0.0, track = 0.0, length = 0.0, width = 0.0):
    """Function to generate line seqmemnts of sides of box
       Returns list of  segments of form [s1,s2,s3,s4]
       Each segment s is a list of two tuples of form [(x1, y1), (x2, y2)]
       So return looks like
       [ [(x0,y0),(x1,y1)], 
         [(x1,y1),(x2,y2)], 
         [(x2,y2),(x3,y3)], 
         [(x3,y3),(x0,y0)] ]
       where x is the east coord and y is the north coord
       north is box relative north coord  of center bottom
       east is box relative east coord  of center bottom
       track is angle of center line of box from bottom to top
       length is length of box
       width is width of box
    """
    from .aiding import RotateFSToNE
    #aiding.RotateFSToNE(heading = -track, forward = pn, starboard = pe)
    lines = []

    # from bottom left to bottom right
    cf = north
    cs = east - width/2.0
    #rotate by track
    bln, ble = RotateFSToNE(heading = track, forward = cf, starboard = cs)

    cf = north
    cs = east + width/2.0
    #rotate by track
    brn, bre = RotateFSToNE(heading = track, forward = cf, starboard = cs)
    lines.append([(ble, bln), (bre, brn)])

    # from bottom right to top right
    cf = north + length
    cs = east + width/2.0
    #rotate by track
    trn, tre = RotateFSToNE(heading = track, forward = cf, starboard = cs)
    lines.append([(bre, brn), (tre, trn)])

    # from top right to top left
    cf = north + length
    cs = east - width/2.0
    #rotate by track
    tln, tle = RotateFSToNE(heading = track, forward = cf, starboard = cs)
    lines.append([(tre, trn), (tle, tln)])

    # from top left to bottom left
    lines.append([(tle, tln), (ble, bln)])

    return lines

def PlotSalinity4(path = './test/logs/', name = "position.txt",
                  depth = 5.0, tolerance = 0.5, 
                  north = 0.0, east = 0.0, track = 0.0, length = 0.0, width = 0.0,
                  figNum = 1, figsize = (6,6)):
    """Function to automatically generate plot of vehicle salinity vs position
       only plots those points that are at the given depth +- tolerance
       Also prints safety box center bottom at north east, track, length, width
       figsize is (width, height)
       needs from pylab import *
       http://www.scipy.org/Cookbook/Matplotlib/MulticoloredLine
       Uses LineCollections to speed things up
    """
    fullname = path + name
    fp = open(fullname, 'rU')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    ni = None #north index
    ei = None # east index
    si = None # salinity index
    di = None # depth index

    chunks = fp.readline().strip().split('\t') #read header labels
    print chunks

    for i, chunk in enumerate(chunks): #gets first occurrence
        if ('north' in chunk) and (ni == None):
            ni = i
        elif ('east' in chunk) and (ei == None):
            ei = i
        elif ('salinity') in chunk  and (si == None) :
            si = i
        elif ('depth') in chunk  and (di == None) :
            di = i

    print "ni = %d ei = %d si = %d di = %d" % (ni,ei,si, di)

    if (ni is None) or (ei is None) or (si is None) or (di is None) :

        print "Bad header format can't find all headers "
        return


    data = ([],[],[],[])

    line = fp.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')

        data[0].append(float(chunks[ni]))
        data[1].append(float(chunks[ei]))
        data[2].append(float(chunks[si]))
        data[3].append(float(chunks[di]))
        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    fig = figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
                 frameon = False )
    subplot(111)


    plotTitle = "Salinity at Position\n" 
    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    n = array(data[0])
    e = array(data[1])
    s = array(data[2])
    d = array(data[3])
    steps = 1000.0
    colors = cm.jet(linspace(0,1,steps + 1))

    high = max(s)
    low = min(s)

    print "low = %0.3f high = %0.3f" % (low, high)

    j = 0
    last = len(n) - 1

    print "Number of points = %d" % (last)


    ax = gca()
    segmentseq = []
    colorseq = []

    while j < last:
        seg = [(e[j], n[j]), (e[j+1], n[j+1])]

        sal = (s[j] + s[j+1])/ 2.0
        index = int(((sal - low) / (high - low)) * steps)
        color = colors[index]
        #print "salinity = %0.3f index = %d color = %s" % (sal, index, color)
        if depth - tolerance <= (d[j] + d[j+1])/2.0 <= depth + tolerance:
            segmentseq.append(seg)
            colorseq.append(color)
        else:
            if segmentseq:
                LC = mpl.collections.LineCollection(segmentseq, colors = colorseq)
                LC.set_linewidth(5)
                ax.add_collection(LC)
                segmentseq = []
                colorseq = []

        j += 1


    #safety box
    boxlines = BoxLineSegs(north = north, east = east, track = track, 
                           length = length, width = width)
    LC = mpl.collections.LineCollection(boxlines)
    LC.set_linewidth(1)
    LC.set_color('black')
    ax.add_collection(LC)



    grid(True)
    #legend(loc = 'upper left') #has to come after plot
    axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    b = [a[0] - (a[1] - a[0])/20.0, a[1] + (a[1] - a[0])/20.0, a[2] - (a[3] - a[2])/20.0, a[3] + (a[3] - a[2])/20.0]
    axis(b)


    cbax, kw = mpl.colorbar.make_axes(ax, shrink = 0.8, pad = 0.1)

    ticks = linspace(low ,high ,11)
    print "ticks = %s" %ticks
    norm = mpl.colors.Normalize(vmin = ticks[0], vmax = ticks[-1])

    cb = mpl.colorbar.ColorbarBase(cbax, cmap = cm.jet, norm = norm, ticks = ticks)
    cb.set_label('Salinity PSU')

    #cb.add_lines()

    show()
    #draw()
    #ion()



def PlotSalinity3(path = './test/logs/', name = "position.txt",
                  depth = 5.0, tolerance = 0.5, figNum = 1, figsize = (6,6)):
    """Function to automatically generate plot of vehicle salinity vs position
       only plots those points that are at the given depth +- tolerance
       figsize is (width, height)
       needs from pylab import *
       http://www.scipy.org/Cookbook/Matplotlib/MulticoloredLine
       Uses LineCollections to speed things up
    """
    fullname = path + name
    fp = open(fullname, 'rU')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    ni = None #north index
    ei = None # east index
    si = None # salinity index
    di = None # depth index

    chunks = fp.readline().strip().split('\t') #read header labels
    print chunks

    for i, chunk in enumerate(chunks): #gets first occurrence
        if ('north' in chunk) and (ni == None):
            ni = i
        elif ('east' in chunk) and (ei == None):
            ei = i
        elif ('salinity') in chunk  and (si == None) :
            si = i
        elif ('depth') in chunk  and (di == None) :
            di = i

    print "ni = %d ei = %d si = %d di = %d" % (ni,ei,si, di)

    if (ni is None) or (ei is None) or (si is None) or (di is None) :

        print "Bad header format can't find all headers "
        return


    data = ([],[],[],[])

    line = fp.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')

        data[0].append(float(chunks[ni]))
        data[1].append(float(chunks[ei]))
        data[2].append(float(chunks[si]))
        data[3].append(float(chunks[di]))
        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    fig = figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
                 frameon = False )
    subplot(111)


    plotTitle = "Salinity at Position\n" 
    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    n = array(data[0])
    e = array(data[1])
    s = array(data[2])
    d = array(data[3])
    steps = 1000.0
    colors = cm.jet(linspace(0,1,steps + 1))

    high = max(s)
    low = min(s)

    print "low = %0.3f high = %0.3f" % (low, high)

    j = 0
    last = len(n) - 1

    print "Number of points = %d" % (last)


    ax = gca()
    segmentseq = []
    colorseq = []

    while j < last:
        seg = [(e[j], n[j]), (e[j+1], n[j+1])]

        sal = (s[j] + s[j+1])/ 2.0
        index = int(((sal - low) / (high - low)) * steps)
        color = colors[index]
        #print "salinity = %0.3f index = %d color = %s" % (sal, index, color)
        if depth - tolerance <= (d[j] + d[j+1])/2.0 <= depth + tolerance:
            segmentseq.append(seg)
            colorseq.append(color)
        else:
            if segmentseq:
                LC = mpl.collections.LineCollection(segmentseq, colors = colorseq)
                LC.set_linewidth(5)
                ax.add_collection(LC)
                segmentseq = []
                colorseq = []

        j += 1



    grid(True)
    #legend(loc = 'upper left') #has to come after plot
    axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    b = [a[0] - (a[1] - a[0])/20.0, a[1] + (a[1] - a[0])/20.0, a[2] - (a[3] - a[2])/20.0, a[3] + (a[3] - a[2])/20.0]
    axis(b)


    cbax, kw = mpl.colorbar.make_axes(ax, shrink = 0.8, pad = 0.1)

    ticks = linspace(low ,high ,11)
    print "ticks = %s" %ticks
    norm = mpl.colors.Normalize(vmin = ticks[0], vmax = ticks[-1])

    cb = mpl.colorbar.ColorbarBase(cbax, cmap = cm.jet, norm = norm, ticks = ticks)
    cb.set_label('Salinity PSU')

    #cb.add_lines()

    show()
    #draw()
    #ion()



def PlotSalinity2(path = './test/logs/', name = "position.txt",
                  figNum = 1, figsize = (6,6)):
    """Function to automatically generate plot of vehicle salinity vs position
       figsize is (width, height)
       needs from pylab import *
       http://www.scipy.org/Cookbook/Matplotlib/MulticoloredLine
       Uses LineCollections to speed things up
    """
    fullname = path + name
    fp = open(fullname, 'rU')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    ni = None #north index
    ei = None # east index
    si = None # temperature index

    chunks = fp.readline().strip().split('\t') #read header labels
    print chunks

    for i, chunk in enumerate(chunks): #gets first occurrence
        if ('north' in chunk) and (ni == None):
            ni = i
        elif ('east' in chunk) and (ei == None):
            ei = i
        elif ('salinity') in chunk  and (si == None) :
            si = i

    if (ni is None) or (ei is None) or (si is None) :
        print "Bad header format can't find all headers %s" % str(chunks)
        return

    print "ni = %d ei = %d si = %d" % (ni,ei,si)

    data = ([],[],[])

    line = fp.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')

        data[0].append(float(chunks[ni]))
        data[1].append(float(chunks[ei]))
        data[2].append(float(chunks[si]))
        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    fig = figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
                 frameon = False )
    subplot(111)


    plotTitle = "Salinity at Position\n" 
    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    n = array(data[0])
    e = array(data[1])
    s = array(data[2])

    steps = 1000.0
    colors = cm.jet(linspace(0,1,steps + 1))

    high = max(s)
    low = min(s)

    print "low = %0.3f high = %0.3f" % (low, high)

    j = 0
    last = len(n) - 1

    print "Number of points = %d" % (last)

    segmentseq = []
    colorseq = []
    #lwseq = []
    while j < last:
        seg = [(e[j], n[j]), (e[j+1], n[j+1])]

        sal = (s[j] + s[j+1])/ 2.0
        index = int(((sal - low) / (high - low)) * steps)
        color = colors[index]
        #print "salinity = %0.3f index = %d color = %s" % (sal, index, color)
        segmentseq.append(seg)
        colorseq.append(color)
        j += 1

    ax = gca()

    LC = mpl.collections.LineCollection(segmentseq, colors = colorseq)
    LC.set_linewidth(5)
    ax.add_collection(LC)

    grid(True)
    #legend(loc = 'upper left') #has to come after plot
    axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    b = [a[0] - (a[1] - a[0])/20.0, a[1] + (a[1] - a[0])/20.0, a[2] - (a[3] - a[2])/20.0, a[3] + (a[3] - a[2])/20.0]
    axis(b)


    cbax, kw = mpl.colorbar.make_axes(ax, shrink = 0.8, pad = 0.1)

    ticks = linspace(low ,high ,11)
    print "ticks = %s" %ticks
    norm = mpl.colors.Normalize(vmin = ticks[0], vmax = ticks[-1])

    cb = mpl.colorbar.ColorbarBase(cbax, cmap = cm.jet, norm = norm, ticks = ticks)
    cb.set_label('Salinity PSU')

    #cb.add_lines()

    show()
    #draw()
    #ion()



def PlotSalinity(path = './test/logs/', name = "position.txt",
                 figNum = 1, figsize = (6,6)):
    """Function to automatically generate plot of vehicle salinity vs position
       figsize is (width, height)
       needs from pylab import *
       http://www.scipy.org/Cookbook/Matplotlib/MulticoloredLine
    """
    fullname = path + name
    fp = open(fullname, 'rU')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    ni = None #north index
    ei = None # east index
    si = None # temperature index

    chunks = fp.readline().strip().split('\t') #read header labels
    print chunks

    for i, chunk in enumerate(chunks): #gets first occurrence
        if ('north' in chunk) and (ni == None):
            ni = i
        elif ('east' in chunk) and (ei == None):
            ei = i
        elif ('salinity') in chunk  and (si == None) :
            si = i

    if (ni is None) or (ei is None) or (si is None) :
        print "Bad header format can't find all headers %s" % str(chunks)
        return

    print "ni = %d ei = %d si = %d" % (ni,ei,si)

    data = ([],[],[])

    line = fp.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')

        data[0].append(float(chunks[ni]))
        data[1].append(float(chunks[ei]))
        data[2].append(float(chunks[si]))
        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )
    subplot(111)


    plotTitle = "Salinity at Position\n" 
    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    n = array(data[0])
    e = array(data[1])
    s = array(data[2])

    steps = 100.0
    colors = cm.jet(linspace(0,1,steps + 1))

    high = max(s)
    low = min(s)

    print "high = %0.3f low = %0.3f" % (high, low)

    j = 0
    last = len(n) - 1

    print "Number of points = %d" % (last)

    while j < last:
        nn = [n[j],n[j+1]]
        ee = [e[j],e[j+1]]
        sal = (s[j] + s[j+1])/ 2.0
        index = int(((sal - low) / (high - low)) * steps)
        color = colors[index]
        #print "salinity = %0.3f index = %d color = %s" % (sal, index, color)
        plot(ee,nn, label = 'Salinity', linewidth=5, color = color )
        j += 1

    grid(True)
    #legend(loc = 'upper left') #has to come after plot
    axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    b = [a[0] - 10, a[1] + 10, a[2] - 10, a[3] + 10]
    axis(b)

    show()
    draw()
    ion()

def PlotTemp(path = './test/logs/', name = "position.txt",
             figNum = 1, figsize = (6,6)):
    """Function to automatically generate plot of vehicle temp vs position
       figsize is (width, height)
       needs from pylab import *
       http://www.scipy.org/Cookbook/Matplotlib/MulticoloredLine
    """
    fullname = path + name
    fp = open(fullname, 'rU')

    #kind, rule, name = fp.readline().split() #read log type line
    #if kind != 'text':
    #   print "Expected text log file got %s" % kind
    #   return


    ni = None #north index
    ei = None # east index
    ti = None # temperature index

    chunks = fp.readline().strip().split('\t') #read header labels
    print chunks

    for i, chunk in enumerate(chunks): #gets first occurrence
        if ('north' in chunk) and (ni == None):
            ni = i
        elif ('east' in chunk) and (ei is None):
            ei = i
        elif ('temperature') in chunk  and (ti is None) :
            ti = i


    print "ni = %d ei = %d ti = %d" % (ni,ei,ti)


    if (ni is None) or (ei is None) or (ti is None) :
        print "Bad header format can't find all headers %s" % str(chunks)
        return


    data = ([],[],[])

    line = fp.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')

        data[0].append(float(chunks[ni]))
        data[1].append(float(chunks[ei]))
        data[2].append(float(chunks[ti]))
        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()


    #Plot position XY
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )
    subplot(111)


    plotTitle = "Temperature at Position\n" 
    title(plotTitle)
    xlabel('East (meters)')
    ylabel('North (meters)')


    n = array(data[0])
    e = array(data[1])
    t = array(data[2])

    steps = 100.0
    colors = cm.jet(linspace(0,1,steps + 1))

    high = max(t)
    low = min(t)

    print "high = %0.3f low = %0.3f" % (high, low)

    j = 0
    last = len(n) - 1

    #last =  100
    #step = 100
    print "Number of points = %d" % (last)

    while j < last:
        nn = [n[j],n[j+1]]
        ee = [e[j],e[j+1]]
        temp = (t[j] + t[j+1])/ 2.0
        index = int(((temp - low) / (high - low)) * steps)
        color = colors[index]
        #print "temp = %0.3f index = %d color = %s" % (temp, index, color)
        plot(ee,nn, label = 'Temperature', linewidth=5, color = color )
        j += 1

    grid(True)
    #legend(loc = 'upper left') #has to come after plot
    axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    b = [a[0] - 10, a[1] + 10, a[2] - 10, a[3] + 10]
    axis(b)

    show()
    draw()
    ion()


def PlotLoggeeVsTime(loggee = 'speed', units = '',
                     path = './test/logs/', name = "state.txt",
                     figNum = 1, figsize = (6,2)):
    """Function to automatically generate plot of log item loggee vs time
       figsize is (width, height)
       needs from pylab import *

    """ 
    fullname = path + name
    fp = open(fullname, 'rU')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    ti = None # time index
    li = None #logee index


    chunks = fp.readline().strip().split('\t') #read header labels
    print chunks

    for i, chunk in enumerate(chunks): #gets first occurrence
        if ('_time' in chunk) and (ti == None):
            ti = i
        elif (loggee in chunk) and (li == None):
            li = i


    if (ti is None) or (li is None) :
        print "Bad header format can't find all headers %s" % str(chunks)
        return

    print "ti = %d li = %d " % (ti,li)


    data = ([],[])

    line = fp.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')

        data[0].append(float(chunks[ti]))
        data[1].append(float(chunks[li]))

        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()

    close(figNum)

    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()
    #figsize is (width, height)
    figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )
    subplot(1,1,1)

    title("%s vs time\n" % (loggee))
    xlabel('Time (seconds)')
    ylabel('%s (%s)' % (loggee, units))


    t = array(data[0])
    l = array(data[1])

    plot(t,l, label = loggee)
    #axis(ymin = 0.0, ymax = 3.5) 
    legend(loc = 'lower right')


    #xticks([0.0,25.0,50.0,75.0,100.0])
    #yticks([-10.0,-7.5,-5.0,-2.5,0.0,2.5,5.0,7.5,10.0])
    grid(True)

    #axis('scaled')
    a = axis()  #[xmin xmax ymin ymax]
    xadj = 0.05 * (a[1] - a[0])
    yadj = 0.05 * (a[3] - a[2])

    b = [a[0] - xadj, a[1] + xadj, a[2] - yadj, a[3] + yadj]
    print b
    axis(b)

    show()
    draw()
    ion()

def PlotLoggeesVsTime(loggees = [], units = [],
                      path = './test/logs/', name = "state.txt",
                      figNum = 1, figsize = (6,3)):
    """Function to automatically generate plot of log items in list loggees vs time
       figsize is (width, height)
       needs from pylab import *

    """ 
    fullname = path + name
    fp = open(fullname, 'rU')

    kind, rule, name = fp.readline().split() #read log type line
    if kind != 'text':
        print "Expected text log file got %s" % kind
        return

    ti = None # time index
    lis = [] #loggees indices
    for loggee in loggees:
        lis.append(None)


    chunks = fp.readline().strip().split('\t') #read header labels
    #print chunks

    for i, chunk in enumerate(chunks): #gets first occurrence
        if ('_time' in chunk) and (ti == None):
            ti = i
        else:
            for j, loggee in enumerate(loggees):
                if (loggee in chunk) and (lis[j] == None):
                    lis[j] = i

    if (ti is None):
        print "Bad header format can't find time header %s" % str(chunks)
        return

    for i in lis:
        if i is None:
            print "Bad header format can't find all headers %s" % str(chunks)
            return

    print "ti = %d " % (ti)
    for j, loggee in enumerate(loggees):
        print "loggee = %s l[%d] = %d" % (loggee, j, lis[j])



    tdata = []

    data = []
    for loggee in loggees:
        data.append([])

    for j in range(len(loggees) - len(units)):
        units.append('')


    line = fp.readline() #empty if end of file

    while (line):
        chunks = line.split('\t')
        #print chunks

        tdata.append(float(chunks[ti]))
        for j, i in enumerate(lis):
            data[j].append(float(chunks[i]))

        line = fp.readline() #empty if end of file


    if fp and not fp.closed:
        fp.close()

    t = array(tdata)


    close(figNum)

    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.90)
    rc('figure.subplot', left= 0.15)
    rc('figure.subplot', right= 0.90)

    ioff()

    subplots = len(loggees)
    w,h = figsize #figsize is (width, height)
    h = h * subplots
    figsize = (w,h)

    figure(figNum,figsize = figsize,dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )

    for j, loggee in enumerate(loggees):
        subplot(subplots,1,j+1)  #The subplot(numrows,numcols,subplotnum) 

        title("%s vs time\n" % (loggee))
        xlabel('Time (seconds)')
        ylabel('%s (%s)' % (loggee, units[j]))


        l = array(data[j])

        plot(t,l, label = loggee)
        legend(loc = 'upper right')

        #axis('scaled')
        #a = axis()  #[xmin xmax ymin ymax]
        print "original = %s " % str(axis())
        xmin, xmax, ymin,ymax = axis()

        tmin = min(t)
        tmax = max(t)
        print "time range = %s to %s" % (tmin, tmax)

        xmin = tmin
        xmax = tmax

        xadj = 0.05 * (xmax - xmin)
        yadj = 0.05 * (ymax - ymin)

        b = (xmin - xadj, xmax + xadj, ymin - yadj, ymax + yadj)
        print "modified = %s" % str(b)
        axis(b)

        print xticks()
        print yticks()

        #xticks([0.0,25.0,50.0,75.0,100.0])
        #yticks([-10.0,-7.5,-5.0,-2.5,0.0,2.5,5.0,7.5,10.0])
        grid(True)


    show()
    draw()
    ion()


def PlotVehicleYawPlane(vs, figNum = 1):
    """Function to automatically generate plot of a yaw plane motion

       needs from pylab import *

    """ 
    close(figNum)
    rc('figure.subplot', hspace= 0.5)
    rc('figure.subplot', bottom= 0.1)
    rc('figure.subplot', top= 0.9)
    rc('figure.subplot', right= 0.95)

    #figsize is (width, height)
    figure(figNum,figsize = (6,6),dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )

    t = array(vs.stamps)

    subplot(211)
    title('Vehicle Rudder')
    xlabel('Time (seconds)')
    ylabel('Rudder (degrees)')

    #axis([0.0,100.0,-12.5,12.5])  #xmin xmax ymin ymax
    #xticks([0.0,25.0,50.0,75.0,100.0])
    #yticks([-10.0,-7.5,-5.0,-2.5,0.0,2.5,5.0,7.5,10.0])
    grid(True)

    r = array(vs.rudders)
    plot(t,r, label = vs.name)

    legend(loc = 'lower right')

    subplot(212)
    title('Vehicle Heading')
    xlabel('Time (seconds)')
    ylabel('Heading (degrees)')

    grid(True)

    h = array(vs.headings)
    plot(t,h, label = vs.name)

    legend(loc = 'lower right')



def PlotVehiclePitchPlane(vs, figNum = 1):
    """Function to automatically generate plot of a pitch plane motion

       needs from pylab import *

    """ 
    close(figNum)
    rc('figure.subplot', hspace= 0.4)
    rc('figure.subplot', bottom= 0.075)
    rc('figure.subplot', top= 0.95)
    rc('figure.subplot', right= 0.95)

    #figsize is (width, height)
    figure(figNum,figsize = (6,9),dpi = 75, facecolor = 1.0, edgecolor = 1.0,
           frameon = False )

    t = array(vs.stamps)

    subplot(311)
    title('Vehicle Stern Plane')
    xlabel('Time (seconds)')
    ylabel('Stern (degrees)')

    #axis([0.0,100.0,-12.5,12.5])  #xmin xmax ymin ymax
    #xticks([0.0,25.0,50.0,75.0,100.0])
    #yticks([-10.0,-7.5,-5.0,-2.5,0.0,2.5,5.0,7.5,10.0])
    grid(True)


    sp = array(vs.sterns)
    plot(t,sp, label = vs.name)

    legend(loc = 'lower right')

    subplot(312)
    title('Vehicle Pitch')
    xlabel('Time (seconds)')
    ylabel('Pitch (degrees)')

    grid(True)


    p = array(vs.pitches)
    plot(t,p, label = vs.name)

    legend(loc = 'lower right')

    subplot(313)
    title('Vehicle Depth')
    xlabel('Time (seconds)')
    ylabel('Depth (meters)')

    grid(True)

    d = array(vs.depths)
    plot(t,d, label = vs.name)

    legend(loc = 'lower right')




def Nudge(dh = 0.0, dv = 0.0):
    """Nudge an axes dh horizontally and dv vertically
       positive is right up

    """
    a = gca()
    p = getp(a, 'position') #p = [left, bottom, width, height] in figure coords


    s = p[:] #make a copy

    s[0] += dh #move horizontal position
    s[1] += dv #move vertical position

    setp(a,position = s)



def Test():
    """tests core code.


    """
    pass


if __name__ == "__main__":
    #module test routines
    Test()

