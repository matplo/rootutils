"""
Graphics.py
 Created on: 28.08.2014
     Author: markusfasel
     
Graphics module, containing basic ROOT plot helper functionality
"""
from ROOT import TCanvas,TH1F,TLegend,TPad,TPaveText,TF1, TGraph, TH1
from ROOT import kBlack

class Frame:
    """
    Helper class handling frame drawing in plots
    """
    
    def __init__(self, name, xmin, xmax, ymin, ymax):
        """
        Construct frame with name and ranges for x and y coordinate
        
        :param name: Name of the frame
        :type name: str
        :param xmin: Min. value of the x-coordinate
        :type xmin: float
        :param xmax: Max. value of the x-coordinate
        :type xmax: float
        :param ymin: Min. value of the y-coordinate
        :type ymin: float
        :param ymax: Max. value of the y-coordinate   
        :type ymax: float
        """
        self.__framehist = TH1F(name, "", 100, xmin, xmax)
        self.__framehist.SetStats(False)
        self.__framehist.GetYaxis().SetRangeUser(ymin, ymax)
                        
    def SetXtitle(self, title):
        """
        Set title of the x axis
        
        :param title: Title of the x-axis
        :type title: str
        """
        self.__framehist.GetXaxis().SetTitle(title)
    
    def SetYtitle(self, title):
        """
        Set title of the y axis
        
        :param title: Title of the y-axis
        :type title: str
        """
        self.__framehist.GetYaxis().SetTitle(title)
        
    def Draw(self):
        """
        Draw the frame.
        """
        self.__framehist.Draw("axis")

class Style:
    """ 
    Class for plot styles (currently only color and marker)
    """
        
    def __init__(self, color, marker, options = None):
        """
        Constructor
        
        :param color: Color definition of the style
        :type color: ROOT.Color_t or int
        :param marker: Marker definition of the style
        :type marker: ROOT.Style_t or int
        :param option: Optional other style definitions  
        :type option: str
        """
        self.__color = color
        self.__marker = marker
        self.__linestyle = None
        self.__linewidth = None
        self.__fillstyle = None
        self.__fillcolor = None
        if options:
            if "fillstyle" in options.keys():
                self.__fillstyle = options["fillstyle"]
            if "fillcolor" in options.keys():
                self.__fillcolor = options["fillcolor"]
            if "linestyle" in options.keys():
                self.__linestyle = options["linestyle"]
            if "linewidth" in options.keys():
                self.__linewidth = options["linewidth"]

    def SetColor(self, color):
        """
        Change color of the graphics object
        
        :param color: The color of the object 
        :type color: ROOT.Color_t or int
        """
        self.__color = color

    def SetMarker(self, marker):
        """
        Change marker style of the graphics object
        
        :param marker: The marker style
        :type marker: ROOT.Style_t or int
        """
        self.__marker = marker
    
    def SetLineStyle(self, linestyle):
        """
        Change the line style
        
        :param linestyle: New line style 
        :type linestyle: ROOT.Style_t or int
        """
        self.__linestyle = linestyle
        
    def SetLineWidth(self, linewidth):
        """
        Change the line width
        
        :param linewidth: New line width
        :type linewidth: ROOT.Style_t or int
        """ 
        self.__linewidth = linewidth
    
    def SetFillStyle(self, fillstyle):
        """
        Change the fill style
        
        :param fillstyle: New fill style
        :type fillstyle: ROOT.Style_t or int
        """
        self.__fillstyle = fillstyle
        
    def SetFillColor(self, fillcolor):
        """
        Change the fill color
        
        :param fillcolor: the new fill color 
        :type fillcolor: ROOT.Color_t or int
        """
        self.__fillcolor = fillcolor

    def GetColor(self):
        """
        Access color of the graphics object
        
        :return: Marker color
        :rtype: ROOT.Color_t or int
        """
        return self.__color

    def GetMarker(self):
        """
        Access marker style
        
        :return: Marker style
        :rtype: ROOT.Style_t or int
        """
        return self.__marker
    
    def GetLineStyle(self):
        """
        Get the line style (if defined)
        
        :return: The line style
        :rtype: ROOT.Style_t or int
        """
        return self.__linestyle
    
    def GetLineWidth(self):
        """
        Get the line width
        
        :return: The line width
        :rtype: ROOT.Style_t or int
        """
        return self.__linewidth
    
    def GetFillStyle(self):
        """
        Get the fill style (if defined)
        
        :return: The fill style
        :rtype: ROOT.Style_t or int
        """
        return self.__fillstyle
    
    def GetFillColor(self):
        """
        Get the fill color (if defined)
        
        :return: The fill color
        :rtype: ROOT.Color_t or int
        """
        return self.__fillcolor
    
    def DefineROOTPlotObject(self, rootobject):
        """
        Sets the style to the root object
        
        :param rootobject: The ROOT graphics object to be defined 
        :type rootobject: F1, TGraph (and deriving), TH1 (and deriving)
        """
        #print "Defining root object"
        rootobject.SetMarkerColor(self.__color)
        if self.__linestyle is not None:
            rootobject.SetLineStyle(self.__linestyle)
        if self.__linewidth is not None:
            rootobject.SetLineWidth(self.__linewidth)
        if not type(rootobject) is TF1:
            rootobject.SetMarkerStyle(self.__marker)
            rootobject.SetLineColor(self.__color)
            if self.__fillstyle is not None:
                rootobject.SetFillStyle(self.__fillstyle)
            if self.__fillcolor is not None:
                rootobject.SetFillColor(self.__fillcolor)
        
