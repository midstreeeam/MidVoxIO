from struct import pack

import numpy as np

from .models import SIZE, XYZI, RGBA, BaseChunk

class Writer():

    def __init__(self,vox_arr:np.ndarray,palette_path):
        self.vox=np.array(vox_arr*255,dtype=int)
        self.rgba=RGBA(palette_path)
        self.xyzi=XYZI(self.mapping())
        self.size=SIZE(vox_arr.shape)
        self.chunks=[self.size,self.xyzi,self.rgba]
        pass

    def _get_color_index(self,color):
        com=lambda x,y:x[0]==y[0] and x[1]==y[1] and x[2]==y[2] and x[3]==y[3]
        arr=self.rgba.palette_arr
        for i in range(255):
            if com(arr[i],color):
                return i+1
            if com(color,[0,0,0,0]):
                return False
        raise ValueError('color {} not found'.format(str(color)))

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
    
    
    def dump(self):
        bstr=pack('4si', b'VOX ', 150)
        bmain_temp=b''
        for chunk in self.chunks:
            chunk:BaseChunk
            b_content=chunk.to_b()
            bmain_temp+=pack('4sii',chunk.id,len(b_content),0)
            bmain_temp+=b_content
        bmain=pack('4sii',b'MAIN',0,len(bmain_temp))+bmain_temp
        bstr=bstr+bmain
        return bstr
    
    def write(self,fname):
        with open(fname,'wb') as f:
            f.write(self.dump())


