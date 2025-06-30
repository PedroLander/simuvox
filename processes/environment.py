"""
Environment process module for the voxel world simulation.
Coordinates all per-frame processes (gravity, transfer, etc).
"""

def update_environment(voxels, property_map, dt=1.0):
    """
    Update all environment processes for the current frame.
    Args:
        voxels: set of Voxel objects representing the world.
        property_map: dict mapping (x, y, z) to property dicts.
        dt: time step in seconds.
    Returns:
        True if any block moved (gravity), else False.
    """
    from .physics import apply_gravity
    from .transfer import transfer_property
    changed = apply_gravity(voxels, dt=dt)
    for prop in ['humidity', 'heat', 'water', 'nutrient']:
        transfer_property(voxels, property_map, prop, dt=dt)
    return changed
