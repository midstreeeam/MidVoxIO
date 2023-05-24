from struct import pack

import numpy as np

from .models import SIZE, XYZI, RGBA

class BaseWriter():
    def __init__(self,palette_path=None,palette_arr=None) -> None:
        self.chunks=[]
        if palette_path:
            self.rgba=RGBA(img_path=palette_path)
        elif palette_arr:
            self.rgba=RGBA(palette_arr=palette_arr)
        else:
            raise Exception("palette missing")
    
    def _get_color_index(self,color):
        com=lambda x,y:x[0]==y[0] and x[1]==y[1] and x[2]==y[2] and x[3]==y[3]
        arr=self.rgba.palette_arr
        for i in range(255):
            if com(arr[i],color):
                return i+1
            if com(color,[0,0,0,0]):
                return False
        raise ValueError('color {} not found'.format(str(color)))
    
    def dump(self):
        bstr=pack('4si', b'VOX ', 150)
        bmain_temp=b''
        for chunk in self.chunks:
            b_content=chunk.to_b()
            bmain_temp+=pack('4sii',chunk.id,len(b_content),0)
            bmain_temp+=b_content
        bmain=pack('4sii',b'MAIN',0,len(bmain_temp))+bmain_temp
        bstr=bstr+bmain
        return bstr
    
    def write(self,fname):
        with open(fname,'wb') as f:
            f.write(self.dump())

class ArrayWriter(BaseWriter):

    def __init__(self,vox_arr:np.ndarray,palette_path=None,palette_arr=None):
        super().__init__(palette_path,palette_arr)

        self.vox=np.array(vox_arr*255,dtype=int)
        self.xyzi=XYZI(self.mapping())
        self.size=SIZE(vox_arr.shape)
        self.chunks=[self.size,self.xyzi,self.rgba]

    def mapping(self):
        voxel=[]
        vox=self.vox
        for x in range(vox.shape[0]):
            for y in range(vox.shape[1]):
                for z in range(vox.shape[2]):
                    c=vox[x,y,z]
                    i=self._get_color_index(c)
                    if i:
                        voxel.append((x,y,z,i))
        return voxel

class ChunkWriter(BaseWriter):
    
    def __init__(self, chunks, palette_path=None, palette_arr=None) -> None:
        super().__init__(palette_path, palette_arr)
        self.chunks=chunks