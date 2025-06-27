import numpy as np
import matplotlib.pyplot as plt

def visualize(vox):
    if not vox.models:
        print("No models to visualize.")
        return

    for i, model in enumerate(vox.models):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        sx, sy, sz = model.size
        voxel_grid = np.zeros((sx, sy, sz), dtype=bool)
        colors = np.empty((sx, sy, sz), dtype=object)

        for voxel in model.voxels:
            voxel_grid[voxel.x, (sy-1)-voxel.y, voxel.z] = True
            
            if voxel.color_index < len(vox.palette):
                c = vox.palette[voxel.color_index]
                colors[voxel.x, (sy-1)-voxel.y, voxel.z] = (c.r/255, c.g/255, c.b/255, c.a/255)
            else:
                colors[voxel.x, (sy-1)-voxel.y, voxel.z] = (0.5, 0.5, 0.5, 0.5)

        ax.voxels(voxel_grid, facecolors=colors, edgecolor='k')

        ax.set_title(f"Model {i+1}")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # Set axis limits to ensure all voxels are visible
        ax.set_xlim(0, sx)
        ax.set_ylim(0, sy)
        ax.set_zlim(0, sz)
        
        plt.show()
