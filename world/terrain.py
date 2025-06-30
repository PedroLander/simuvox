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
        for x in range(10):
            for z in range(10):
                self.voxels.add(Voxel(x, 0, z))
        for _ in range(30):
            x = random.randint(0, 9)
            z = random.randint(0, 9)
            y = random.randint(1, 9)
            self.voxels.add(Voxel(x, y, z))

    def get_voxels(self):
        return self.voxels
