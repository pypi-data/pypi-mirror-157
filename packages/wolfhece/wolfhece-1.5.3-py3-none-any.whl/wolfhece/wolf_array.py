import os
import sys
from unicodedata import decimal
import numpy as np
import numpy.ma as ma
import math as m
from OpenGL.GL  import *
import math
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
from sympy import false
import re

from .PyTranslate import _

try:
    from . import wolfogl
except:
    print('Error importing wolfogl.pyd')
    print('   Python version : ' + sys.version)
    print('   If your Python version is not 3.7.x or 3.9.x, you need to compile an adapted library with compile_wcython.py in wolfhece library path')
    print('   See comments in compile_wcython.py or launch *python compile_wcython.py build_ext --inplace* in :')
    print('      ' + os.path.dirname(__file__))
    exit()

from .xyz_file import XYZFile
from .PyPalette import wolfpalette
from .PyVertexvectors import Zones, vector,wolfvertex, zone

WOLF_ARRAY_FULL_SINGLE      = 1
WOLF_ARRAY_FULL_DOUBLE      = 2
WOLF_ARRAY_SYM_DOUBLE       = 8
WOLF_ARRAY_FULL_LOGICAL     = 4
WOLF_ARRAY_CSR_DOUBLE       = 5
WOLF_ARRAY_FULL_INTEGER     = 6
WOLF_ARRAY_FULL_SINGLE_3D   = 7
WOLF_ARRAY_FULL_INTEGER8    = 8

WOLF_ARRAY_MB_SINGLE        = 3
WOLF_ARRAY_MB_INTEGER       = 9

WOLF_ARRAY_FULL_INTEGER16   = 11
WOLF_ARRAY_MNAP_INTEGER     = 20

WOLF_ARRAY_MB = [WOLF_ARRAY_MB_SINGLE,WOLF_ARRAY_MB_INTEGER,WOLF_ARRAY_MNAP_INTEGER]

def getkeyblock(i,addone=True):
    if addone:
        return 'block'+str(i+1)
    else:
        return 'block'+str(i)

class header_wolf():
    
    def __init__(self) -> None:
        self.origx = 0.0
        self.origy = 0.0
        self.origz = 0.0
        
        self.translx = 0.0
        self.transly = 0.0
        self.translz = 0.0

        self.dx = 0.0
        self.dy = 0.0
        self.dz = 0.0
        
        self.nbx = 0
        self.nby = 0
        self.nbz = 0

        self.nb_blocks = 0
        self.head_blocks={}