class GraphicsObject:
    """
    Container for styled objects, inheriting from TGraph, TH1 or TF1
    """
    
    def __init__(self, data, style = None, drawoption = "epsame"):
        """
        Initialise new graphics object with underlying data (can be TH1 or TGraph(Errors)),
        and optionally a plot style. If no plot style is provided, then the default style (black,
        filled circles) is chosen.
        
        :param data: Underlying data as root object
        :type data: TF1, TGraph (and deriving), TH1 (and deriving)
        :param style: Plot style applied
        :type style: Style
        :param drawoption: Draw option   
        :type drawoption: str
        """
        self.__data = data
        mystyle = Style(kBlack, 20)
        if style:
            mystyle = style
        self.SetStyle(mystyle)
        self.__drawoption = "epsame"
        if drawoption:
            self.__drawoption = drawoption
            if not "same" in self.__drawoption:
                self.__drawoption += "same"
        if type(self.__data) is TF1:
            self.__drawoption = "lsame"
    
    def SetStyle(self, style):
        """
        Initialise underlying object with style
        
        :param style: The plot style used 
        :type style: Style
        """
        style.DefineROOTPlotObject(self.__data)
        
    def GetData(self):
        """
        Provide access to underlying data
        
        :return: The underlying root object
        :rtype: TF1, TGraph (and deriving), TH1 (and deriving) 
        """
        return self.__data
        
    def Draw(self):
        """
        Draw graphics object. By default, the plot option is 
        "epsame". Option strings will always have the option same
        """
        #print "Drawing option %s" %(self.__drawoption)
        self.__data.Draw(self.__drawoption)
    
    def AddToLegend(self, legend, title):
        """
        Add graphics object to a legend provided from outside
        
        :param legend: The legend the object is added to
        :type legend: TLegend
        :param title: Legend entry title  
        :type title: str
        """
        option = self.__drawoption
        if type(self.__data) is TF1:
            option = "l"
        elif self.__IsBoxStyle(self.__data):
            option = "f"
        if option == "lp" or option == "pl": 
            option = "lep"
        legend.AddEntry(self.__data, title, option)
        
    def __IsBoxStyle(self, plotobject):
        """
        Check whether plot object is drawn in a box style
        
        :param plotobject: The object to check
        :type plotobject: TF1, TGraph (and deriving) TH1 (and deriving)
        :return: True if in box style, False otherwise 
        :rtype: bool
        """
        if type(self.__data) is TF1:
            return False
        elif issubclass(type(self.__data), TGraph):
            for i in range(2, 6):
                if "%d" %(i) in self.__drawoption.lower():
                    return True
                return False
        elif issubclass(type(self.__data), TH1):
            return True if "b" in self.__drawoption.lower() else False 

