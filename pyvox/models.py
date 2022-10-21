from ast import Mod
from collections import namedtuple
from pprint import pformat
from struct import unpack_from, calcsize, pack

import numpy as np
from PIL import Image

from .exceptions import DumpingException

ModelAttr=namedtuple('ModelAttr','attr_dic id')

class XYZI():
    '''
    Chunk id 'XYZI' : model voxels, paired with the SIZE chunk
    -------------------------------------------------------------------------------
    Bytes  | Type       | Value
    -------------------------------------------------------------------------------
    4        | int        | numVoxels (N)
    4 x N    | int        | (x, y, z, colorIndex) : 1 byte for each component
    -------------------------------------------------------------------------------
    '''
    id=b'XYZI'
    def __init__(self,xyzi_arr):
        self.xyzi=xyzi_arr
        pass
    
    def to_b(self):
        length=len(self.xyzi)
        bstr=pack('i',length)
        for i in self.xyzi:
            bstr+=pack('4B',i[0],i[1],i[2],i[3])
        return bstr

class SIZE():
    '''
     Chunk id 'SIZE' : model size
    -------------------------------------------------------------------------------
    Bytes  | Type       | Value
    -------------------------------------------------------------------------------
    4        | int        | size x
    4        | int        | size y
    4        | int        | size z : gravity direction
    -------------------------------------------------------------------------------
    '''
    id=b'SIZE'
    def __init__(self,shape):
        self.size=shape[:-1]
    def to_b(self):
        return pack('3i',self.size[0],self.size[1],self.size[2])

class RGBA():
    '''
    Chunk id 'RGBA' : palette
    -------------------------------------------------------------------------------
    Bytes  | Type       | Value
    -------------------------------------------------------------------------------
    4 x 256  | int        | (R, G, B, A) : 1 byte for each component
                        | * <NOTICE>
                        | * color [0-254] are mapped to palette index [1-255], e.g : 
                        | 
                        | for ( int i = 0; i <= 254; i++ ) {
                        |     palette[i + 1] = ReadRGBA(); 
                        | }
    -------------------------------------------------------------------------------
    '''
    id=b'RGBA'
    def __init__(self,img_path=None,palette_arr=None):
        if palette_arr:
            self.palette_arr=palette_arr
        else:
            self.palette_arr=self._get_palette_arr_from_img(img_path)
        pass

    def _get_palette_arr_from_img(self,img_path):
        img=Image.open(img_path)
        color=np.array(img)
        return color[0]
    
    def to_b(self):
        bstr=b''
        for i in self.palette_arr:
            bstr+=pack('4B',i[0],i[1],i[2],i[3])
        return bstr


class nTRN():
    '''
    Transform Node Chunk : "nTRN"

    int32	: node id
    DICT	: node attributes
        (_name : string)
        (_hidden : 0/1)
    int32 	: child node id
    int32 	: reserved id (must be -1)
    int32	: layer id
    int32	: num of frames (must be greater than 0)

    // for each frame
    {
    DICT	: frame attributes
        (_r : int8)    ROTATION, see (c)
        (_t : int32x3) translation
        (_f : int32)   frame index, start from 0 
    }xN
    '''
    id=b'nTRN'
    def __init__(self,node_id,node_attributes,
    child_node_id,reversed_id,layer_id,frames):
        self.node_id=node_id
        self.node_attributes=node_attributes
        self.child_node_id=child_node_id
        self.reversed_id=reversed_id
        self.layer_id=layer_id
        self.frames=frames
    
    def to_b(self):
        byts=pack('i',self.node_id)
        byts+=Bdict(py_dict=self.node_attributes).bytes
        byts+=pack('4i',self.child_node_id,
                        self.reversed_id,
                        self.layer_id,
                        len(self.frames))
        for frame in self.frames:
            byts+=Bdict(py_dict=frame).bytes
        return byts

    def __repr__(self):
        ret=f'''
====nTRN====
node_id:{self.node_id}
frames:{format(self.frames)}
child_node_id:{self.child_node_id}
layer_id:{self.layer_id}
'''
        return ret

class NGRP():
    '''
    Group Node Chunk : "nGRP" 
    int32	: node id
    DICT	: node attributes
    int32 	: num of children nodes

    // for each child
    {
    int32	: child node id
    }xN
    '''
    def __init__(self,node_id,dic,num,child_lst):
        self.node_id=node_id
        self.node_attr=dic
        self.children_num=num
        self.children_ids=child_lst
        pass
    def __repr__(self):
        ret=f'''
====nGPR====
node_id:{self.node_id}
children_ids:{self.children_ids}
'''
        return ret


