# MidVoxIO

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/midstreeeam/MidVoxIO/python-publish.yml)
![PyPI](https://img.shields.io/pypi/v/midvoxio)
[![Downloads](https://static.pepy.tech/badge/midvoxio)](https://pepy.tech/project/midvoxio)

The python IO to load/write/visualize [magical voxel](https://ephtracy.github.io/)'s [.vox format](https://github.com/ephtracy/voxel-model).

## Installation

```bash
pip install midvoxio
```

## Basic Usage

```python
from midvoxio import VoxModel

# Load a VOX file
model = VoxModel.load("path/to/model.vox")

# Visualize it
model.visualize()

# Create a new model
new_model = VoxModel.create(size=(10, 10, 10))
new_model.add_voxel(5, 5, 5, (255, 0, 0))  # Add a red voxel in the center
new_model.save("my_model.vox")
```

## API Reference

### Loading Models

```python
# Load a model from a file
model = VoxModel.load("path/to/model.vox")

# Load with verbose output
model = VoxModel.load("path/to/model.vox", verbose=True)
```

### Creating Models

```python
# Create an empty model
model = VoxModel.create()  # Default size is (32, 32, 32)

# Create with specific size
model = VoxModel.create(size=(16, 16, 16))

# Create from a NumPy array
import numpy as np
array = np.zeros((10, 10, 10, 4))  # RGBA array
array[5, 5, 5] = [1.0, 0.0, 0.0, 1.0]  # Red voxel at center
model = VoxModel.from_array(array)
```

### Adding Voxels

```python
# Add voxels with RGB or RGBA colors
model.add_voxel(1, 2, 3, (255, 0, 0))       # Red voxel with RGB
model.add_voxel(4, 5, 6, (0, 255, 0, 255))  # Green voxel with RGBA

# Method chaining is supported
model = (VoxModel.create()
         .add_voxel(1, 1, 1, (255, 0, 0))
         .add_voxel(2, 2, 2, (0, 255, 0))
         .add_voxel(3, 3, 3, (0, 0, 255)))
```

### Visualizing Models

```python
# Visualize the model
model.visualize()

# Visualize a specific submodel (for files with multiple models)
model.visualize(model_index=1)

# Visualize the combined model
model.visualize(model_index=-1)
```

When visualizing, a 3D plot will be displayed:

<img src="/img/3x3x3.jpg" width="25%">

### Converting to Array

```python
# Get a NumPy array representation of the model
array = model.to_array()

# Array has shape (width, height, depth, 4) with RGBA channels
# Values range from 0.0 to 1.0
```

### Saving Models

```python
# Save a model
model.save("output.vox")
```

### Model Information

```python
# Get model information
print(f"Model has {model.get_models_count()} models")
print(f"Chunk names: {model.get_chunk_names()}")
print(f"Materials: {model.get_materials()}")
print(f"Cameras: {model.get_cameras()}")
print(f"Rendering attributes: {model.get_rendering_attributes()}")
```

## Examples

### Creating a Cube

```python
from midvoxio import VoxModel

# Create a new model
model = VoxModel.create(size=(10, 10, 10))

# Create a cube
for x in range(2, 5):
    for y in range(2, 5):
        for z in range(2, 5):
            # Add different colors to different sides
            if x == 2:
                color = (255, 0, 0)  # Red
            elif x == 4:
                color = (0, 255, 0)  # Green
            elif y == 2:
                color = (0, 0, 255)  # Blue
            elif y == 4:
                color = (255, 255, 0)  # Yellow
            elif z == 2:
                color = (255, 0, 255)  # Magenta
            elif z == 4:
                color = (0, 255, 255)  # Cyan
            else:
                color = (255, 255, 255)  # White
                
            model.add_voxel(x, y, z, color)

# Visualize the result
model.visualize()
```

### Creating a Checkerboard Pattern

```python
from midvoxio import VoxModel

# Create a new model
model = VoxModel.create(size=(8, 8, 8))

# Create a checkerboard floor
for x in range(8):
    for z in range(8):
        if (x + z) % 2 == 0:
            model.add_voxel(x, 0, z, (255, 255, 255))  # White
        else:
            model.add_voxel(x, 0, z, (0, 0, 0, 255))   # Black

# Add pillars at the corners
model.add_voxel(1, 1, 1, (255, 0, 0))
model.add_voxel(1, 2, 1, (255, 0, 0))
model.add_voxel(6, 1, 1, (0, 255, 0))
model.add_voxel(6, 2, 1, (0, 255, 0))
model.add_voxel(1, 1, 6, (0, 0, 255))
model.add_voxel(1, 2, 6, (0, 0, 255))
model.add_voxel(6, 1, 6, (255, 255, 0))
model.add_voxel(6, 2, 6, (255, 255, 0))

# Visualize the result
model.visualize()
```

### Modifying an Existing Model

```python
from midvoxio import VoxModel

# Load an existing model
model = VoxModel.load("path/to/model.vox")

# Convert to array
array = model.to_array()

# Modify the array
array[0, 0, 0] = [1.0, 0.0, 0.0, 1.0]  # Add a red voxel at origin

# Create a new model from the modified array
modified_model = VoxModel.from_array(array)

# Visualize and save
modified_model.visualize()
modified_model.save("modified_model.vox")
```

## Notes

- The previous functional API (`vox_to_arr`, `viz_vox`, etc.) is still available but considered legacy. New code should use the `VoxModel` class.
- This library supports MagicaVoxel 0.99 and later versions.

## License

MIT

## Others

- This project was originally created for me to use it myself, so the API design is casual and the error message is not complete. Will consider make it more formal if there are really people using it.
- Gromgull's [py-vox-io](https://github.com/gromgull/py-vox-io) is good to use, but only for MagicalVoxel 0.98 or older version, and he somehow stop updating. This voxio reuse some of Gromgull's code (mostly in parser), but now it fit MagicalVoxel 0.99. Also, there are also new features like `viz_vox()` to visualize the vox array without using magicalvoxel.
- Lots of functions are still under development.