class PlotBase:
    """
    base class for plot objects
    """
    
    class _FramedPad:
        """
        Defining the pad structure inside the canvas. A pad has a frame with
        axes definition, and optionally a legend and one or several label(s)
        """
        
        class GraphicsEntry:
            """
            Definition of a graphics entry
            """
            
            def __init__(self, graphobject, title = None, addToLegend = False):
                self.__object = graphobject
                self.__title = title
                self.__addToLegend = addToLegend
                
            def __cmp__(self, other):
                """
                Comparison is done accoring to the object title
                
                :param other: object to compare with
                :type other: GraphicsEntry
                :return: 0 if objects are equal, 1 if this object is larger, -1 if object is smaller 
                :rtype: int
                """
                # 1st case: either or both of the titles missing
                if not self.__title and not other.GetTitle():
                    return None
                if not self.__title and other.GetTitle():
                    return -1
                if self.__title and not other.GetTitle():
                    return 1
                # second case: both of the titles available
                if self.__title == other.GetTitle():
                    return 0
                if self.__title < other.GetTitle():
                    return -1
                return 1                
                
            def GetObject(self):
                """
                Accessor to graphics object
                
                :return: Underlying object
                :rtype: GraphicsObject
                """
                return self.__object
            
            def GetTitle(self):
                """
                Get the title of the object
                
                :return: Title of the object
                :rtype: int
                """
                return self.__title
            
            def IsAddToLegend(self):
                """
                Check whether graphics is foreseen to be added to legend
                
                :return: True if the object is added to the legend
                :rtype: bool
                """
                return self.__addToLegend
            
            def SetTitle(self, title):
                """
                Change title of the graphics object
                
                :param title: Title of the object 
                :type title: str
                """
                self.__title = title
                
            def SetAddToLegend(self, doAdd):
                """
                Define whether object should be added to a legend
                
                :param doAdd: Switch for adding object to a legend
                :type doAdd: bool
                """ 
                self.__addToLegend = doAdd
        
        def __init__(self, pad):
            """
            Constructor, creating a framed pad structure for a TPad
            
            :param pad: Underlying ROOT pad 
            :type pad: ROOT TPad
            """
            self.__pad = pad
            self.__Frame = None
            self.__legend = None
            self.__graphicsObjects = []
            self.__labels = []
            
        def DrawFrame(self, frame):
            """
            Draw a frame, defined from outside, within the pad
            The pad becomes owner of the frame
            
            :param frame: Frame of the pad 
            :type frame: Frame
            """
            self.__frame = frame
            self.__frame.Draw()
            
        def DrawGraphicsObject(self, graphics, addToLegend = False, title = None):
            """
            Draw a graphics object into the pad. If addToLegend is set, then the object is added to to the 
            legend.
            
            :param graphics: Graphics object to be added
            :type graphics: GraphicsObject
            """
            self.__graphicsObjects.append(self.GraphicsEntry(graphics, title, addToLegend))
            graphics.Draw()
            
            
        def DefineLegend(self, xmin, ymin, xmax, ymax):
            """
            create a new legend within the frame with the 
            given boundary coordinates
            
            :param xmin: Min. x value of the legend
            :type xmin: float
            :param ymin: Max. x value of the legend
            :type ymin: float
            :param xmax: Min. y value of the legend
            :type ymin: float
            :param ymax: Max. y value of the legend
            :type ymax: float
            """
            if not self.__legend:
                self.__legend = TLegend(xmin, ymin, xmax, ymax)
                self.__legend.SetBorderSize(0)
                self.__legend.SetFillStyle(0)
                self.__legend.SetTextFont(42)
                
        def CreateLegend(self, xmin, ymin, xmax, ymax):
            """
            Create Legend from all graphics entries
            
            :param xmin: Min. x value of the legend
            :type xmin: float
            :param ymin: Max. x value of the legend
            :type ymin: float
            :param xmax: Min. y value of the legend
            :type ymin: float
            :param ymax: Max. y value of the legend
            :type ymax: float
            """
            if not self.__legend:
                self.DefineLegend(xmin, ymin, xmax, ymax)
                for entry in sorted(self.__graphicsObjects):
                    if entry.IsAddToLegend():
                        self.AddToLegend(entry.GetObject(), entry.GetTitle())
                self.DrawLegend()
            
        def GetLegend(self):
            """
            Provide access to legend
            
            :return: the legend
            :rtype: ROOT TLegend
            """
            return self.__legend
        
        def AddToLegend(self, graphicsObject, title):
            """
            Special method adding graphics objects to a legend
            
            :param graphicsObject: graphics object to be added to the legend 
            :type graphicsObject: GraphicsObject
            :param title: Legend entry title 
            :type title: str
            """
            if self.__legend:
                graphicsObject.AddToLegend(self.__legend, title)
            
        def DrawLegend(self):
            """
            Draw the legend
            """
            if self.__legend:
                self.__legend.Draw()
        
        def DrawLabel(self, xmin, ymin, xmax, ymax, text):
            """
            Add a new label to the pad and draw it
            
            :param xmin: Min. x value of the label
            :type xmin: float
            :param xmax: Max. x value of the label
            :type xmax: float
            :param ymin: Min. y value of the label
            :type ymin: float
            :param ymax: Max. y value of the label
            :type ymax: float
            :param text: Label text
            :type text: str
            """
            label = TPaveText(xmin, ymin, xmax, ymax, "NDC")
            label.SetBorderSize(0)
            label.SetFillStyle(0)
            label.SetTextFont(42)
            label.AddText(text)
            label.Draw()
            self.__labels.append(label)
        
        def GetPad(self):
            """
            Provide direct access to the pad
            
            :return: Underlying ROOT pad
            :rtype: ROOT TPad
            """
            return self.__pad
            
    class _FrameContainer:
        """
        Container for framed pad objects
        """
        
        def __init__(self):
            """
            Create new empty frame container
            """
            self.__Frames = {}
            
        def AddFrame(self, frameID, frame):
            """
            Add a new framed pad to the frame container
            
            :param frameID: ID of the frame
            :type frameID: int
            :param frame: Frame to be added for pad with ID  
            :type frame: Frame
            """
            self.__Frames[frameID] = frame
            
        def GetFrame(self, frameID):
            """
            Provide access to frame
            
            :param frameID: ID of the frame
            :type frameID: Frame
            :return: The frame for the pad 
            :rtype: Frame
            """
            if not self.__Frames.has_key(frameID):
                return None
            return self.__Frames[frameID]

    def __init__(self):
        """
        Initialise new plot
        """
        self._canvas = None
        self._frames = self._FrameContainer()
        
    def _OpenCanvas(self, canvasname, canvastitle, xsize = 1000, ysize = 800):
        """
        Initialise canvas with name, title and sizes
        
        :param canvasname: Name of the canvas
        :type canvasname: str
        :param canvastitle: Title of the canvas
        :type canvastitle: str
        :param xsize: Canvas size in x-direction
        :type xsize: int
        :param ysize: Canvas size in y-direction   
        :type ysize: int
        """
        self._canvas = TCanvas(canvasname, canvastitle, xsize, ysize)
        self._canvas.cd()
        
    def SaveAs(self, filenamebase):
        """
        Save plot to files:
        Creating a file with a common name in the formats
        eps, pdf, jpeg, gif and pdf
        
        :param filenamebase: Basic part of the filename (without endings) 
        :type filenamebase: str
        """
        for t in ["eps", "pdf", "jpeg", "gif", "png"]:
            self._canvas.SaveAs("%s.%s" %(filenamebase, t))
            
