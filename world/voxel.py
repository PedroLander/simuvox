"""
Voxel data structure for the voxel world simulation.
Represents a single block in the world.
"""

class Voxel:
    """
    Voxel object representing a block at (x, y, z).
    Implements hash and equality for set/dict use.
    """
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __repr__(self):
        return f"Voxel({self.x}, {self.y}, {self.z})"
