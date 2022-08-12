import matplotlib.pylab as plt
import numpy as np

from src.parser import Parser

class Voxio():

    @staticmethod
    def vox_to_arr(fname):
        vox=Parser(fname).parse()
        return vox.to_list()
    
    @staticmethod
    def viz_vox(fname):
        arr=Voxio.vox_to_arr(fname)
        Voxio.plot_3d(arr)

    @staticmethod
    def show_chunks(fname):
        vox=Parser(fname).parse()
        print([i.name for i in vox.chunks])
    
    @staticmethod
    def get_rendering_attributes(fname):
        vox=Parser(fname).parse()
        for obj in vox.robjs:
            print(obj)

    @staticmethod
    def plot_3d(arr):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        u = np.moveaxis(arr, (0, 1), (0, 1))
        m = ax.voxels((u[:, :, :, 3] > 0.1), facecolors=np.clip(u[:, :, :, :4], 0, 1))
        plt.show()
        plt.close()