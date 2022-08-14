from struct import unpack_from, calcsize

class NGPR():
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
    '''
    DICT type
        int32	: num of key-value pairs
        // for each key-value pair
        {
        STRING	: key
        STRING	: value
        }xN
    '''
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
