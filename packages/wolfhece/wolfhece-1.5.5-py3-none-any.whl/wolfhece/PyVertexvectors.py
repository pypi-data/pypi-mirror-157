import matplotlib.path as mpltPath
import numpy as np
from wx.dataview import *
from wx.core import BoxSizer, FlexGridSizer, TreeItemId
import wx
from OpenGL.GL  import *
from shapely.geometry import LineString, MultiLineString

from .PyTranslate import _
from .CpGrid import CpGrid
from .PyVertex import wolfvertex,getIfromRGB,getRGBfromI
from .PyParams import Wolf_Param

class vectorproperties:
    
    used:bool
    
    color:int
    width:int
    style:int
    alpha:int
    closed=bool
    filled:bool
    legendvisible:bool
    transparent:bool
    flash:bool

    legendtext:str
    legendrelpos:int
    legendx:float
    legendy:float

    legendbold:bool
    legenditalic:bool
    legendunderlined:bool
    legendfontname=str
    legendfontsize:int
    legendcolor:int

    extrude:bool = False

    myprops:Wolf_Param = None

    def __init__(self,lines=[]) -> None:
        
        if len(lines)>0:
            line1=lines[0].split(',')
            line2=lines[1].split(',')

            self.color=int(line1[0])
            self.width=int(line1[1])
            self.style=int(line1[2])
            self.closed=line1[3]=='#TRUE#'
            self.filled=line1[4]=='#TRUE#'
            self.legendvisible=line1[5]=='#TRUE#'
            self.transparent=line1[6]=='#TRUE#'
            self.alpha=int(line1[7])
            self.flash=line1[8]=='#TRUE#'

            self.legendtext=line2[0]
            self.legendrelpos=int(line2[1])
            self.legendx=float(line2[2])
            self.legendy=float(line2[3])
            self.legendbold=line2[4]=='#TRUE#'
            self.legenditalic=line2[5]=='#TRUE#'
            self.legendfontname=str(line2[6])
            self.legendfontsize=int(line2[7])
            self.legendcolor=int(line2[8])
            self.legendunderlined=line2[9]=='#TRUE#'

            self.used=lines[2]=='#TRUE#'
        else:
            self.color=0
            self.width=1
            self.style=1
            self.closed=False
            self.filled=False
            self.legendvisible=False
            self.transparent=False
            self.alpha=0
            self.flash=False

            self.legendtext=''
            self.legendrelpos=5
            self.legendx=0.
            self.legendy=0.
            self.legendbold=False
            self.legenditalic=False
            self.legendfontname='Arial'
            self.legendfontsize=10
            self.legendcolor=0
            self.legendunderlined=False

            self.used=True
        pass

    def save(self,f):
        line1 = str(self.color) + ',' + str(self.width)+','+ str(self.style)

        added = ',#TRUE#' if self.closed else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.filled else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.legendvisible else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.transparent else ',#FALSE#'
        line1+=added
        line1+=','+str(self.alpha)
        added = ',#TRUE#' if self.flash else ',#FALSE#'
        line1+=added
        
        f.write(line1+'\n')

        line1 = self.legendtext + ',' + str(self.legendrelpos)+','+ str(self.legendx)+','+ str(self.legendy)
        added = ',#TRUE#' if self.legendbold else ',#FALSE#'
        line1+=added
        added = ',#TRUE#' if self.legenditalic else ',#FALSE#'
        line1+=added
        line1+= ','+self.legendfontname + ',' + str(self.legendfontsize)+ ',' + str(self.legendcolor)
        added = ',#TRUE#' if self.legendunderlined else ',#FALSE#'
        line1+=added
                
        f.write(line1+'\n')
        
        added = '#TRUE#' if self.used else '#FALSE#'
        f.write(added+'\n')
            
    def fill_property(self):
        
        curdict=self.myprops.myparams
        if 'Draw' in curdict.keys():
            keysactive = curdict['Draw'].keys()
            if 'Color' in keysactive:
                self.color = getIfromRGB(curdict['Draw']['Color']['value'].replace('(','').replace(')','').split(', '))
            if 'Width' in keysactive:
                self.width = int(curdict['Draw']['Width']['value'])
            if 'Style' in keysactive:
                self.style = int(curdict['Draw']['Style']['value'])
            if 'Closed' in keysactive:
                self.closed = bool(curdict['Draw']['Closed']['value'])
            if 'Filled' in keysactive:
                self.filled = bool(curdict['Draw']['Filled']['value'])
            if 'Transparent' in keysactive:
                self.transparent = bool(curdict['Draw']['Transparent']['value'])
            if 'Alpha' in keysactive:
                self.alpha = int(curdict['Draw']['Alpha']['value'])
            if 'Flash' in keysactive:
                self.flash = bool(curdict['Draw']['Flash']['value'])

        if 'Legend' in curdict.keys():
            keysactive = curdict['Legend'].keys()
            if 'Underlined' in keysactive:
                self.legendunderlined = bool(curdict['Legend']['Underlined']['value'])
            if 'Bold' in keysactive:
                self.legendbold = bool(curdict['Legend']['Bold']['value'])
            if 'Font name' in keysactive:
                self.legendfontname = str(curdict['Legend']['Font name']['value'])
            if 'Font size' in keysactive:
                self.legendfontsize = int(curdict['Legend']['Font size']['value'])
            if 'Color' in keysactive:
                self.legendcolor = getIfromRGB(curdict['Legend']['Color']['value'].replace('(','').replace(')','').split(', '))
            if 'Italic' in keysactive:
                self.legenditalic = bool(curdict['Legend']['Italic']['value'])
            if 'relative Position' in keysactive:
                self.legendrelpos = int(curdict['Legend']['relative Position']['value'])
            if 'Text' in keysactive:
                self.legendtext = str(curdict['Legend']['Text']['value'])
            if 'Visible' in keysactive:
                self.legendvisible = bool(curdict['Legend']['Visible']['value'])
            if 'X' in keysactive:
                self.legendx = float(curdict['Legend']['X']['value'])
            if 'Y' in keysactive:
                self.legendy = float(curdict['Legend']['Y']['value'])

    def defaultprop(self):
        if self.myprops is None:
            self.myprops=Wolf_Param(title='Vector Properties',to_read=False)
            self.myprops.callbackdestroy = self.destroyprop
            self.myprops.callback=self.fill_property
            self.myprops.saveme.Disable()
            self.myprops.loadme.Disable()
            self.myprops.reloadme.Disable()

        self.myprops.addparam('Draw','Color',(0,0,0),'Color','Drawing color',whichdict='Default')
        self.myprops.addparam('Draw','Width',1,'Integer','Drawing width',whichdict='Default')
        self.myprops.addparam('Draw','Style',1,'Integer','Drawing style',whichdict='Default')
        self.myprops.addparam('Draw','Closed',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Draw','Filled',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Draw','Transparent',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Draw','Alpha',0,'Integer','Transparent intensity',whichdict='Default')
        self.myprops.addparam('Draw','Flash',False,'Logical','',whichdict='Default')

        self.myprops.addparam('Legend','Visible',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Legend','Text','','String','',whichdict='Default')
        self.myprops.addparam('Legend','relative Position',5,'Integer','',whichdict='Default')
        self.myprops.addparam('Legend','X',0,'Float','',whichdict='Default')
        self.myprops.addparam('Legend','Y',0,'Float','',whichdict='Default')
        self.myprops.addparam('Legend','Bold',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Legend','Italic',False,'Logical','',whichdict='Default')
        self.myprops.addparam('Legend','Font name','Arial','String','',whichdict='Default')
        self.myprops.addparam('Legend','Font size',10,'Integer','',whichdict='Default')
        self.myprops.addparam('Legend','Color',(0,0,0),'Color','',whichdict='Default')
        self.myprops.addparam('Legend','Underlined',False,'Logical','',whichdict='Default')

    def destroyprop(self):
        self.myprops=None

    def show(self):
        self.defaultprop()

        self.myprops.addparam('Draw','Color',getRGBfromI(self.color),'Color','Drawing color')
        self.myprops.addparam('Draw','Width',self.width,'Integer','Drawing width')
        self.myprops.addparam('Draw','Style',self.style,'Integer','Drawing style')
        self.myprops.addparam('Draw','Closed',self.closed,'Logical','')
        self.myprops.addparam('Draw','Filled',self.filled,'Logical','')
        self.myprops.addparam('Draw','Transparent',self.transparent,'Logical','')
        self.myprops.addparam('Draw','Alpha',self.alpha,'Integer','Transparent intensity')
        self.myprops.addparam('Draw','Flash',self.flash,'Logical','')

        self.myprops.addparam('Legend','Visible',self.legendvisible,'Logical','')
        self.myprops.addparam('Legend','Text',self.legendtext,'String','')
        self.myprops.addparam('Legend','relative Position',self.legendrelpos,'Integer','')
        self.myprops.addparam('Legend','X',self.legendx,'Float','')
        self.myprops.addparam('Legend','Y',self.legendy,'Float','')
        self.myprops.addparam('Legend','Bold',self.legendbold,'Logical','')
        self.myprops.addparam('Legend','Italic',self.legenditalic,'Logical','')
        self.myprops.addparam('Legend','Font name',self.legendfontname,'String','')
        self.myprops.addparam('Legend','Font size',self.legendfontsize,'Integer','')
        self.myprops.addparam('Legend','Color',getRGBfromI(self.legendcolor),'Color','')
        self.myprops.addparam('Legend','Underlined',self.legendunderlined,'Logical','')

        self.myprops.Populate()
        self.myprops.Show()


class vector:

    myname:str
    nbvertices:int
    myvertices:list
    myprop:vectorproperties
    minx:float
    miny:float
    maxx:float
    maxy:float

    mytree:TreeListCtrl
    myitem:TreeItemId

    def __init__(self,lines:list=[],is2D=True,name='',parentzone=None) -> None:
            
        self.is2D = is2D
        self.closed=False
        self.parentzone=parentzone
        
        if type(lines)==list:
            if len(lines)>0:
                self.myname=lines[0]
                self.nbvertices=int(lines[1])
                self.myvertices=[]

                if is2D:
                    for i in range(self.nbvertices):
                        try:
                            curx,cury=lines[2+i].split()
                        except:
                            curx,cury=lines[2+i].split(',')
                        curvert = wolfvertex(float(curx),float(cury))
                        self.myvertices.append(curvert)
                else:
                    for i in range(self.nbvertices):
                        try:
                            curx,cury,curz=lines[2+i].split()
                        except:
                            curx,cury,curz=lines[2+i].split(',')
                        curvert = wolfvertex(float(curx),float(cury),float(curz))
                        self.myvertices.append(curvert)

                self.myprop=vectorproperties(lines[self.nbvertices+2:])

        if name!='':
            self.myname=name
            self.nbvertices=0
            self.myvertices=[]
            self.myprop=vectorproperties()
        
        self.linestring = None

    def save(self,f):
        f.write(self.myname+'\n')
        f.write(str(self.nbvertices)+'\n')

        if self.is2D:
            for curvert in self.myvertices:
                f.write(f'{curvert.x} {curvert.y}'+'\n')
        else:
            for curvert in self.myvertices:
                f.write(f'{curvert.x} {curvert.y} {curvert.z}'+'\n')
                
        self.myprop.save(f)

    def isinside(self,x,y):
        polygon=np.asarray(list([vert.x,vert.y] for vert in self.myvertices))
        path = mpltPath.Path(polygon)
        inside2 = path.contains_points([[x,y]])
        return inside2
    
    def asshapely_ls(self):
        polygon=np.asarray(list([vert.x,vert.y] for vert in self.myvertices))
        return LineString(polygon)

    def prepare_shapely(self):
        self.linestring = self.asshapely_ls()
        
    def intersection(self,vec2 = None,eval_dist=False,norm=False):
        ls1 = self.asshapely_ls() if self.linestring is None else self.linestring
        ls2 = vec2.asshapely_ls()
        
        myinter = ls1.intersection(ls2)
        
        if eval_dist:
            mydists = ls1.project(myinter,normalized=norm)
            return ls1.intersection(ls2),mydists
        else:
            return ls1.intersection(ls2)

    def reset(self):
        self.nbvertices=0
        self.myvertices=[]
        self.linestring=None
    
    def add_vertex(self,addedvert):
        if type(addedvert) is list:
            for curvert in addedvert:
                self.add_vertex(curvert)
        else:
            self.myvertices.append(addedvert)
            self.nbvertices+=1

    def count(self):
        self.nbvertices=len(self.myvertices)

    def close_force(self):
        if self.myvertices[-1] is not self.myvertices[0] and (self.myvertices[-1].x!=self.myvertices[0].x and self.myvertices[-1].y!=self.myvertices[0].y and self.myvertices[-1].z!=self.myvertices[0].z):
            self.add_vertex(self.myvertices[0])
            self.closed=True

    def nblines(self):
        return self.nbvertices+5

    def find_minmax(self):
        self.minx=min(vert.x for vert in self.myvertices)
        self.miny=min(vert.y for vert in self.myvertices)
        self.maxx=max(vert.x for vert in self.myvertices)
        self.maxy=max(vert.y for vert in self.myvertices)

    def plot(self):

        if self.myprop.used:
            
            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)        
            glLineWidth(float(self.myprop.width))
            #glPointSize(float(self.myprop.width))

            glBegin(GL_LINE_STRIP)
            #!J'aimerais bien changer la largeur du trait mais je n'y parviens pas...
            #!call glGet(GL_ALIASED_LINE_WIDTH_RANGE, max_width)
            rgb=getRGBfromI(self.myprop.color)
            
            if self.myprop.color==65536:
                a=1
            
            glColor3ub(int(rgb[0]),int(rgb[1]),int(rgb[2]))
            for curvertex in self.myvertices:
                glVertex2d(curvertex.x, curvertex.y)

            if self.myprop.closed and (self.myvertices[0].x != self.myvertices[-1].x or self.myvertices[0].y != self.myvertices[-1].y):
                curvertex = self.myvertices[0]
                glVertex2d(curvertex.x, curvertex.y)

            glEnd()

    def add2tree(self,tree:TreeListCtrl,root):
        self.mytree=tree
        self.myitem=tree.AppendItem(root, self.myname,data=self)
        if self.myprop.used:
            tree.CheckItem(self.myitem)

    def unuse(self):
        self.myprop.used=False
        self.mytree.UncheckItem(self.myitem)

    def use(self):
        self.myprop.used=True
        self.mytree.CheckItem(self.myitem)

    def fillgrid(self,gridto:CpGrid):
        curv:wolfvertex

        gridto.SetColLabelValue(0,'X')
        gridto.SetColLabelValue(1,'Y')
        gridto.SetColLabelValue(2,'Z')
        gridto.SetColLabelValue(3,'value')
        
        nb=gridto.GetNumberRows()
        if len(self.myvertices)-nb>0:
            gridto.AppendRows(len(self.myvertices)-nb)
        k=0
        for curv in self.myvertices:
           gridto.SetCellValue(k,0,str(curv.x))
           gridto.SetCellValue(k,1,str(curv.y))
           gridto.SetCellValue(k,2,str(curv.z))
           k+=1

    def updatefromgrid(self,gridfrom:CpGrid):
        curv:wolfvertex
       
        nbl=gridfrom.GetNumberRows()       
        k=0
        while k<nbl:
            x=gridfrom.GetCellValue(k,0)
            y=gridfrom.GetCellValue(k,1)
            z=gridfrom.GetCellValue(k,2)
            if z=='':
                z=0.
            if x!='':
                if k<self.nbvertices:
                    self.myvertices[k].x=float(x)
                    self.myvertices[k].y=float(y)
                    self.myvertices[k].z=float(z)
                else:
                    newvert=wolfvertex(float(x),float(y),float(z))
                    self.add_vertex(newvert)
                k+=1
            else:
                break

        while k<self.nbvertices:
            self.myvertices.pop(k)
            self.nbvertices-=1

class zone:

    myname:str
    nbvectors:int
    myvectors:list
    minx:float
    miny:float
    maxx:float
    maxy:float
    selected_vectors:list
    mytree:TreeListCtrl
    myitem:TreeItemId
    active_vector:vector

    def __init__(self,lines=[],name='') -> None:
        
        self.idgllist = -99999
        self.active_vector=None

        if len(lines)>0:
            self.myname=lines[0]
            self.nbvectors=int(lines[1])
            self.myvectors=[]
            curstart=2
            for i in range(self.nbvectors):
                curvec=vector(lines[curstart:],parentzone=self)
                curstart+=curvec.nblines()
                self.myvectors.append(curvec)

        if name!='':
            self.myname=name
            self.nbvectors=0
            self.myvectors=[]
        
        self.selected_vectors=[]
        self.multils = None

        pass

    def save(self,f):
        f.write(self.myname+'\n')
        f.write(str(self.nbvectors)+'\n')
        for curvect in self.myvectors:
            curvect.save(f)

    def add_vector(self,addedvect):
        self.myvectors.append(addedvect)
        self.nbvectors+=1

    def count(self):
        self.nbvectors=len(self.myvectors)

    def nblines(self):
        nb=2
        for curvec in self.myvectors:
            nb+=curvec.nblines()
        
        return nb

    def find_minmax(self,update=False):
        if update:
            for vect in self.myvectors:
                vect.find_minmax()

        self.minx=min(vect.minx for vect in self.myvectors)
        self.miny=min(vect.miny for vect in self.myvectors)
        self.maxx=max(vect.maxx for vect in self.myvectors)
        self.maxy=max(vect.maxy for vect in self.myvectors)

    def plot(self,prep=False):
        
        if prep:
            if self.idgllist==-99999:
                self.idgllist = glGenLists(1)
            
            glNewList(self.idgllist,GL_COMPILE)
            for curvect in self.myvectors:
                curvect.plot()        
            glEndList()
        else:
            if self.idgllist!=-99999:
                glCallList(self.idgllist)
            else:
                for curvect in self.myvectors:
                    curvect.plot()

    def select_vectors_from_point(self,x:float,y:float):
        curvect:vector
        self.selected_vectors.clear()
        for curvect in self.myvectors:
            if curvect.isinside(x,y):
                self.selected_vectors.append(curvect)

    def add2tree(self,tree:TreeListCtrl,root):
        self.mytree=tree
        self.myitem=tree.AppendItem(root, self.myname,data=self)
        tree.CheckItem(self.myitem)
        for curvect in self.myvectors:
            curvect.add2tree(tree,self.myitem)

    def unuse(self):
        for curvect in self.myvectors:
            curvect.unuse()
        self.mytree.UncheckItem(self.myitem)

    def use(self):
        for curvect in self.myvectors:
            curvect.use()
        self.mytree.CheckItem(self.myitem)

    def asshapely_ls(self):
        mylines=[]
        curvect:vector
        for curvect in self.myvectors:
            mylines.append(curvect.asshapely_ls())
        return MultiLineString(mylines)

    def prepare_shapely(self):
        self.multils = self.asshapely_ls()

class Zones(wx.Frame):

    idx:str
    tx:float
    ty:float
    minx:float
    miny:float
    maxx:float
    maxy:float

    nbzones:int

    myzones:list
    treelist:TreeListCtrl
    xls:CpGrid

    def __init__(self,myfile='',ox:float=0.,oy:float=0.,tx:float=0.,ty:float=0.,parent=None):
        self.loaded=True
        self.active_vector = None
        self.active_zone = None
        self.last_active = None
        
        if myfile!='':
            f = open(myfile, 'r')
            lines = f.read().splitlines()
            f.close()

            try:
                tx,ty=lines[0].split()
            except:
                tx,ty=lines[0].split(',')
            self.tx=float(tx)
            self.ty=float(ty)
            self.nbzones=int(lines[1])
            self.myzones=[]

            curstart=2
            for i in range(self.nbzones):
                curzone=zone(lines[curstart:])
                self.myzones.append(curzone)
                curstart+=curzone.nblines()

            self.find_minmax(True)
        else:
            self.minx=ox
            self.miny=oy
            self.tx=tx
            self.ty=ty
            self.myzones=[]
            self.nbzones=0
            
        self.filename=myfile

        try:
            super(Zones, self).__init__(parent, size=(300, 400))
            self.Bind(wx.EVT_CLOSE,self.OnClose)
        except:
            pass
        
        self.parent = None

    def prep_listogl(self):
        for curzone in self.myzones:
            curzone.plot(True)
        
    def check_plot(self):
        self.plotted = True

    def uncheck_plot(self,unload=True):
        self.plotted = False
    
    def saveas(self,filename=''):
        if filename!='':
            self.filename=filename
        
        with open(self.filename, 'w') as f:
            f.write(f'{self.tx} {self.ty}'+'\n')
            f.write(str(self.nbzones)+'\n')
            for curzone in self.myzones:
                curzone.save(f)

    def OnClose(self,e):
        self.Hide()
        pass

    def add_zone(self,addedzone):
        self.myzones.append(addedzone)
        self.nbzones+=1

    def find_minmax(self,update=False):
        
        if update:
            for zone in self.myzones:
                zone.find_minmax(update)

        if len(self.myzones)>0:
            self.minx=min(zone.minx for zone in self.myzones)
            self.miny=min(zone.miny for zone in self.myzones)
            self.maxx=max(zone.maxx for zone in self.myzones)
            self.maxy=max(zone.maxy for zone in self.myzones)
        else:
            self.minx=0.
            self.miny=0.
            self.maxx=1.
            self.maxy=1.
            
    def plot(self):
        for curzone in self.myzones:
            curzone.plot()

    def select_vectors_from_point(self,x:float,y:float):
        curzone:zone
        for curzone in self.myzones:
            curzone.select_vectors_from_point(x,y)

    def showstructure(self,parent,parentGUI=None):

        self.parent = parent
        self.parentGUI = parent
        if parentGUI is not None:
            self.parentGUI = parentGUI

        box = BoxSizer(orient=wx.HORIZONTAL)
        
        boxleft = BoxSizer(orient=wx.VERTICAL)
        boxright = BoxSizer(orient=wx.VERTICAL)

        boxzone = BoxSizer(orient=wx.VERTICAL)
        boxvector = BoxSizer(orient=wx.VERTICAL)
        
        self.xls=CpGrid(self,-1,wx.WANTS_CHARS)
        self.xls.CreateGrid(10,4)

        self.addrows = wx.Button(self,label=_('Add rows'))
        self.addrows.Bind(wx.EVT_BUTTON,self.Onaddrows)

        self.updatevertices = wx.Button(self,label=_('Update coordinates'))
        self.updatevertices.Bind(wx.EVT_BUTTON,self.Onupdatevertices)

        self.capturevertices = wx.Button(self,label=_('Capture clicks'))
        self.capturevertices.Bind(wx.EVT_BUTTON,self.Oncapture)

        boxright.Add(self.xls,1,wx.EXPAND)
        boxright.Add(self.addrows,0,wx.EXPAND)
        boxright.Add(self.updatevertices,0,wx.EXPAND)
        boxright.Add(self.capturevertices,0,wx.EXPAND)

        self.treelist = TreeListCtrl(self,style=TL_CHECKBOX)
        self.treelist.AppendColumn('Zones')
        self.treelist.Bind(EVT_TREELIST_ITEM_CHECKED, self.OnCheckItem)
        self.treelist.Bind(EVT_TREELIST_ITEM_ACTIVATED, self.OnActivateItem)

        self.treelist.Bind(wx.EVT_CHAR,self.OnEditLabel)

        self.addzone = wx.Button(self,label=_('Add zone'))
        self.deletezone = wx.Button(self,label=_('Delete zone'))
        self.addvector = wx.Button(self,label=_('Add vector'))
        self.deletevector = wx.Button(self,label=_('Delete vector'))

        self.addzone.Bind(wx.EVT_BUTTON,self.OnClickadd_zone)
        self.addvector.Bind(wx.EVT_BUTTON,self.OnClickadd_vector)
        self.deletezone.Bind(wx.EVT_BUTTON,self.OnClickdelete_zone)
        self.deletevector.Bind(wx.EVT_BUTTON,self.OnClickdelete_vector)

        boxzone.Add(self.addzone,1,wx.EXPAND)
        boxzone.Add(self.deletezone,1,wx.EXPAND)

        boxvector.Add(self.addvector,1,wx.EXPAND)
        boxvector.Add(self.deletevector,1,wx.EXPAND)

        boxleft.Add(self.treelist,1,wx.EXPAND)
        boxleft.Add(boxzone,0,wx.EXPAND)
        boxleft.Add(boxvector,0,wx.EXPAND)

        box.Add(boxleft,1,wx.EXPAND)
        box.Add(boxright,1,wx.EXPAND)

        self.fill_structure()

        self.treelist.SetSize(200,500)

        self.SetSizer(box)
        self.Show()
    
    def fill_structure(self):
        self.treelist.DeleteAllItems()

        root = self.treelist.GetRootItem()
        mynode=self.treelist.AppendItem(root, 'All zones',data=self)
        self.treelist.CheckItem(mynode)
        
        curzone:zone
        for curzone in self.myzones:
            curzone.add2tree(self.treelist,mynode)

    def Oncapture(self,event):
        self.parentGUI.action='capture vertices'

    def Onupdatevertices(self,event):
        self.active_vector.updatefromgrid(self.xls)
        self.find_minmax(True)

    def Onaddrows(self,event):
        nbrows=None
        dlg=wx.TextEntryDialog(None,_('How many rows?'),value='1')
        while nbrows is None:
            rc = dlg.ShowModal()
            if rc == wx.ID_OK:
                nbrows = int(dlg.GetValue())
                self.xls.AppendRows(nbrows)
            else:
                return
        

    def OnClickadd_zone(self,event):
        curname=None
        dlg=wx.TextEntryDialog(None,_('Choose a name for the new zone'),value='New_Zone')
        while curname is None:
            rc = dlg.ShowModal()
            if rc == wx.ID_OK:
                curname = str(dlg.GetValue())
                newzone = zone(name=curname)
                self.add_zone(newzone)
                self.fill_structure()
                self.active_zone = newzone
            else:
                return
    
    def OnClickadd_vector(self,event):
        curname=None
        dlg=wx.TextEntryDialog(None,_('Choose a name for the new vector'),value='New_Vector')
        while curname is None:
            rc = dlg.ShowModal()
            if rc == wx.ID_OK:
                curname = str(dlg.GetValue())
                newvec = vector(name=curname)
                self.active_zone.add_vector(newvec)
                self.fill_structure()
                self.active_vector = newvec
            else:
                return

    def OnClickdelete_zone(self,event):
        curname=self.active_zone.myname
        r = wx.MessageDialog(
            None,
            _('The zone ' +curname+' will be deleted. Continue?'),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        ).ShowModal()

        if r != wx.ID_YES:
            return

        self.myzones.pop(self.myzones.index(self.active_zone))
        self.fill_structure()
        self.find_minmax(True)

    def OnClickdelete_vector(self,event):
        curname=self.active_vector.myname
        r = wx.MessageDialog(
            None,
            _('The vector ' +curname+' will be deleted. Continue?'),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        ).ShowModal()

        if r != wx.ID_YES:
            return

        actzone =self.active_zone
        actzone.myvectors.pop(actzone.myvectors.index(self.active_vector))
        self.fill_structure()
        self.find_minmax(True)

    def unuse(self):
        for curzone in self.myzones:
            curzone.unuse()

    def use(self):
        for curzone in self.myzones:
            curzone.use()

    def OnCheckItem(self,event):

        myitem=event.GetItem()
        check = self.treelist.GetCheckedState(myitem)
        myitemdata=self.treelist.GetItemData(myitem)
        if check:
            myitemdata.use()
        else:
            myitemdata.unuse()

    def OnActivateItem(self,event):
        myitem=event.GetItem()
        myitemdata=self.treelist.GetItemData(myitem)
        
        if type(myitemdata) is vector:
            self.xls.ClearGrid()
            myitemdata.fillgrid(self.xls)
            myitemdata.myprop.show()
            
            self.active_vector = myitemdata
            if myitemdata.parentzone is not None:
                self.active_zone = myitemdata.parentzone
                myitemdata.parentzone.active_vector = myitemdata
            
        elif type(myitemdata) is zone:
            self.active_zone = myitemdata
            if myitemdata.active_vector is not None:
                self.active_vector = myitemdata.active_vector
            elif myitemdata.nbvectors>0:
                self.active_vector = myitemdata.myvectors[0]

        if not self.parent is None:
            self.parent.Active_vector(self.active_vector)

        self.last_active = myitemdata

    def OnEditLabel(self,event):
        key=event.GetKeyCode()

        if key==wx.WXK_F2:
            if self.last_active is not None:        
                curname=None
                dlg=wx.TextEntryDialog(None,_('Choose a new name'),value=self.last_active.myname)
                while curname is None:
                    rc = dlg.ShowModal()
                    if rc == wx.ID_OK:
                        curname = str(dlg.GetValue())
                        self.last_active.myname = curname
                        self.fill_structure()
                    else:
                        return
            
class Grid(Zones):

    def __init__(self, size:float=1000.,ox:float=0.,oy:float=0.,ex:float=1000.,ey:float=1000., parent=None):
        super().__init__(ox=ox, oy=oy, parent=parent)

        mygrid=zone(name='mygrid')
        self.add_zone(mygrid)
        mygridx=vector(name='mygridx')
        mygridy=vector(name='mygridy')
        contour=vector(name='contour')
        mygrid.add_vector(mygridx)
        mygrid.add_vector(mygridy)
        mygrid.add_vector(contour)
        self.creategrid(size,ox,oy,ex,ey)

    def creategrid(self,size:float=100.,ox:float=0.,oy:float=0.,ex:float=1000.,ey:float=1000.):

        mygridx=self.myzones[0].myvectors[0]
        mygridy=self.myzones[0].myvectors[1]
        contour=self.myzones[0].myvectors[2]
        mygridx.reset()
        mygridy.reset()
        contour.reset()

        locox=int(ox/size)*size
        locoy=int(oy/size)*size
        locex=(int(ex/size))*size
        locey=(int(ey/size))*size

        nbx=int((locex-locox)/size)
        nby=int((locey-locoy)/size)

        dx=locex-locox
        dy=locey-locoy

        #grillage vertical        
        xloc=locox
        yloc=locoy
        for i in range(nbx):
            newvert=wolfvertex(xloc,yloc)
            mygridx.add_vertex(newvert)
            
            yloc+=dy
            newvert=wolfvertex(xloc,yloc)
            mygridx.add_vertex(newvert)
            
            xloc+=size
            dy=-dy

        #grillage horizontal        
        xloc=locox
        yloc=locoy
        for i in range(nby):
            newvert=wolfvertex(xloc,yloc)
            mygridy.add_vertex(newvert)
            
            xloc+=dx
            newvert=wolfvertex(xloc,yloc)
            mygridy.add_vertex(newvert)
            
            yloc+=size
            dx=-dx

        newvert=wolfvertex(locox,locoy)
        contour.add_vertex(newvert)
        newvert=wolfvertex(locex,locoy)
        contour.add_vertex(newvert)
        newvert=wolfvertex(locex,locey)
        contour.add_vertex(newvert)
        newvert=wolfvertex(locox,locey)
        contour.add_vertex(newvert)

        self.find_minmax(True)