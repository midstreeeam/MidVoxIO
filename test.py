from voxio import Voxio
import matplotlib.pylab as plt
import numpy as np

def plot_3d(arr):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    u = np.moveaxis(arr, (0, 1), (0, 1))
    m = ax.voxels((u[:, :, :, 3] > 0.1), facecolors=np.clip(u[:, :, :, :4], 0, 1))
    plt.show()
    plt.close()

plot_3d(Voxio.vox_to_arr('vox/99/3x3x3.vox'))

plot_3d(Voxio.vox_to_arr('vox/98/cat1-0.vox'))