'''
User API
'''
import matplotlib.pylab as plt
import numpy as np

from .exceptions import DumpingException

from .writer import ArrayWriter, ChunkWriter
from .parser import Parser
from .vox import Vox


def _get_attr(attr_lst):
    return [str(i) for i in attr_lst]

def vox_to_arr(fname:str,vox_index=0):
    '''
    Return an array of the vox file.
    fname: path to vox file
    vox_index: which model to show if there is multiple models
                index -1 means show all the model to gether
    '''
    vox=Parser(fname).parse()
    return vox.to_list(vox_index)

def viz_vox(fname:str,vox_index=0):
    '''
    Viz vox file by using matplotlib
    fname: path to vox file
    vox_index: which model to show if there is multiple models
                index -1 means show all the model to gether
    '''
    arr=vox_to_arr(fname,vox_index)
    plot_3d(arr)

def show_chunks(fname:str):
    '''
    print chunk names of all chuncks in the vox file
    '''
    vox=Parser(fname).parse()
    print([i.name for i in vox.chunks])

def get_rendering_attributes(fname:str):
    '''
    return all redering attributes of a vox file
    '''
    vox=Parser(fname).parse()
    return _get_attr(vox.robjs)

def get_materials(fname:str):
    '''
    return all material attributes of a vox file
    '''
    vox=Parser(fname).parse()
    return _get_attr(vox.materials)

def get_cameras(fname:str):
    '''
    return all cameras attributes of a vox file
    '''
    vox=Parser(fname).parse()
    return _get_attr(vox.cameras)

def get_vox(fname:str) -> Vox:
    '''
    return a Vox class of the vox file
    '''
    return Parser(fname).parse()

def write_list_to_vox(arr,vox_fname:str,palette_path=None,palette_arr=None):
    '''
    dump and write an arr into vox file
    arr: python list or numpy array that contains voxel information
    vox_fname: the name of created vox file
    palette_path: if you want to use your own palette
    palette_arr: if you want to use your own palette
    '''
    if palette_arr:
        t=ArrayWriter(arr,palette_arr=palette_arr)
    elif palette_path:
        t=ArrayWriter(arr,palette_path=palette_path)
    else:
        raise DumpingException("missing the required palette")
    t.write(vox_fname)

def plot_3d(arr):
    '''
    plot vox array
    '''
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    u = np.moveaxis(arr, (0, 1), (0, 1))
    m = ax.voxels((u[:, :, :, 3] > 0.1), facecolors=np.clip(u[:, :, :, :4], 0, 1))
    plt.show()
    plt.close()