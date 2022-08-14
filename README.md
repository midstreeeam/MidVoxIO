# PyVox
The python IO for [magical voxel](https://ephtracy.github.io/)'s [.vox files](https://github.com/ephtracy/voxel-model).


## Install
- clone the repo
- add the repo to path

## Usage
#### vox_to_arr()
use `vox_to_arr()` to parse .vox file into numpy array.
```Python
from voxio import Voxio

print(Voxio.vox_to_arr('vox/99/3x3x3.vox').shape)
```
result:
```Python
(3, 3, 3, 4) # the four axis are (x,y,z,color), color is [r,g,b,a] here
```

</br>

#### viz_vox()
use `viz_vox()` to parse .vox file into numpy array.
```Python
from voxio import Voxio

Voxio.viz_vox('vox/99/3x3x3')
```
then, the python will give you a 3d plot.
<img src="/img/3x3x3.jpg" width="30%">

#### get other info
use `get_rendering_attributes()`,`get_cameras()`, and `get_materials()` to get vox info.
```Python
>>> from voxio import Voxio
>>> print(Voxio.get_cameras('vox/99/cars.vox')[0])
{'id': (0,), 'attributes': {'_mode': 'pers', '_focus': '0 0 0', '_angle': '0 0 0', '_radius': '0', '_frustum': '0.414214', '_fov': '45'}}
>>> print(Voxio.get_rendering_attributes('vox/99/3x3x3.vox')[0])
{'_type': '_inf', '_i': '0.6', '_k': '255 255 255', '_angle': '50 50', '_area': '0.07'}
>>> print(Voxio.get_materials('vox/99/3x3x3.vox')[0])
{'id': (0,), 'properties': {'_type': '_diffuse', '_weight': '1', '_rough': '0.1', '_spec': '0.5', '_ior': '0.3'}}
```

## Others
- This project was originally created for me to use it myself.
- Gromgull's [py-vox-io](https://github.com/gromgull/py-vox-io) is good to use, but only for MagicalVoxel 0.98 or older version, and he somehow stop updating. This repo reuse some of Gromgull's code, but now it fit MagicalVoxel 0.99.
- Lots of functions are still under development.