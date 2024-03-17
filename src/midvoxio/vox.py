from math import prod
from struct import unpack_from
import logging
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

import numpy as np

from .config import *
from .exceptions import AssigningException, ParsingException
from .models import *

class Chunk():
    
    def __init__(self,id,content=None,children=None):
        self.id = id
        self.name = str(id)[2:-1]
        self.content = content or b''
        self.children = children or []
        self.offset=0
        self._parse()
    
    def _parse(self):

        if self.id == b'MAIN':
            if len(self.content):
                raise ParsingException('Empty main chunk')
        
        elif self.id == b'PACK':
            logging.debug('Detect Pack chunk which is not supportted in current version, skip now')
        
        elif self.id == b'SIZE':
            self.size=unpack_from(SIZE_FMT,self.content,0)

        elif self.id == b'XYZI':
            n = int(unpack_from(XYZI_FMT_1,self.content,0)[0])
            self.voxels = []
            for i in range(n):
                self.voxels.append(unpack_from(XYZI_FMT_2, self.content, 4+4*i))

        elif self.id == b'RGBA':
            self.palette=[]
            for i in range(255):
                self.palette.append(unpack_from(RGBA_FMT, self.content, 4*i))

        elif self.id == b'MATL':
            _id = unpack_from('i', self.content)
            _dict = Bdict(self.content,4).dic
            self.material=Material(_id,_dict)

        elif self.id == b'nTRN':
            _id = int(unpack_from('i', self.content)[0])
            frames = []
            bdict = Bdict(self.content,4)
            (c_id,r_id,l_id,frames_num)=unpack_from('iiii', self.content,bdict.offset)
            offset=16+bdict.offset
            for i in range(frames_num):
                _bdict=Bdict(self.content,offset)
                frames.append(_bdict.dic)
                offset=_bdict.offset
            self.ntrn=nTRN(_id,bdict.dic,c_id,r_id,l_id,frames)
            
        elif self.id == b'rOBJ':
            self.robj = ROBJ(Bdict(self.content).dic)
            
        elif self.id == b'nGRP':
            _node_id = int(unpack_from('i', self.content)[0])
            bdict=Bdict(self.content,4)
            _node_attr = bdict.dic
            children_num = int(unpack_from('i', self.content,bdict.offset)[0])
            child_ids = []
            offset=bdict.offset+4
            for i in range(children_num):
                child_ids.append(int(unpack_from('i',self.content,offset+4*i)[0]))
            self.ngrp=NGRP(_node_id,_node_attr,children_num,child_ids)

        elif self.id == b'nSHP':
            _node_id = int(unpack_from('i', self.content)[0])
            bdict=Bdict(self.content,4)
            _node_attr = bdict.dic
            model_num = int(unpack_from('i', self.content,bdict.offset)[0])
            models=[]
            offset=bdict.offset+4
            for i in range(model_num):
                _id=int(unpack_from('i',self.content,offset)[0])
                _bdict=Bdict(self.content,offset+4)
                _attr_dic=_bdict.dic
                offset=_bdict.offset
                mod=ModelAttr(attr_dic=_attr_dic,id=_id)
                models.append(mod)
            self.nshp=nSHP(_node_id,models,node_attr=_node_attr)

        elif self.id == b'LAYR':
            _id = unpack_from('i', self.content)
            bdic=Bdict(self.content,4)
            _rev_id = unpack_from('i',self.content,bdic.offset)
            self.layer=Layer(_id,bdic.dic,_rev_id)

        elif self.id == b'rCAM':
            _id = unpack_from('i', self.content)
            _dict = Bdict(self.content,4).dic
            self.camera=Camera(_id,_dict)

        elif self.id == b'NOTE':
            num = int(unpack_from('i', self.content)[0])
            _name_list=[]
            offset=4
            for i in range(num):
                bstr=Bstring(self.content,offset)
                offset+=bstr.byte_length
                _name_list.append(bstr.string)

            self.palette_note=Note(num,_name_list)

        elif self.id == b'IMAP':
            pass

        elif self.id == b'MATT':
            # TODO: Warn user that we are skipping depracated chunk type
            pass


        else:
            raise ParsingException('Unknown chunk type: %s'%self.id)

