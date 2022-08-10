from struct import unpack_from, calcsize
import logging

from .config import *
from .exceptions import ParsingException
from .models import Chunk,Vox

log = logging.getLogger(__name__)

class Parser():

    def __init__(self,fname):
        with open(fname, 'rb') as f:
            self.content = f.read()
        
        self.offset=0
        pass

    def unpack(self, fmt):
        r = unpack_from(fmt, self.content, self.offset)
        self.offset += calcsize(fmt)
        return r
    
    def _parseChunk(self):
    
        _id, N, M = self.unpack(CHUNK_FMT)
        # print(_id, N, M)

        log.debug("Found chunk id %s / len %s / children %s", _id, N, M)

        content = self.unpack('%ds'%N)[0]

        start = self.offset
        chunks = [ ]
        while self.offset<start+M:
            chunks.append(self._parseChunk())

        return Chunk(_id, content, chunks)

    def parse(self):
        header, version = self.unpack(VOX_FMT)
        if header != VOX_HEADER: 
            raise ParsingException("Not a vox file")
        if version != VOX_VERSION: 
            raise ParsingException("Unknown vox version: %s expected %s"%(version,VOX_VERSION))
        main=self._parseChunk()
        if main.id != b'MAIN': raise ParsingException("Missing MAIN Chunk")
        chunks:list[Chunk]=list(main.children)
            
        return Vox(chunks)


    pass