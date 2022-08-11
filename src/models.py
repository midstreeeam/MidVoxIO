import logging
from struct import unpack_from, calcsize
import numpy as np

from .config import *
from .exceptions import AssigningException, ParsingException


class Chunk():
    
    def __init__(self,id,content=None,children=None):
        self.id = id
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
            _id, _type, _weight, _rough, _spec, _ior, _att, _flux = unpack_from('is6f', content)
            # print(_id, _type, _weight, _rough, _spec, _ior, _att, _flux)
        elif id == b'nTRN':
            pass
        elif id == b'rOBJ':
            pass
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
        self._palette = None
        self.size = None
        self.voxels = None
        for chunk in chunks:
            if chunk.id==b'RGBA':
                self._palette = chunk.palette
            if chunk.id==b'SIZE':
                self.size = chunk.size
            if chunk.id==b'XYZI':
                self.voxels = chunk.voxels
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