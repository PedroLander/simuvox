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
    # --- Water block height and spill logic ---
    from world.voxel import Voxel
    to_remove = set()
    to_add = []
    for (x, y, z) in list(voxels):
        props = property_map.get((x, y, z), {})
        if props.get('type') == 'water':
            water = props.get('water', 0)
            # Set block height proportional to water content (max 1.0)
            h = max(0.05, min(1.0, water))
            # Update block_height if present
            v = None
            for vv in voxels:
                if vv.x == x and vv.y == y and vv.z == z:
                    v = vv
                    break
            if v is not None:
                v.block_height = h
            # Remove water block if almost empty
            if water < 0.01:
                to_remove.add(v)
            # Spill to lower neighbor if possible
            below = Voxel(x, y-1, z)
            if below in voxels:
                bprops = property_map.get((below.x, below.y, below.z), {})
                if bprops.get('type') == 'water' and bprops.get('water', 0) < water:
                    # Transfer some water down
                    transfer = min(0.1, water - bprops.get('water', 0))
                    props['water'] -= transfer
                    bprops['water'] += transfer
            elif y > 0:
                # Create new water block below if not solid
                bprops = property_map.get((x, y-1, z), {})
                if bprops.get('type', 'air') == 'air':
                    if water > 0.1:
                        to_add.append((Voxel(x, y-1, z), {'type': 'water', 'water': water*0.5, 'humidity': 1.0, 'heat': 0.5, 'nutrient': 0.5}))
                        props['water'] *= 0.5
    for v in to_remove:
        voxels.remove(v)
    for v, p in to_add:
        voxels.add(v)
        property_map[(v.x, v.y, v.z)] = p
    return changed
