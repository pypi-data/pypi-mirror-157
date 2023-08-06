from matplotlib import collections
import wx
import numpy as np
import numpy.ma as ma
from bisect import bisect_left
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from collections import OrderedDict

from .PyTranslate import _

class wolfpalette(wx.Frame,LinearSegmentedColormap):
    '''
    Palette de couleurs basée sur l'objet "LinearSegmentedColormap" de Matplotlib (Colormap objects based on lookup tables using linear segments)    
    '''
    filename:str
    nb:int
    colors:np.array
    colorsflt:np.array

    def __init__(self, parent, title,w=100,h=500,nseg=1024):

        self.filename=''
        self.nb = 0
        self.values = None
        self.colormin = np.array([1.,1.,1.])
        self.colormax = np.array([0,0,0])
        self.nseg=nseg

        #Appel à l'initialisation d'un frame général
        if(parent!=None):
            wx.Frame.__init__(self, parent, title=title, size=(w,h),style=wx.DEFAULT_FRAME_STYLE)
        LinearSegmentedColormap.__init__(self,'wolf',{},nseg)
        self.set_bounds()

    def set_bounds(self):
        self.set_under(tuple(self.colormin))
        self.set_over(tuple(self.colormax))

    def get_rgba(self,x):
        return self((x-self.values[0])/(self.values[-1]-self.values[0]))        
    
    def export_palette_matplotlib(self):
        cmaps = OrderedDict()
        cmaps['Perceptually Uniform Sequential'] = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
        cmaps['Sequential'] = ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds','YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu',
                               'BuPu','GnBu', 'PuBu', 'YlGnBu','PuBuGn', 'BuGn', 'YlGn']
        cmaps['Sequential (2)'] = ['binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink','spring', 'summer', 'autumn', 'winter',
                                   'cool', 'Wistia','hot', 'afmhot', 'gist_heat', 'copper']
        cmaps['Diverging'] = ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu','RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']
        cmaps['Cyclic'] = ['twilight', 'twilight_shifted', 'hsv']
        cmaps['Qualitative'] = ['Pastel1', 'Pastel2', 'Paired', 'Accent','Dark2', 'Set1', 'Set2', 'Set3','tab10', 'tab20', 'tab20b', 'tab20c']
        cmaps['Miscellaneous'] = ['flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern','gnuplot', 'gnuplot2',
                                  'CMRmap', 'cubehelix', 'brg','gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']
        # for cmap_category, cmap_list in cmaps.items():
        #     self=plt.get_cmap(cmap_list)        

    def lookupcolor(self,x):
        if x < self.values[0]:  return wx.Colour(self.colormin)
        if x > self.values[-1]: return wx.Colour(self.colormax)

        i = bisect_left(self.values, x)
        k = (x - self.values[i-1])/(self.values[i] - self.values[i-1])
        
        r=int(k*(float(self.colors[i,0]-self.colors[i-1,0]))) + self.colors[i-1,0]
        g=int(k*(float(self.colors[i,1]-self.colors[i-1,1]))) + self.colors[i-1,1]
        b=int(k*(float(self.colors[i,2]-self.colors[i-1,2]))) + self.colors[i-1,2]
        a=int(k*(float(self.colors[i,3]-self.colors[i-1,3]))) + self.colors[i-1,3]

        y = wx.Colour(r,g,b,a)

        return y    

    def lookupcolorrgb(self,x):
        if x < self.values[0]:  return wx.Colour(self.colormin)
        if x > self.values[-1]: return wx.Colour(self.colormax)

        i = bisect_left(self.values, x)
        k = (x - self.values[i-1])/(self.values[i] - self.values[i-1])
        
        r=int(k*(float(self.colors[i,0]-self.colors[i-1,0]))) + self.colors[i-1,0]
        g=int(k*(float(self.colors[i,1]-self.colors[i-1,1]))) + self.colors[i-1,1]
        b=int(k*(float(self.colors[i,2]-self.colors[i-1,2]))) + self.colors[i-1,2]
        a=int(k*(float(self.colors[i,3]-self.colors[i-1,3]))) + self.colors[i-1,3]

        return r,g,b,a   
    
    def default16(self):
        '''Palette 16 coulrurs par défaut dans WOLF'''
        self.nb=16
        self.values = np.linspace(0.,1.,16)
        self.colors = np.zeros((self.nb,4) , dtype=int)
        self.colorsflt = np.zeros((self.nb,4) , dtype=float)
        
        self.colors[0,:] = [128,255,255,255]
        self.colors[1,:] = [89,172,255,255]
        self.colors[2,:] = [72,72,255,255]
        self.colors[3,:] = [0,0,255,255]
        self.colors[4,:] = [0,128,0,255]
        self.colors[5,:] = [0,221,55,255]
        self.colors[6,:] = [128,255,128,255]
        self.colors[7,:] = [255,255,0,255]
        self.colors[8,:] = [255,128,0,255]
        self.colors[9,:] = [235,174,63,255]
        self.colors[10,:] = [255,0,0,255]
        self.colors[11,:] = [209,71,12,255]
        self.colors[12,:] = [128,0,0,255]
        self.colors[13,:] = [185,0,0,255]
        self.colors[14,:] = [111,111,111,255]
        self.colors[15,:] = [192,192,192,255]

        self.fill_segmentdata()

    def fill_segmentdata(self):
        '''Mise à jour de la palatte de couleurs'''

        self.colorsflt = self.colors.astype(float)/255.

        if (self.values[-1]-self.values[0])>0.:
            normval = (self.values-self.values[0])/(self.values[-1]-self.values[0])
        else:
            normval = self.values
        
        normval[0]=0.
        normval[-1]=1.
        self._segmentdata = {"red": np.column_stack([normval, self.colorsflt[:,0], self.colorsflt[:,0]]),
                             "green": np.column_stack([normval, self.colorsflt[:,1], self.colorsflt[:,1]]),
                             "blue": np.column_stack([normval, self.colorsflt[:,2], self.colorsflt[:,2]]),
                             "alpha": np.column_stack([normval, self.colorsflt[:,3], self.colorsflt[:,3]])}

    def readfile(self,*args):
        '''Lecture de la palette sur base d'un fichier WOLF .pal'''
        if len(args)>0:
            #s'il y a un argument on le prend tel quel
            self.filename = str(args[0])
        else:
            #ouverture d'une boîte de dialogue
            file=wx.FileDialog(self,"Choose .pal file", wildcard="pal (*.pal)|*.pal|all (*.*)|*.*")
            if file.ShowModal() == wx.ID_CANCEL: 
                return
            else:
                #récuparétaion du nom de fichier avec chemin d'accès
                self.filename =file.GetPath()

        #lecture du contenu
        with open(self.filename, 'r') as myfile:
            #split des lignes --> récupération des infos sans '\n' en fin de ligne
            #  différent de .readlines() qui lui ne supprime pas les '\n'
            mypallines = myfile.read().splitlines()
            myfile.close()

            self.nb = int(mypallines[0])
            self.values = np.zeros(self.nb , dtype=float)
            self.colors = np.zeros((self.nb,3) , dtype=int)

            for i in range(self.nb):
                self.values[i] = mypallines[i*4+1]
                self.colors[i,0] = mypallines[i*4+2]
                self.colors[i,1] = mypallines[i*4+3]
                self.colors[i,2] = mypallines[i*4+4]
                self.colors[i,3] = 255

    def isopop(self,array: ma.masked_array,nbnotnull=99999):
        '''Remplissage des valeurs de palette sur base d'une équirépartition de valeurs'''

        sortarray = array.flatten(order='F')
        sortarray.sort(axis=-1)

        #valeurs min et max
        self.values[0] = sortarray[0]
        
        if(nbnotnull==99999):
            self.values[-1] = sortarray[-1]
            nb = sortarray.count()
        else:
            self.values[-1] = sortarray[nbnotnull-1]
            nb = nbnotnull

        interv = int(nb / (self.nb-1))
        if interv==0:
            self.values[:] = self.values[-1]
            self.values[0] = self.values[-1]-1.
        else:
            for cur in range(1,self.nb-1):
                self.values[cur] = sortarray[cur * interv]

        self.fill_segmentdata()
