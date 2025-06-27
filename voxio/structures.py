import struct
from collections import namedtuple

class Model:
    def __init__(self, size, voxels):
        self.size = size
        self.voxels = voxels
    
    def __repr__(self):
        return f"Model(size={self.size}, num_voxels={len(self.voxels)})"

    def get_voxel(self, x, y, z):
        """Returns the voxel at a specific coordinate, or None if it doesn't exist."""
        for voxel in self.voxels:
            if voxel.x == x and voxel.y == y and voxel.z == z:
                return voxel
        return None

    def set_voxel(self, x, y, z, color_index):
        """
        Sets the color of a voxel at a specific coordinate.
        If a voxel exists, it updates its color.
        If no voxel exists, it creates a new one.
        """
        existing_voxel = self.get_voxel(x, y, z)
        if existing_voxel:
            existing_voxel.color_index = color_index
        else:
            self.voxels.append(Voxel(x, y, z, color_index))

class Voxel:
    def __init__(self, x, y, z, color_index):
        self.x = x
        self.y = y
        self.z = z
        self.color_index = color_index

    def __repr__(self):
        return f"Voxel(x={self.x}, y={self.y}, z={self.z}, color_index={self.color_index})"

class Color:
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __repr__(self):
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

class Chunk:
    def __init__(self, id, content, children_chunks):
        self.id = id
        self.content = content
        self.children_chunks = children_chunks

    def __repr__(self):
        return f"Chunk(id='{self.id}', content_size={len(self.content)}, num_children={len(self.children_chunks)})"

    def to_bytes(self):
        children_bytes = b''.join(c.to_bytes() for c in self.children_chunks)
        header = struct.pack('<4sII', self.id.encode('ascii'), len(self.content), len(children_bytes))
        return header + self.content + children_bytes
