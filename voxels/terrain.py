# voxels/terrain.py
import random
from .voxel import Voxel

class Terrain:
    def __init__(self, grid_size, voxel_count=None):
        self.grid_size = grid_size
        self.voxel_count = voxel_count
        self.voxels = set()
        self.generate_surface()

    def generate_surface(self):
        # Fill a 10x10 surface at the bottom (y=0), and optionally a few random blocks above
        for x in range(10):
            for z in range(10):
                self.voxels.add(Voxel(x, 0, z))
        # Optionally, add a few random blocks above the surface for variety
        for _ in range(30):
            x = random.randint(0, 9)
            z = random.randint(0, 9)
            y = random.randint(1, 9)
            self.voxels.add(Voxel(x, y, z))

    def get_voxels(self):
        return self.voxels
