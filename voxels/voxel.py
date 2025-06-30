# voxels/voxel.py

class Voxel:
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
