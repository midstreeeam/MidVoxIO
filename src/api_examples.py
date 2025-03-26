"""
Examples
"""
from midvoxio.api import VoxModel

# Example 1: Loading and visualizing a VOX file
print("=== Example 1: Loading and visualizing a VOX file ===")
model = VoxModel.load("assets/vox/99/3x3x3.vox", verbose=True)
print(f"Model has {model.get_models_count()} models and {len(model.get_chunks())} chunks")
print(f"Chunk names: {model.get_chunk_names()}")

# Visualize the model
model.visualize()
print("Visualized loaded model")

# Example 2: Saving a model to a new file
print("\n=== Example 2: Saving a model to a new file ===")
# model.save("output.vox")
print("Model can be saved with model.save('output.vox')")

# Example 3: Creating a model from scratch
print("\n=== Example 3: Creating a model from scratch ===")
new_model = VoxModel.create(size=(10, 10, 10))

# Create a simple cube
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
                
            new_model.add_voxel(x, y, z, color)

# Visualize the model
new_model.visualize()
# new_model.save("cube.vox")
print("Visualized cube model")

# Example 4: Method chaining for model creation
print("\n=== Example 4: Method chaining for model creation ===")
simple_model = (VoxModel.create(size=(5, 5, 5))
                .add_voxel(1, 1, 1, (255, 0, 0))
                .add_voxel(2, 1, 1, (0, 255, 0))
                .add_voxel(3, 1, 1, (0, 0, 255))
                .add_voxel(1, 2, 1, (255, 255, 0))
                .add_voxel(2, 2, 1, (255, 0, 255))
                .add_voxel(3, 2, 1, (0, 255, 255)))

simple_model.visualize()
# simple_model.save("simple.vox")
print("Visualized simple model created with method chaining")

# Example 5: Loading an existing model and modifying it
print("\n=== Example 5: Loading and modifying a model ===")
model = VoxModel.load("assets/vox/99/3x3x3.vox")
array = model.to_array()
print(f"Loaded model with shape {array.shape}")

# Get the array, modify it, and create a new model
array[0, 0, 0] = [255, 0, 0, 255]  # Add a red voxel at 0,0,0
modified_model = VoxModel.from_array(array)
modified_model.visualize()
# modified_model.save("modified.vox")
print("Visualized modified model")

# Example 6: Creating and modifying a model directly
print("\n=== Example 6: Creating and modifying a model directly ===")
direct_model = VoxModel.create(size=(8, 8, 8))

# Create a pattern
for x in range(8):
    for z in range(8):
        # Create a checkered pattern
        if (x + z) % 2 == 0:
            direct_model.add_voxel(x, 0, z, (255, 255, 255))  # White
        else:
            direct_model.add_voxel(x, 0, z, (0, 0, 0, 255))   # Black

# Add some colored pillars
direct_model.add_voxel(1, 1, 1, (255, 0, 0))
direct_model.add_voxel(1, 2, 1, (255, 0, 0))
direct_model.add_voxel(6, 1, 1, (0, 255, 0))
direct_model.add_voxel(6, 2, 1, (0, 255, 0))
direct_model.add_voxel(1, 1, 6, (0, 0, 255))
direct_model.add_voxel(1, 2, 6, (0, 0, 255))
direct_model.add_voxel(6, 1, 6, (255, 255, 0))
direct_model.add_voxel(6, 2, 6, (255, 255, 0))

# Visualize the model
direct_model.visualize()
# direct_model.save("checker.vox")
print("Visualized checker pattern model") 