# Objet Wolf Array en simple précision
class WolfArray(header_wolf):
    """ Classe pour l'importation de WOLF arrays"""
    array : ma.masked_array
    mygrid:dict
    idx:str

    myselection:list

    def __init__(self,fname = None,mold = None,masknull=True,crop=None,whichtype=WOLF_ARRAY_FULL_SINGLE,preload=True):
        super().__init__()
        
        self.filename = ""
        self.nbdims = 2
        self.isblock=False
        self.blockindex=0
        self.wolftype = whichtype
        
        self.preload = preload
        self.loaded = False
        self.masknull=masknull
        
        self.rgb=None
        self.mypal = None
    
        self.nullvalue = 0.
        self.nbnotnull = 99999
        self.nbtoplot = 0

        self.gridsize=100
        self.gridmaxscales = -1
        
        self.plotted=False
        self.plotting=False

        self.mypal=wolfpalette(None,"Palette of colors")
        self.mypal.default16()
        self.mygrid={}
        self.myselection=[]
        
        self.cropini=crop

        """ Constructeur d'un WOLF array """
        if fname is not None:
            self.filename = fname
            self.read_all()
            if masknull and self.preload:
                self.mask_data(0.)
            return
        
        if mold is not None:
            self.nbdims = mold.nbdims
            self.nbx = mold.nbx
            self.nby = mold.nby
            self.nbz = mold.nbz
            self.dx = mold.dx
            self.dy = mold.dy
            self.dz = mold.dz
            self.origx = mold.origx
            self.origy = mold.origy
            self.origz = mold.origz
            self.translx = mold.translx
            self.transly = mold.transly
            self.translz = mold.translz
            self.array = ma.copy(mold.array)
            #return
            
        self.rgb=np.ones((self.nbx,self.nby,4),order='F',dtype=np.integer)

    def copy_mask(self,source):
        self.array.mask = source.array.mask
        self.nbnotnull = source.nbnotnull
        self.updatepalette(0)
        self.delete_lists()

    def check_plot(self):
        self.plotted = True
        
        if not self.loaded and self.filename!='':
            self.read_data()
            if self.masknull:
                self.mask_data(0.)
        
        self.loaded=True

        if self.rgb is None:
            self.rgb=np.ones((self.nbx,self.nby,4),order='F',dtype=np.integer)
            self.updatepalette(0)
    
    def uncheck_plot(self,unload=True):
        self.plotted = False
        
        if unload:
            self.array=np.zeros([1])
            self.delete_lists()
            self.rgb=None
            self.loaded=False
    
    def get_header(self,abs=True) -> header_wolf():
        curhead=header_wolf()

        curhead.origx = self.origx
        curhead.origy = self.origy
        curhead.origz = self.origz

        curhead.dx = self.dx
        curhead.dy = self.dy
        curhead.dz = self.dz

        curhead.nbx = self.nbx
        curhead.nby = self.nby
        curhead.nbz = self.nbz

        curhead.translx = self.translx
        curhead.transly = self.transly
        curhead.translz = self.translz
        
        curhead.nb_blocks = self.nb_blocks

        if abs:
            curhead.origx+=curhead.translx
            curhead.origy+=curhead.transly
            curhead.origz+=curhead.translz
            
            curhead.translx=0.
            curhead.transly=0.
            curhead.translz=0.
        return curhead
                
    def set_header(self,header:header_wolf):
        self.origx = header.origx
        self.origy = header.origy
        self.origz = header.origz
        
        self.translx = header.translx
        self.transly = header.transly
        self.translz = header.translz

        self.dx = header.dx
        self.dy = header.dy
        self.dz = header.dz
        
        self.nbx = header.nbx
        self.nby = header.nby
        self.nbz = header.nbz

        self.nb_blocks = header.nb_blocks
        self.head_blocks=header.head_blocks.copy()

    def __add__(self, other):
        """Surcharge de l'opérateur d'addition"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        newArray.array = self.array + other.array
        return newArray

    def __sub__(self, other):
        """Surcharge de l'opérateur de soustraction"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        newArray.array = self.array - other.array
        return newArray

    def __pow__(self, other):
        """Surcharge de l'opérateur puissance"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        newArray.array = self.array**other
        return newArray

    def __truediv__(self, other):
        """Surcharge de l'opérateur puissance"""
        newArray = WolfArray()
        newArray.nbdims = self.nbdims
        newArray.nbx = self.nbx
        newArray.nby = self.nby
        newArray.dx = self.dx
        newArray.dy = self.dy
        newArray.origx = self.origx
        newArray.origy = self.origy
        newArray.translx = self.translx
        newArray.transly = self.transly

        if self.nbdims==3:
            newArray.nbz = self.nbz
            newArray.dz = self.dz
            newArray.origz = self.origz
            newArray.translz = self.translz
        
        newArray.array=np.where(other==0.,0.,self.array/other.array)
        return newArray

    def get_xy_infootprint_vect(self,myvect:vector) -> np.ndarray:
        i1,j1=self.get_ij_from_xy(myvect.minx,myvect.miny)
        i2,j2=self.get_ij_from_xy(myvect.maxx,myvect.maxy)
        mypts=np.zeros(((i2-i1+1)*(j2-j1+1),2))
        k=0
        for j in range(j1,j2+1): 
            for i in range(i1,i2+1):
                x,y=self.get_xy_from_ij(i,j)
                mypts[k]=[x,y]
                k+=1
        return mypts

    def select_insidepoly(self,myvect:vector):
        mypoints=self.get_xy_infootprint_vect(myvect)
        polygon=np.asarray(list([vert.x,vert.y] for vert in myvect.myvertices))
        path = mpltPath.Path(polygon)
        inside = path.contains_points(mypoints)
        self.myselection = list(np.where(inside,mypoints))

    def plot_selection(self):
        if len(self.myselection)==0:
            return
        glBegin(GL_QUADS)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        for cursel in self.myselection:
            x1=cursel[0]-self.dx/2.
            x2=cursel[0]+self.dx/2.
            y1=cursel[1]-self.dy/2.
            y2=cursel[1]+self.dy/2.
            glColor3f(1.,0.,0.)
            glVertex2f(x1,y1)
            glVertex2f(x2,y1)
            glVertex2f(x2,y2)
            glVertex2f(x1,y2)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        for cursel in self.myselection:
            x1=cursel[0]-self.dx/2.
            x2=cursel[0]+self.dx/2.
            y1=cursel[1]-self.dy/2.
            y2=cursel[1]+self.dy/2.
            glColor3f(0.,1.,0.)
            glVertex2f(x1,y1)
            glVertex2f(x2,y1)
            glVertex2f(x2,y2)
            glVertex2f(x1,y2)
        glEnd()

    def reset(self):
        if self.nbdims==2:
            self.array[:,:] = 0.0
        elif self.nbdims==3:
            self.array[:,:,:] = 0.0

    def allocate_ressources(self):
        if self.nbdims==2:
            self.array = ma.ones([self.nbx,self.nby]) 
        elif self.nbdims==3:
            self.array = ma.ones([self.nbx,self.nby,self.nbz]) 

    def read_all(self):
        """ Lecture d'un Wolf aray depuis le nom de fichier """
        self.read_txt_header()
        if self.preload:
            self.read_data()
            self.loaded=True
        return

    def write_all(self):
        """ Ecriture de tous les fichiers d'un Wolf array """
        self.write_txt_header()
        self.write_array()
        
    def rebin(self, factor, operation='mean'):
        """ Adaptation de la résolution"""
        operation = operation.lower()
        if not operation in ['sum', 'mean']:
            raise ValueError("Operation not supported.")
        
        self.nbx = int(self.nbx/factor)
        self.nby = int(self.nby/factor)
        self.dx = self.dx*float(factor)
        self.dy = self.dy*float(factor)
        new_shape=(self.nbx,self.nby)
        
        compression_pairs = [(d, c//d) for d,c in zip(new_shape,
                                                    self.array.shape)]
        flattened = [l for p in compression_pairs for l in p]
        self.array = self.array.reshape(flattened)
        for i in range(len(new_shape)):
            op = getattr(self.array, operation)
            self.array = np.float32(op(-1*(i+1)))

    def read_txt_header(self):
        """ Lecture du header .txt """
        if self.filename.endswith('.flt'):
            #Fichier .flt
            f = open(self.filename[:-4] + '.hdr', 'r')
            lines = f.read().splitlines()
            f.close()            
            
            tmp = lines[0].split(' ')
            self.nbx = int(tmp[-1])
            tmp = lines[1].split(' ')
            self.nby = int(tmp[-1])
            tmp = lines[2].split(' ')
            self.origx = float(tmp[-1])
            tmp = lines[3].split(' ')
            self.origy = float(tmp[-1])
            tmp = lines[4].split(' ')
            self.dx = self.dy = float(tmp[-1])
            pass
        else:
            with open(self.filename + '.txt', 'r') as f:
                lines = f.read().splitlines()

            tmp = lines[0].split(':')
            self.nbx = int(tmp[1])
            tmp = lines[1].split(':')
            self.nby = int(tmp[1])
            tmp = lines[2].split(':')
            self.origx = float(tmp[1])
            tmp = lines[3].split(':')
            self.origy = float(tmp[1])
            tmp = lines[4].split(':')
            self.dx = float(tmp[1])
            tmp = lines[5].split(':')
            self.dy = float(tmp[1])
            tmp = lines[6].split(':')
            self.wolftype = int(tmp[1])
            tmp = lines[7].split(':')
            self.translx = float(tmp[1])
            tmp = lines[8].split(':')
            self.transly = float(tmp[1])

            decal=9
            if self.wolftype==WOLF_ARRAY_FULL_SINGLE_3D:
                self.nbdims=3
                tmp = lines[9].split(':')
                self.nbz = int(tmp[1])
                tmp = lines[10].split(':')
                self.origz = float(tmp[1])
                tmp = lines[11].split(':')
                self.dz = float(tmp[1])
                tmp = lines[12].split(':')
                self.translz = float(tmp[1])
                decal=13
                
            if self.wolftype in WOLF_ARRAY_MB:
                tmp = lines[decal].split(':')
                self.nb_blocks = int(tmp[1])
                
                decal+=1
                for i in range(self.nb_blocks):
                    curhead = header_wolf()
                    tmp = lines[decal].split(':')
                    curhead.nbx = int(tmp[1])
                    tmp = lines[decal+1].split(':')
                    curhead.nby = int(tmp[1])
                    tmp = lines[decal+2].split(':')
                    curhead.origx = float(tmp[1])
                    tmp = lines[decal+3].split(':')
                    curhead.origy = float(tmp[1])
                    tmp = lines[decal+4].split(':')
                    curhead.dx = float(tmp[1])
                    tmp = lines[decal+5].split(':')
                    curhead.dy = float(tmp[1])
                    decal+=6
                    
                    curhead.translx = self.translx + self.origx
                    curhead.transly = self.transly + self.origy
                    
                    self.head_blocks[getkeyblock(i)]=curhead

    def write_txt_header(self):
        """ Ecriture de l'en-tête de Wolf array """
        f = open(self.filename + '.txt', 'w')
        f.write('NbX :\t{0}\n'.format(str(self.nbx)))
        f.write('NbY :\t{0}\n'.format(str(self.nby)))
        f.write('OrigX :\t{0}\n'.format(str(self.origx)))
        f.write('OrigY :\t{0}\n'.format(str(self.origy)))
        f.write('DX :\t{0}\n'.format(str(self.dx)))
        f.write('DY :\t{0}\n'.format(str(self.dy)))
        f.write('TypeEnregistrement :\t{0}\n'.format(str(self.wolftype)))
        f.write('TranslX :\t{0}\n'.format(str(self.translx)))
        f.write('TranslY :\t{0}\n'.format(str(self.transly)))
        if self.wolftype==WOLF_ARRAY_FULL_SINGLE_3D:
            f.write('NbZ :\t{0}\n'.format(str(self.nbz)))
            f.write('OrigZ :\t{0}\n'.format(str(self.origz)))
            f.write('DZ :\t{0}\n'.format(str(self.dz)))
            f.write('TranslZ :\t{0}\n'.format(str(self.translz)))

        if self.wolftype in WOLF_ARRAY_MB:
            f.write('Nb Blocs :\t{0}\n'.format(str(self.nb_blocks)))            
            for i in range(self.nb_blocks):
                curhead = self.head_blocks[getkeyblock(i)]
                f.write('NbX :\t{0}\n'.format(str(curhead.nbx)))
                f.write('NbY :\t{0}\n'.format(str(curhead.nby)))
                f.write('OrigX :\t{0}\n'.format(str(curhead.origx)))
                f.write('OrigY :\t{0}\n'.format(str(curhead.origy)))
                f.write('DX :\t{0}\n'.format(str(curhead.dx)))
                f.write('DY :\t{0}\n'.format(str(curhead.dy)))
                            
        f.close()

    def read_data(self):
        if self.cropini is None:            
            with open(self.filename, 'rb') as f:
                self._read_binary_data(f)
        else:                    
            with open(self.filename, 'rb') as f:
                if self.wolftype==1 or self.wolftype==7:
                    
                    imin,jmin = self.get_ij_from_xy(self.cropini[0][0],self.cropini[1][0]) 
                    imax,jmax = self.get_ij_from_xy(self.cropini[0][1],self.cropini[1][1])
                    
                    imin=int(imin)
                    jmin=int(jmin)
                    imax=int(imax)
                    jmax=int(jmax)
                    
                    oldnbx = self.nbx
                    oldnby = self.nby
                                    
                    self.nbx = imax-imin
                    self.nby = jmax-jmin
                    self.origx,self.origy = self.get_xy_from_ij(imin,jmin)
                    self.origx -=self.dx/2.
                    self.origy -=self.dy/2.
                    
                    locarray = np.zeros([self.nbx,self.nby])
                    
                    #on boucle sur les 'j'
                    nbi = imax-imin
                    if self.filename.endswith('.flt'):
                        f.seek(((oldnby-jmax)*oldnbx+imin)*4)
                    else:
                        f.seek((imin+jmin*oldnbx)*4)                    

                    for j in range(jmin,jmax):
                        locarray[0:imax-imin,j-jmin] = np.frombuffer(f.read(4*nbi),dtype=np.float32)                        
                        f.seek((oldnbx-nbi)*4,1)
                    
                    self.array = ma.masked_array(locarray, dtype=np.float32)

            if self.filename.endswith('.flt'):
                #fichier .flt --> miroir "horizontal"
                self.array = np.fliplr(self.array)

    def _read_binary_data(self,f,seek=0):
        
        if seek>0:
            f.seek(0)
        
        if self.wolftype==WOLF_ARRAY_FULL_SINGLE or self.wolftype==WOLF_ARRAY_FULL_SINGLE_3D:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*4), dtype=np.float32)
            self.array = ma.masked_array(locarray.copy(), dtype=np.float32)
        elif self.wolftype ==WOLF_ARRAY_FULL_DOUBLE:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*8), dtype=np.float64)
            self.array = ma.masked_array(locarray.copy(), dtype=np.float64)
        elif self.wolftype==WOLF_ARRAY_FULL_INTEGER:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*4), dtype=np.int32)
            self.array = ma.masked_array(locarray.copy(), dtype=np.int32)
        elif self.wolftype==WOLF_ARRAY_FULL_INTEGER16:
            locarray = np.frombuffer(f.read(self.nbx*self.nby*2), dtype=np.int16)
            self.array = ma.masked_array(locarray.copy(), dtype=np.int16)

        if self.nbdims==2:
            self.array = self.array.reshape(self.nbx, self.nby, order='F')
        elif self.nbdims==3:
            self.array = self.array.reshape(self.nbx, self.nby, self.nbz, order='F')
                                    
    def write_array(self):
        """ Ecriture du tableau en binaire """
        self.array.data.transpose().tofile(self.filename, "")

    def write_xyz(self, fname):
        """ Ecriture d un fichier xyz avec toutes les données du Wolf Array """
        my_file = XYZFile(fname)
        my_file.fill_from_wolf_array(self)
        my_file.write_to_file()

    def get_xyz(self,which='all'):
        x1,y1 = self.get_xy_from_ij(0,0)
        x2,y2 = self.get_xy_from_ij(self.nbx,self.nby,aswolf=True)
        xloc=np.linspace(x1,x2,self.nbx)
        yloc=np.linspace(y1,y2,self.nby)
        xy=np.meshgrid(xloc,yloc,indexing='xy')
        
        xyz = np.column_stack([xy[0].flatten(),xy[1].flatten(),self.array.flatten()])
        
        filter = np.invert(ma.getmaskarray(self.array).flatten())
                
        return xyz[filter]

    def set_general_frame_from_xyz(self, fname, dx, dy):
        """ Lecture d'un fichier xyz et initialisation des données de base """
        my_file = XYZFile(fname)
        my_file.read_from_file()
        (xlim, ylim) = my_file.get_extent()

        self.dx = dx
        self.dy = dy
        self.origx = m.floor(xlim[0]) - 5.0*self.dx
        self.origy = m.floor(ylim[0]) - 5.0 * self.dy
        self.nbx = int((m.floor(xlim[1]) - m.ceil(xlim[0]))/self.dx) + 10
        self.nby = int((m.floor(ylim[1]) - m.ceil(ylim[0]))/self.dy) + 10

        self.array = np.zeros((self.nbx, self.nby))

    def mask_reset(self):
        if self.nbdims==2:
            self.array.mask = np.zeros((self.nbx,self.nby))
            self.nbnotnull = self.nbx * self.nby
        elif self.nbdims==3:
            self.array.mask = np.zeros((self.nbx,self.nby,self.nbz))
            self.nbnotnull = self.nbx * self.nby * self.nbz 

    def mask_data(self, value):
        self.array.mask = self.array.data == value
        #self.array = np.ma.masked_where(self.array == value, self.array)
        self.nbnotnull = self.array.count()

    def mask_allexceptdata(self, value):
        self.array.mask = self.array.data != value
        self.nbnotnull = self.array.count()

    def mask_invert(self):
        self.array.mask = not(self.array.mask)
        self.nbnotnull = self.array.count()

    def meshgrid(self,mode='gc'):
        x_start = self.translx + self.origx
        y_start = self.transly + self.origy
        if mode == 'gc':
            x_discr = np.linspace(x_start + self.dx / 2, x_start + self.nbx * self.dx - self.dx / 2, self.nbx)
            y_discr = np.linspace(y_start + self.dy / 2, y_start + self.nby * self.dy - self.dy / 2, self.nby)
        elif mode == 'borders':
            x_discr = np.linspace(x_start, x_start + self.nbx * self.dx , self.nbx+1)
            y_discr = np.linspace(y_start , y_start + self.nby * self.dy , self.nby+1)

        y, x = np.meshgrid(y_discr, x_discr)
        return x, y

    def crop(self,i_start,j_start,nbx,nby,k_start=1,nbz=1):
        newWolfArray = WolfArray()
        newWolfArray.nbx = nbx
        newWolfArray.nby = nby
        newWolfArray.dx = self.dx
        newWolfArray.dy = self.dy
        newWolfArray.origx = self.origx + i_start*self.dx
        newWolfArray.origy = self.origy + j_start * self.dy
        newWolfArray.translx = self.translx
        newWolfArray.transly = self.transly

        if self.nbdims ==3:
            newWolfArray.nbz = nbz
            newWolfArray.dz = self.dz
            newWolfArray.origz = self.origz + k_start*self.dz
            newWolfArray.translz = self.translz
            
            newWolfArray.array = self.array[i_start:i_start+nbx, j_start:j_start+nby, k_start:k_start+nbz]
        elif self.nbdims==2:
            newWolfArray.array = self.array[i_start:i_start+nbx, j_start:j_start+nby]
        
        return newWolfArray

    def extremum(self,which='min'):
        if which=='min':
            my_extr = np.amin(self.array)
        else:
            my_extr = np.amax(self.array)

        return my_extr
    
    def get_bounds(self,abs=True):
        if abs:
            return ([self.origx+self.translx, self.origx+self.translx + float(self.nbx)*self.dx],
                    [self.origy+self.transly, self.origy+self.transly + float(self.nby)*self.dy])
        else:
            return ([self.origx, self.origx + float(self.nbx)*self.dx],
                    [self.origy, self.origy + float(self.nby)*self.dy])

    def get_ij_from_xy(self,x,y,z=0.,scale=1.,aswolf=False,abs=True):

        locx = np.float64(x) - self.origx
        locy = np.float64(y) - self.origy
        locz = np.float64(z) - self.origz
        if abs:
            locx = locx -self.translx
            locy = locy -self.transly
            locz = locz -self.translz
            
        i = np.int32(locx / (self.dx*scale))
        j = np.int32(locy / (self.dy*scale))

        if aswolf:
            i+=1
            j+=1

        if self.nbdims==3:
            k = np.int32(locz / (self.dz*scale))
            if aswolf:
                k+=1
            return i, j, k # ATTENTION, Indices en numérotation Python --> WOLF ajouter +1
        elif self.nbdims==2:
            return i, j # ATTENTION, Indices en numérotation Python --> WOLF ajouter +1

    def get_xy_from_ij(self,i,j,k=0,scale=1.,aswolf=False,abs=True):
        
        i=np.int32(i)
        j=np.int32(j)

        if aswolf:
            i += -1
            j += -1

        if abs:
            x= (np.float64(i) + .5) * (self.dx*scale) + self.origx + self.translx
            y= (np.float64(j) + .5) * (self.dy*scale) + self.origy + self.transly
        else:
            x= (np.float64(i) + .5) * (self.dx*scale) + self.origx
            y= (np.float64(j) + .5) * (self.dy*scale) + self.origy

        if self.nbdims==3:
            k=np.int32(k)
            if aswolf:
                k += -1

            if abs:
                z= (np.float64(k) - .5) * (self.dz*scale) + self.origz + self.translz
            else:
                z= (np.float64(k) - .5) * (self.dz*scale) + self.origz
                
            return x,y,z
        
        elif self.nbdims==2:
            return x,y
        
    def get_value(self,x,y,z=0.):

        if self.nbdims==2:        
            i, j = self.get_ij_from_xy(x,y)
            if i>=0 and i<self.nbx and j>=0 and j<self.nby:
                value = self.array[i,j]
            else:
                value = -99999
        elif self.nbdims==3:
            i, j, k = self.get_ij_from_xy(x,y,z)
            if i>=0 and i<self.nbx and j>=0 and j<self.nby and k>=0 and k<self.nbz:
                value = self.array[i,j,k]
            else:
                value = -99999

        return value

    def get_xlim(self,window_x,window_y):
        a_x = window_x / (self.nbx*self.dx)
        a_y = window_y / (self.nby*self.dy)
        if a_x < a_y :
            #C'est la mise à l'échelle selon x qui compte
            return (self.origx + self.translx, self.origx + self.translx + self.nbx * self.dx)
        else:
            #C'est la mise à l'échelle selon y qui compte
            l = (self.nby * self.dy) / window_y * window_x
            return (self.origx + self.translx + self.nbx * self.dx * 0.5 - l * 0.5,
                    self.origx + self.translx + self.nbx * self.dx * 0.5 + l * 0.5)

    def get_ylim(self,window_x,window_y):
        a_x = window_x / (self.nbx * self.dx)
        a_y = window_y / (self.nby * self.dy)
        if a_x < a_y:
            # C'est la mise à l'échelle selon x qui compte
            l = (self.nbx * self.dx) / window_x * window_y
            return (self.origy + self.transly + self.nby * self.dy * 0.5 - l * 0.5,
                    self.origy + self.transly + self.nby * self.dy * 0.5 + l * 0.5)
        else:
            # C'est la mise à l'échelle selon y qui compte
            return (self.origy + self.transly, self.origy + self.transly + self.nby * self.dy)

    def updatepalette(self,which=0,onzoom=[]):
        
        if onzoom!=[]:
            istart,jstart = self.get_ij_from_xy(onzoom[0],onzoom[2])
            iend,jend = self.get_ij_from_xy(onzoom[1],onzoom[3])
            
            istart= 0 if istart < 0 else istart
            jstart= 0 if jstart < 0 else jstart
            iend= self.nbx if iend > self.nbx else iend
            jend= self.nby if jend > self.nby else jend
            
            partarray=self.array[istart:iend,jstart:jend]
            self.mypal.isopop(partarray[partarray.mask==False],partarray.count())            
        else:
            self.mypal.isopop(self.array[self.array.mask==False],self.nbnotnull)
        
        self.rgb = self.mypal.get_rgba(self.array)
        pass

    def plot(self, sx=None, sy=None,xmin=None,ymin=None,xmax=None,ymax=None):
        
        self.plotting=True
        
        if not self.plotted:
            return

        if self.plotted and sx is None:
            sx=self.sx
            sy=self.sy
            xmin=self.xmin
            xmax=self.xmax
            ymin=self.ymin
            ymax=self.ymax
        else:
            self.sx=sx
            self.sy=sy
            self.xmin=xmin
            self.xmax=xmax
            self.ymin=ymin
            self.ymax=ymax

        nbpix=min(sx*self.dx,sy*self.dy)
        if nbpix>=1.:
            #si une maille est tracée sur au moins 2 pixels
            curscale=1
        elif math.ceil(1./nbpix)<=3:
            curscale = math.ceil(math.ceil(1./nbpix))
        else:
            curscale = math.ceil(math.ceil(1./nbpix)/3)*3

        curscale=max(curscale,1)
        cursize = curscale #2.**curscale
        curnbx = max(math.ceil(float(self.nbx)/(self.gridsize*cursize)),1)
        curnby = max(math.ceil(float(self.nby)/(self.gridsize*cursize)),1)

        if not cursize in self.mygrid.keys():
            self.mygrid[cursize]={}
            curlist=self.mygrid[cursize]
            curlist['nbx']=curnbx
            curlist['nby']=curnby
            print('réservation listes ')
            numlist = glGenLists(curnbx*curnby)
            curlist['firstlist']=numlist
            print(numlist)
            curlist['mylists']= np.linspace(numlist,numlist+curnbx*curnby-1,num=curnbx*curnby,dtype=np.integer).reshape((curnbx,curnby),order='F')
            curlist['done']=np.zeros((curnbx,curnby),dtype=np.integer,order='F')

        if(curnbx==1 and curnby==1):
            if(self.gridmaxscales==-1):
                self.gridmaxscales=curscale
            elif curscale>self.gridmaxscales:
                curscale=self.gridmaxscales
                cursize = curscale
                curnbx = max(math.ceil(float(self.nbx)/(self.gridsize*cursize)),1)
                curnby = max(math.ceil(float(self.nby)/(self.gridsize*cursize)),1)
            
        istart,jstart = self.get_ij_from_xy(xmin,ymin,scale=cursize*float(self.gridsize))
        iend,jend     = self.get_ij_from_xy(xmax,ymax,scale=cursize*float(self.gridsize))

        istart=max(0,istart)
        jstart=max(0,jstart)
        iend=min(curnbx-1,iend)
        jend=min(curnby-1,jend)
        
        for j in range(jstart,jend+1):
            for i in range(istart,iend+1):
                self.fillonecellgrid(curscale,i,j)
                try:
                    mylistdone = self.mygrid[cursize]['done'][i,j]
                    if mylistdone==1 :
                        mylist = self.mygrid[cursize]['mylists'][i,j]
                        if mylist>0:
                            glCallList(self.mygrid[cursize]['mylists'][i,j])                        
                except:
                    pass
                
        self.plotting=False
                
    def delete_lists(self):
        for idx,cursize in enumerate(self.mygrid):
            curlist=self.mygrid[cursize]
            nbx=curlist['nbx']
            nby=curlist['nby']
            first=curlist['firstlist']
            glDeleteLists(first,nbx*nby)
            print(first,nbx*nby)

        self.mygrid={}

    def plot_matplotlib(self):

        self.mask_data(0.)
        self.updatepalette(0)

        fig = plt.figure()

        ax = fig.add_subplot(111)
        plt.imshow(self.array.transpose(),origin='lower',cmap=self.mypal,extent=(self.origx,self.origx+self.dx*self.nbx,self.origy,self.origy+self.dy*self.nby))
        ax.set_aspect('equal')

        plt.show()
                            
    def fillonecellgrid(self,curscale,loci,locj,force=False):

        cursize = curscale #2**curscale

        curlist=self.mygrid[cursize]
        exists=curlist['done'][loci,locj]

        if exists==0 or force:
            #print('Computing OpenGL List for '+str(loci)+';' +str(locj) + ' on scale factor '+str(curscale))
            
            ox=self.origx+self.translx
            oy=self.origy+self.transly
            dx=self.dx
            dy=self.dy

            numlist = int(curlist['mylists'][loci,locj])
            #print(numlist)

            glNewList(numlist,GL_COMPILE)
            glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)      

            step=self.gridsize*cursize
            jstart = max(locj*step,0)
            jend = min(jstart+step,self.nby)
            istart = max(loci*step,0)
            iend = min(istart+step,self.nbx)
            
            try:
                if self.wolftype!=WOLF_ARRAY_FULL_SINGLE:
                    if self.nbnotnull!=self.nbx*self.nby:
                        if self.nbnotnull>0:  
                            wolfogl.addme(self.array.astype(dtype=np.float32),self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue)
                    elif self.nbnotnull>0:
                        wolfogl.addmeall(self.array.astype(dtype=np.float32),self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue)
                else:
                    if self.nbnotnull!=self.nbx*self.nby:
                        if self.nbnotnull>0:  
                            wolfogl.addme(self.array,self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue)
                    else:
                        wolfogl.addmeall(self.array,self.rgb,ox,oy,dx,dy,jstart,jend,istart,iend,cursize,self.nullvalue)
            except:
                pass
            glEndList()

            curlist['done'][loci,locj]=1
            
