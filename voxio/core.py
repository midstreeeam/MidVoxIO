import struct
import io
from .structures import Chunk, Model, Voxel, Color

class Vox:
    def __init__(self, filename):
        self.filename = filename
        self.version = None
        self.main_chunk = None
        self._models = None
        self._palette = None
        self.load()

    @staticmethod
    def read_chunk(f):
        try:
            chunk_id_bytes = f.read(4)
            if not chunk_id_bytes:
                return None
            
            chunk_id = chunk_id_bytes.decode('ascii')
            content_size, children_size = struct.unpack('<II', f.read(8))
            content = f.read(content_size)
            children_data = f.read(children_size)
            
            children_chunks = []
            if children_size > 0:
                children_stream = io.BytesIO(children_data)
                while children_stream.tell() < children_size:
                    child_chunk = Vox.read_chunk(children_stream)
                    if child_chunk:
                        children_chunks.append(child_chunk)
                    else:
                        break

            return Chunk(chunk_id, content, children_chunks)
        except (struct.error, EOFError, UnicodeDecodeError):
            return None

    def load(self):
        with open(self.filename, 'rb') as f:
            magic = f.read(4).decode('ascii')
            if magic != 'VOX ':
                raise ValueError("Not a .vox file")

            self.version = struct.unpack('<I', f.read(4))[0]
            
            self.main_chunk = self.read_chunk(f)
            if not self.main_chunk or self.main_chunk.id != 'MAIN':
                raise ValueError("MAIN chunk not found")

    @property
    def models(self):
        if self._models is None:
            self._models = []
            model_chunks = []
            
            for child in self.main_chunk.children_chunks:
                if child.id == 'SIZE':
                    model_chunks.append({'size': child})
                elif child.id == 'XYZI':
                    if model_chunks:
                        model_chunks[-1]['xyzi'] = child

            for m_chunks in model_chunks:
                if 'size' in m_chunks and 'xyzi' in m_chunks:
                    size_chunk = m_chunks['size']
                    xyzi_chunk = m_chunks['xyzi']
                    
                    sx, sy, sz = struct.unpack('<III', size_chunk.content)
                    
                    num_voxels = struct.unpack('<I', xyzi_chunk.content[:4])[0]
                    voxels = []
                    for i in range(num_voxels):
                        offset = 4 + i * 4
                        vx, vy, vz, ci = struct.unpack('<BBBB', xyzi_chunk.content[offset:offset+4])
                        voxels.append(Voxel(vx, vy, vz, ci))
                    
                    self._models.append(Model(size=(sx, sy, sz), voxels=voxels))
        return self._models

    @property
    def palette(self):
        if self._palette is None:
            self._palette = []
            for child in self.main_chunk.children_chunks:
                if child.id == 'RGBA':
                    palette_data = child.content
                    for i in range(0, len(palette_data), 4):
                        r, g, b, a = struct.unpack('<BBBB', palette_data[i:i+4])
                        self._palette.append(Color(r, g, b, a))
                    break
        return self._palette

    def write(self, filename):
        self._update_chunks()
        with open(filename, 'wb') as f:
            f.write(b'VOX ')
            f.write(struct.pack('<I', self.version))
            f.write(self.main_chunk.to_bytes())

    def _update_chunks(self):
        """
        If models or palette have been modified, update the raw chunk content.
        """
        if self._models is None and self._palette is None:
            # Nothing has been parsed, so nothing to update.
            return

        # --- Update model chunks (SIZE and XYZI) ---
        if self._models is not None:
            model_chunks = [c for c in self.main_chunk.children_chunks if c.id in ('SIZE', 'XYZI')]
            # This is a simple implementation assuming a 1-to-1 mapping
            # of models to SIZE/XYZI chunk pairs in the file.
            for i, model in enumerate(self.models):
                size_chunk = model_chunks[i*2]
                xyzi_chunk = model_chunks[i*2 + 1]

                # Update SIZE chunk
                size_chunk.content = struct.pack('<III', *model.size)

                # Update XYZI chunk
                xyzi_content = struct.pack('<I', len(model.voxels))
                for v in model.voxels:
                    xyzi_content += struct.pack('<BBBB', v.x, v.y, v.z, v.color_index)
                xyzi_chunk.content = xyzi_content
        
        # --- Update palette chunk (RGBA) ---
        if self._palette is not None:
            for chunk in self.main_chunk.children_chunks:
                if chunk.id == 'RGBA':
                    rgba_content = b''
                    for c in self.palette:
                        rgba_content += struct.pack('<BBBB', c.r, c.g, c.b, c.a)
                    # Pad to 256 colors if necessary
                    rgba_content += b'\x00' * (1024 - len(rgba_content))
                    chunk.content = rgba_content
                    break

    @staticmethod
    def _read_string_from_stream(stream):
        try:
            size = struct.unpack('<I', stream.read(4))[0]
            return stream.read(size).decode('utf-8', errors='ignore')
        except (struct.error, EOFError):
            return "Error reading string"

    @staticmethod
    def _read_dict_from_stream(stream):
        d = {}
        try:
            num_pairs = struct.unpack('<I', stream.read(4))[0]
            for _ in range(num_pairs):
                key = Vox._read_string_from_stream(stream)
                value = Vox._read_string_from_stream(stream)
                d[key] = value
            return d
        except (struct.error, EOFError):
            return {"Error": "reading dict"}

    def _parse_chunk_content(self, chunk):
        stream = io.BytesIO(chunk.content)
        
        if not chunk.content:
            return "empty"

        try:
            if chunk.id == 'PACK':
                if len(chunk.content) == 4:
                    return f"num_models: {struct.unpack('<I', chunk.content)[0]}"
            elif chunk.id == 'SIZE':
                if len(chunk.content) == 12:
                    return f"size: {struct.unpack('<III', chunk.content)}"
            elif chunk.id == 'XYZI':
                if len(chunk.content) >= 4:
                    return f"num_voxels: {struct.unpack('<I', chunk.content[:4])[0]}"
            elif chunk.id == 'RGBA':
                return f"num_colors: {len(chunk.content) // 4}"
            elif chunk.id in ('nTRN', 'nGRP', 'nSHP'):
                node_id = struct.unpack('<I', stream.read(4))[0]
                attrs = self._read_dict_from_stream(stream)
                content_str = f"id: {node_id}, attrs: {attrs}"
                if chunk.id == 'nTRN':
                    child_id = struct.unpack('<I', stream.read(4))[0]
                    content_str += f", child_id: {child_id}"
                elif chunk.id == 'nGRP':
                    num_children = struct.unpack('<I', stream.read(4))[0]
                    children_ids = struct.unpack(f'<{num_children}I', stream.read(4 * num_children))
                    content_str += f", children_ids: {children_ids}"
                return content_str
            elif chunk.id == 'MATL':
                mat_id = struct.unpack('<I', stream.read(4))[0]
                props = self._read_dict_from_stream(stream)
                return f"id: {mat_id}, props: {props}"
            elif chunk.id == 'LAYR':
                layer_id = struct.unpack('<I', stream.read(4))[0]
                attrs = self._read_dict_from_stream(stream)
                return f"id: {layer_id}, attrs: {attrs}"
            elif chunk.id in ('rOBJ', 'rCAM', 'NOTE', 'IMAP'):
                return "Complex chunk data..."
        except (struct.error, EOFError):
            return f"Error parsing content. Preview: {chunk.content[:32]}..."

        return f"raw data preview: {chunk.content[:32]}..."

    def summary(self):
        """Prints a summary of the chunk structure and scene graph."""
        if not self.main_chunk:
            print("No data loaded.")
            return
        
        print(f"File: {self.filename}, Version: {self.version}\n")
        
        print("--- File Chunk Hierarchy ---")
        self._print_chunk_hierarchy(self.main_chunk, 0)
        
        nodes = {}
        child_to_parent = {}

        scene_chunks = [c for c in self.main_chunk.children_chunks if c.id in ('nTRN', 'nGRP', 'nSHP')]
        
        for chunk in scene_chunks:
            stream = io.BytesIO(chunk.content)
            try:
                node_id = struct.unpack('<I', stream.read(4))[0]
                nodes[node_id] = chunk
                if chunk.id == 'nTRN':
                    _ = self._read_dict_from_stream(stream)
                    child_id = struct.unpack('<I', stream.read(4))[0]
                    child_to_parent[child_id] = node_id
                elif chunk.id == 'nGRP':
                    _ = self._read_dict_from_stream(stream)
                    num_children = struct.unpack('<I', stream.read(4))[0]
                    for _ in range(num_children):
                        child_id = struct.unpack('<I', stream.read(4))[0]
                        child_to_parent[child_id] = node_id
            except (struct.error, EOFError):
                continue
    
        root_nodes = sorted([node_id for node_id in nodes if node_id not in child_to_parent])
        
        if root_nodes:
            print("\n--- Scene Graph Hierarchy ---")
            for node_id in root_nodes:
                self._print_scene_node(node_id, nodes, 0)

    def _print_chunk_hierarchy(self, chunk, level):
        indent = "  " * level
        print(f"{indent}- {chunk.id} (content: {len(chunk.content)} bytes, nested children: {len(chunk.children_chunks)})")
        for child in chunk.children_chunks:
            self._print_chunk_hierarchy(child, level + 1)

    def _get_child_nodes(self, chunk):
        child_ids = []
        stream = io.BytesIO(chunk.content)
        try:
            stream.read(4)
            if chunk.id == 'nTRN':
                _ = self._read_dict_from_stream(stream)
                child_ids.append(struct.unpack('<I', stream.read(4))[0])
            elif chunk.id == 'nGRP':
                _ = self._read_dict_from_stream(stream)
                num_children = struct.unpack('<I', stream.read(4))[0]
                for _ in range(num_children):
                    child_ids.append(struct.unpack('<I', stream.read(4))[0])
        except (struct.error, EOFError):
            pass
        return child_ids

    def _print_scene_node(self, node_id, nodes, level):
        indent = "  " * level
        chunk = nodes.get(node_id)
        if not chunk:
            print(f"{indent}- [Broken Link] Node ID: {node_id}")
            return
        
        print(f"{indent}- {chunk.id} (ID: {node_id})")
        print(f"{indent}  Content: {self._parse_chunk_content(chunk)}")
        
        for child_id in self._get_child_nodes(chunk):
            self._print_scene_node(child_id, nodes, level + 1)
