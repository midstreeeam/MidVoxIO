from inspect import classify_class_attrs
from struct import pack,calcsize
from pyvox.parser import Parser

from pyvox.voxio import Plotio, Voxio

from pyvox.writer import Writer

# print(Voxio.vox_to_arr('vox/99/3x3x3.vox').shape)
# Voxio.viz_vox('vox/98/cat.vox')
# Voxio.show_chunks('vox/99/cars.vox')
# Voxio.viz_vox('vox/99/cars.vox',1)
# Voxio.show_rendering_attributes('vox/99/3x3x3.vox')
# vox = Voxio.get_vox('vox/99/3x3x3.vox')

v=Voxio.vox_to_arr('vox/98/cat.vox')
path='palette/cat.png'

Voxio.write_list_to_vox(v,'test.vox',path)

# t=Writer(v,palette_path=path)
# t.write('test.vox')