class Vox():

    def __init__(self,chunks):
        self.chunks=chunks
        self.palettes = []
        self.sizes = []
        self.voxels = []
        self.materials = []
        self.robjs=[]
        self.layers=[]
        self.ngrps=[]
        self.ntrns=[]
        self.nshps=[]
        self.cameras=[]
        self.palette_notes=[]
        self._parse_chunk()
        if len(self.palettes)==0:
            self.palettes.append(default_palette)
        self.full_vox = [self._to_full(v) for v in self.voxels]
        self._trans(self._get_transform())
        pass

    def _to_full(self, model):
        vc = np.array(model)
        shape = 1 + vc.max(axis=0)
        full = np.zeros(shape=shape[:-1], dtype=np.uint8)
        full[vc[:, 0], vc[:, 1], vc[:, 2]] = vc[:, 3]
        return full

    def _trans(self, transforms):
        """Transform all models and merge into one"""

        if len(transforms) != len(self.voxels):
            print(f"_t in nTRN not match models, transform not applied")
            return

        # calculate the size of the combined module
        transform_coords = np.array([t for (t, _) in transforms])
        min_tran = transform_coords.min(axis=0)
        max_tran = transform_coords.max(axis=0)
        max_sizes = np.array(self.sizes).max(axis=0)
        combined_size = max_sizes + max_tran - min_tran

        self.sizes.append(combined_size)

        # combine models
        combined_model = np.zeros(shape=combined_size, dtype=np.uint8)
        for (transform, _), voxel_chunk in zip(transforms, self.voxels):
            transform = np.array(transform)
            offset = transform - min_tran
            vc = np.array(voxel_chunk)
            vc[:, 0:3] += offset
            combined_model[vc[:, 0], vc[:, 1], vc[:, 2]] = vc[:, 3]

        self.full_vox.append(combined_model)

    def _get_transform(self,frame_index=0):
        '''
        the function returns ([x,y,z],model_id)
        '''
        trn:nTRN
        shp:nSHP
        trlinks=[]
        for trn in self.ntrns:
            for shp in self.nshps:
                if trn.child_node_id==shp.node_id:
                    try:
                        trn.frames[frame_index]['_t']
                    except KeyError:
                        trn.frames[frame_index]['_t']='0 0 0'
                        raise Exception
                    except:
                        raise Exception
                    for model in shp.models:
                        trlinks.append((
                            [int(i) for i in trn.frames[frame_index]['_t'].split()],
                            model.id))
        return trlinks
    
    def _parse_chunk(self):
        for chunk in self.chunks:
            chunk:Chunk
            if chunk.id==b'RGBA':
                self.palettes.append(chunk.palette)
            elif chunk.id==b'SIZE':
                self.sizes.append(chunk.size)
            elif chunk.id==b'XYZI':
                self.voxels.append(chunk.voxels)
            elif chunk.id==b"LAYR":
                self.layers.append(chunk.layer)
            elif chunk.id==b'MATL':
                self.materials.append(chunk.material)
            elif chunk.id==b'rOBJ':
                self.robjs.append(chunk.robj)
            elif chunk.id==b'nTRN':
                self.ntrns.append(chunk.ntrn)
            elif chunk.id==b'nGRP':
                self.ngrps.append(chunk.ngrp)
            elif chunk.id==b'nSHP':
                self.nshps.append(chunk.nshp)
            elif chunk.id==b'rCAM':
                self.cameras.append(chunk.camera)
            elif chunk.id==b'NOTE':
                self.palette_notes.append(chunk.palette_note)


    def to_list(self,vox_index=0,palette_index=0):
        shape = (*self.sizes[vox_index], 4)

        # add blank to lookup to avoid negation
        color = [UNSET] + self.palettes[palette_index]
        vox = self.full_vox[vox_index]
        uniques, inverse = np.unique(vox, return_inverse = True)
        arr = np.array([color[x] for x in uniques], dtype=np.uint8)
        arr = arr[inverse].reshape((*vox.shape, 4))

        # fill to correct volume
        if shape != arr.shape:
            padding = [(0, s-a) for s, a in zip(shape, arr.shape)]
            arr = np.pad(arr, padding)

        return arr / 255