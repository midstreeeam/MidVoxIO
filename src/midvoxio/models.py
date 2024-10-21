from ast import Mod
from collections import namedtuple
from pprint import pformat
from struct import unpack_from, calcsize, pack

import numpy as np
from PIL import Image

from .exceptions import DumpingException

UNSET = np.array([0,0,0,0])

ModelAttr=namedtuple('ModelAttr','attr_dic id')
default_palette=[
    0x00000000, 0xffffffff, 0xffccffff, 0xff99ffff, 0xff66ffff, 0xff33ffff, 0xff00ffff, 0xffffccff, 0xffccccff, 0xff99ccff, 0xff66ccff, 0xff33ccff, 0xff00ccff, 0xffff99ff, 0xffcc99ff, 0xff9999ff,
    0xff6699ff, 0xff3399ff, 0xff0099ff, 0xffff66ff, 0xffcc66ff, 0xff9966ff, 0xff6666ff, 0xff3366ff, 0xff0066ff, 0xffff33ff, 0xffcc33ff, 0xff9933ff, 0xff6633ff, 0xff3333ff, 0xff0033ff, 0xffff00ff,
    0xffcc00ff, 0xff9900ff, 0xff6600ff, 0xff3300ff, 0xff0000ff, 0xffffffcc, 0xffccffcc, 0xff99ffcc, 0xff66ffcc, 0xff33ffcc, 0xff00ffcc, 0xffffcccc, 0xffcccccc, 0xff99cccc, 0xff66cccc, 0xff33cccc,
    0xff00cccc, 0xffff99cc, 0xffcc99cc, 0xff9999cc, 0xff6699cc, 0xff3399cc, 0xff0099cc, 0xffff66cc, 0xffcc66cc, 0xff9966cc, 0xff6666cc, 0xff3366cc, 0xff0066cc, 0xffff33cc, 0xffcc33cc, 0xff9933cc,
    0xff6633cc, 0xff3333cc, 0xff0033cc, 0xffff00cc, 0xffcc00cc, 0xff9900cc, 0xff6600cc, 0xff3300cc, 0xff0000cc, 0xffffff99, 0xffccff99, 0xff99ff99, 0xff66ff99, 0xff33ff99, 0xff00ff99, 0xffffcc99,
    0xffcccc99, 0xff99cc99, 0xff66cc99, 0xff33cc99, 0xff00cc99, 0xffff9999, 0xffcc9999, 0xff999999, 0xff669999, 0xff339999, 0xff009999, 0xffff6699, 0xffcc6699, 0xff996699, 0xff666699, 0xff336699,
    0xff006699, 0xffff3399, 0xffcc3399, 0xff993399, 0xff663399, 0xff333399, 0xff003399, 0xffff0099, 0xffcc0099, 0xff990099, 0xff660099, 0xff330099, 0xff000099, 0xffffff66, 0xffccff66, 0xff99ff66,
    0xff66ff66, 0xff33ff66, 0xff00ff66, 0xffffcc66, 0xffcccc66, 0xff99cc66, 0xff66cc66, 0xff33cc66, 0xff00cc66, 0xffff9966, 0xffcc9966, 0xff999966, 0xff669966, 0xff339966, 0xff009966, 0xffff6666,
    0xffcc6666, 0xff996666, 0xff666666, 0xff336666, 0xff006666, 0xffff3366, 0xffcc3366, 0xff993366, 0xff663366, 0xff333366, 0xff003366, 0xffff0066, 0xffcc0066, 0xff990066, 0xff660066, 0xff330066,
    0xff000066, 0xffffff33, 0xffccff33, 0xff99ff33, 0xff66ff33, 0xff33ff33, 0xff00ff33, 0xffffcc33, 0xffcccc33, 0xff99cc33, 0xff66cc33, 0xff33cc33, 0xff00cc33, 0xffff9933, 0xffcc9933, 0xff999933,
    0xff669933, 0xff339933, 0xff009933, 0xffff6633, 0xffcc6633, 0xff996633, 0xff666633, 0xff336633, 0xff006633, 0xffff3333, 0xffcc3333, 0xff993333, 0xff663333, 0xff333333, 0xff003333, 0xffff0033,
    0xffcc0033, 0xff990033, 0xff660033, 0xff330033, 0xff000033, 0xffffff00, 0xffccff00, 0xff99ff00, 0xff66ff00, 0xff33ff00, 0xff00ff00, 0xffffcc00, 0xffcccc00, 0xff99cc00, 0xff66cc00, 0xff33cc00,
    0xff00cc00, 0xffff9900, 0xffcc9900, 0xff999900, 0xff669900, 0xff339900, 0xff009900, 0xffff6600, 0xffcc6600, 0xff996600, 0xff666600, 0xff336600, 0xff006600, 0xffff3300, 0xffcc3300, 0xff993300,
    0xff663300, 0xff333300, 0xff003300, 0xffff0000, 0xffcc0000, 0xff990000, 0xff660000, 0xff330000, 0xff0000ee, 0xff0000dd, 0xff0000bb, 0xff0000aa, 0xff000088, 0xff000077, 0xff000055, 0xff000044,
    0xff000022, 0xff000011, 0xff00ee00, 0xff00dd00, 0xff00bb00, 0xff00aa00, 0xff008800, 0xff007700, 0xff005500, 0xff004400, 0xff002200, 0xff001100, 0xffee0000, 0xffdd0000, 0xffbb0000, 0xffaa0000,
    0xff880000, 0xff770000, 0xff550000, 0xff440000, 0xff220000, 0xff110000, 0xffeeeeee, 0xffdddddd, 0xffbbbbbb, 0xffaaaaaa, 0xff888888, 0xff777777, 0xff555555, 0xff444444, 0xff222222, 0xff111111
]


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
    def __init__(self, xyzi_arr):
        self.xyzi=xyzi_arr
    
    def to_b(self):
        length=self.xyzi.size
        bstr=pack("i", length)
        x, y, z = np.mgrid[slice(self.xyzi.shape[0]), slice(self.xyzi.shape[1]), slice(self.xyzi.shape[2])]
        arr = np.c_[x.flatten(), y.flatten(), z.flatten(), self.xyzi.flatten()]
        bstr += arr.astype(np.uint8).tobytes()
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
        if not palette_arr is None:
            self.palette_arr=palette_arr
        else:
            self.palette_arr=self._get_palette_arr_from_img(img_path)
        pass

    def _get_palette_arr_from_img(self,img_path):
        img=Image.open(img_path)
        color=np.array(img)
        color = color[0]
        
        # Add missing alpha to PNG data with no alpha for consistent matching
        if color.shape[-1] == 3:
            color = np.append( color, np.full((256, 1), 255), axis=1 )

        return color
    
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
