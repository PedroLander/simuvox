"""
Voxel data structure for the voxel world simulation.
Represents a single block in the world.
"""

import math

class Voxel:
    """
    Voxel object representing a block at (x, y, z).
    Each voxel has a position in the grid and real-world coordinates (lat, lon, height).
    Implements hash and equality for set/dict use.
    """
    # Reference point for (0,0,0):
    LAT0 = 0.0  # degrees
    LON0 = 0.0  # degrees
    HEIGHT0 = 0.0  # meters (sea level)
    SIZE = 1.0  # meters (side length)
    # Approximate meters per degree latitude/longitude at equator
    METERS_PER_DEG_LAT = 111320.0
    METERS_PER_DEG_LON = 111320.0

    def __init__(self, x, y, z, lat=None, lon=None, height=None):
        self.x = x
        self.y = y
        self.z = z
        # Optionally allow explicit lat/lon/height, else compute from grid
        if lat is not None and lon is not None and height is not None:
            self.lat = lat
            self.lon = lon
            self.height = height
        else:
            self.lat, self.lon, self.height = self.grid_to_geo(x, y, z)

    @classmethod
    def grid_to_geo(cls, x, y, z):
        """
        Convert grid coordinates to (lat, lon, height in meters).
        """
        dlat = (z * cls.SIZE) / cls.METERS_PER_DEG_LAT
        dlon = (x * cls.SIZE) / cls.METERS_PER_DEG_LON
        lat = cls.LAT0 + dlat
        lon = cls.LON0 + dlon
        height = cls.HEIGHT0 + y * cls.SIZE
        return lat, lon, height

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __repr__(self):
        return f"Voxel({self.x}, {self.y}, {self.z}, lat={self.lat:.6f}, lon={self.lon:.6f}, h={self.height:.2f})"