class WolfArrayMB(WolfArray):
    
    myblocks:dict
    
    def __init__(self, fname=None, mold=None, masknull=True, crop=None):
        self.myblocks={}
        super().__init__(fname, mold, masknull, crop)
        self.wolftype = WOLF_ARRAY_MB_SINGLE

    def check_plot(self):
        self.plotted = True
        self.mimic_plotdata()
        
        if not self.loaded and self.filename!='':
            self.read_data()
            if self.masknull:
                self.mask_data(0.)
            if self.rgb is None:
                self.rgb=np.ones((self.nbx,self.nby,4),order='F',dtype=np.integer)
            self.updatepalette(0)
            self.loaded=True
    
    def uncheck_plot(self,unload=True):
        self.plotted = False
        self.mimic_plotdata()
        
        if unload:
            for curblock in self.myblocks.values():
                curblock.uncheck_plot(unload)
            self.rgb = None
            self.myblocks={}
            self.loaded=False
        
    def mask_data(self, value):
        self.nbnotnull=0
        for i in range(self.nb_blocks):
            curblock=self.myblocks[getkeyblock(i)]
            curarray=curblock.array
            curarray.mask = curarray.data == value
            
            nbnotnull=curarray.count()
            curblock.nbnotnull = nbnotnull
            self.nbnotnull += nbnotnull
    
    def read_data(self):
                
        with open(self.filename, 'rb') as f:
            
            for i in range(self.nb_blocks):
                curblock = WolfArray(whichtype=WOLF_ARRAY_FULL_SINGLE)
                curblock.isblock=True
                curblock.blockindex = i
                curblock.set_header(self.head_blocks[getkeyblock(i)])
                curblock._read_binary_data(f)
                self.myblocks[getkeyblock(i)]=curblock                    

    def write_array(self):
        """ Ecriture du tableau en binaire """
        with open(self.filename,'wb') as f:
            for i in range(self.nb_blocks):
                curarray = self.myblocks[getkeyblock(i)]
                f.write(curarray.array.data.transpose().tobytes())

    def get_ij_from_xy(self, x, y, z=0, scale=1, aswolf=False,abs=True,which_block=1):
        return self.myblocks[getkeyblock(which_block,False)].get_ij_from_xy(x, y, z, scale, aswolf,abs)
    
    def get_values_as_wolf(self,i,j,which_block=1):

        keyblock=getkeyblock(which_block,False)
        curblock=self.myblocks[keyblock]
        
        nbx = curblock.nbx
        nby = curblock.nby

        if(i>0 and i<=nbx and j>0 and j<=nby):
            h = curblock.array[i-1,j-1]
        
        return h

    def get_value(self,x,y,abs=True):

        h = np.NaN
        for curblock in self.myblocks.values():
            curblock:WolfArray
            nbx = curblock.nbx
            nby = curblock.nby
            
            i,j=curblock.get_ij_from_xy(x,y,abs=abs)

            if(i>0 and i<=nbx and j>0 and j<=nby):
                h = curblock.array[i,j]
                if not curblock.array.mask[i,j]:
                    break

        return h

    def get_xy_from_ij(self,i,j,which_block,aswolf=False,abs=True):
        x,y = self.myblocks[getkeyblock(which_block,False)].get_xy_from_ij(i,j,aswolf=aswolf,abs=abs)
        return x,y

    def get_blockij_from_xy(self,x,y,abs=True):

        exists=False
        k=1
        for curblock in self.myblocks.values():
            curblock:WolfArray
            nbx = curblock.nbx
            nby = curblock.nby
            
            i,j=curblock.get_ij_from_xy(x,y,abs=abs)

            if(i>0 and i<=nbx and j>0 and j<=nby):
                if not curblock.array.mask[i,j]:
                    exists=True
                    break
            k+=1
        
        if exists:
            return i,j,k
        else:
            return -1,-1,-1

    def link_palette(self):
        for curblock in self.myblocks.values():
            curblock.mypal = self.mypal
    
    def updatepalette(self,which=0,onzoom=[]):
        
        if onzoom!=[]:
            allarrays=[]
            for curblock in self.myblocks.values():
                istart,jstart = curblock.get_ij_from_xy(onzoom[0],onzoom[2])
                iend,jend = curblock.get_ij_from_xy(onzoom[1],onzoom[3])
                
                istart= 0 if istart < 0 else istart
                jstart= 0 if jstart < 0 else jstart
                iend= curblock.nbx if iend > curblock.nbx else iend
                jend= curblock.nby if jend > curblock.nby else jend
                
                partarray=curblock.array[istart:iend,jstart:jend]
                partarray=partarray[partarray.mask==False]
                if len(partarray)>0:
                    allarrays.append(partarray.flatten())
            
            allarrays=np.concatenate(allarrays)            
            self.mypal.isopop(allarrays,allarrays.count())            
        else:
            allarrays = np.concatenate([curblock.array[curblock.array.mask==False].flatten() for curblock in self.myblocks.values()])
            self.mypal.isopop(allarrays,self.nbnotnull)
        
        self.link_palette()
        for curblock in self.myblocks.values():
            curblock.rgb = self.mypal.get_rgba(curblock.array)

    def delete_lists(self):
        for curblock in self.myblocks.values():
            curblock.delete_lists()

    def mimic_plotdata(self): 
        for curblock in self.myblocks.values():
            curblock:WolfArray
            curblock.plotted = self.plotted
            curblock.plotting = self.plotting
            
    def plot(self, sx=None, sy=None,xmin=None,ymin=None,xmax=None,ymax=None):
        
        self.plotting=True
        self.mimic_plotdata()
        
        for curblock in self.myblocks.values():
            curblock.plot(sx, sy,xmin,ymin,xmax,ymax)
        
        self.plotting=False
        self.mimic_plotdata()
            
    def fillonecellgrid(self,curscale,loci,locj,force=False):
        for curblock in self.myblocks.values():
                curblock.fillonecellgrid(curscale,loci,locj,force)
                
