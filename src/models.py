import logging
from struct import unpack_from, calcsize
import numpy as np

from .config import *
from .exceptions import AssigningException, ParsingException

class Bstring():
    def __init__(self,bytes,offset=0):
        self.string=None
        self.content=bytes
        self.length=int(unpack_from('i',bytes,offset)[0])
        self.offset=offset+4
        self._unpack()
        self.byte_length=calcsize('i')+self.length*calcsize('s')
    
    def _unpack(self):
        fmt=str(self.length)+'s'
        self.string=str(unpack_from(fmt,self.content,self.offset)[0])[2:-1]

class Bdict():
    def __init__(self,bytes,offset=0):
        self.dic={}
        self.content=bytes
        self.length=int(unpack_from('i', bytes,offset)[0])
        self.offset=offset+4
        self._unpack()
        
    def _unpack(self):
        for i in range(self.length):
            bs1=Bstring(self.content,self.offset)
            key=bs1.string
            self.offset+=bs1.byte_length
            bs2=Bstring(self.content,self.offset)
            value=bs2.string
            self.offset+=bs2.byte_length
            self.dic[key]=value


class Chunk():
    
    def __init__(self,id,content=None,children=None):
        self.id = id
        self.name = str(id)[2:-1]
        self.content = content or b''
        self.children = children or []
        
        if id == b'MAIN':
            if len(self.content): raise ParsingException('Empty main chunk')
        elif id == b'PACK':
            logging.error('Detect Pack chunk which is not supportted in current version')
        elif id == b'SIZE':
            self.size=unpack_from(SIZE_FMT,self.content,0)
        elif id == b'XYZI':
            n = int(unpack_from(XYZI_FMT_1,self.content,0)[0])
            self.voxels = []
            for i in range(n):
                self.voxels.append(unpack_from(XYZI_FMT_2, content, 4+4*i))
        elif id == b'RGBA':
            self.palette=[]
            for i in range(255):
                self.palette.append(unpack_from(RGBA_FMT, content, 4*i))
        elif id == b'MATL':
            _id = unpack_from('i', content)
            _dict = Bdict(content,4).dic
            self.material=_dict
        elif id == b'nTRN':
            pass
        elif id == b'rOBJ':
            self.robj = Bdict(content).dic
        elif id == b'nGRP':
            pass
        elif id == b'nSHP':
            pass
        elif id == b'LAYR':
            pass
        elif id == b'NOTE':
            pass
        elif id == b'IMAP':
            pass


        else:
            raise ParsingException('Unknown chunk type: %s'%self.id)

class Vox():

    def __init__(self,chunks):
        self.chunks=chunks
        self._palette = None
        self.size = None
        self.voxels = None
        self.materials = []
        self.robjs=[]
        self._parse_chunk()

        pass

    def _parse_chunk(self):
        for chunk in self.chunks:
            if chunk.id==b'RGBA':
                self._palette = chunk.palette
            if chunk.id==b'SIZE':
                self.size = chunk.size
            if chunk.id==b'XYZI':
                self.voxels = chunk.voxels
            if chunk.id==b'MATL':
                self.materials.append(chunk.material)
            if chunk.id==b'rOBJ':
                self.robjs.append(chunk.robj)
        pass

    def to_list(self):
        l,w,h=self.size
        arr=np.zeros((l,w,h,4))
        color=np.array(self.palette)
        for i in self.voxels:
            x=i[0]
            y=i[1]
            z=i[2]
            c=i[3]
            arr[x,y,z]=color[c-1]/255
        return arr
    

    @property
    def palette(self):
        return self._palette

    @palette.setter
    def palette(self, val:list):
        if type(val)==list and np.array(val).shape==(255,4):
            self._palette = val
            self.default_palette = False
        else:
            raise AssigningException('The value seems not a palette.')

    pass