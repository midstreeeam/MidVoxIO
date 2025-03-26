"""
MidVoxIO - A Python library for working with MagicaVoxel's VOX format.

This library provides tools for reading, writing, and manipulating VOX files.
"""

# Import the original API for backward compatibility
from .voxio import (
    vox_to_arr,
    viz_vox,
    show_chunks,
    get_rendering_attributes,
    get_materials,
    get_cameras,
    get_vox,
    write_list_to_vox,
    plot_3d
)

# Import the new API
from .api import VoxModel

__all__ = [
    # Original API
    'vox_to_arr',
    'viz_vox',
    'show_chunks',
    'get_rendering_attributes',
    'get_materials',
    'get_cameras',
    'get_vox',
    'write_list_to_vox',
    'plot_3d',
    
    # New API
    'VoxModel'
]

__version__ = '0.2.0'
