"""
Terrain generation for the voxel world simulation.
Creates and manages a set of voxels representing the world.
"""

import random
from .voxel import Voxel

class Terrain:
    """
    Terrain object for managing a set of voxels.
    Methods:
        generate_surface: Fills a 10x10 surface at y=0 and adds random blocks above.
        get_voxels: Returns the set of voxels.
    """
    def __init__(self, grid_size, voxel_count=None):
        self.grid_size = grid_size
        self.voxel_count = voxel_count
        self.voxels = set()
        self.generate_surface()

    def generate_surface(self):
        grid = 10
        min_soil = 2
        max_soil = 4
        # Fill each column from y=0 up to a random surface height (no floating blocks)
        for x in range(grid):
            for z in range(grid):
                surface = random.randint(min_soil, max_soil)
                for y in range(surface):
                    self.voxels.add(Voxel(x, y, z))
                # Optionally add a water, rock, or organic block above ground
                if random.random() < 0.15:
                    self.voxels.add(Voxel(x, surface, z))

    def get_voxels(self):
        return self.voxels
