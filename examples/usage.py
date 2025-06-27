import sys
import os

# Add the project root to the Python path to allow importing the library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voxio import Vox, visualize

def main():
    """
    This script demonstrates the core functionalities of the voxio library:
    1. Loading a .vox file.
    2. Inspecting its structure with a summary.
    3. Modifying the model data by updating and adding voxels.
    4. Visualizing the modified model.
    5. Saving the changes to a new .vox file.
    """
    
    input_file = "3x3x3.vox"
    output_file = "usage_output.vox"

    try:
        # 1. Load the .vox file
        print(f"--- Loading file: {input_file} ---")
        vox = Vox(input_file)

        # 2. Inspect the file structure
        print("\n--- Original File Summary ---")
        vox.summary()

        model = vox.models[0]
        print(f"\nOriginal voxel count: {len(model.voxels)}")

        # 3. Modify the model data
        print("\n--- Modifying Model ---")
        
        # Update the color of the first voxel found
        if model.voxels:
            voxel_to_update = model.voxels[0]
            print(f"Updating voxel at ({voxel_to_update.x}, {voxel_to_update.y}, {voxel_to_update.z}) to color index 100")
            model.set_voxel(voxel_to_update.x, voxel_to_update.y, voxel_to_update.z, 100)

        # Add a new voxel at the first available empty space
        sx, sy, sz = model.size
        for x in range(sx):
            for y in range(sy):
                for z in range(sz):
                    if model.get_voxel(x, y, z) is None:
                        print(f"Adding new voxel at ({x}, {y}, {z}) with color index 101")
                        model.set_voxel(x, y, z, 101)
                        break
                else: continue
                break
            else: continue
            break
            
        print(f"New voxel count: {len(model.voxels)}")

        # 4. Visualize the modified model
        print("\n--- Visualizing Modified Model ---")
        visualize(vox)

        # 5. Save the changes to a new file
        print(f"\n--- Saving changes to: {output_file} ---")
        vox.write(output_file)
        print("Save complete.")

    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
