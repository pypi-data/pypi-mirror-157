from tkinter import Button
from matplotlib.pyplot import axes, show
import wx
import wx.lib.agw.aui as aui
import wx.lib.mixins.inspection as wit

from matplotlib import figure as mplfig
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas, NavigationToolbar2WxAgg as NavigationToolbar

from .PyCrosssections import profile
from .PyTranslate import _
from .PyVertex import getIfromRGB,getRGBfromI

class Plot(wx.Panel):
    '''Un seul Panneau du notebook'''

    figure:mplfig.Figure

    def __init__(self, parent, id=-1, dpi=None, **kwargs):
        super().__init__(parent, id=id, **kwargs)
        self.figure = mplfig.Figure(dpi=dpi, figsize=(2, 2))    #Création d'une figure Matplotlib
        self.canvas = FigureCanvas(self, -1, self.figure)       #Création d'un Canvas wx pour contenir le dessin de la figure Matplotlib
        self.toolbar = NavigationToolbar(self.canvas)           #Ajout d'une barre d'outils pour la figure courante
        self.toolbar.Realize()

        self.sizer = wx.BoxSizer(wx.VERTICAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        self.sizer.Add(self.canvas, 1, wx.EXPAND)                    #ajout du canvas
        self.sizer.Add(self.toolbar, 0, wx.LEFT| wx.EXPAND)         #ajout de la barre
        self.SetSizer(self.sizer)                                    #application du sizer

    def add_ax(self):
        self.myax = self.figure.add_subplot()
        return self.myax

class PlotCS(Plot):
    
    def __init__(self, parent, id=-1, dpi=None, mycs=None, **kwargs):
        
        super().__init__(parent, id, dpi, **kwargs)
        
        self.second_fig = None
        self.second_ax = None
        
        self.sizernextprev = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        self.sizerposbank = wx.BoxSizer(wx.HORIZONTAL)                        #ajout d'un sizer pour placer la figure et la barre d'outils l'une au-dessus de l'autre
        
        self.sizer.Add(self.sizernextprev)
        self.sizer.Add(self.sizerposbank)

        self.ButPrev = wx.Button(self,label=_("Previous"))
        self.ButNext = wx.Button(self,label=_("Next"))

        self.ButBLLeft = wx.Button(self,name="BLLeft",label=_("BL left"))
        self.ButBLRight = wx.Button(self,name="BLRight",label=_("BL right"))
        self.ButBRLeft = wx.Button(self,name="BedLeft",label=_("Bed left"))
        self.ButBRRight = wx.Button(self,name="BedRight",label=_("Bed right"))
        self.ButBedLeft = wx.Button(self,name="BRLeft",label=_("BR left"))
        self.ButBedRight = wx.Button(self,name="BRRight",label=_("BR right"))
        
        self.sizernextprev.Add(self.ButPrev,0,wx.LEFT| wx.EXPAND)
        self.sizernextprev.Add(self.ButNext,0,wx.LEFT| wx.EXPAND)
        self.sizerposbank.Add(self.ButBLLeft,0,wx.LEFT| wx.EXPAND)
        self.sizerposbank.Add(self.ButBLRight,0,wx.LEFT| wx.EXPAND)
        self.sizerposbank.Add(self.ButBedLeft,0,wx.LEFT| wx.EXPAND)
        self.sizerposbank.Add(self.ButBedRight,0,wx.LEFT| wx.EXPAND)
        self.sizerposbank.Add(self.ButBRLeft,0,wx.LEFT| wx.EXPAND)
        self.sizerposbank.Add(self.ButBRRight,0,wx.LEFT| wx.EXPAND)
        
        self.mycs = mycs
        self.ButPrev.Bind(wx.EVT_BUTTON,self.plot_up)
        self.ButNext.Bind(wx.EVT_BUTTON,self.plot_down)
        self.ButBLLeft.Bind(wx.EVT_BUTTON,self.movebanks)
        self.ButBLRight.Bind(wx.EVT_BUTTON,self.movebanks)
        self.ButBedLeft.Bind(wx.EVT_BUTTON,self.movebanks)
        self.ButBedRight.Bind(wx.EVT_BUTTON,self.movebanks)
        self.ButBRLeft.Bind(wx.EVT_BUTTON,self.movebanks)
        self.ButBRRight.Bind(wx.EVT_BUTTON,self.movebanks)
        
    def movebanks(self,event:wx.Event):
        '''Mouvement des berges'''
        id = event.GetEventObject().GetName()
        
        cs:profile = self.mycs
        
        if id=="BLLeft":
            cs.movebankbed('left','left')
        elif id=="BLRight":
            cs.movebankbed('left','right')
        elif id=="BRLeft":
            cs.movebankbed('right','left')
        elif id=="BRRight":  
            cs.movebankbed('right','right')
        elif id=="BedLeft":
            cs.movebankbed('bed','left')
        elif id=="BedRight":  
            cs.movebankbed('bed','right')
            
        self.plot_cs()
    
    def plot_cs(self):
        cs:profile = self.mycs
        cs.plot_cs(fig=self.figure,ax=self.myax)
        if self.second_fig is not None:
            cs.plot_cs(fig=self.second_fig,ax=self.second_ax,forceaspect=False)
                            
    def plot_up(self,event):
        
        self.mycs:profile
        
        self.mycs.myprop.width=1
        self.mycs.myprop.color=0

        if self.mycs.up is not None:
            self.mycs = self.mycs.up    
        
        self.plot_cs()
                
        self.mycs.myprop.width=2
        self.mycs.myprop.color=getIfromRGB([255,0,0])
    
    def plot_down(self,event):
        
        self.mycs.myprop.width=1
        self.mycs.myprop.color=0

        if self.mycs.down is not None:
            self.mycs = self.mycs.down
        
        self.plot_cs()
                
        self.mycs.myprop.width=2
        self.mycs.myprop.color=getIfromRGB([255,0,0])

class PlotNotebook(wx.Panel):
    '''
    Fenêtre contenant potentiellement plusieurs graphiques Matplotlib
    '''
    
    def __init__(self, parent = None, id=-1,show=True,framesize=(1024,768)):
        '''Initialisation
         Si un parent est fourni, on l'attache, sinon on crée une fenêtre indépendante
        '''
        if parent is None:
            self.frame = wx.Frame(None, -1, 'Plotter',size=framesize)
            super().__init__(self.frame, id=id)
        else:
            self.frame=parent
            super().__init__(parent, id=id)

        self.ntb = aui.AuiNotebook(self)    #ajout du notebook 
        sizer = wx.BoxSizer()               #sizer pour servir de contenant au notebook
        sizer.Add(self.ntb, 1, wx.EXPAND)   #ajout du notebook au sizer et demande d'étendre l'objet en cas de redimensionnement
        self.SetSizer(sizer)                #applique le sizer
        if show:
            self.frame.Show()
            
        self.Bind(wx.EVT_CLOSE , self.OnClose)

    def OnClose(self):
        self.Hide()

    def add(self, name="plot",which=""):
        '''
        Ajout d'un onglet au notebook
        L'onglet contient une Figure Matplotlib
        On retourne la figure du nouvel onglet
        '''
        
        if which=="":
            page = Plot(self.ntb)               #crée un objet Plot
            self.ntb.AddPage(page, name)        #ajout de l'objet Plot au notebook
        elif which=="CS":
            page = PlotCS(self.ntb)               #crée un objet Plot
            page2 = Plot(self.ntb)               #crée un objet Plot
            self.ntb.AddPage(page, name)        #ajout de l'objet Plot au notebook
            self.ntb.AddPage(page2, name+' expand')        #ajout de l'objet Plot au notebook
            
            ax=page.add_ax()
            ax2=page2.add_ax()
            
            page.second_fig = page2.figure
            page.second_ax = ax2
            
        return page                  

    def getfigure(self,index = -1, caption="") -> mplfig.Figure:
        if index!=-1:
            return self.ntb.GetPage(index).figure
        elif caption!="":
            for curpage in range(self.ntb.GetPageCount()):
                if caption==self.ntb.GetPageText(curpage):
                    return self.ntb.GetPage(curpage).figure
            return
        else:
            return

def demo():
    app = wx.App()
    # frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook()
    axes1 = plotter.add('figure 1').figure.add_subplot()
    axes1.plot([1, 2, 3], [2, 1, 4])
    # axes2 = plotter.add('figure 2').add_subplot()
    # axes2.plot([1, 2, 3, 4, 5], [2, 1, 4, 2, 3])

    fig=plotter.getfigure(0)
    fig.get_axes()[0].plot([5, 6, 10], [2, 1, 10])
    app.MainLoop()

if __name__ == "__main__":
    demo()