class WolfArrayMNAP(WolfArrayMB):
    
    contour:Zones
    
    def __init__(self, fname=None, mold=None, masknull=True, crop=None):
        super().__init__(fname, mold, masknull, crop)
        
        self.contour=Zones()
        
    def read_data(self):
        with open(self.filename+'.mnap') as f:
            lines=f.read().splitlines()
            
            self.nb_blocks=abs(int(lines[0]))
            self.contour= Zones()
            
            decal=1
            for i in range(self.nb_blocks):
                curkey = getkeyblock(i)
                curarray = WolfArray()
                self.myblocks[curkey]=curarray
                
                curarray.wolftype=WOLF_ARRAY_FULL_INTEGER8
                curarray.isblock=True
                curarray.blockindex = i
                
                tmp=re.sub('\\s+', ' ', lines[decal].strip()).split(' ')
                curarray.dx = float(tmp[0])
                curarray.dy = float(tmp[1])

                tmp=re.sub('\\s+', ' ', lines[decal+1].strip()).split(' ')
                curarray.origx = float(tmp[0])-self.origx

                tmp=re.sub('\\s+', ' ', lines[decal+2].strip()).split(' ')
                curarray.origy = float(tmp[0])-self.origy
                
                tmp=re.sub('\\s+', ' ', lines[decal+3].strip()).split(' ')
                curarray.nbx = int(tmp[0])
                curarray.nby = int(tmp[1])
                
                decal+=4
                myarray=[]
                
                for j in range(curarray.nby):
                    newline = [np.int32(curval) for curval in re.sub('\\s+', ' ',lines[decal].strip()).split()]
                    while len(newline) != curarray.nbx:
                        decal+=1
                        newline = np.concatenate([newline,[np.int32(curval) for curval in re.sub('\\s+', ' ',lines[decal].strip()).split()]])
                    myarray.append(newline)
                    decal+=1
                                
                curarray.array = np.flipud(np.ma.asarray(myarray,order='C'))                                                

                curzone=zone(name=curkey)
                contourblock = vector(name='contour')
                
                curzone.add_vector(contourblock)
                self.contour.add_zone(curzone)

                nbvert = int(lines[decal])
                for j in range(nbvert):
                    decal+=1
                    xy = re.sub('\\s+', ' ', lines[decal].strip()).split(' ')
                    myvert = wolfvertex(float(xy[0]),float(xy[1]))
                    contourblock.add_vertex(myvert)
                decal+=1
                curarray.translx = self.translx+self.origx
                curarray.transly = self.transly+self.origy
    
    def read_txt_header(self):
        
        with open(self.filename+'.trl') as f:
            lines=f.read().splitlines()
            self.translx = float(lines[1])
            self.transly = float(lines[2])

        with open(self.filename+'.par') as f:
            lines=f.read().splitlines()
            self.dx = float(lines[7])
            self.dy = float(lines[8])
            self.nbx = int(lines[9])
            self.nby = int(lines[10])
            self.origx = float(lines[11])
            self.origy = float(lines[12])
            
        self.wolftype = WOLF_ARRAY_MNAP_INTEGER
        