class nSHP():
    '''
    Shape Node Chunk : "nSHP" 

    int32	: node id
    DICT	: node attributes
    int32 	: num of models (must be greater than 0)

    // for each model
    {
    int32	: model id
    DICT	: model attributes : reserved
        (_f : int32)   frame index, start from 0
    }xN
    '''
    def __init__(self,node_id,models,node_attr={}):
        self.node_id=node_id
        self.node_attr=node_attr
        self.models=models
    def __repr__(self):
        ret=f'''
====nSHP====
node_id:{self.node_id}
models:{pformat([i for i in self.models])}
'''
        return ret
    def to_b(self):
        byts=pack('i',self.node_id)
        byts+=Bdict(py_dict=self.node_attr).bytes
        byts+=pack('i',len(self.models))
        for model in self.models:
            byts+=pack('i',model.id)
            byts+=Bdict(py_dict=model.attr_dic)
        return byts

class Material():
    '''
    Material Chunk : "MATL"
        int32	: material id
        DICT	: material properties
            (_type : str) _diffuse, _metal, _glass, _emit
            (_weight : float) range 0 ~ 1
            (_rough : float)
            (_spec : float)
            (_ior : float)
            (_att : float)
            (_flux : float)
            (_plastic)
    '''
    def __init__(self,id,dic):
        self.id=id
        self.dic=dic
        pass

    def __str__(self):
        return str({'id':self.id,
                'properties':self.dic
                })

class Camera():
    '''
    Render Camera Chunk : "rCAM"
        int32	: camera id
        DICT	: camera attribute
            (_mode : string)
            (_focus : vec(3))
            (_angle : vec(3))
            (_radius : int)
            (_frustum : float)
            (_fov : int)
    '''
    def __init__(self,id,dic):
        self.id=id
        self.dic=dic
        pass

    def __str__(self):
        return str({'id':self.id,
                'attributes':self.dic
                })

class Layer():
    '''
    Layer Chunk : "LAYR"
        int32	: layer id
        DICT	: layer attribute
            (_name : string)
            (_hidden : 0/1)
        int32	: reserved id, must be -1
    '''
    def __init__(self,id,dic,rev_id):
        self.id=id
        self.dic=dic
        self.rev_id=rev_id

class Note():
    '''
    Palette Note Chunk : "NOTE"
        int32	: num of color names

        // for each name
        {
        STRING	: color name
        }xN
    '''
    def __init__(self,num,color_names):
        self.num=num
        self.color_names=color_names

class ROBJ():
    '''
    Render Objects Chunk : "rOBJ"
        DICT	: rendering attributes
    '''
    def __init__(self,dic):
        self.dic=dic
    
    def __str__(self):
        return str(self.dic)

class Bstring():
    '''
    STRING type
        int32   : buffer size (in bytes)
        int8xN	: buffer (without the ending "\0")
    '''
    def __init__(self,bytes=None,offset=0,py_str=None):
        if bytes:
            self.string=None
            self.bytes=bytes
            self.length=int(unpack_from('i',bytes,offset)[0])
            self.offset=offset+4
            self._unpack()
            self.byte_length=calcsize('i')+self.length*calcsize('s')
        elif isinstance(py_str,str):
            self.string=py_str
            self.bytes=self.to_b()
        else:
            raise Exception("no bytes nor str")
    
    def _unpack(self):
        fmt=str(self.length)+'s'
        self.string=str(unpack_from(fmt,self.bytes,self.offset)[0])[2:-1]

    def to_b(self):
        byts=pack('i',len(self.string))
        fmt=str(len(self.string))+'s'
        byts+=pack(fmt,self.string.encode('utf8'))
        return byts

class Bdict():
    '''
    DICT type
        int32	: num of key-value pairs
        // for each key-value pair
        {
        STRING	: key
        STRING	: value
        }xN
    '''
    def __init__(self,bytes=None,offset=0,py_dict=None):
        if bytes:
            self.dic={}
            self.bytes=bytes
            self.length=int(unpack_from('i', bytes,offset)[0])
            self.offset=offset+4
            self._unpack()
        elif isinstance(py_dict,dict):
            self.dic=py_dict
            self.bytes=self.to_b()
        else:
            raise Exception("non bytes nor dict")
        
    def _unpack(self):
        for _ in range(self.length):
            bs1=Bstring(self.bytes,self.offset)
            key=bs1.string
            self.offset+=bs1.byte_length
            bs2=Bstring(self.bytes,self.offset)
            value=bs2.string
            self.offset+=bs2.byte_length
            self.dic[key]=value
    
    def to_b(self):
        byts=pack('i',len(self.dic))
        for key,value in self.dic.items():
            byts+=Bstring(py_str=key).bytes
            byts+=Bstring(py_str=str(value)).bytes
        return byts
