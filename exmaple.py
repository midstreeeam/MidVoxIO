from pyvox.models import *
from pyvox.voxio import  * 

# print(vox_to_arr('vox/99/3x3x3.vox'))
# viz_vox('vox/98/cat.vox')
# show_chunks('vox/99/cars.vox')
# viz_vox('vox/99/cars.vox',1)
# print(get_rendering_attributes('vox/99/3x3x3.vox'))
# vox = get_vox('vox/99/cars.vox')

# v=vox_to_arr('vox/98/cat.vox')
# path='palette/cat.png'

# write_list_to_vox(v,'test.vox',path)

# t=ArrayWriter(v,palette_path=path)
# t.write('test.vox')


# # create new nodes
# kwargs={
#     'node_id':1,
#     'node_attr':{},
#     'models':[ModelAttr({},0)]
# }

# shape=nSHP(**kwargs)

# kwargs={
#     'node_id':2,
#     'node_attributes':{},
#     'child_node_id':1,
#     'reversed_id':-1,
#     'layer_id':1,
#     'frames':[
#             {
#             '_t': '10 10 10'
#         }
#     ]
# }
# trans=nTRN(**kwargs)
