# MidVoxIO

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/midstreeeam/MidVoxIO/python-publish.yml)
![PyPI](https://img.shields.io/pypi/v/midvoxio)
[![Downloads](https://static.pepy.tech/badge/midvoxio)](https://pepy.tech/project/midvoxio)

The python IO to load/write/visualize [magical voxel](https://ephtracy.github.io/)'s [.vox format](https://github.com/ephtracy/voxel-model).


## Install

### pip
```
pip install midvoxio
```

### through repo
- clone the repo
- add the repo to path
- Install numpy and matplotlib if you haven't

## Usage
#### vox_to_arr()
use `vox_to_arr()` to parse .vox file into numpy array.
```Python
from midvoxio.voxio import vox_to_arr

print(vox_to_arr('vox/99/3x3x3.vox').shape)
```
result:
```Python
(3, 3, 3, 4) # the four axis are (x,y,z,color), color is [r,g,b,a] here
```

#### multiple models
if there are multiple models in one vox file, use `vox_to_arr('path',n)` to get the nth model's array.
use `vox_to_arr('path',-1)` to get the array of combined model.

#### viz_vox()

use `viz_vox()` to visualize your .vox file. It uses `matplotlib` to plot the file internally.
```Python
from midvoxio.voxio import viz_vox

viz_vox('vox/99/3x3x3.vox')
```
then, the python will give you a 3d plot.
<img src="/img/3x3x3.jpg" width="25%">



#### get other info

use `get_rendering_attributes()`,`get_cameras()`, and `get_materials()` to get vox info.
```Python
>>> from midvoxio.voxio import *
>>> print(get_cameras('vox/99/cars.vox')[0])
{'id': (0,), 'attributes': {'_mode': 'pers', '_focus': '0 0 0', '_angle': '0 0 0', '_radius': '0', '_frustum': '0.414214', '_fov': '45'}}
>>> print(get_rendering_attributes('vox/99/3x3x3.vox')[0])
{'_type': '_inf', '_i': '0.6', '_k': '255 255 255', '_angle': '50 50', '_area': '0.07'}
>>> print(get_materials('vox/99/3x3x3.vox')[0])
{'id': (0,), 'properties': {'_type': '_diffuse', '_weight': '1', '_rough': '0.1', '_spec': '0.5', '_ior': '0.3'}}
```



#### write_list_to_vox()

use `write_list_to_vox` to generate vox file from exist python list. You can use this function to export the python list as vox file, so you will be able to edit vox file in python.

```Python
from midvoxio.voxio import write_list_to_vox,plot_3d

arr=[] # define your python list that represent the 3d model here

# define your palette that relate to your model here
# palette will be able to be automatically generated in the future
palette=[]


# you can use plotio to viz your arr before you save it to vox
plot_3d(arr) # visualize your arr

write_list_to_vox(arr,'fname.vox',palette_arr=palette) # then, you save the 'fname.vox'

# you can also use png palette
palette_path='palette.png'
write_list_tov_vox(arr,'fname.vox',palette_path) # then, you save the 'fname.vox'
```



## Others

- This project was originally created for me to use it myself, so the API design is casual and the error message is not complete. Will consider make it more formal if there are really people using it.
- Gromgull's [py-vox-io](https://github.com/gromgull/py-vox-io) is good to use, but only for MagicalVoxel 0.98 or older version, and he somehow stop updating. This voxio reuse some of Gromgull's code (mostly in parser), but now it fit MagicalVoxel 0.99. Also, there are also new features like `viz_vox()` to visualize the vox array without using magicalvoxel.
- Lots of functions are still under development.
