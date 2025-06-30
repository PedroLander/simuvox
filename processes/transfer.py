"""
Transfer process module for the voxel world simulation.
Handles humidity, heat, water, and nutrient transfer between adjacent blocks.
"""

def transfer_property(voxels, property_map, prop, rate=0.1, dt=1.0):
    """
    Simulate transfer of a property (e.g., humidity, heat, water, nutrient) between adjacent voxels.
    Args:
        voxels: set of Voxel objects representing the world.
        property_map: dict mapping (x, y, z) to property dicts.
        prop: property name to transfer.
        rate: transfer rate (float).
        dt: time step in seconds.
    """
    from collections import defaultdict
    from world.voxel import Voxel
    deltas = defaultdict(float)
    eff_rate = rate * dt
    for (x, y, z) in voxels:
        val = property_map.get((x, y, z), {}).get(prop, 0)
        for dx, dy, dz in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
            n = Voxel(x+dx, y+dy, z+dz)
            if n in voxels:
                nval = property_map.get((n.x, n.y, n.z), {}).get(prop, 0)
                diff = (val - nval) * eff_rate
                deltas[(x, y, z)] -= diff
                deltas[(n.x, n.y, n.z)] += diff
    for k, d in deltas.items():
        if k not in property_map:
            property_map[k] = {'humidity': 0.5, 'heat': 0.5, 'water': 0.5, 'nutrient': 0.5}
        property_map[k][prop] = property_map[k].get(prop, 0) + d
