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

print(Voxio.vox_to_arr('vox/99/3x3x3').shape)
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

## Others
- This project was originally created for me to use it myself.
- Gromgull's [py-vox-io](https://github.com/gromgull/py-vox-io) is good to use, but only for MagicalVoxel 0.98 or older version, and he somehow stop updating. This repo reuse some of Gromgull's code, but now it fit MagicalVoxel 0.99.
- Lots of functions are still under development.