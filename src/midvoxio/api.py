from pathlib import Path
from typing import List, Optional, Union, Tuple, Dict, Any, Iterator, overload

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from .parser import Parser
from .writer import ArrayWriter, ChunkWriter
from .vox import Vox, Chunk
from .models import ModelAttr, nTRN, nSHP, RGBA


class VoxModel:
    """
    Interface for working with VOX files.
    
    Examples:
        # Loading a VOX file
        model = VoxModel.load("path/to/model.vox")
        
        # Visualizing
        model.visualize()
        
        # Accessing voxel data
        voxel_array = model.to_array()
        
        # Saving to a new file
        model.save("path/to/output.vox")
        
        # Creating a new model
        model = VoxModel.create(size=(10, 10, 10))
        model.add_voxel(1, 2, 3, color=(255, 0, 0))
        model.save("new_model.vox")
        
        # Method chaining for creation
        model = (VoxModel.create(size=(5, 5, 5))
                .add_voxel(1, 1, 1, (255, 0, 0))
                .add_voxel(2, 1, 1, (0, 255, 0))
                .save("model.vox"))
    """
    
    def __init__(self, vox: Vox, editable: bool = False):
        """Initialize a VoxModel from a Vox object."""
        self._vox = vox
        self._editable = editable
        self._size = None
        self._voxels = None
        self._palette = None
        
        # Initialize editable state if needed
        if editable:
            # Extract size from vox if available, otherwise use default
            if self._vox.sizes:
                self._size = tuple(self._vox.sizes[0])
            else:
                self._size = (32, 32, 32)
                
            # Extract voxels if available
            if self._vox.full_vox:
                self._voxels = np.array(self._vox.full_vox[0], dtype=np.uint8)
                
                # Convert to RGBA format
                arr = self.to_array(0)
                self._voxels = (arr * 255).astype(np.uint8)
            else:
                self._voxels = np.zeros((*self._size, 4), dtype=np.uint8)
                
            # Extract palette if available
            if self._vox.palettes:
                self._palette = np.array(self._vox.palettes[0], dtype=np.uint8)
            else:
                # Default palette
                self._palette = np.array([
                    [0, 0, 0, 0],  # First color is transparent
                    *[[r, g, b, 255] for r, g, b in [
                        (255, 255, 255),  # White
                        (255, 0, 0),      # Red
                        (0, 255, 0),      # Green
                        (0, 0, 255),      # Blue
                        (255, 255, 0),    # Yellow
                        (255, 0, 255),    # Magenta
                        (0, 255, 255),    # Cyan
                    ]]
                ], dtype=np.uint8)
    
    @classmethod
    def load(cls, file_path: Union[str, Path], verbose: bool = False) -> 'VoxModel':
        """
        Load a VOX file.
        
        Args:
            file_path: Path to the VOX file
            verbose: Whether to print verbose information
            
        Returns:
            A VoxModel instance
        """
        path = Path(file_path) if isinstance(file_path, str) else file_path
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        vox = Parser(str(path)).parse()
        if verbose:
            print(f"Loaded VOX file with {len(vox.chunks)} chunks")
            print(f"Models: {len(vox.voxels)}")
            print(f"Palettes: {len(vox.palettes)}")
        
        return cls(vox)
    
    @classmethod
    def create(cls, size: Tuple[int, int, int] = (32, 32, 32)) -> 'VoxModel':
        """
        Create a new empty VoxModel for editing.
        
        Args:
            size: The size of the voxel grid (x, y, z)
            
        Returns:
            A VoxModel instance ready for editing
        """
        # Create a minimal array with the specified size
        array = np.zeros((*size, 4), dtype=np.uint8)
        
        # Create a default palette
        default_palette = np.array([
            [0, 0, 0, 0],  # First color is transparent
            *[[r, g, b, 255] for r, g, b in [
                (255, 255, 255),  # White
                (255, 0, 0),      # Red
                (0, 255, 0),      # Green
                (0, 0, 255),      # Blue
                (255, 255, 0),    # Yellow
                (255, 0, 255),    # Magenta
                (0, 255, 255),    # Cyan
            ]]
        ], dtype=np.uint8)
        
        # Create writer and get chunks
        writer = ArrayWriter(array / 255.0, palette_arr=default_palette)
        
        # Create chunks for Vox
        from .vox import Chunk
        
        # Create chunks directly without parsing
        chunks = []
        
        # SIZE chunk
        size_chunk = Chunk(b'SIZE', b'', skip_parse=True)
        size_chunk.size = size
        chunks.append(size_chunk)
        
        # XYZI chunk
        xyzi_chunk = Chunk(b'XYZI', b'', skip_parse=True)
        xyzi_chunk.voxels = []
        chunks.append(xyzi_chunk)
        
        # RGBA chunk
        rgba_chunk = Chunk(b'RGBA', b'', skip_parse=True)
        rgba_chunk.palette = default_palette
        chunks.append(rgba_chunk)
        
        # Create a new Vox object from the chunks
        vox = Vox(chunks)
        
        # Return a new VoxModel in editable mode
        model = cls(vox, editable=True)
        model._size = size
        model._voxels = array.copy()
        model._palette = default_palette.copy()
        return model
    
    @classmethod
    def from_array(cls, 
                  array: np.ndarray, 
                  palette: Optional[Union[str, np.ndarray]] = None) -> 'VoxModel':
        """
        Create a VoxModel from a numpy array.
        
        Args:
            array: Numpy array with shape (x, y, z, 4) for RGB+Alpha values
            palette: Either a path to a palette image or a numpy array of colors
            
        Returns:
            A VoxModel instance
        """
        # Create a minimal Vox object from the array
        array_normalized = np.array(array)
        if array_normalized.dtype != np.uint8 and array_normalized.max() <= 1:
            array_normalized = (array_normalized * 255).astype(np.uint8)
        
        # Process palette
        if palette is None:
            # Default palette
            palette_arr = np.array([
                [0, 0, 0, 0],  # First color is transparent
                *[[r, g, b, 255] for r, g, b in [
                    (255, 255, 255),  # White
                    (255, 0, 0),      # Red
                    (0, 255, 0),      # Green
                    (0, 0, 255),      # Blue
                    (255, 255, 0),    # Yellow
                    (255, 0, 255),    # Magenta
                    (0, 255, 255),    # Cyan
                ]]
            ], dtype=np.uint8)
        elif isinstance(palette, str):
            img = Image.open(palette)
            palette_arr = np.array(img)
            # Add missing alpha if needed
            if palette_arr.shape[-1] == 3:
                palette_arr = np.append(palette_arr, np.full((256, 1), 255), axis=1)
        else:
            palette_arr = palette
            
        # Create chunks for Vox
        from .vox import Chunk
        
        # Get the size
        size = array.shape[:-1]  # Get size excluding color dimension
        
        # Create chunks directly without parsing
        chunks = []
        
        # SIZE chunk
        size_chunk = Chunk(b'SIZE', b'', skip_parse=True)
        size_chunk.size = size
        chunks.append(size_chunk)
        
        # XYZI chunk
        xyzi_chunk = Chunk(b'XYZI', b'', skip_parse=True)
        xyzi_chunk.voxels = []
        
        # Add voxels - extract non-zero voxels from the array
        non_zero_mask = array_normalized[:, :, :, 3] > 0
        if np.any(non_zero_mask):
            x, y, z = np.nonzero(non_zero_mask)
            colors = array_normalized[x, y, z]
            color_indices = []
            
            # Match each color to the palette - simple implementation for now
            for color in colors:
                found = False
                for i, pal_color in enumerate(palette_arr):
                    if np.array_equal(pal_color, color):
                        color_indices.append(i)
                        found = True
                        break
                if not found:
                    # Default to index 1 if not found
                    color_indices.append(1)
            
            # Create voxels list in the required format
            xyzi_chunk.voxels = [(x[i], y[i], z[i], color_indices[i]) for i in range(len(x))]
        
        chunks.append(xyzi_chunk)
        
        # RGBA chunk
        rgba_chunk = Chunk(b'RGBA', b'', skip_parse=True)
        rgba_chunk.palette = palette_arr
        chunks.append(rgba_chunk)
        
        # Create a new Vox object from the chunks
        vox = Vox(chunks)
        
        # Return a new model that's editable
        model = cls(vox, editable=True)
        model._voxels = array_normalized
        model._palette = palette_arr
        model._size = size
        return model
    
    def to_array(self, model_index: int = 0) -> np.ndarray:
        """
        Convert the VOX model to a numpy array.
        
        Args:
            model_index: Index of the model to convert (use -1 for combined model)
            
        Returns:
            Numpy array with shape (x, y, z, 4) for RGB+Alpha values
        """
        if self._editable and self._voxels is not None:
            return self._voxels / 255.0
        return self._vox.to_list(model_index)
    
    def visualize(self, model_index: int = 0) -> None:
        """
        Visualize the VOX model using matplotlib.
        
        Args:
            model_index: Index of the model to visualize (use -1 for combined model)
        """
        arr = self.to_array(model_index)
        self._plot_3d(arr)
        
    def save(self, 
            file_path: Union[str, Path], 
            model_index: Optional[int] = None) -> 'VoxModel':
        """
        Save the VOX model to a file.
        
        Args:
            file_path: Path to save the VOX file
            model_index: Optional model index to save (if None, saves all models)
            
        Returns:
            Self for method chaining
        """
        path = str(file_path) if isinstance(file_path, str) else str(file_path)
        
        if self._editable and self._voxels is not None:
            # Save the edited model
            writer = ArrayWriter(self._voxels / 255.0, palette_arr=self._palette)
            writer.write(path)
        elif model_index is not None:
            # Save only the specified model
            array = self.to_array(model_index)
            palette_arr = self._vox.palettes[0] if self._vox.palettes else None
            writer = ArrayWriter(array, palette_arr=palette_arr)
            writer.write(path)
        else:
            # Save the full VOX file with all models and chunks
            writer = ChunkWriter(self._vox.chunks, 
                               palette_arr=self._vox.palettes[0] if self._vox.palettes else None)
            writer.write(path)
            
        return self
    
    def get_chunks(self) -> List[Chunk]:
        """Get all chunks in the VOX model."""
        return self._vox.chunks
    
    def get_chunk_names(self) -> List[str]:
        """Get the names of all chunks in the VOX model."""
        return [chunk.name for chunk in self._vox.chunks]
    
    def get_models_count(self) -> int:
        """Get the number of models in the VOX file."""
        return len(self._vox.voxels)
    
    def get_materials(self) -> List[str]:
        """Get material information from the VOX model."""
        return [str(material) for material in self._vox.materials]
    
    def get_cameras(self) -> List[str]:
        """Get camera information from the VOX model."""
        return [str(camera) for camera in self._vox.cameras]
    
    def get_rendering_attributes(self) -> List[str]:
        """Get rendering attributes from the VOX model."""
        return [str(robj) for robj in self._vox.robjs]
    
    def _plot_3d(self, arr: np.ndarray) -> None:
        """Internal method to plot a 3D array."""
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        u = np.moveaxis(arr, (0, 1), (0, 1))
        ax.voxels((u[:, :, :, 3] > 0.1), facecolors=np.clip(u[:, :, :, :4], 0, 1))
        plt.show()
        plt.close()
        
    # Model building methods
    
    def add_voxel(self, 
                 x: int, 
                 y: int, 
                 z: int, 
                 color: Union[Tuple[int, int, int, int], Tuple[int, int, int]]) -> 'VoxModel':
        """
        Add a voxel at the specified position with the given color.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
            color: RGB or RGBA color tuple
            
        Returns:
            Self for method chaining
        """
        if not self._editable:
            raise ValueError("This model is not in editable mode. Create a new model with VoxModel.create() or use from_array().")
            
        if x < 0 or y < 0 or z < 0 or x >= self._size[0] or y >= self._size[1] or z >= self._size[2]:
            raise ValueError(f"Position ({x}, {y}, {z}) out of bounds for size {self._size}")
        
        if len(color) == 3:
            color = (*color, 255)  # Add alpha if not provided
        
        self._voxels[x, y, z] = color
        return self
    
    def add_palette_color(self, color: Union[Tuple[int, int, int, int], Tuple[int, int, int]]) -> int:
        """
        Add a color to the palette and return its index.
        
        Args:
            color: RGB or RGBA color tuple
            
        Returns:
            Index of the color in the palette
        """
        if not self._editable:
            raise ValueError("This model is not in editable mode. Create a new model with VoxModel.create() or use from_array().")
            
        if len(color) == 3:
            color = (*color, 255)  # Add alpha if not provided
        
        # Check if color already exists in palette
        for i, pal_color in enumerate(self._palette):
            if np.array_equal(pal_color, color):
                return i
        
        # Add color to palette if not found
        if len(self._palette) < 256:
            self._palette = np.vstack([self._palette, color])
            return len(self._palette) - 1
        else:
            raise ValueError("Palette is full (maximum 256 colors)")
    
    def clear(self) -> 'VoxModel':
        """
        Clear all voxels while keeping the palette.
        
        Returns:
            Self for method chaining
        """
        if not self._editable:
            raise ValueError("This model is not in editable mode. Create a new model with VoxModel.create() or use from_array().")
            
        self._voxels = np.zeros((*self._size, 4), dtype=np.uint8)
        return self
    
    def resize(self, new_size: Tuple[int, int, int]) -> 'VoxModel':
        """
        Resize the voxel grid.
        
        Args:
            new_size: New size (x, y, z)
            
        Returns:
            Self for method chaining
        """
        if not self._editable:
            raise ValueError("This model is not in editable mode. Create a new model with VoxModel.create() or use from_array().")
            
        old_voxels = self._voxels
        self._size = new_size
        self._voxels = np.zeros((*new_size, 4), dtype=np.uint8)
        
        # Copy old voxels to new array where possible
        min_x = min(old_voxels.shape[0], new_size[0])
        min_y = min(old_voxels.shape[1], new_size[1])
        min_z = min(old_voxels.shape[2], new_size[2])
        
        self._voxels[:min_x, :min_y, :min_z] = old_voxels[:min_x, :min_y, :min_z]
        return self
        
    def __repr__(self) -> str:
        if self._editable:
            return f"VoxModel(size={self._size}, editable=True)"
        return f"VoxModel(models={self.get_models_count()}, chunks={len(self.get_chunks())})" 