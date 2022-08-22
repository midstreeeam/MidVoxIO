import matplotlib.pylab as plt
import numpy as np

from .writer import Writer
from .parser import Parser

class Voxio():

    @staticmethod
    def _get_attr(attr_lst):
        ret=[]
        for i in attr_lst:
            ret.append(str(i))
        return ret

    @staticmethod
    def vox_to_arr(fname,vox_index=0):
        vox=Parser(fname).parse()
        return vox.to_list(vox_index)
    
    @staticmethod
    def viz_vox(fname,vox_index=0):
        arr=Voxio.vox_to_arr(fname,vox_index)
        Plotio.plot_3d(arr)

    @staticmethod
    def show_chunks(fname):
        vox=Parser(fname).parse()
        print([i.name for i in vox.chunks])
    
    @staticmethod
    def get_rendering_attributes(fname):
        vox=Parser(fname).parse()
        return Voxio._get_attr(vox.robjs)
    
    @staticmethod
    def get_materials(fname):
        vox=Parser(fname).parse()
        return Voxio._get_attr(vox.materials)
    
    @staticmethod
    def get_cameras(fname):
        vox=Parser(fname).parse()
        return Voxio._get_attr(vox.cameras)
    
    @staticmethod
    def get_vox(fname):
        return Parser(fname).parse()

    @staticmethod
    def write_list_to_vox(arr,vox_fname,palette_path=None,palette_arr=None):
        if palette_arr:
            t=Writer(arr,palette_arr=palette_arr)
        if palette_path:
            t=Writer(arr,palette_path=palette_path)
        t.write(vox_fname)

class Plotio():

    @staticmethod
    def plot_3d(arr):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        u = np.moveaxis(arr, (0, 1), (0, 1))
        m = ax.voxels((u[:, :, :, 3] > 0.1), facecolors=np.clip(u[:, :, :, :4], 0, 1))
        plt.show()
        plt.close()