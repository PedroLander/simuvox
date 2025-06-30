# processes/physics.py
"""
Physics process module for the voxel world simulation.
Handles gravity and block movement.
"""

def apply_gravity(voxels, gravity=0.01, dt=1.0):
    """
    Move blocks down if there is air below (simple gravity).
    Args:
        voxels: set of Voxel objects representing the world.
        gravity: unused, placeholder for future improvements.
        dt: time step in seconds (unused for now).
    Returns:
        True if any block moved, else False.
    """
    moved = set()
    for voxel in list(voxels):
        below = type(voxel)(voxel.x, voxel.y-1, voxel.z)
        if voxel.y > 0 and below not in voxels:
            moved.add(voxel)
    for voxel in moved:
        voxels.remove(voxel)
        voxels.add(type(voxel)(voxel.x, voxel.y-1, voxel.z))
    return len(moved) > 0