class SinglePanelPlot(PlotBase):
    
    def __init__(self):
        """
        Initialise single panel plot
        """
        PlotBase.__init__(self)
        
    def _OpenCanvas(self, canvasname, canvastitle):
        """
        Create canvas and add it to the list of framed pads
        
        :param canvasname: Name of the canvas
        :type canvasname: str
        :param canvastitle: Title of the canvas
        :type canvastitle: str
        """
        PlotBase._OpenCanvas(self, canvasname, canvastitle, 1000, 800)
        self._frames.AddFrame(0, self._FramedPad(self._canvas))
        
    def _GetFramedPad(self):
        """
        Access to framed pad
        
        :return: The underlying framed pad
        :rtype: _FramedPad
        """
        return self._frames.GetFrame(0)
    
class MultipanelPlot(PlotBase):
    """
    Base Class For multiple panel plots
    """
    
    def __init__(self, nrow, ncol):
        """
        Create new Multi-panel plot with a given number of row and cols
        """
        PlotBase.__init__(self)
        self.__nrow = nrow
        self.__ncol = ncol
        
    def _OpenCanvas(self, canvasname, canvastitle, xsize, ysize):
        """
        Create new canvas and split it into the amount of pads as defined
        
        :param canvasname: Name of the canvas
        :type canvasname: str
        :param canvastitle: Title of the canvas
        :type canvastitle: str
        :param xsize: Canvas size in x-direction
        :type xsize: int
        :param ysize: Canvas size in y-direction   
        :type ysize: int
        """
        PlotBase._OpenCanvas(self, canvasname, canvastitle, xsize, ysize)
        self._canvas.Divide(self.__ncol, self.__nrow)
        
    def _OpenPad(self, padID):
        """
        Create new framed pad in a multi-panel plot for a given pad ID
        
        :param padID: ID number of the pad
        :return: The framed pad
        """
        if padID < 0 or padID > self.__GetMaxPadID():
            return None
        mypad = self._GetPad(padID)
        if not mypad:
            mypad = self._FramedPad(self._canvas.cd(padID+1))
            self._frames.AddFrame(padID, mypad)
        return mypad
    
    def _OpenPadByRowCol(self, row, col):
        """
        Create new framed pad in a multi-panel plot for a given row an col
        
        :param row: row of the pad
        :type row: int
        :param col: column of the pad  
        :type col: int
        :return: The new pad at this position 
        :rtype: int
        """
        return self._OpenPad(self.__GetPadID(row, col))
    
    def _GetPad(self, padID):
        """
        Access to Pads by pad ID
        
        :param padID: ID number of the pad
        :type padID: int
        :return: The framed pad
        :rtype: _FramedPad
        """
        return self._frames.GetFrame(padID)
    
    def _GetPadByRowCol(self, row, col):
        """
        Access Pad by row and col
        
        :param row: row of the pad
        :type row: int
        :param col: column of the pad  
        :type col: int
        :return: The pad at this position 
        :rtype: int
        """
        return self._frames.GetFrame(self.__GetPadID(row, col))
    
    def __GetPadID(self, row, col):
        """
        Calculate ID of the pad
        
        :param row: row of the pad
        :type row: int
        :param col: column of the pad  
        :type col: int
        :return: The pad ID for this combination
        :rtype: int
        """
        if (row < 0 or row >= self.__nrow) or (col < 0 or col >= self.__ncol):
            return -1
        return 1 + row * self.__ncol + col
    
    def __GetMaxPadID(self):
        """
        Calculate the maximum allowed pad ID
        
        :return: The maximum pad ID
        :rtype: int
        """
        return 1 + self.__ncol * self.__nrow
    
class TwoPanelPlot(MultipanelPlot):
    """
    A plot with two panels
    """
    
    def __init__(self):
        """
        Initialise two-panel plot
        """
        MultipanelPlot.__init__(self, 1, 2)
        
    def _CreateCanvas(self, canvasname, canvastitle):
        """
        Create Canvas with the dimensions of a four-panel plot
        
        :param canvasname: Name of the canvas
        :type canvasname: str
        :param canvastitle: Title of the canvas
        :type canvastitle: str
        """
        MultipanelPlot._OpenCanvas(self, canvasname, canvastitle, 1000, 500)
    
class FourPanelPlot(MultipanelPlot):
    """
    A plot with four (2x2) panels
    """
    
    def __init__(self):
        """
        Initialise four-panel plot
        """
        MultipanelPlot.__init__(self, 2, 2)
        
    def _OpenCanvas(self, canvasname, canvastitle):
        """
        Create Canvas with the dimensions of a four-panel plot
        
        :param canvasname: Name of the canvas
        :type canvasname: str
        :param canvastitle: Title of the canvas
        :type canvastitle: str
        """
        MultipanelPlot._OpenCanvas(self, canvasname, canvastitle, 1000, 1000)