from struct import pack

import numpy as np

from .models import SIZE, XYZI, RGBA, UNSET

class BaseWriter():
    def __init__(self,palette_path=None,palette_arr=None) -> None:
        self.chunks=[]
        if palette_path:
            self.rgba=RGBA(img_path=palette_path)
        elif palette_arr:
            self.rgba=RGBA(palette_arr=palette_arr)
        else:
            raise Exception("palette missing")
    
    def _get_color_index(self, color):
        if not np.any(color):
            return False
        where = np.asarray(np.all(self.rgba.palette_arr == color, axis=1)).nonzero()
        if len(where):
            return 1 + where[0][0]
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
        super().__init__(palette_path, palette_arr)

        self.vox=np.array(vox_arr*255, dtype=np.uint8)
        self.xyzi=XYZI(self.mapping())
        self.size=SIZE(vox_arr.shape)
        self.chunks=[self.size, self.xyzi, self.rgba]
    
    def mapping(self):
        safepalette = np.array([UNSET, *self.rgba.palette_arr[:-1]], dtype=np.uint8)
        bytepallet = np.frombuffer(safepalette.tobytes(), dtype=np.uint32)
        d = {v: k for (k, v) in enumerate(bytepallet.tolist())}

        flatvox = self.vox.reshape(-1, self.vox.shape[-1])
        flatbytes = np.frombuffer(flatvox.tobytes(), dtype=np.uint32)

        uniques, inverse = np.unique(flatbytes, return_inverse = True)
        arr = np.array([d.get(x, 0) for x in uniques], dtype=np.uint8)
        return arr[inverse].reshape(*self.vox.shape[:-1]) 

class ChunkWriter(BaseWriter):
    
    def __init__(self, chunks, palette_path=None, palette_arr=None) -> None:
        super().__init__(palette_path, palette_arr)
        self.chunks=chunks
